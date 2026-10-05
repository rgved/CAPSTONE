"""
backend/services/efficient_fetch/chunking.py

Phase 5.1 Security Structure Extractor.

Instead of fixed-size text chunking, this service:
1. Strips boilerplate (scripts, styles, stylesheets, prefetch) using BeautifulSoup.
2. Extracts atomic SecurityElement objects (forms, standalone inputs, standalone buttons, endpoints).
3. Detects security signals (password_field, csrf_token, login_form, session_endpoint, etc.).
4. Fallbacks to paragraph chunking for plain text (maintaining test backward compatibility).
"""
from __future__ import annotations

import json
import re
from bs4 import BeautifulSoup

from backend.services.efficient_fetch.fetch_models import Chunk, SecurityElement

_TARGET_MIN = 500
_TARGET_MAX = 1000

# Matches sentence-ending punctuation followed by whitespace or end-of-string.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _naive_token_count(text: str) -> int:
    """Whitespace-based token count (word count approximation)."""
    return len(text.split())


def _split_long_paragraph(paragraph: str) -> list[str]:
    """
    Break a single paragraph that exceeds _TARGET_MAX tokens.

    Tries single-newline splits, then sentence splits, then word-level splits.
    Any resulting piece still over the limit is force-split by words.
    """
    pieces: list[str] = []
    current: list[str] = []
    current_count = 0

    # Try single-newline segments first.
    segments = paragraph.splitlines()
    for segment in segments:
        seg_count = _naive_token_count(segment)
        if current_count + seg_count > _TARGET_MAX and current:
            pieces.append("\n".join(current))
            current = [segment]
            current_count = seg_count
        else:
            current.append(segment)
            current_count += seg_count

    if current:
        remainder = "\n".join(current)
        if _naive_token_count(remainder) > _TARGET_MAX:
            # Fall back to sentence-level splitting.
            for sentence in _SENTENCE_SPLIT.split(remainder):
                stripped = sentence.strip()
                if not stripped:
                    continue
                if _naive_token_count(stripped) > _TARGET_MAX:
                    # Last resort: word-level splitting.
                    pieces.extend(_split_by_words(stripped))
                else:
                    pieces.append(stripped)
        else:
            pieces.append(remainder)

    return [p for p in pieces if p.strip()]


def _split_by_words(text: str) -> list[str]:
    """Force-split *text* into _TARGET_MAX-word chunks."""
    words = text.split()
    chunks: list[str] = []
    for start in range(0, len(words), _TARGET_MAX):
        chunks.append(" ".join(words[start : start + _TARGET_MAX]))
    return chunks


def _detect_signals(elem_type: str, content: dict) -> list[str]:
    """Lightweight rule-based detector for security-relevant signals."""
    signals = []

    def contains_any(val: str, keywords: list[str]) -> bool:
        v = val.lower()
        return any(kw in v for kw in keywords)

    auth_keywords = ["login", "signin", "sign-in", "session", "auth"]
    csrf_keywords = ["csrf", "xsrf", "authenticity_token", "token"]
    upload_keywords = ["upload", "import"]
    admin_keywords = ["admin", "manage"]

    if elem_type == "form":
        action = content.get("action", "")
        # login_form and session_endpoint
        if contains_any(action, auth_keywords):
            signals.append("login_form")
            signals.append("session_endpoint")

        # Check form inputs
        has_password = False
        has_file = False
        has_csrf = False
        for inp in content.get("inputs", []):
            inp_type = inp.get("type", "").lower()
            inp_name = inp.get("name", "").lower()
            if inp_type == "password":
                has_password = True
            if inp_type == "file":
                has_file = True
            if contains_any(inp_name, csrf_keywords):
                has_csrf = True

        if has_password:
            signals.append("password_field")
            if "login_form" not in signals:
                signals.append("login_form")
        if has_csrf:
            signals.append("csrf_token")
        if has_file:
            signals.append("multipart_form")
            signals.append("file_input")

        # upload_endpoint
        if contains_any(action, upload_keywords):
            signals.append("upload_endpoint")
        # admin_route
        if contains_any(action, admin_keywords):
            signals.append("admin_route")

    elif elem_type == "input":
        inp_type = content.get("type", "").lower()
        inp_name = content.get("name", "").lower()
        if inp_type == "password":
            signals.append("password_field")
        if inp_type == "file":
            signals.append("file_input")
        if contains_any(inp_name, csrf_keywords):
            signals.append("csrf_token")

    elif elem_type == "endpoint":
        endpoint = content.get("endpoint", "")
        if contains_any(endpoint, auth_keywords):
            signals.append("session_endpoint")
        if contains_any(endpoint, upload_keywords):
            signals.append("upload_endpoint")
        if contains_any(endpoint, admin_keywords):
            signals.append("admin_route")

    return list(set(signals))


def _chunk_text_document(source_text: str) -> list[Chunk]:
    """Fallback paragraph-level chunker for raw text/non-HTML sources."""
    paragraphs: list[str] = re.split(r"\n{2,}", source_text)

    raw_pieces: list[str] = []
    for paragraph in paragraphs:
        stripped = paragraph.strip()
        if not stripped:
            continue
        if _naive_token_count(stripped) > _TARGET_MAX:
            raw_pieces.extend(_split_long_paragraph(stripped))
        else:
            raw_pieces.append(stripped)

    merged: list[str] = []
    buffer: list[str] = []
    buffer_count = 0

    for piece in raw_pieces:
        piece_count = _naive_token_count(piece)
        if buffer_count + piece_count > _TARGET_MAX and buffer:
            merged.append("\n\n".join(buffer))
            buffer = [piece]
            buffer_count = piece_count
        else:
            buffer.append(piece)
            buffer_count += piece_count

    if buffer:
        merged.append("\n\n".join(buffer))

    chunks: list[Chunk] = []
    for i, text in enumerate(merged):
        stripped_text = text.strip()
        if not stripped_text:
            continue
        element = SecurityElement(
            type="text",
            content={"text": stripped_text},
            security_signals=[],
            raw_snippet=stripped_text
        )
        chunks.append(Chunk(
            index=i,
            text=stripped_text,
            token_count=_naive_token_count(stripped_text),
            element=element
        ))
    return chunks


def _chunk_html_document(source_text: str) -> list[Chunk]:
    """Parses HTML, removes boilerplate, and extracts atomic SecurityElements."""
    soup = BeautifulSoup(source_text, "html.parser")

    # --- Stage 1: Boilerplate Removal ---
    # Strip script, style, svg, iframe, template tags
    for tag in soup(["script", "style", "svg", "iframe", "template"]):
        if tag is None or tag.attrs is None:
            continue
        tag.decompose()

    # Strip stylesheet links and prefetch links
    for tag in soup.find_all("link"):
        if tag is None or tag.attrs is None:
            continue
        rel_val = tag.get("rel")
        if isinstance(rel_val, list):
            rel = [r.lower() for r in rel_val]
        else:
            rel = [str(rel_val).lower()]
        if "stylesheet" in rel or "dns-prefetch" in rel or "preconnect" in rel:
            tag.decompose()

    # --- Stage 2: Security Structure Extraction ---
    elements: list[SecurityElement] = []

    # 1. Forms (extract action, method, nested inputs/buttons)
    form_tags = soup.find_all("form")
    for form_tag in form_tags:
        if form_tag is None or form_tag.attrs is None:
            continue
        form_inputs = []
        for input_tag in form_tag.find_all("input"):
            if input_tag is None or input_tag.attrs is None:
                continue
            form_inputs.append({
                "name": input_tag.get("name") or input_tag.get("id") or "",
                "type": input_tag.get("type") or "text",
                "value": input_tag.get("value") or ""
            })

        form_buttons = []
        for button_tag in form_tag.find_all(["button", "input"]):
            if button_tag is None or button_tag.attrs is None:
                continue
            if button_tag.name == "input" and button_tag.get("type") not in ("submit", "button"):
                continue
            form_buttons.append({
                "name": button_tag.get("name") or "",
                "type": button_tag.get("type") or "submit",
                "value": button_tag.get("value") or button_tag.get_text().strip() or ""
            })

        content = {
            "action": form_tag.get("action") or "",
            "method": (form_tag.get("method") or "GET").upper(),
            "inputs": form_inputs,
            "buttons": form_buttons
        }

        signals = _detect_signals("form", content)

        elements.append(SecurityElement(
            type="form",
            content=content,
            security_signals=signals,
            raw_snippet=str(form_tag)
        ))
        form_tag.decompose()

    # 2. Standalone Inputs
    input_tags = soup.find_all("input")
    for input_tag in input_tags:
        if input_tag is None or input_tag.attrs is None:
            continue
        content = {
            "name": input_tag.get("name") or input_tag.get("id") or "",
            "type": input_tag.get("type") or "text",
            "value": input_tag.get("value") or ""
        }
        signals = _detect_signals("input", content)
        elements.append(SecurityElement(
            type="input",
            content=content,
            security_signals=signals,
            raw_snippet=str(input_tag)
        ))
        input_tag.decompose()

    # 3. Standalone Buttons
    button_tags = soup.find_all("button")
    for button_tag in button_tags:
        if button_tag is None or button_tag.attrs is None:
            continue
        content = {
            "name": button_tag.get("name") or "",
            "type": button_tag.get("type") or "button",
            "value": button_tag.get("value") or button_tag.get_text().strip() or ""
        }
        signals = _detect_signals("button", content)
        elements.append(SecurityElement(
            type="button",
            content=content,
            security_signals=signals,
            raw_snippet=str(button_tag)
        ))
        button_tag.decompose()

    # 4. Standalone Links / Endpoints
    link_tags = soup.find_all("a", href=True)
    for link_tag in link_tags:
        if link_tag is None or link_tag.attrs is None:
            continue
        href = link_tag.get("href")
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
        content = {
            "endpoint": href,
            "text": link_tag.get_text().strip()
        }
        signals = _detect_signals("endpoint", content)
        elements.append(SecurityElement(
            type="endpoint",
            content=content,
            security_signals=signals,
            raw_snippet=str(link_tag)
        ))
        link_tag.decompose()

    # Convert to Chunks
    chunks: list[Chunk] = []
    for i, el in enumerate(elements):
        serialized_text = json.dumps({
            "type": el.type,
            "content": el.content,
            "security_signals": el.security_signals
        })
        chunks.append(Chunk(
            index=i,
            text=serialized_text,
            token_count=_naive_token_count(serialized_text),
            element=el
        ))
    return chunks


def chunk_document(source_text: str) -> list[Chunk]:
    """Main chunk_document interface. Branches by content type."""
    if not source_text.strip():
        return []

    # Heuristic check to see if the content is HTML
    is_html = "<" in source_text and ">" in source_text
    if is_html:
        return _chunk_html_document(source_text)
    else:
        return _chunk_text_document(source_text)

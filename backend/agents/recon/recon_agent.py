"""
backend/agents/recon/recon_agent.py

Recon Agent worker for structural extraction and worker-scoped failure handling.
"""
import asyncio
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Comment
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from backend.models.form import Form, HttpMethod
from backend.models.recon_result import ReconResult
from backend.models.task import Task
from backend.models.worker_response import WorkerError, WorkerResponse
from backend.services.logger import get_logger

logger = get_logger(__name__)

_VALID_METHODS: set[str] = {"GET", "POST", "PUT", "DELETE"}


class ReconAgent:
    def __init__(self) -> None:
        self._last_headers: dict[str, str] = {}
        self._last_status: int = 200
        self._discovered_api_routes: set[str] = set()

    async def fetch_html(self, url: str) -> str:
        logger.info("Fetching HTML - url=%s", url)
        self._last_headers = {}
        self._last_status = 200
        self._discovered_api_routes = set()
        try:
            html = await self._fetch_html_with_playwright(url)
        except Exception as exc:
            logger.warning(
                "Playwright browser launch or navigation failed - falling back to HTTP fetch - url=%s reason=%s",
                url,
                exc,
            )
            html = await self._fetch_html_with_http(url)

        logger.info("HTML fetched - %d bytes", len(html))
        return html

    async def _fetch_html_with_playwright(self, url: str) -> str:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            try:
                page = await browser.new_page()

                # Intercept background API routes triggered by React / fetch / XHR
                def on_request(request: Any) -> None:
                    try:
                        req_url = request.url
                        resource_type = getattr(request, "resource_type", "") or ""
                        if (
                            "/api/" in req_url
                            or "json" in resource_type
                            or resource_type in {"fetch", "xhr"}
                            or "/actuator/" in req_url
                            or "/graphql" in req_url
                        ):
                            self._discovered_api_routes.add(req_url)
                    except Exception:
                        pass

                page.on("request", on_request)

                # Wait for React DOM & background API calls to complete
                response = None
                try:
                    response = await page.goto(url, wait_until="networkidle", timeout=15_000)
                except PlaywrightTimeoutError:
                    logger.warning("networkidle timed out for url=%s, falling back to loaded DOM", url)
                    try:
                        if response is None:
                            response = await page.goto(url, wait_until="domcontentloaded", timeout=10_000)
                    except Exception:
                        pass

                html = await page.content()
                self._last_headers = await response.all_headers() if response else {}
                self._last_status = response.status if response else 200
                return html
            finally:
                await browser.close()

    async def _fetch_html_with_http(self, url: str) -> str:
        return await asyncio.to_thread(self._fetch_html_sync, url)

    def _fetch_html_sync(self, url: str) -> str:
        import urllib.error
        import ssl
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        try:
            with urlopen(request, timeout=20, context=ctx) as response:
                body = response.read()
                encoding = response.headers.get_content_charset() or "utf-8"
                self._last_headers = dict(response.headers)
                self._last_status = response.status
                return body.decode(encoding, errors="replace")
        except urllib.error.HTTPError as exc:
            # 404, 403, 500, etc. are normal HTTP responses in web reconnaissance
            body = exc.read() if hasattr(exc, "read") else b""
            encoding = "utf-8"
            if hasattr(exc, "headers") and exc.headers:
                if hasattr(exc.headers, "get_content_charset"):
                    encoding = exc.headers.get_content_charset() or "utf-8"
                self._last_headers = dict(exc.headers)
            else:
                self._last_headers = {}
            self._last_status = exc.code if hasattr(exc, "code") else 404
            return body.decode(encoding, errors="replace") if isinstance(body, bytes) else str(body)

    def parse_html(
        self,
        url: str,
        html: str,
        headers: dict[str, str] | None = None,
        status_code: int = 200,
        discovered_api_routes: list[str] | set[str] | None = None,
    ) -> ReconResult:
        logger.info("Parsing HTML - url=%s", url)
        soup = BeautifulSoup(html, "lxml")

        links = self._extract_links(soup)
        # Merge background API routes discovered during network interception
        api_routes = discovered_api_routes if discovered_api_routes is not None else self._discovered_api_routes
        if api_routes:
            for route in sorted(api_routes):
                if route and route not in links:
                    links.append(route)

        forms = self._extract_forms(soup)
        inputs, input_fields = self._extract_input_fields(soup)
        buttons = self._extract_buttons(soup)
        scripts = self._extract_scripts(soup)
        script_tags = self._extract_script_tags(soup)
        inline_scripts = self._extract_inline_scripts(soup)
        meta_tags = self._extract_meta_tags(soup)
        comments = self._extract_comments(soup)
        final_status = status_code if status_code != 200 else self._last_status
        error_signatures = self._extract_error_signatures(soup, html, final_status)
        reflected_parameters = self._detect_reflected_parameters(url, html)

        result = ReconResult(
            url=url,
            forms=forms,
            inputs=inputs,
            input_fields=input_fields,
            buttons=buttons,
            links=links,
            scripts=scripts,
            script_tags=script_tags,
            inline_scripts=inline_scripts,
            meta_tags=meta_tags,
            headers=headers if headers is not None else self._last_headers,
            status_code=final_status,
            comments=comments,
            error_signatures=error_signatures,
            reflected_parameters=reflected_parameters,
        )

        logger.info(
            "Parsing complete - links=%d forms=%d inputs=%d buttons=%d scripts=%d inline_scripts=%d meta_tags=%d comments=%d",
            len(links),
            len(forms),
            len(inputs),
            len(buttons),
            len(scripts),
            len(inline_scripts),
            len(meta_tags),
            len(comments),
        )
        return result

    async def execute(self, task: Task) -> WorkerResponse:
        if task.task_id is None:
            raise ValueError("Task must have task_id before recon execution")

        logger.info("ReconAgent starting - task_id=%s url=%s", task.task_id, task.target)

        validation_error = self._validate_url(task.target)
        if validation_error is not None:
            return self._failure_response(task.task_id, validation_error)

        try:
            html = await self.fetch_html(task.target)
            result = self.parse_html(task.target, html, headers=self._last_headers, status_code=self._last_status)
        except PlaywrightTimeoutError as exc:
            return self._failure_response(
                task.task_id,
                WorkerError(error_type="REQUEST_TIMEOUT", message=self._safe_message(exc, "Request timed out")),
            )
        except PlaywrightError as exc:
            classified_error = self._classify_playwright_error(exc)
            return self._failure_response(task.task_id, classified_error)
        except Exception as exc:
            logger.exception("Unexpected recon failure - task_id=%s", task.task_id)
            return self._failure_response(
                task.task_id,
                WorkerError(error_type="RECON_FAILURE", message=self._safe_message(exc, "Recon execution failed")),
            )

        logger.info("ReconAgent complete - task_id=%s url=%s", task.task_id, task.target)
        return WorkerResponse(
            status="success",
            worker="recon",
            task_id=task.task_id,
            data=result.model_dump(),
            new_findings=[],
            errors=[],
        )

    def _validate_url(self, url: str) -> WorkerError | None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return WorkerError(
                error_type="INVALID_URL",
                message="URL must include a valid http or https scheme and hostname",
            )
        return None

    def _classify_playwright_error(self, exc: PlaywrightError) -> WorkerError:
        message = self._safe_message(exc, "Recon request failed")
        lowered = message.lower()

        if "err_name_not_resolved" in lowered or "name not resolved" in lowered or "dns" in lowered:
            return WorkerError(
                error_type="DNS_RESOLUTION_FAILED",
                message="Unable to resolve hostname",
            )

        if "err_connection_refused" in lowered or "connection refused" in lowered:
            return WorkerError(
                error_type="CONNECTION_REFUSED",
                message="Connection refused by target host",
            )

        if "invalid url" in lowered or "cannot navigate to invalid url" in lowered:
            return WorkerError(
                error_type="INVALID_URL",
                message="URL must include a valid http or https scheme and hostname",
            )

        return WorkerError(error_type="RECON_FAILURE", message=message)

    def _failure_response(self, task_id: str, error: WorkerError) -> WorkerResponse:
        logger.warning("ReconAgent failure - task_id=%s error_type=%s", task_id, error.error_type)
        return WorkerResponse(
            status="failure",
            worker="recon",
            task_id=task_id,
            data={},
            new_findings=[],
            errors=[error],
        )

    def _safe_message(self, exc: Exception, default: str) -> str:
        message = str(exc).strip()
        return message or default

    def _extract_links(self, soup: BeautifulSoup) -> list[str]:
        links: list[str] = []
        for tag in soup.find_all("a", href=True):
            href: str = tag["href"].strip()
            if href and href != "#":
                links.append(href)

        for tag in soup.find_all(attrs={"data-href": True}):
            val = tag["data-href"].strip()
            if val and val != "#" and val not in links:
                links.append(val)

        for tag in soup.find_all(attrs={"data-to": True}):
            val = tag["data-to"].strip()
            if val and val != "#" and val not in links:
                links.append(val)

        # Check buttons and elements for explicit SPA interactive & auth navigation
        for btn in soup.find_all(["button", "div", "span"]):
            btn_aria = (btn.get("aria-label") or "").lower()
            btn_text = btn.get_text(strip=True).lower()
            if "account" in btn_aria or "user account" in btn_aria or "personal profile" in btn_aria or "login" in btn_text or "sign in" in btn_text:
                if "/login" not in links:
                    links.append("/login")
                if "/account" not in links:
                    links.append("/account")
            if "register" in btn_text or "sign up" in btn_text or "signup" in btn_text:
                if "/signup" not in links:
                    links.append("/signup")
            if "contact" in btn_text or "contact us" in btn_aria:
                if "/contact" not in links:
                    links.append("/contact")

        return links

    def _extract_forms(self, soup: BeautifulSoup) -> list[Form]:
        forms: list[Form] = []
        for tag in soup.find_all("form"):
            action: str = (tag.get("action") or "").strip() or "/"
            raw_method: str = (tag.get("method") or "GET").strip().upper()
            method: HttpMethod = raw_method if raw_method in _VALID_METHODS else "UNKNOWN"  # type: ignore[assignment]
            enctype: str = (tag.get("enctype") or "application/x-www-form-urlencoded").strip().lower()
            form_id: str = (tag.get("id") or "").strip()

            form_inputs: list[dict[str, Any]] = []
            for inp in tag.find_all(["input", "textarea"]):
                inp_type = (inp.get("type") or ("textarea" if inp.name == "textarea" else "text")).strip().lower()
                raw_name = (inp.get("name") or "").strip()
                resolved_name = raw_name
                if not resolved_name and inp_type not in {"submit", "button", "reset", "image"}:
                    resolved_name = (
                        (inp.get("id") or "").strip()
                        or (inp.get("autocomplete") or "").strip()
                        or (inp.get("placeholder") or "").strip()
                        or (inp.get("aria-label") or "").strip()
                        or (inp_type if inp_type != "text" else "")
                    )

                form_inputs.append({
                    "name": raw_name or resolved_name,
                    "type": inp_type,
                    "value_present": bool(inp.get("value") or (inp.get_text(strip=True) if inp.name == "textarea" else "")),
                    "id": (inp.get("id") or "").strip(),
                })

            forms.append(Form(
                action=action,
                method=method,
                enctype=enctype,
                id=form_id,
                inputs=form_inputs,
            ))
        return forms

    def _extract_input_fields(self, soup: BeautifulSoup) -> tuple[list[str], list[dict[str, Any]]]:
        names: list[str] = []
        detailed: list[dict[str, Any]] = []
        for tag in soup.find_all(["input", "textarea"]):
            input_type: str = (tag.get("type") or ("textarea" if tag.name == "textarea" else "text")).strip().lower()
            has_value: bool = bool(tag.get("value") or (tag.get_text(strip=True) if tag.name == "textarea" else ""))
            placeholder: str = (tag.get("placeholder") or "").strip()
            elem_id: str = (tag.get("id") or "").strip()
            autocomplete: str = (tag.get("autocomplete") or "").strip()
            aria_label: str = (tag.get("aria-label") or "").strip()

            raw_name: str = (tag.get("name") or "").strip()
            resolved_name = raw_name
            if not resolved_name and input_type not in {"submit", "button", "reset", "image"}:
                resolved_name = (
                    elem_id
                    or autocomplete
                    or placeholder
                    or aria_label
                    or (input_type if input_type != "text" else "")
                )

            if resolved_name:
                names.append(resolved_name)

            detailed.append({
                "name": raw_name or resolved_name,
                "type": input_type,
                "value_present": has_value,
                "placeholder": placeholder,
                "id": elem_id,
                "autocomplete": autocomplete,
            })
        return names, detailed

    def _extract_inputs(self, soup: BeautifulSoup) -> list[str]:
        names, _ = self._extract_input_fields(soup)
        return names

    def _extract_buttons(self, soup: BeautifulSoup) -> list[str]:
        buttons: list[str] = []
        for tag in soup.find_all("button"):
            text: str = tag.get_text(strip=True)
            if not text:
                text = (tag.get("aria-label") or "").strip() or (tag.get("value") or "").strip()
            if text and text not in buttons:
                buttons.append(text)
        return buttons

    def _extract_scripts(self, soup: BeautifulSoup) -> list[str]:
        scripts: list[str] = []
        for tag in soup.find_all("script", src=True):
            src: str = tag["src"].strip()
            if src:
                scripts.append(src)
        return scripts

    def _extract_inline_scripts(self, soup: BeautifulSoup) -> list[str]:
        inline: list[str] = []
        for tag in soup.find_all("script"):
            if not tag.get("src"):
                text = tag.get_text(strip=True)
                if text:
                    inline.append(text[:1000])
        return inline

    def _extract_meta_tags(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        meta_tags: list[dict[str, Any]] = []
        for tag in soup.find_all("meta"):
            name: str = (tag.get("name") or "").strip()
            content: str = (tag.get("content") or "").strip()
            if name and content:
                meta_tags.append({"name": name, "content": content})
        return meta_tags

    def _extract_comments(self, soup: BeautifulSoup) -> list[str]:
        comments: list[str] = []
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            cleaned = comment.strip()
            if cleaned:
                comments.append(cleaned[:500])
        return comments

    def _extract_script_tags(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        tags: list[dict[str, Any]] = []
        for tag in soup.find_all("script", src=True):
            src: str = tag["src"].strip()
            if src:
                integrity = (tag.get("integrity") or "").strip() or None
                crossorigin = (tag.get("crossorigin") or "").strip() or None
                parsed_src = urlparse(src)
                is_external = bool(parsed_src.netloc)
                tags.append({
                    "src": src,
                    "integrity": integrity,
                    "crossorigin": crossorigin,
                    "is_external": is_external,
                })
        return tags

    def _extract_error_signatures(self, soup: BeautifulSoup, html: str, status_code: int) -> list[str]:
        signatures: list[str] = []
        patterns = [
            "Traceback (most recent call last)",
            "Whitelabel Error Page",
            "SQLSTATE[",
            "SyntaxError:",
            "TypeError:",
            "ZeroDivisionError",
            "NullPointerException",
            "org.springframework",
            "django.core.exceptions",
            "Fatal error:",
            "Unhandled Exception",
        ]
        html_lower = html.lower()
        for pattern in patterns:
            if pattern.lower() in html_lower:
                signatures.append(pattern)
        if status_code >= 500 and not signatures:
            signatures.append(f"HTTP {status_code} Internal Server Error")
        return signatures

    def _detect_reflected_parameters(self, url: str, html: str) -> list[dict[str, Any]]:
        reflected: list[dict[str, Any]] = []
        parsed = urlparse(url)
        if not parsed.query:
            return reflected
        from urllib.parse import parse_qs
        qs = parse_qs(parsed.query)
        for param, values in qs.items():
            for val in values:
                if len(val) >= 3 and val in html:
                    reflected.append({
                        "param": param,
                        "value": val,
                        "reflected": True,
                    })
        return reflected


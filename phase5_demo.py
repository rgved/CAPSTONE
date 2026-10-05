"""
phase5_demo.py

Demonstrates the Phase 5 Efficient Fetch Service end-to-end.

Shows two complementary outputs:

  SECTION A - Full Mission Run
    Runs RUN_RECON -> EXTRACT_FEATURES -> RUN_EFFICIENT_FETCH -> STOP against
    https://github.com/login and prints the orchestrator's mission result.

  SECTION B - Standalone Context Reduction Demo
    Fetches the raw HTML (~73 KB) from https://github.com/login directly,
    passes it through efficient_fetch(), and prints the token reduction
    metrics.  This is the definitive proof of concept for Phase 5.

Usage
-----
    python phase5_demo.py
"""
from __future__ import annotations

import asyncio
import sys
import textwrap
import urllib.request

import os
sys.path.insert(0, os.path.dirname(__file__))

TARGET_URL = "https://github.com/login"
SEPARATOR = "=" * 50


def _divider() -> None:
    print(SEPARATOR)


def _context_reduction_pct(naive: int, efficient: int) -> float:
    if naive == 0:
        return 0.0
    return (naive - efficient) / naive * 100


def _print_summary(
    title: str,
    feature_name: str,
    naive: int,
    efficient: int,
    structured_content: str,
) -> None:
    reduction = _context_reduction_pct(naive, efficient)

    _divider()
    print(title)
    _divider()
    print()
    print("Feature:")
    print(f"  {feature_name}")
    print()
    print("Original Tokens:")
    print(f"  {naive:,}")
    print()
    print("Reduced Tokens:")
    print(f"  {efficient:,}")
    print()
    print("Reduction:")
    print(f"  {reduction:.1f}%")
    print()
    _divider()
    print()
    print("Structured Content (first 500 characters):")
    print()
    preview = structured_content[:500]
    print(textwrap.fill(preview, width=72, subsequent_indent="  "))
    if len(structured_content) > 500:
        remaining = len(structured_content) - 500
        print(f"\n  ... [{remaining:,} more characters] ...")
    print()
    _divider()
    print()


# ---------------------------------------------------------------------------
# SECTION A - Full orchestrator mission
# ---------------------------------------------------------------------------

async def _run_mission() -> tuple[str, int, int, str]:
    """
    Run a full mission and return (feature_name, naive, efficient, content).
    """
    from backend.orchestrator.orchestrator import Orchestrator

    orchestrator = Orchestrator()

    _orig_dispatch = orchestrator._dispatcher.dispatch
    step_labels: dict[str, str] = {
        "RUN_RECON": "  [x] Recon Agent complete",
        "EXTRACT_FEATURES": "  [x] Feature Extraction Agent complete",
        "RUN_EFFICIENT_FETCH": "  [x] Efficient Fetch Worker complete",
    }

    async def _tracked_dispatch(task):  # type: ignore[override]
        response = await _orig_dispatch(task)
        label = step_labels.get(task.action)
        if label:
            print(label)
        return response

    orchestrator._dispatcher.dispatch = _tracked_dispatch  # type: ignore[method-assign]
    mission = await orchestrator.run(TARGET_URL)

    if mission.status == "failed":
        print("ERROR: Mission failed.")
        if orchestrator.last_response and orchestrator.last_response.errors:
            for err in orchestrator.last_response.errors:
                print(f"  {err}")
        sys.exit(1)

    feature_name = "unknown"
    if orchestrator.last_saved_feature is not None:
        feature_name = orchestrator.last_saved_feature.name

    ef_data = orchestrator.last_efficient_fetch_data or {}
    naive: int = ef_data.get("token_count_naive", 0)
    efficient: int = ef_data.get("token_count_efficient", 0)
    content: str = ef_data.get("structured_content", "")
    return feature_name, naive, efficient, content


# ---------------------------------------------------------------------------
# SECTION B - Standalone raw-HTML demonstration
# ---------------------------------------------------------------------------

def _fetch_raw_html(url: str) -> str:
    """Download raw HTML from *url* via urllib (no Playwright overhead)."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _run_standalone_demo(feature_name: str) -> None:
    from backend.services.efficient_fetch import efficient_fetch

    print("Fetching raw HTML for standalone context-reduction demo ...")
    html = _fetch_raw_html(TARGET_URL)
    print(f"  Raw HTML: {len(html):,} bytes")
    print()

    result = efficient_fetch(html, query_hint="authentication login form security")

    _print_summary(
        "EFFICIENT FETCH SUMMARY (raw HTML -> compressed context)",
        feature_name,
        result.token_count_naive,
        result.token_count_efficient,
        result.structured_content,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    print()
    _divider()
    print(f"Phase 5 Demo - Target: {TARGET_URL}")
    _divider()
    print()

    # -- Section A ----------------------------------------------------------
    print("SECTION A: Full Orchestrator Mission")
    print()
    print("  Running: RUN_RECON -> EXTRACT_FEATURES -> RUN_EFFICIENT_FETCH -> STOP")
    print()

    feature_name, naive_a, efficient_a, content_a = await _run_mission()

    _print_summary(
        "SECTION A RESULT (mission recon-dict context)",
        feature_name,
        naive_a,
        efficient_a,
        content_a,
    )

    # -- Section B ----------------------------------------------------------
    print("SECTION B: Standalone Raw-HTML Context Reduction")
    print()
    _run_standalone_demo(feature_name)


if __name__ == "__main__":
    asyncio.run(main())

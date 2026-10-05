"""
main.py - Phase 2 entry point.

Usage:
    python main.py <url>
"""
import asyncio
import sys

from backend.orchestrator.orchestrator import Orchestrator
from backend.services.logger import get_logger
from backend.services.storage_service import get_report

logger = get_logger("main")


async def main(url: str) -> None:
    logger.info("Mission start - target=%s", url)
    orchestrator = Orchestrator()
    mission = await orchestrator.run(url)
    result = orchestrator.last_response
    recon_data = orchestrator.last_recon_data or {}
    saved_route = orchestrator.last_saved_route
    saved_feature = orchestrator.last_saved_feature
    report = get_report(db_path=orchestrator._db_path)  # noqa: SLF001

    if result is None:
        print()
        print("=" * 50)
        print("  MISSION FAILED")
        print("=" * 50)
        print(f"  Mission  : {mission.mission_id}")
        print(f"  Status   : {mission.status}")
        print("  No worker response received")
        print("=" * 50)
        print()
        return

    if result.status == "failure":
        print()
        print("=" * 50)
        print("  MISSION FAILED")
        print("=" * 50)
        print(f"  Mission  : {mission.mission_id}")
        print(f"  Status   : {mission.status}")
        print(f"  URL      : {url}")
        for error in result.errors:
            print(f"  Error    : {error.error_type} - {error.message}")
        print("=" * 50)
        print()
        return

    if saved_route is None:
        print()
        print("=" * 50)
        print("  MISSION FAILED")
        print("=" * 50)
        print(f"  Mission  : {mission.mission_id}")
        print(f"  Status   : {mission.status}")
        print("  Route persistence did not complete")
        print("=" * 50)
        print()
        return

    if saved_feature is None:
        print()
        print("=" * 50)
        print("  MISSION FAILED")
        print("=" * 50)
        print(f"  Mission  : {mission.mission_id}")
        print(f"  Status   : {mission.status}")
        print("  Feature persistence did not complete")
        print("=" * 50)
        print()
        return

    print()
    print("=" * 50)
    print("  SCAN SUMMARY")
    print("=" * 50)
    print(f"  Mission  : {mission.mission_id}")
    print(f"  Status   : {mission.status}")
    print(f"  URL      : {saved_route.url}")
    print(f"  Route ID : {saved_route.route_id}")
    print(f"  Feature  : {saved_feature.name}")
    print(f"  Score    : {saved_feature.classification_confidence:.2f}")
    print()
    print("  Routes Found  : 1")
    print(f"  Forms Found   : {len(recon_data.get('forms', []))}")
    print(f"  Inputs Found  : {len(recon_data.get('inputs', []))}")
    print(f"  Buttons Found : {len(recon_data.get('buttons', []))}")
    print(f"  Scripts Found : {len(recon_data.get('scripts', []))}")
    print(f"  Links Found   : {len(recon_data.get('links', []))}")
    print(f"  Meta Tags     : {len(recon_data.get('meta_tags', []))}")
    print("=" * 50)
    print()

    if report is not None:
        print("=" * 50)
        print("  REPORT SUMMARY")
        print("=" * 50)
        print(f"  Mission   : {report.mission_id}")
        print(f"  Target    : {report.target_url}")
        print(f"  Routes    : {report.statistics.get('routes_discovered', 0)}")
        print(f"  Features  : {report.statistics.get('features_identified', 0)}")
        print(f"  Findings  : {report.statistics.get('findings_generated', 0)}")
        breakdown = report.statistics.get("severity_breakdown", {})
        print(f"  High      : {breakdown.get('High', 0)}")
        print(f"  Medium    : {breakdown.get('Medium', 0)}")
        print(f"  Low       : {breakdown.get('Low', 0)}")
        print(f"  Report ID : {report.report_id}")
        print("=" * 50)
        print()

    logger.info(
        "Mission complete - mission_id=%s route_id=%d feature_id=%s",
        mission.mission_id,
        saved_route.route_id,
        saved_feature.feature_id,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <url>")
        print("Example: python main.py https://example.com")
        sys.exit(1)

    target_url = sys.argv[1]
    asyncio.run(main(target_url))

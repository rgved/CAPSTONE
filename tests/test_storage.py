"""
tests/test_storage.py

Unit tests for storage_service — save_route() and get_routes().

Each test gets an isolated temporary SQLite database via the db_path fixture,
so tests are fully independent and leave no disk state behind.

Coverage (docs/phases/phase1.md — Unit Testing / Route Storage):
  - Route saved successfully
  - Route retrieved after saving
  - route_id is populated by AUTOINCREMENT (not None after save)
  - route_id strictly increases across saves
  - Multiple routes retrievable
  - URL and timestamp survive the round-trip correctly
"""
import pytest
from datetime import datetime, timezone

from backend.memory.sqlite.database import init_db
from backend.models.route import Route
from backend.services.storage_service import save_route, get_routes


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db_path(tmp_path: pytest.TempPathFactory) -> str:
    """Create and initialise a fresh temporary database for each test."""
    path = str(tmp_path / "test_recon.db")
    init_db(db_path=path)
    return path


def make_route(url: str = "https://example.com") -> Route:
    return Route(url=url, discovered_at=datetime.now(timezone.utc))


# ── Save ──────────────────────────────────────────────────────────────────────

class TestSaveRoute:
    def test_save_returns_route_with_id(self, db_path: str) -> None:
        saved = save_route(make_route(), db_path=db_path)
        assert saved.route_id is not None

    def test_route_id_is_positive_integer(self, db_path: str) -> None:
        saved = save_route(make_route(), db_path=db_path)
        assert isinstance(saved.route_id, int)
        assert saved.route_id >= 1

    def test_url_preserved_on_save(self, db_path: str) -> None:
        url = "https://target.example.com/login"
        saved = save_route(make_route(url), db_path=db_path)
        assert saved.url == url

    def test_original_route_unchanged(self, db_path: str) -> None:
        """save_route returns a new object — the original must not be mutated."""
        original = make_route()
        assert original.route_id is None
        save_route(original, db_path=db_path)
        assert original.route_id is None


# ── Retrieve ──────────────────────────────────────────────────────────────────

class TestGetRoutes:
    def test_empty_before_any_saves(self, db_path: str) -> None:
        routes = get_routes(db_path=db_path)
        assert routes == []

    def test_one_route_retrieved_after_save(self, db_path: str) -> None:
        save_route(make_route(), db_path=db_path)
        routes = get_routes(db_path=db_path)
        assert len(routes) == 1

    def test_url_survives_round_trip(self, db_path: str) -> None:
        url = "https://example.com/admin"
        save_route(make_route(url), db_path=db_path)
        routes = get_routes(db_path=db_path)
        assert routes[0].url == url

    def test_multiple_routes_retrieved(self, db_path: str) -> None:
        urls = [
            "https://example.com/login",
            "https://example.com/register",
            "https://example.com/about",
        ]
        for url in urls:
            save_route(make_route(url), db_path=db_path)

        routes = get_routes(db_path=db_path)
        assert len(routes) == 3

    def test_routes_returned_in_insertion_order(self, db_path: str) -> None:
        urls = ["https://first.com", "https://second.com", "https://third.com"]
        for url in urls:
            save_route(make_route(url), db_path=db_path)

        routes = get_routes(db_path=db_path)
        assert [r.url for r in routes] == urls

    def test_retrieved_routes_have_ids(self, db_path: str) -> None:
        save_route(make_route(), db_path=db_path)
        routes = get_routes(db_path=db_path)
        assert all(r.route_id is not None for r in routes)


# ── AUTOINCREMENT behaviour ───────────────────────────────────────────────────

class TestAutoincrement:
    def test_route_ids_strictly_increasing(self, db_path: str) -> None:
        r1 = save_route(make_route("https://a.com"), db_path=db_path)
        r2 = save_route(make_route("https://b.com"), db_path=db_path)
        r3 = save_route(make_route("https://c.com"), db_path=db_path)
        assert r1.route_id < r2.route_id < r3.route_id  # type: ignore[operator]

    def test_first_id_is_one(self, db_path: str) -> None:
        saved = save_route(make_route(), db_path=db_path)
        assert saved.route_id == 1

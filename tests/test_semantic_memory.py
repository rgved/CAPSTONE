from datetime import datetime, timezone

from backend.memory.chroma.vector_store import SemanticMemoryStore
from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.recon_result import ReconResult
from backend.models.route import Route


class FakeCollection:
    def __init__(self) -> None:
        self.upserts: list[dict] = []
        self.query_result = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    def upsert(self, ids, documents, metadatas, embeddings) -> None:
        self.upserts.append(
            {
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas,
                "embeddings": embeddings,
            }
        )

    def query(self, query_embeddings, n_results, include):
        return self.query_result


class FakeClient:
    def __init__(self) -> None:
        self.collections: dict[str, FakeCollection] = {}

    def get_or_create_collection(self, name: str, metadata=None) -> FakeCollection:
        if name not in self.collections:
            self.collections[name] = FakeCollection()
        return self.collections[name]


class TestSemanticMemoryStore:
    def test_initialize_creates_required_collections(self) -> None:
        client = FakeClient()
        store = SemanticMemoryStore(client=client)

        store.initialize()

        assert set(store.collection_names()) == {"findings", "features", "routes"}

    def test_upsert_route_indexes_route_summary(self) -> None:
        client = FakeClient()
        store = SemanticMemoryStore(client=client)
        store.initialize()
        route = Route(route_id=1, url="https://example.com/login", discovered_at=datetime.now(timezone.utc))
        recon_result = ReconResult(
            url=route.url,
            forms=[],
            inputs=["username", "password"],
            buttons=["Login"],
            links=["/register"],
            scripts=[],
            meta_tags=[],
        )

        store.upsert_route(route, recon_result=recon_result)

        upsert = client.collections["routes"].upserts[0]
        assert upsert["ids"] == ["route-1"]
        assert upsert["metadatas"] == [{"route": "https://example.com/login", "route_id": 1}]
        assert "username, password" in upsert["documents"][0]

    def test_upsert_feature_indexes_feature_summary(self) -> None:
        client = FakeClient()
        store = SemanticMemoryStore(client=client)
        store.initialize()
        feature = Feature(
            feature_id="AUTH-001",
            name="authentication",
            routes=["https://example.com/login"],
            classification_confidence=0.96,
            analyzed=False,
        )

        store.upsert_feature(feature)

        upsert = client.collections["features"].upserts[0]
        assert upsert["ids"] == ["AUTH-001"]
        assert upsert["metadatas"] == [{"feature": "authentication", "feature_id": "AUTH-001"}]
        assert "https://example.com/login" in upsert["documents"][0]

    def test_search_routes_returns_typed_results(self) -> None:
        client = FakeClient()
        store = SemanticMemoryStore(client=client)
        store.initialize()
        client.collections["routes"].query_result = {
            "ids": [["route-1"]],
            "documents": [["https://example.com/admin\nButtons: Manage Users"]],
            "metadatas": [[{"route": "https://example.com/admin", "route_id": 1}]],
            "distances": [[0.12]],
        }

        results = store.search_routes("admin controls", limit=1)

        assert len(results) == 1
        assert results[0].document_id == "route-1"
        assert results[0].metadata["route"] == "https://example.com/admin"
        assert results[0].distance == 0.12

    def test_upsert_finding_indexes_finding_summary(self) -> None:
        client = FakeClient()
        store = SemanticMemoryStore(client=client)
        store.initialize()
        finding = Finding(
            finding_id="FIND-001",
            type="missing_csrf",
            title="Potential Missing CSRF Protection",
            feature="authentication",
            severity="low",
            security_confidence=0.82,
            evidence=["POST form detected", "No CSRF token observed"],
            description="The login flow appears to submit without an observed token.",
            route_id=1,
        )

        store.upsert_finding(finding)

        upsert = client.collections["findings"].upserts[0]
        assert upsert["ids"] == ["FIND-001"]
        assert upsert["metadatas"] == [
            {
                "finding_id": "FIND-001",
                "feature": "authentication",
                "severity": "low",
                "type": "missing_csrf",
                "route_id": 1,
            }
        ]
        assert "Potential Missing CSRF Protection" in upsert["documents"][0]

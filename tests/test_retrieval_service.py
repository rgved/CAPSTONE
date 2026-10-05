from backend.models.feature import Feature
from backend.models.semantic_search_result import SemanticSearchResult
from backend.memory.sqlite.database import init_db
from backend.services.retrieval_service import RetrievalService
from backend.services.storage_service import save_feature


class StubSemanticRetriever:
    def __init__(self, results: list[SemanticSearchResult]) -> None:
        self._results = results

    def search_features(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        return self._results[:limit]

    def search_routes(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        return self._results[:limit]


class TestRetrievalService:
    def test_get_feature_by_name_uses_structured_storage(self, tmp_path) -> None:
        db_path = str(tmp_path / "retrieval.db")
        init_db(db_path=db_path)
        save_feature(
            Feature(
                name="search",
                routes=["https://example.com/search"],
                classification_confidence=0.88,
                analyzed=False,
            ),
            db_path=db_path,
        )
        service = RetrievalService(
            feature_retriever=StubSemanticRetriever([]),
            route_retriever=StubSemanticRetriever([]),
            db_path=db_path,
        )

        feature = service.get_feature_by_name("search")

        assert feature is not None
        assert feature.name == "search"
        assert feature.routes == ["https://example.com/search"]

    def test_search_features_returns_semantic_matches(self) -> None:
        result = SemanticSearchResult(
            document_id="AUTH-001",
            document="authentication\nRoutes: https://example.com/login",
            metadata={"feature": "authentication"},
            distance=0.04,
        )
        service = RetrievalService(
            feature_retriever=StubSemanticRetriever([result]),
            route_retriever=StubSemanticRetriever([]),
        )

        matches = service.search_features("login", limit=1)

        assert matches == [result]

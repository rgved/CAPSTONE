"""
backend/services/retrieval_service.py

Phase 4 retrieval layer for structured and semantic memory access.
"""
from __future__ import annotations

from typing import Optional, Protocol

from backend.models.feature import Feature
from backend.models.semantic_search_result import SemanticSearchResult
from backend.services.storage_service import get_features


class FeatureSemanticRetriever(Protocol):
    def search_features(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        """Return semantically similar feature records."""


class RouteSemanticRetriever(Protocol):
    def search_routes(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        """Return semantically similar route records."""


class FindingSemanticRetriever(Protocol):
    def search_findings(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        """Return semantically similar finding records."""


class RetrievalService:
    def __init__(
        self,
        feature_retriever: FeatureSemanticRetriever,
        route_retriever: RouteSemanticRetriever,
        finding_retriever: FindingSemanticRetriever | None = None,
        db_path: Optional[str] = None,
    ) -> None:
        self._feature_retriever = feature_retriever
        self._route_retriever = route_retriever
        self._finding_retriever = finding_retriever
        self._db_path = db_path

    def get_feature_by_name(self, name: str) -> Feature | None:
        for feature in get_features(db_path=self._db_path):
            if feature.name == name:
                return feature
        return None

    def search_features(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        return self._feature_retriever.search_features(query=query, limit=limit)

    def search_routes(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        return self._route_retriever.search_routes(query=query, limit=limit)

    def search_findings(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        if self._finding_retriever is None:
            return []
        return self._finding_retriever.search_findings(query=query, limit=limit)

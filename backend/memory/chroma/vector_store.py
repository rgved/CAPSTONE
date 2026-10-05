"""
backend/memory/chroma/vector_store.py

Phase 4 semantic memory built on ChromaDB.
"""
from __future__ import annotations

import math
import re
from typing import Any, Protocol, cast

from backend.config import CHROMA_PATH
from backend.models.feature import Feature
from backend.models.finding import Finding
from backend.models.recon_result import ReconResult
from backend.models.route import Route
from backend.models.semantic_search_result import SemanticSearchResult
from backend.services.logger import get_logger

logger = get_logger(__name__)

_EMBEDDING_DIMENSION = 64
_TOKEN_PATTERN = re.compile(r"[a-z0-9_./:-]+")


class ChromaDependencyError(RuntimeError):
    """Raised when ChromaDB is required but unavailable."""


class CollectionProtocol(Protocol):
    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
        embeddings: list[list[float]],
    ) -> None:
        """Insert or update semantic memory records."""

    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int,
        include: list[str],
    ) -> dict[str, list[list[Any]]]:
        """Run a semantic query."""


class ClientProtocol(Protocol):
    def get_or_create_collection(self, name: str, metadata: dict[str, Any] | None = None) -> CollectionProtocol:
        """Return an existing collection or create it."""


class SemanticMemoryStore:
    def __init__(self, client: ClientProtocol | None = None) -> None:
        self._client = client or self._build_default_client()
        self._collections: dict[str, CollectionProtocol] = {}

    def initialize(self) -> None:
        for collection_name in ("findings", "features", "routes"):
            self._collections[collection_name] = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"phase": "phase4"},
            )
        logger.info("Semantic memory initialised with %d collection(s)", len(self._collections))

    def upsert_route(self, route: Route, recon_result: ReconResult | None = None) -> None:
        collection = self._get_collection("routes")
        document = self._build_route_document(route, recon_result)
        metadata: dict[str, Any] = {"route": route.url}
        if route.route_id is not None:
            metadata["route_id"] = route.route_id

        collection.upsert(
            ids=[self._route_document_id(route)],
            documents=[document],
            metadatas=[metadata],
            embeddings=[self._embed_text(document)],
        )
        logger.info("Indexed route in semantic memory - url=%s", route.url)

    def upsert_feature(self, feature: Feature) -> None:
        collection = self._get_collection("features")
        document = self._build_feature_document(feature)
        metadata: dict[str, Any] = {"feature": feature.name}
        if feature.feature_id is not None:
            metadata["feature_id"] = feature.feature_id

        collection.upsert(
            ids=[self._feature_document_id(feature)],
            documents=[document],
            metadatas=[metadata],
            embeddings=[self._embed_text(document)],
        )
        logger.info("Indexed feature in semantic memory - feature=%s", feature.name)

    def upsert_finding(self, finding: Finding) -> None:
        collection = self._get_collection("findings")
        document = self._build_finding_document(finding)
        metadata: dict[str, Any] = {
            "finding_id": finding.finding_id or "",
            "feature": finding.feature,
            "severity": finding.severity,
            "type": finding.type,
        }
        if finding.route_id is not None:
            metadata["route_id"] = finding.route_id

        collection.upsert(
            ids=[finding.finding_id or self._finding_document_id(finding)],
            documents=[document],
            metadatas=[metadata],
            embeddings=[self._embed_text(document)],
        )
        logger.info("Indexed finding in semantic memory - finding_id=%s title=%s", finding.finding_id, finding.title)

    def search_routes(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        return self._search_collection("routes", query=query, limit=limit)

    def search_features(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        return self._search_collection("features", query=query, limit=limit)

    def search_findings(self, query: str, limit: int = 3) -> list[SemanticSearchResult]:
        return self._search_collection("findings", query=query, limit=limit)

    def collection_names(self) -> list[str]:
        return list(self._collections.keys())

    def _search_collection(self, collection_name: str, query: str, limit: int) -> list[SemanticSearchResult]:
        if limit < 1:
            raise ValueError("limit must be at least 1")

        collection = self._get_collection(collection_name)
        raw_result = collection.query(
            query_embeddings=[self._embed_text(query)],
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )
        return self._build_search_results(raw_result)

    def _get_collection(self, name: str) -> CollectionProtocol:
        if name not in self._collections:
            raise RuntimeError("Semantic memory store must be initialized before use")
        return self._collections[name]

    def _build_default_client(self) -> ClientProtocol:
        try:
            import chromadb
        except ImportError as exc:
            raise ChromaDependencyError(
                "chromadb is not installed. Install dependencies from requirements.txt for Phase 4."
            ) from exc

        client = chromadb.PersistentClient(path=CHROMA_PATH)
        return cast(ClientProtocol, client)

    def _build_search_results(self, raw_result: dict[str, list[list[Any]]]) -> list[SemanticSearchResult]:
        ids = raw_result.get("ids", [[]])
        documents = raw_result.get("documents", [[]])
        metadatas = raw_result.get("metadatas", [[]])
        distances = raw_result.get("distances", [[]])

        first_ids = ids[0] if ids else []
        first_documents = documents[0] if documents else []
        first_metadatas = metadatas[0] if metadatas else []
        first_distances = distances[0] if distances else []

        results: list[SemanticSearchResult] = []
        for index, document_id in enumerate(first_ids):
            document = first_documents[index] if index < len(first_documents) else ""
            metadata = first_metadatas[index] if index < len(first_metadatas) else {}
            distance = first_distances[index] if index < len(first_distances) else None
            results.append(
                SemanticSearchResult(
                    document_id=str(document_id),
                    document=str(document),
                    metadata=dict(metadata or {}),
                    distance=float(distance) if distance is not None else None,
                )
            )
        return results

    def _build_route_document(self, route: Route, recon_result: ReconResult | None) -> str:
        lines = [route.url]
        if recon_result is not None:
            lines.append(f"Forms: {len(recon_result.forms)}")
            lines.append(f"Inputs: {', '.join(recon_result.inputs) if recon_result.inputs else 'none'}")
            lines.append(f"Buttons: {', '.join(recon_result.buttons) if recon_result.buttons else 'none'}")
            lines.append(f"Links: {', '.join(recon_result.links) if recon_result.links else 'none'}")
        return "\n".join(lines)

    def _build_feature_document(self, feature: Feature) -> str:
        routes = ", ".join(feature.routes) if feature.routes else "none"
        return "\n".join(
            [
                feature.name,
                f"Routes: {routes}",
                f"Classification confidence: {feature.classification_confidence:.2f}",
            ]
        )

    def _build_finding_document(self, finding: Finding) -> str:
        evidence = "\n".join(finding.evidence) if finding.evidence else "none"
        return "\n".join(
            [
                finding.title,
                finding.description or "No description",
                f"Feature: {finding.feature}",
                f"Severity: {finding.severity}",
                f"Type: {finding.type}",
                f"Evidence: {evidence}",
            ]
        )

    def _route_document_id(self, route: Route) -> str:
        if route.route_id is not None:
            return f"route-{route.route_id}"
        return f"route-{route.url}"

    def _feature_document_id(self, feature: Feature) -> str:
        if feature.feature_id is not None:
            return feature.feature_id
        return f"feature-{feature.name}"

    def _finding_document_id(self, finding: Finding) -> str:
        if finding.finding_id is not None:
            return finding.finding_id
        return f"finding-{finding.title}"

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * _EMBEDDING_DIMENSION
        tokens = _TOKEN_PATTERN.findall(text.lower())
        if not tokens:
            return vector

        for token in tokens:
            slot = hash(token) % _EMBEDDING_DIMENSION
            vector[slot] += 1.0

        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0.0:
            return vector
        return [value / magnitude for value in vector]

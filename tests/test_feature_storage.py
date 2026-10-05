from backend.memory.sqlite.database import init_db
from backend.models.feature import Feature
from backend.services.storage_service import get_features, save_feature


class TestFeatureStorage:
    def test_save_feature_assigns_feature_id(self, tmp_path) -> None:
        db_path = str(tmp_path / "feature_storage.db")
        init_db(db_path=db_path)

        saved = save_feature(
            Feature(
                name="authentication",
                routes=["https://example.com/login"],
                classification_confidence=0.96,
                analyzed=False,
            ),
            db_path=db_path,
        )

        assert saved.feature_id == "AUTH-001"

    def test_get_features_returns_saved_features(self, tmp_path) -> None:
        db_path = str(tmp_path / "feature_storage.db")
        init_db(db_path=db_path)
        save_feature(
            Feature(
                name="search",
                routes=["https://example.com/search"],
                classification_confidence=0.87,
                analyzed=False,
            ),
            db_path=db_path,
        )

        features = get_features(db_path=db_path)

        assert len(features) == 1
        assert features[0].feature_id == "SEARCH-001"
        assert features[0].name == "search"
        assert features[0].routes == ["https://example.com/search"]
        assert features[0].classification_confidence == 0.87

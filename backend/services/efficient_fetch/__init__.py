"""
backend/services/efficient_fetch/__init__.py
"""
from backend.services.efficient_fetch.efficient_fetch_service import efficient_fetch
from backend.services.efficient_fetch.fetch_models import EfficientFetchResult

__all__ = ["efficient_fetch", "EfficientFetchResult"]

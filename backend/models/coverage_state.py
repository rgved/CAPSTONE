"""
backend/models/coverage_state.py

Phase 2 mission coverage state.
"""
from pydantic import BaseModel


class CoverageState(BaseModel):
    recon_completed: bool = False

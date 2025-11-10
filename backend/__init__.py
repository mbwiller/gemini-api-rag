"""
YouTube Channel RAG Backend
A Flask-based API for scraping YouTube channels and querying transcripts using RAG
"""

__version__ = "1.0.0"

from .gemini_service import (
    GeminiFileSearchService,
    GeminiService,  # Backwards compatibility alias
    get_service,
    reset_service
)

__all__ = [
    'GeminiFileSearchService',
    'GeminiService',
    'get_service',
    'reset_service'
]

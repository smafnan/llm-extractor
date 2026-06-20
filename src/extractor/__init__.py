"""extractor - reliable structured extraction from LLMs, provider-agnostic."""

from .engine import extract, ExtractionResult, ExtractionError, extract_json_object
from .schema import SupportTicket, Urgency, Sentiment
from .providers import get_provider, AVAILABLE_PROVIDERS, ProviderError, MockProvider

__all__ = [
    "extract", "ExtractionResult", "ExtractionError", "extract_json_object",
    "SupportTicket", "Urgency", "Sentiment",
    "get_provider", "AVAILABLE_PROVIDERS", "ProviderError", "MockProvider",
]
__version__ = "1.0.0"

"""NLP Processing Pipeline for code2llm.

Provides query normalization, intent matching, and entity resolution
with multilingual support and fuzzy matching.
"""

__version__ = "0.5.99"

from .pipeline import NLPPipeline
from .normalization import QueryNormalizer
from .intent_matching import IntentMatcher
from .entity_resolution import EntityResolver
from .config import NLPConfig, FAST_NLP_CONFIG, PRECISE_NLP_CONFIG

__all__ = [
    "NLPPipeline",
    "QueryNormalizer", 
    "IntentMatcher",
    "EntityResolver",
    "NLPConfig",
    "FAST_NLP_CONFIG",
    "PRECISE_NLP_CONFIG",
]

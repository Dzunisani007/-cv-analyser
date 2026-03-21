"""Lazy model loader for HF Spaces to prevent startup freezes."""

import logging
from typing import Optional
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from transformers import AutoModelForTokenClassification, AutoTokenizer

logger = logging.getLogger(__name__)

# Global variables for cached models
_embed_model: Optional[SentenceTransformer] = None
_ner_model: Optional[pipeline] = None

def get_embed_model() -> SentenceTransformer:
    """Get embeddings model, loading it on first call."""
    global _embed_model
    if _embed_model is None:
        logger.info("Loading embeddings model...")
        _embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Embeddings model loaded successfully")
    return _embed_model

def get_ner_model() -> pipeline:
    """Get NER model, loading it on first call."""
    global _ner_model
    if _ner_model is None:
        logger.info("Loading NER model...")
        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        _ner_model = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
        logger.info("NER model loaded successfully")
    return _ner_model

def reset_models():
    """Reset cached models (useful for testing)."""
    global _embed_model, _ner_model
    _embed_model = None
    _ner_model = None

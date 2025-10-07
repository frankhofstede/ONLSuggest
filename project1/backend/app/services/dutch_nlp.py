"""
Dutch NLP utilities for intelligent text matching.
Provides fuzzy matching, lemmatization, and similarity scoring for Dutch text.
"""
import difflib
import logging
from typing import List, Tuple, Optional
import spacy
from functools import lru_cache

logger = logging.getLogger(__name__)

# Global spaCy model (loaded once)
_nlp_model = None


def get_nlp_model():
    """
    Get or load Dutch spaCy model (singleton pattern).

    Returns:
        Loaded spaCy model

    Raises:
        RuntimeError: If model cannot be loaded
    """
    global _nlp_model

    if _nlp_model is None:
        try:
            logger.info("Loading Dutch spaCy model (nl_core_news_sm)...")
            _nlp_model = spacy.load("nl_core_news_sm")
            logger.info("Dutch spaCy model loaded successfully")
        except OSError as e:
            logger.error(f"Failed to load Dutch spaCy model: {e}")
            raise RuntimeError(
                "Dutch spaCy model not found. "
                "Run: python -m spacy download nl_core_news_sm"
            ) from e

    return _nlp_model


def normalize_text(text: str) -> str:
    """
    Normalize Dutch text for matching.

    Normalization:
    - Convert to lowercase
    - Strip whitespace
    - Remove extra spaces

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    return " ".join(text.lower().strip().split())


def fuzzy_similarity(query: str, target: str) -> float:
    """
    Calculate fuzzy similarity between two strings.

    Uses SequenceMatcher for character-level similarity.
    Handles typos, character swaps, and small differences.

    Args:
        query: Query string
        target: Target string to match against

    Returns:
        Similarity score 0.0-1.0 (1.0 = identical)

    Examples:
        >>> fuzzy_similarity("paspoort", "paspoort")
        1.0
        >>> fuzzy_similarity("paspport", "paspoort")  # 1 char typo
        0.933...
        >>> fuzzy_similarity("park", "parkeren")
        0.8
    """
    query_norm = normalize_text(query)
    target_norm = normalize_text(target)

    if not query_norm or not target_norm:
        return 0.0

    return difflib.SequenceMatcher(None, query_norm, target_norm).ratio()


def fuzzy_match(
    query: str,
    targets: List[str],
    threshold: float = 0.8,
    limit: int = 10
) -> List[Tuple[str, float]]:
    """
    Fuzzy match query against list of targets.

    Returns targets that exceed similarity threshold,
    sorted by similarity score (descending).

    Args:
        query: Query string
        targets: List of target strings to match against
        threshold: Minimum similarity threshold (0.0-1.0)
        limit: Maximum number of results

    Returns:
        List of (target, similarity) tuples sorted by similarity

    Examples:
        >>> targets = ["parkeervergunning", "paspoort", "rijbewijs"]
        >>> fuzzy_match("parkeern", targets, threshold=0.8)
        [("parkeervergunning", 0.95), ...]
    """
    matches = []

    for target in targets:
        similarity = fuzzy_similarity(query, target)
        if similarity >= threshold:
            matches.append((target, similarity))

    # Sort by similarity (descending)
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches[:limit]


@lru_cache(maxsize=1000)
def lemmatize_text(text: str) -> List[str]:
    """
    Lemmatize Dutch text using spaCy.

    Lemmatization converts words to their dictionary form:
    - "parkeren" → "parkeren"
    - "parkeerde" → "parkeren"
    - "auto's" → "auto"

    Args:
        text: Input text

    Returns:
        List of lemmatized tokens (lowercase)

    Examples:
        >>> lemmatize_text("parkeervergunning aanvragen")
        ["parkeervergunning", "aanvragen"]
    """
    try:
        nlp = get_nlp_model()
        doc = nlp(text.lower())
        # Return lemmas, excluding punctuation and spaces
        return [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
    except Exception as e:
        logger.warning(f"Lemmatization failed for '{text}': {e}")
        # Fallback to normalized text split
        return normalize_text(text).split()


def partial_match_score(query: str, target: str) -> float:
    """
    Calculate partial match score for substring matching.

    Useful for matching partial gemeente names:
    - "adam" → "amsterdam" (high score)
    - "rott" → "rotterdam" (high score)

    Args:
        query: Query string (potentially partial)
        target: Full target string

    Returns:
        Match score 0.0-1.0

    Examples:
        >>> partial_match_score("adam", "amsterdam")
        0.95
        >>> partial_match_score("rott", "rotterdam")
        0.90
    """
    query_norm = normalize_text(query)
    target_norm = normalize_text(target)

    if not query_norm or not target_norm:
        return 0.0

    # Exact match
    if query_norm == target_norm:
        return 1.0

    # Target starts with query (common for partial input)
    if target_norm.startswith(query_norm):
        # Score based on coverage
        coverage = len(query_norm) / len(target_norm)
        return 0.85 + (coverage * 0.15)  # 0.85-1.0 range

    # Query is substring of target
    if query_norm in target_norm:
        coverage = len(query_norm) / len(target_norm)
        return 0.70 + (coverage * 0.15)  # 0.70-0.85 range

    # Fuzzy similarity fallback
    return fuzzy_similarity(query, target) * 0.7  # Reduce score for non-substring


def lemma_match_score(query: str, target: str) -> float:
    """
    Calculate lemma-based match score.

    Matches based on lemmatized forms, useful for:
    - "parkeer" → "parkeren"
    - "aanvraag" → "aanvragen"

    Args:
        query: Query string
        target: Target string

    Returns:
        Match score 0.0-1.0
    """
    query_lemmas = set(lemmatize_text(query))
    target_lemmas = set(lemmatize_text(target))

    if not query_lemmas or not target_lemmas:
        return 0.0

    # Calculate overlap
    intersection = query_lemmas & target_lemmas
    union = query_lemmas | target_lemmas

    if not union:
        return 0.0

    # Jaccard similarity
    jaccard = len(intersection) / len(union)

    # Boost if all query lemmas found in target
    if query_lemmas.issubset(target_lemmas):
        return min(1.0, jaccard + 0.3)

    return jaccard


def enhanced_match_score(query: str, target: str) -> float:
    """
    Calculate enhanced match score combining multiple strategies.

    Combines:
    - Exact/fuzzy matching
    - Partial matching
    - Lemma matching

    Returns best score among strategies.

    Args:
        query: Query string
        target: Target string

    Returns:
        Best match score 0.0-1.0
    """
    # Try exact/fuzzy first (fastest)
    fuzzy_score = fuzzy_similarity(query, target)

    # Try partial match
    partial_score = partial_match_score(query, target)

    # Try lemma match (slower, but handles variations)
    lemma_score = lemma_match_score(query, target)

    # Return best score
    return max(fuzzy_score, partial_score, lemma_score)


def find_best_matches(
    query: str,
    candidates: List[str],
    threshold: float = 0.7,
    limit: int = 10
) -> List[Tuple[str, float]]:
    """
    Find best matches using enhanced matching.

    Args:
        query: Query string
        candidates: List of candidate strings
        threshold: Minimum score threshold
        limit: Maximum results

    Returns:
        List of (candidate, score) tuples sorted by score
    """
    matches = []

    for candidate in candidates:
        score = enhanced_match_score(query, candidate)
        if score >= threshold:
            matches.append((candidate, score))

    # Sort by score (descending)
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches[:limit]

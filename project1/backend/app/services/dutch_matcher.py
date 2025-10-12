"""
Story 1.4: Dutch Language Processing and Natural Question Formation

This module handles Dutch language processing to match partial input
with gemeentes and services in the database.

Acceptance Criteria:
- Handles common Dutch spelling variations
- Recognizes gemeente names (full and partial)
- Identifies service keywords in partial input
- Handles typos gracefully (fuzzy matching)
- Prioritizes more relevant suggestions first
"""

from typing import List, Dict, Tuple
import re


class DutchMatcher:
    """
    Dutch language matcher for gemeentes and services
    Handles partial matches, spelling variations, and keyword matching
    """

    def __init__(self):
        # Common Dutch spelling variations and normalizations
        self.spelling_variations = {
            'ij': ['y', 'ij'],
            'ei': ['ey', 'ei'],
            'ou': ['ouw', 'ou'],
            'au': ['auw', 'au'],
        }

        # Dutch stop words (low-value words to filter out)
        self.stop_words = {
            'de', 'het', 'een', 'en', 'van', 'in', 'op', 'is', 'bij',
            'voor', 'naar', 'met', 'aan', 'om', 'uit', 'te', 'wat',
            'hoe', 'waar', 'wanneer', 'welke', 'kan', 'ik', 'mijn',
        }

    def normalize_text(self, text: str) -> str:
        """
        Normalize Dutch text for comparison
        - Lowercase
        - Remove diacritics (ë -> e, ï -> i, etc.)
        - Trim whitespace
        """
        text = text.lower().strip()

        # Remove common Dutch diacritics
        diacritic_map = {
            'ë': 'e', 'ï': 'i', 'ü': 'u',
            'é': 'e', 'è': 'e', 'ê': 'e',
            'á': 'a', 'à': 'a', 'â': 'a',
            'ó': 'o', 'ò': 'o', 'ô': 'o',
        }

        for accented, plain in diacritic_map.items():
            text = text.replace(accented, plain)

        return text

    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract meaningful keywords from query
        Removes stop words and normalizes text
        """
        normalized = self.normalize_text(query)

        # Split on whitespace and punctuation
        words = re.findall(r'\w+', normalized)

        # Filter out stop words and short words
        keywords = [
            word for word in words
            if word not in self.stop_words and len(word) >= 2
        ]

        return keywords

    def fuzzy_match(self, query: str, target: str, threshold: float = 0.6) -> Tuple[bool, float]:
        """
        Perform fuzzy string matching between query and target

        Args:
            query: The search query
            target: The target string to match against
            threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            Tuple of (is_match, confidence_score)
        """
        query_norm = self.normalize_text(query)
        target_norm = self.normalize_text(target)

        # Exact match
        if query_norm == target_norm:
            return (True, 1.0)

        # Substring match
        if query_norm in target_norm:
            # Confidence based on how much of the target is matched
            confidence = len(query_norm) / len(target_norm)
            return (True, min(0.95, 0.7 + confidence * 0.25))

        if target_norm in query_norm:
            # Target is contained in query
            confidence = len(target_norm) / len(query_norm)
            return (True, min(0.90, 0.65 + confidence * 0.25))

        # Word-level matching (for multi-word queries)
        query_words = set(self.extract_keywords(query))
        target_words = set(self.extract_keywords(target))

        if not query_words or not target_words:
            return (False, 0.0)

        # Calculate Jaccard similarity
        intersection = len(query_words & target_words)
        union = len(query_words | target_words)

        if intersection > 0:
            jaccard_score = intersection / union
            if jaccard_score >= threshold:
                return (True, jaccard_score * 0.85)

        # Partial word matching (for typos)
        partial_matches = 0
        for q_word in query_words:
            for t_word in target_words:
                if len(q_word) >= 3 and len(t_word) >= 3:
                    # Check if one word is a substring of another
                    if q_word in t_word or t_word in q_word:
                        partial_matches += 1
                        break

        if partial_matches > 0:
            partial_score = partial_matches / max(len(query_words), len(target_words))
            if partial_score >= threshold:
                return (True, partial_score * 0.70)

        return (False, 0.0)

    def match_gemeentes(self, query: str, gemeentes: List[Dict]) -> List[Tuple[Dict, float]]:
        """
        Match query against gemeente names

        Args:
            query: The search query
            gemeentes: List of gemeente dictionaries with 'name' field

        Returns:
            List of tuples (gemeente, confidence_score) sorted by confidence
        """
        matches = []

        for gemeente in gemeentes:
            is_match, confidence = self.fuzzy_match(query, gemeente['name'])
            if is_match:
                matches.append((gemeente, confidence))

        # Sort by confidence (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def match_services(
        self,
        query: str,
        services: List[Dict],
        min_confidence: float = 0.5
    ) -> List[Tuple[Dict, float]]:
        """
        Match query against service names, descriptions, and keywords

        Args:
            query: The search query
            services: List of service dictionaries
            min_confidence: Minimum confidence threshold

        Returns:
            List of tuples (service, confidence_score) sorted by confidence
        """
        matches = []

        for service in services:
            max_confidence = 0.0

            # Check service name (highest priority)
            is_match, confidence = self.fuzzy_match(query, service['name'])
            if is_match:
                max_confidence = max(max_confidence, confidence * 1.0)

            # Check keywords (high priority)
            if 'keywords' in service and service['keywords']:
                for keyword in service['keywords']:
                    is_match, confidence = self.fuzzy_match(query, keyword)
                    if is_match:
                        max_confidence = max(max_confidence, confidence * 0.95)

            # Check description (lower priority)
            if 'description' in service and service['description']:
                is_match, confidence = self.fuzzy_match(query, service['description'])
                if is_match:
                    max_confidence = max(max_confidence, confidence * 0.70)

            # Check category (lowest priority)
            if 'category' in service and service['category']:
                is_match, confidence = self.fuzzy_match(query, service['category'])
                if is_match:
                    max_confidence = max(max_confidence, confidence * 0.60)

            if max_confidence >= min_confidence:
                matches.append((service, max_confidence))

        # Sort by confidence (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def combine_matches(
        self,
        query: str,
        gemeente_matches: List[Tuple[Dict, float]],
        service_matches: List[Tuple[Dict, float]],
        associations: List[Dict],
        max_results: int = 5
    ) -> List[Dict]:
        """
        Combine gemeente and service matches based on associations

        Args:
            query: The search query
            gemeente_matches: List of (gemeente, confidence) tuples
            service_matches: List of (service, confidence) tuples
            associations: List of associations from database
            max_results: Maximum number of results to return

        Returns:
            List of matched combinations with confidence scores
        """
        combined_results = []

        # Build association lookup for quick access
        association_map = {}
        for assoc in associations:
            key = (assoc['gemeente_id'], assoc['service_id'])
            association_map[key] = assoc

        # If we have both gemeente and service matches, combine them
        if gemeente_matches and service_matches:
            for service, service_conf in service_matches:
                for gemeente, gemeente_conf in gemeente_matches:
                    key = (gemeente['id'], service['id'])
                    if key in association_map:
                        # Combined confidence: weighted average
                        combined_conf = (service_conf * 0.7 + gemeente_conf * 0.3)
                        combined_results.append({
                            'service': service,
                            'gemeente': gemeente['name'],
                            'confidence': combined_conf
                        })

        # If only service matches, pair with all associated gemeentes
        elif service_matches:
            for service, service_conf in service_matches:
                # Find all gemeentes associated with this service
                service_gemeentes = [
                    assoc for assoc in associations
                    if assoc['service_id'] == service['id']
                ]

                if service_gemeentes:
                    for assoc in service_gemeentes[:3]:  # Limit to top 3 gemeentes per service
                        # Find the gemeente details
                        for g_match in gemeente_matches or []:
                            if g_match[0]['id'] == assoc['gemeente_id']:
                                gemeente_name = g_match[0]['name']
                                break
                        else:
                            # If gemeente not in matches, use first associated gemeente
                            gemeente_name = None
                            # We'd need to look it up from the database here
                            # For now, skip this combination

                        if gemeente_name:
                            combined_results.append({
                                'service': service,
                                'gemeente': gemeente_name,
                                'confidence': service_conf * 0.9  # Slight penalty for no gemeente match
                            })

        # If only gemeente matches, pair with all associated services
        elif gemeente_matches:
            for gemeente, gemeente_conf in gemeente_matches:
                # Find all services associated with this gemeente
                gemeente_services = [
                    assoc for assoc in associations
                    if assoc['gemeente_id'] == gemeente['id']
                ]

                for assoc in gemeente_services[:3]:  # Limit to top 3 services per gemeente
                    # Find the service details
                    for s_match in service_matches or []:
                        if s_match[0]['id'] == assoc['service_id']:
                            service = s_match[0]
                            break
                    else:
                        # Service not in original matches, skip
                        continue

                    combined_results.append({
                        'service': service,
                        'gemeente': gemeente['name'],
                        'confidence': gemeente_conf * 0.85  # Penalty for no service match
                    })

        # Sort by confidence and return top results
        combined_results.sort(key=lambda x: x['confidence'], reverse=True)
        return combined_results[:max_results]


# Global matcher instance
dutch_matcher = DutchMatcher()

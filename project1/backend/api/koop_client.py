"""
KOOP API Client for ONLSuggest
Mock implementation for Story 3.2 - will be replaced with real API calls
"""
from typing import List, Dict

class KoopAPIClient:
    """Client for KOOP API suggestions"""

    def __init__(self):
        # TODO: Add real API credentials/config in Story 3.2
        self.api_url = "https://api.koop.overheid.nl/v1/suggestions"  # Placeholder

    def get_suggestions(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Get suggestions from KOOP API

        For now this returns mock data with [KOOP] prefix to show it's working.
        Story 3.2 will implement real API calls.
        """
        # Mock implementation - returns suggestions with [KOOP] prefix
        mock_suggestions = [
            {
                "suggestion": f"[KOOP API] Hoe kan ik informatie vinden over '{query}'?",
                "confidence": 0.90,
                "service": {
                    "id": 9001,
                    "name": "KOOP Informatieservice",
                    "description": f"Zoekresultaten voor '{query}' via KOOP API",
                    "category": "Overheid"
                },
                "gemeente": None
            },
            {
                "suggestion": f"[KOOP API] Waar vind ik officiële documenten over '{query}'?",
                "confidence": 0.85,
                "service": {
                    "id": 9002,
                    "name": "KOOP Documentatie",
                    "description": "Officiële overheidsdocumentatie",
                    "category": "Overheid"
                },
                "gemeente": None
            },
            {
                "suggestion": f"[KOOP API] Welke regelgeving geldt voor '{query}'?",
                "confidence": 0.80,
                "service": {
                    "id": 9003,
                    "name": "KOOP Wetgeving",
                    "description": "Relevante wet- en regelgeving",
                    "category": "Overheid"
                },
                "gemeente": None
            }
        ]

        return mock_suggestions[:max_results]

# Global instance
koop_client = KoopAPIClient()

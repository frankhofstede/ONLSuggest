"""
KOOP API Client for ONLSuggest
Real implementation for Story 3.2
"""
from typing import List, Dict
import requests
import json

class KoopAPIError(Exception):
    """Raised when KOOP API call fails"""
    pass

class KoopAPIClient:
    """Client for KOOP API suggestions"""

    def __init__(self):
        # According to tech spec: use /api/suggest endpoint
        self.api_url = "https://onl-suggester.koop-innovatielab-tst.test5.s15m.nl/api/suggest"
        self.timeout = 5.0  # 5 second timeout

    def get_suggestions(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Get suggestions from KOOP API

        KOOP Response format (from tech spec):
        {
          "suggestions": [
            {
              "category": "Dienst" | "Wegwijzer Overheid",
              "suggest_entries": [
                {
                  "id": "url",
                  "title": "Display title",
                  "url": "Direct link",
                  "uri": "Semantic URI",
                  "helptext_after_select": "Help text",
                  "source": "WEGWIJZER" | "UPL"
                }
              ]
            }
          ]
        }
        """
        try:
            # Build request payload
            payload = {
                "text": query,
                "max_items": max_results,
                "categories": ["Dienst", "Wegwijzer Overheid"]
            }

            # Make HTTP request using requests library (works in serverless)
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
                verify=False  # Skip SSL verification for test environment
            )
            response.raise_for_status()
            koop_data = response.json()

            # Transform KOOP response to our format
            return self._transform_response(koop_data, max_results)

        except requests.exceptions.Timeout as e:
            raise KoopAPIError(f"Request timeout: {e}")
        except requests.exceptions.RequestException as e:
            raise KoopAPIError(f"Network error: {e}")
        except json.JSONDecodeError as e:
            raise KoopAPIError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise KoopAPIError(f"Unexpected error: {e}")

    def _transform_response(self, koop_data: Dict, max_results: int) -> List[Dict]:
        """
        Transform KOOP nested response format to our Suggestion interface

        KOOP has: suggestions[].suggest_entries[]
        We need: flat list of suggestions
        """
        transformed = []

        for category_group in koop_data.get("suggestions", []):
            category = category_group.get("category", "Dienst")

            for entry in category_group.get("suggest_entries", []):
                # Extract fields
                title = entry.get("title", "")
                uri = entry.get("uri") or entry.get("url") or entry.get("id")
                helptext = entry.get("helptext_after_select")
                source = entry.get("source", "UNKNOWN")

                # Create suggestion in our format
                suggestion = {
                    "suggestion": title,
                    "confidence": 0.85,  # KOOP doesn't provide confidence
                    "category": category,
                    "uri": uri,
                    "source": source,
                    "helptext": helptext,
                    "service": {
                        "id": None,  # KOOP doesn't map to our service IDs
                        "name": title,
                        "description": helptext or "",
                        "category": category
                    },
                    "gemeente": None  # KOOP is cross-gemeente
                }

                transformed.append(suggestion)

                # Stop if we have enough
                if len(transformed) >= max_results:
                    return transformed

        return transformed

# Global instance
koop_client = KoopAPIClient()

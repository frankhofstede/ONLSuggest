"""
KOOP API Client for ONLSuggest
Real implementation for Story 3.2
"""
from typing import List, Dict
import urllib.request
import urllib.error
import json
import ssl

class KoopAPIError(Exception):
    """Raised when KOOP API call fails"""
    pass

class KoopAPIClient:
    """Client for KOOP API suggestions"""

    def __init__(self):
        # According to tech spec: use /api/suggest endpoint
        self.api_url = "https://onl-suggester.koop-innovatielab-tst.test5.s15m.nl/api/suggest"
        self.timeout = 5.0  # 5 second timeout

        # Create SSL context that doesn't verify certificates for test environment
        # In production, this should be removed or use proper certificate verification
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

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

            # Make HTTP request
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context) as response:
                koop_data = json.loads(response.read().decode('utf-8'))

            # Transform KOOP response to our format
            return self._transform_response(koop_data, max_results)

        except urllib.error.URLError as e:
            raise KoopAPIError(f"Network error: {e}")
        except urllib.error.HTTPError as e:
            raise KoopAPIError(f"HTTP error {e.code}: {e.reason}")
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

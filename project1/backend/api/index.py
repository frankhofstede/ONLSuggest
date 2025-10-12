from http.server import BaseHTTPRequestHandler
import json
import time
from urllib.parse import urlparse, parse_qs

# Import our custom modules with isolated error handling
# Database import (highest priority - isolated from other modules)
db = None
DB_AVAILABLE = False
DB_ERROR = None

try:
    from database import db
    if db is not None:
        DB_AVAILABLE = True
except Exception as e:
    DB_ERROR = f"Database import failed: {str(e)}"
    print(f"[ERROR] Database import failed: {e}")

# Optional suggestion engine modules (isolated imports)
template_engine = None
dutch_matcher = None
koop_client = None
KoopAPIError = Exception  # Fallback

try:
    from template_engine import template_engine
except Exception as e:
    print(f"[WARNING] template_engine not available: {e}")

try:
    from dutch_matcher import dutch_matcher
except Exception as e:
    print(f"[WARNING] dutch_matcher not available: {e}")

try:
    from koop_client import koop_client, KoopAPIError
except Exception as e:
    print(f"[WARNING] koop_client not available: {e}")
    KoopAPIError = Exception  # Keep fallback

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Enhanced diagnostics for troubleshooting
            import sys
            import os

            response = {
                "status": "healthy",
                "version": "0.2.0",
                "service": "ONLSuggest API",
                "database": {
                    "available": DB_AVAILABLE,
                    "error": DB_ERROR,
                    "db_object_loaded": db is not None
                },
                "modules": {
                    "template_engine": template_engine is not None,
                    "dutch_matcher": dutch_matcher is not None,
                    "koop_client": koop_client is not None
                },
                "environment": {
                    "python_version": sys.version.split()[0],
                    "cwd": os.getcwd()
                }
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _generate_suggestions_from_koop(self, query: str, max_results: int = 5):
        """
        Generate suggestions using KOOP API
        Story 3.2: KOOP API Integration

        Note: Raises KoopAPIError on failure - caller should handle fallback
        """
        return koop_client.get_suggestions(query, max_results)

    def _generate_suggestions_from_database(self, query: str, max_results: int = 5):
        """
        Generate suggestions using real database, template engine, and Dutch matcher
        Stories 1.3 + 1.4: Template Engine + Dutch Language Processing
        """
        try:
            # Fetch all data from database
            all_gemeentes = db.get_all_gemeentes()
            all_services = db.get_all_services()
            all_associations = db.get_all_associations()

            # Match query against gemeentes and services
            gemeente_matches = dutch_matcher.match_gemeentes(query, all_gemeentes)
            service_matches = dutch_matcher.match_services(query, all_services, min_confidence=0.5)

            # Combine matches based on associations
            combined_matches = dutch_matcher.combine_matches(
                query=query,
                gemeente_matches=gemeente_matches,
                service_matches=service_matches,
                associations=all_associations,
                max_results=max_results * 2  # Get more candidates
            )

            # Generate question suggestions using template engine
            suggestions = template_engine.generate_suggestions(
                query=query,
                matched_services=combined_matches,
                max_results=max_results
            )

            return suggestions

        except Exception as e:
            # Return empty list on error, will be handled by caller
            print(f"Error generating suggestions: {e}")
            return []

    def do_POST(self):
        if self.path == '/api/v1/suggestions':
            start_time = time.time()

            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))

            query = request_data.get('query', '').strip()
            max_results = request_data.get('max_results', 5)

            # Validate input (Story 1.2)
            if not query or len(query) < 2:
                self.send_response(400)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {
                    "error": "Query must be at least 2 characters",
                    "query": query
                }
                self.wfile.write(json.dumps(error_response).encode())
                return

            # Check which suggestion engine to use (Story 3.1 + 3.2)
            suggestion_engine = "template"  # Default
            if DB_AVAILABLE:
                try:
                    # Get the active suggestion engine from settings
                    suggestion_engine = db.get_setting('suggestion_engine') or 'template'
                except:
                    suggestion_engine = "template"  # Fallback to template on error

            # Generate suggestions based on selected engine with fallback
            fallback_occurred = False
            fallback_reason = None

            if suggestion_engine == "koop":
                try:
                    suggestions = self._generate_suggestions_from_koop(query, max_results)
                except KoopAPIError as e:
                    # Fallback to template engine on KOOP failure
                    print(f"[WARNING] KOOP API failed, falling back to template: {e}")
                    suggestion_engine = "template"  # Update for response
                    fallback_occurred = True
                    fallback_reason = str(e)

                    if DB_AVAILABLE:
                        suggestions = self._generate_suggestions_from_database(query, max_results)
                    else:
                        suggestions = self._get_mock_suggestions(query, max_results)

            if suggestion_engine == "template":
                if DB_AVAILABLE:
                    suggestions = self._generate_suggestions_from_database(query, max_results)
                else:
                    # Fallback to mock data if database unavailable
                    suggestions = self._get_mock_suggestions(query, max_results)

            response_time_ms = (time.time() - start_time) * 1000

            response = {
                "query": request_data.get('query'),
                "suggestions": suggestions,
                "response_time_ms": response_time_ms,
                "using_database": DB_AVAILABLE,
                "suggestion_engine": suggestion_engine  # Story 3.2: Show which engine was used
            }

            # Add fallback information if applicable
            if fallback_occurred:
                response["fallback_occurred"] = True
                response["fallback_reason"] = fallback_reason

            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def _get_mock_suggestions(self, query: str, max_results: int):
        """Fallback mock data when database is unavailable"""
        query_lower = query.lower()

        # Mock data - matching frontend Suggestion interface
        MOCK_SUGGESTIONS = {
                "parkeer": [
                    {
                        "suggestion": "Hoe kan ik een parkeervergunning aanvragen?",
                        "confidence": 0.95,
                        "service": {
                            "id": 1,
                            "name": "Parkeervergunning aanvragen",
                            "description": "Vraag een parkeervergunning aan voor uw auto",
                            "category": "Verkeer"
                        },
                        "gemeente": "Amsterdam"
                    },
                    {
                        "suggestion": "Wat kost een parkeervergunning?",
                        "confidence": 0.90,
                        "service": {
                            "id": 2,
                            "name": "Parkeervergunning kosten",
                            "description": "Informatie over de kosten van een parkeervergunning",
                            "category": "Verkeer"
                        },
                        "gemeente": "Amsterdam"
                    },
                    {
                        "suggestion": "Waar kan ik parkeren in het centrum?",
                        "confidence": 0.85,
                        "service": {
                            "id": 3,
                            "name": "Parkeerinformatie centrum",
                            "description": "Informatie over parkeren in het centrum",
                            "category": "Verkeer"
                        },
                        "gemeente": "Amsterdam"
                    }
                ],
                "paspoort": [
                    {
                        "suggestion": "Hoe vraag ik een nieuw paspoort aan?",
                        "confidence": 0.95,
                        "service": {
                            "id": 4,
                            "name": "Paspoort aanvragen",
                            "description": "Vraag een nieuw paspoort aan",
                            "category": "Identiteit"
                        },
                        "gemeente": "Amsterdam"
                    },
                    {
                        "suggestion": "Wat kost een paspoort?",
                        "confidence": 0.90,
                        "service": {
                            "id": 5,
                            "name": "Paspoort kosten",
                            "description": "Informatie over de kosten van een paspoort",
                            "category": "Identiteit"
                        },
                        "gemeente": "Amsterdam"
                    },
                    {
                        "suggestion": "Hoe lang duurt het om een paspoort te krijgen?",
                        "confidence": 0.88,
                        "service": {
                            "id": 6,
                            "name": "Paspoort levertijd",
                            "description": "Informatie over de levertijd van een paspoort",
                            "category": "Identiteit"
                        },
                        "gemeente": "Amsterdam"
                    }
                ],
                "verhuizen": [
                    {
                        "suggestion": "Hoe meld ik mijn verhuizing?",
                        "confidence": 0.95,
                        "service": {
                            "id": 7,
                            "name": "Verhuizing doorgeven",
                            "description": "Geef uw verhuizing door aan de gemeente",
                            "category": "Burgerzaken"
                        },
                        "gemeente": "Amsterdam"
                    },
                    {
                        "suggestion": "Wat moet ik regelen bij verhuizen?",
                        "confidence": 0.92,
                        "service": {
                            "id": 8,
                            "name": "Verhuischecklist",
                            "description": "Checklist voor verhuizen",
                            "category": "Burgerzaken"
                        },
                        "gemeente": "Amsterdam"
                    },
                    {
                        "suggestion": "Binnen welke termijn moet ik verhuizing doorgeven?",
                        "confidence": 0.88,
                        "service": {
                            "id": 9,
                            "name": "Verhuizing termijn",
                            "description": "Termijn voor doorgeven verhuizing",
                            "category": "Burgerzaken"
                        },
                        "gemeente": "Amsterdam"
                    }
                ],
                "trouwen": [
                    {
                        "suggestion": "Hoe kan ik trouwen bij de gemeente?",
                        "confidence": 0.95,
                        "service": {
                            "id": 10,
                            "name": "Trouwen gemeente",
                            "description": "Informatie over trouwen bij de gemeente",
                            "category": "Burgerzaken"
                        },
                        "gemeente": "Amsterdam"
                    },
                    {
                        "suggestion": "Wat zijn de kosten voor trouwen?",
                        "confidence": 0.90,
                        "service": {
                            "id": 11,
                            "name": "Trouwkosten",
                            "description": "Informatie over de kosten van trouwen",
                            "category": "Burgerzaken"
                        },
                        "gemeente": "Amsterdam"
                    },
                    {
                        "suggestion": "Welke documenten heb ik nodig om te trouwen?",
                        "confidence": 0.88,
                        "service": {
                            "id": 12,
                            "name": "Trouwdocumenten",
                            "description": "Benodigde documenten voor trouwen",
                            "category": "Burgerzaken"
                        },
                        "gemeente": "Amsterdam"
                    }
                ]
            }

        suggestions = []
        for keyword, mock_suggestions in MOCK_SUGGESTIONS.items():
            if keyword in query_lower:
                suggestions = mock_suggestions[:max_results]
                break

        if not suggestions:
            suggestions = [
                {
                    "suggestion": f"Wat kan ik doen met '{query}'?",
                    "confidence": 0.50,
                    "service": {
                        "id": 999,
                        "name": "Algemene informatie",
                        "description": "Algemene vraag",
                        "category": "Algemeen"
                    },
                    "gemeente": None
                },
                {
                    "suggestion": f"Hoe vraag ik informatie aan over '{query}'?",
                    "confidence": 0.45,
                    "service": {
                        "id": 1000,
                        "name": "Informatie aanvragen",
                        "description": "Informatie aanvragen",
                        "category": "Algemeen"
                    },
                    "gemeente": None
                }
            ]

        return suggestions[:max_results]

from http.server import BaseHTTPRequestHandler
import json
import time
from urllib.parse import urlparse, parse_qs

# Import our custom modules
try:
    from database import db
    from template_engine import template_engine
    from dutch_matcher import dutch_matcher
    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    DB_ERROR = str(e)

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
            response = {"status": "healthy", "version": "0.1.0", "service": "ONLSuggest API"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

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

            # Try to use database-powered suggestions
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
                "using_database": DB_AVAILABLE
            }

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

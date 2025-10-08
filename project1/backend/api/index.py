from http.server import BaseHTTPRequestHandler
import json
import time
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

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

    def do_POST(self):
        if self.path == '/api/v1/suggestions':
            start_time = time.time()

            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))

            query = request_data.get('query', '').lower()
            max_results = request_data.get('max_results', 5)

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
                if keyword in query:
                    suggestions = mock_suggestions[:max_results]
                    break

            if not suggestions:
                original_query = request_data.get('query')
                suggestions = [
                    {
                        "suggestion": f"Wat kan ik doen met '{original_query}'?",
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
                        "suggestion": f"Hoe vraag ik informatie aan over '{original_query}'?",
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

            response_time_ms = (time.time() - start_time) * 1000

            response = {
                "query": request_data.get('query'),
                "suggestions": suggestions[:max_results],
                "response_time_ms": response_time_ms
            }

            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

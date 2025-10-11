"""
Admin API endpoints for ONLSuggest
Basic authentication + CRUD operations
"""
from http.server import BaseHTTPRequestHandler
import json
import base64
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Try importing database, capture error if it fails
db = None
db_error = None
try:
    from database import db
except Exception as e:
    db_error = str(e)

# Admin credentials (in production, use environment variables)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def _check_auth(self):
        """Check basic authentication"""
        auth_header = self.headers.get('Authorization')
        if not auth_header:
            return False

        try:
            auth_type, auth_string = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                return False

            decoded = base64.b64decode(auth_string).decode('utf-8')
            username, password = decoded.split(':', 1)

            return username == ADMIN_USERNAME and password == ADMIN_PASSWORD
        except:
            return False

    def _send_unauthorized(self):
        self.send_response(401)
        self._set_cors_headers()
        self.send_header('WWW-Authenticate', 'Basic realm="ONLSuggest Admin"')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())

    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        # Custom JSON encoder to handle datetime objects
        def json_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        self.wfile.write(json.dumps(data, default=json_encoder).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if not self._check_auth():
            self._send_unauthorized()
            return

        # Check for database errors
        if db_error:
            self._send_json_response(500, {"error": "Database import failed", "details": db_error})
            return

        parsed = urlparse(self.path)
        path = parsed.path

        # DASHBOARD STATS
        if path == '/api/admin/stats':
            stats = db.get_stats()
            stats['_deployment_version'] = 'v3-with-settings'
            self._send_json_response(200, stats)

        # GEMEENTES
        elif path == '/api/admin/gemeentes':
            gemeentes = db.get_all_gemeentes()
            self._send_json_response(200, {"gemeentes": gemeentes})

        elif path.startswith('/api/admin/gemeentes/'):
            gemeente_id = int(path.split('/')[-1])
            gemeente = db.get_gemeente(gemeente_id)
            if gemeente:
                # Include associated services
                associations = db.get_associations_by_gemeente(gemeente_id)
                service_ids = [a["service_id"] for a in associations]
                services = [db.get_service(sid) for sid in service_ids]
                gemeente["services"] = [s for s in services if s]
                self._send_json_response(200, gemeente)
            else:
                self._send_json_response(404, {"error": "Gemeente not found"})

        # SERVICES
        elif path == '/api/admin/services':
            services = db.get_all_services()
            self._send_json_response(200, {"services": services})

        elif path.startswith('/api/admin/services/'):
            service_id = int(path.split('/')[-1])
            service = db.get_service(service_id)
            if service:
                # Include associated gemeentes
                associations = db.get_associations_by_service(service_id)
                gemeente_ids = [a["gemeente_id"] for a in associations]
                gemeentes = [db.get_gemeente(gid) for gid in gemeente_ids]
                service["gemeentes"] = [g for g in gemeentes if g]
                self._send_json_response(200, service)
            else:
                self._send_json_response(404, {"error": "Service not found"})

        # ASSOCIATIONS
        elif path == '/api/admin/associations':
            try:
                all_associations = db.get_all_associations()
                # Enrich with gemeente and service details
                enriched = []
                for assoc in all_associations:
                    try:
                        gemeente = db.get_gemeente(assoc["gemeente_id"])
                        service = db.get_service(assoc["service_id"])
                        if gemeente and service:  # Only include if both exist
                            assoc["gemeente"] = gemeente
                            assoc["service"] = service
                            enriched.append(assoc)
                    except Exception as e:
                        # Skip this association if there's an error
                        continue
                self._send_json_response(200, {"associations": enriched})
            except Exception as e:
                self._send_json_response(500, {"error": str(e)})

        # TEST ENDPOINT (to verify deployment)
        elif path == '/api/admin/test-settings':
            self._send_json_response(200, {"message": "Settings endpoint exists!", "version": "v2"})

        # SETTINGS (Epic 3 Story 3.1)
        elif path == '/api/admin/settings':
            try:
                engine = db.get_setting('suggestion_engine')
                if engine is None:
                    # Default if setting doesn't exist
                    self._send_json_response(200, {"suggestion_engine": "template"})
                else:
                    self._send_json_response(200, {"suggestion_engine": engine})
            except Exception as e:
                self._send_json_response(500, {"error": str(e)})

        else:
            self._send_json_response(404, {"error": "Not found"})

    def do_POST(self):
        if not self._check_auth():
            self._send_unauthorized()
            return

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body.decode('utf-8'))

        path = self.path

        # CREATE GEMEENTE
        if path == '/api/admin/gemeentes':
            if 'name' not in data:
                self._send_json_response(400, {"error": "Name required"})
                return

            # Check for duplicates
            existing = [g for g in db.get_all_gemeentes() if g["name"].lower() == data["name"].lower()]
            if existing:
                self._send_json_response(400, {"error": "Gemeente already exists"})
                return

            gemeente = db.create_gemeente(data["name"], data.get("metadata", {}))
            self._send_json_response(201, gemeente)

        # CREATE SERVICE
        elif path == '/api/admin/services':
            required = ['name', 'description', 'category']
            if not all(k in data for k in required):
                self._send_json_response(400, {"error": "Missing required fields"})
                return

            # Check for duplicates
            existing = [s for s in db.get_all_services() if s["name"].lower() == data["name"].lower()]
            if existing:
                self._send_json_response(400, {"error": "Service already exists"})
                return

            service = db.create_service(
                data["name"],
                data["description"],
                data["category"],
                data.get("keywords", [])
            )
            self._send_json_response(201, service)

        # CREATE ASSOCIATION
        elif path == '/api/admin/associations':
            if 'gemeente_id' not in data or 'service_id' not in data:
                self._send_json_response(400, {"error": "Missing gemeente_id or service_id"})
                return

            association = db.create_association(data["gemeente_id"], data["service_id"])
            self._send_json_response(201, association)

        else:
            self._send_json_response(404, {"error": "Not found"})

    def do_PUT(self):
        if not self._check_auth():
            self._send_unauthorized()
            return

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body.decode('utf-8'))

        path = self.path

        # UPDATE GEMEENTE
        if path.startswith('/api/admin/gemeentes/'):
            gemeente_id = int(path.split('/')[-1])
            gemeente = db.update_gemeente(
                gemeente_id,
                data.get("name"),
                data.get("metadata")
            )
            if gemeente:
                self._send_json_response(200, gemeente)
            else:
                self._send_json_response(404, {"error": "Gemeente not found"})

        # UPDATE SERVICE
        elif path.startswith('/api/admin/services/'):
            service_id = int(path.split('/')[-1])
            service = db.update_service(
                service_id,
                data.get("name"),
                data.get("description"),
                data.get("category"),
                data.get("keywords")
            )
            if service:
                self._send_json_response(200, service)
            else:
                self._send_json_response(404, {"error": "Service not found"})

        # UPDATE SETTINGS (Epic 3 Story 3.1)
        elif path == '/api/admin/settings':
            if 'suggestion_engine' not in data:
                self._send_json_response(400, {"error": "Missing suggestion_engine field"})
                return

            engine = data['suggestion_engine']

            # Validate value
            if engine not in ['template', 'koop']:
                self._send_json_response(400, {"error": "Invalid suggestion_engine value. Must be 'template' or 'koop'"})
                return

            # Update setting
            try:
                success = db.update_setting('suggestion_engine', engine)
                if success:
                    self._send_json_response(200, {
                        "success": True,
                        "suggestion_engine": engine
                    })
                else:
                    self._send_json_response(500, {"error": "Failed to update setting"})
            except Exception as e:
                self._send_json_response(500, {"error": str(e)})

        else:
            self._send_json_response(404, {"error": "Not found"})

    def do_DELETE(self):
        if not self._check_auth():
            self._send_unauthorized()
            return

        path = self.path

        # DELETE GEMEENTE
        if path.startswith('/api/admin/gemeentes/'):
            gemeente_id = int(path.split('/')[-1])
            if db.delete_gemeente(gemeente_id):
                self._send_json_response(200, {"message": "Deleted"})
            else:
                self._send_json_response(404, {"error": "Gemeente not found"})

        # DELETE SERVICE
        elif path.startswith('/api/admin/services/'):
            service_id = int(path.split('/')[-1])
            if db.delete_service(service_id):
                self._send_json_response(200, {"message": "Deleted"})
            else:
                self._send_json_response(404, {"error": "Service not found"})

        # DELETE ASSOCIATION
        elif path.startswith('/api/admin/associations/'):
            association_id = int(path.split('/')[-1])
            if db.delete_association(association_id):
                self._send_json_response(200, {"message": "Deleted"})
            else:
                self._send_json_response(404, {"error": "Association not found"})

        else:
            self._send_json_response(404, {"error": "Not found"})
# Trigger deployment

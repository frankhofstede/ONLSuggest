"""
Settings API endpoint for ONLSuggest
Epic 3 Story 3.1: Admin Feature Toggle for Suggestion Engine Selection
"""
from http.server import BaseHTTPRequestHandler
import json
import base64
import os

# Try importing database, capture error if it fails
db = None
db_error = None
try:
    from database import db
except Exception as e:
    db_error = str(e)

# Admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "onlsuggest2024")

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
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
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Get current suggestion engine setting"""
        if not self._check_auth():
            self._send_unauthorized()
            return

        # Check for database errors
        if db_error:
            self._send_json_response(500, {"error": "Database import failed", "details": db_error})
            return

        try:
            # Get suggestion_engine setting
            engine = db.get_setting('suggestion_engine')

            if engine is None:
                # Setting doesn't exist - return default
                self._send_json_response(200, {"suggestion_engine": "template"})
            else:
                self._send_json_response(200, {"suggestion_engine": engine})

        except Exception as e:
            self._send_json_response(500, {"error": str(e)})

    def do_PUT(self):
        """Update suggestion engine setting"""
        if not self._check_auth():
            self._send_unauthorized()
            return

        # Check for database errors
        if db_error:
            self._send_json_response(500, {"error": "Database import failed", "details": db_error})
            return

        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            # Validate input
            if 'suggestion_engine' not in data:
                self._send_json_response(400, {"error": "Missing suggestion_engine field"})
                return

            engine = data['suggestion_engine']

            # Validate value
            if engine not in ['template', 'koop']:
                self._send_json_response(400, {"error": "Invalid suggestion_engine value. Must be 'template' or 'koop'"})
                return

            # Update setting
            success = db.update_setting('suggestion_engine', engine)

            if success:
                self._send_json_response(200, {
                    "success": True,
                    "suggestion_engine": engine
                })
            else:
                self._send_json_response(500, {"error": "Failed to update setting"})

        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})

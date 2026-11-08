"""POST /api/analyze  {"message": "...", "attack": "None"|<attack name>}"""
import json
from http.server import BaseHTTPRequestHandler

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import send_json  # noqa: E402
from src.service import MAX_CHARS, analyse


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_CHARS * 8:
                return send_json(self, 413, {"error": "Message is too long."})
            data = json.loads(self.rfile.read(length) or b"{}")
            send_json(self, 200, analyse(data.get("message", ""), data.get("attack", "None")))
        except ValueError as exc:
            send_json(self, 400, {"error": str(exc)})
        except Exception as exc:  # pragma: no cover
            send_json(self, 500, {"error": f"Analysis failed: {exc}"})

    def do_GET(self):
        send_json(self, 405, {"error": "Use POST with a JSON body: {\"message\": \"...\"}"})

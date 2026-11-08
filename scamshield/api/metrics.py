"""GET /api/metrics -> evaluation tables and the list of obfuscation attacks."""
from http.server import BaseHTTPRequestHandler

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import send_json  # noqa: E402
from src.service import metrics


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            send_json(self, 200, metrics())
        except Exception as exc:  # pragma: no cover
            send_json(self, 500, {"error": str(exc)})

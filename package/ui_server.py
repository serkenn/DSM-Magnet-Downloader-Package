#!/usr/bin/env python3
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer


PKG_NAME = "dsm-magnet-dl"
TARGET_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(TARGET_DIR, "ui")
VAR_DIR = f"/var/packages/{PKG_NAME}/var"
LOG_FILE = os.path.join(VAR_DIR, "package.log")
PORT = int(os.environ.get("UI_PORT", "18765"))


def log(message: str) -> None:
    os.makedirs(VAR_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path: str, content_type: str) -> None:
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            self._serve_file(os.path.join(UI_DIR, "index.html"), "text/html; charset=utf-8")
            return
        if self.path.startswith("/images/"):
            img = os.path.basename(self.path)
            f = os.path.join(UI_DIR, "images", img)
            if os.path.isfile(f):
                self._serve_file(f, "image/png")
                return
        if self.path == "/api/health":
            self._send_json(200, {"ok": True})
            return
        self._send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/api/fetch":
            self._send_json(404, {"ok": False, "error": "not found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "invalid json"})
            return

        url = str(payload.get("url", "")).strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            self._send_json(400, {"ok": False, "error": "invalid url"})
            return

        cmd = ["python3", os.path.join(TARGET_DIR, "magnet_fetcher.py"), url]
        log(f"[ui] run: {' '.join(cmd)}")
        try:
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=300)
        except Exception as e:
            log(f"[ui] failed: {e}")
            self._send_json(500, {"ok": False, "error": str(e)})
            return

        out = (proc.stdout or "") + (proc.stderr or "")
        log(f"[ui] exit={proc.returncode}")
        if proc.returncode == 0:
            self._send_json(200, {"ok": True, "output": out[-8000:]})
        else:
            self._send_json(500, {"ok": False, "output": out[-8000:]})

    def log_message(self, fmt, *args):  # noqa: A003
        log("[http] " + fmt % args)


def main() -> None:
    os.makedirs(VAR_DIR, exist_ok=True)
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    log(f"[ui] server started on :{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()

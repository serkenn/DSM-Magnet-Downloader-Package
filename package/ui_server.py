#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PKG_NAME = "dsm-magnet-dl"
TARGET_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(TARGET_DIR, "ui")
VAR_DIR = f"/var/packages/{PKG_NAME}/var"
LOG_FILE = os.path.join(VAR_DIR, "package.log")
SETTINGS_FILE = os.path.join(VAR_DIR, "settings.json")
RUNTIME_CONF = os.path.join(VAR_DIR, "runtime.conf")
PORT = int(os.environ.get("UI_PORT", "18765"))

DEFAULT_SETTINGS = {
    "proxy_url": "",
    "transmission_host": "localhost",
    "transmission_port": 9091,
    "transmission_user": "",
    "transmission_password": "",
    "require_vpn": False,
    "wg_conf": "/usr/local/etc/mullvad-wg.conf",
    "wg_bin": "/usr/local/bin/wg-quick",
}


def log(message: str) -> None:
    os.makedirs(VAR_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def load_settings() -> dict:
    data = dict(DEFAULT_SETTINGS)
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                data.update(raw)
        except Exception as e:
            log(f"[ui] load settings failed: {e}")
    return data


def save_settings(data: dict) -> None:
    os.makedirs(VAR_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    runtime = [
        f"WG_CONF='{str(data.get('wg_conf', DEFAULT_SETTINGS['wg_conf'])).replace("'", "'\\''")}'",
        f"WG_BIN='{str(data.get('wg_bin', DEFAULT_SETTINGS['wg_bin'])).replace("'", "'\\''")}'",
        f"REQUIRE_VPN={'1' if data.get('require_vpn') else '0'}",
    ]
    with open(RUNTIME_CONF, "w", encoding="utf-8") as f:
        f.write("\n".join(runtime) + "\n")


def sanitize_settings(payload: dict) -> dict:
    data = dict(DEFAULT_SETTINGS)
    for k in data.keys():
        if k in payload:
            data[k] = payload[k]

    data["proxy_url"] = str(data["proxy_url"]).strip()
    data["transmission_host"] = str(data["transmission_host"]).strip() or "localhost"
    try:
        data["transmission_port"] = int(data["transmission_port"])
    except Exception:
        data["transmission_port"] = 9091
    data["transmission_port"] = max(1, min(65535, data["transmission_port"]))
    data["transmission_user"] = str(data["transmission_user"]).strip()
    data["transmission_password"] = str(data["transmission_password"])
    data["require_vpn"] = bool(data["require_vpn"])
    data["wg_conf"] = str(data["wg_conf"]).strip() or DEFAULT_SETTINGS["wg_conf"]
    data["wg_bin"] = str(data["wg_bin"]).strip() or DEFAULT_SETTINGS["wg_bin"]
    return data


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

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        return json.loads(raw.decode("utf-8"))

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
        if self.path == "/api/settings":
            self._send_json(200, {"ok": True, "settings": load_settings()})
            return
        self._send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path == "/api/settings":
            try:
                payload = self._read_json_body()
            except Exception:
                self._send_json(400, {"ok": False, "error": "invalid json"})
                return
            data = sanitize_settings(payload if isinstance(payload, dict) else {})
            save_settings(data)
            self._send_json(200, {"ok": True, "settings": data})
            return

        if self.path != "/api/fetch":
            self._send_json(404, {"ok": False, "error": "not found"})
            return

        try:
            payload = self._read_json_body()
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid json"})
            return

        url = str(payload.get("url", "")).strip() if isinstance(payload, dict) else ""
        if not (url.startswith("http://") or url.startswith("https://")):
            self._send_json(400, {"ok": False, "error": "invalid url"})
            return

        s = load_settings()
        cmd = [
            sys.executable,
            os.path.join(TARGET_DIR, "magnet_fetcher.py"),
            url,
            "--host",
            str(s.get("transmission_host", "localhost")),
            "--port",
            str(s.get("transmission_port", 9091)),
        ]
        if s.get("transmission_user"):
            cmd += ["--user", str(s.get("transmission_user")), "--password", str(s.get("transmission_password", ""))]
        if s.get("proxy_url"):
            cmd += ["--proxy-url", str(s.get("proxy_url"))]

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
    if not os.path.isfile(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
    try:
        server = HTTPServer(("0.0.0.0", PORT), Handler)
    except Exception as e:
        log(f"[ui] server bind failed on :{PORT}: {e}")
        raise
    log(f"[ui] server started on :{PORT}")
    try:
        server.serve_forever()
    except Exception as e:
        log(f"[ui] server crashed: {e}")
        raise


if __name__ == "__main__":
    main()

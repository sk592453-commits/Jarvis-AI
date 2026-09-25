import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

CURRENT_MODE = "girl"
CURRENT_STATE = "listening"
STATE_LOCK = threading.Lock()
MESSAGE_HANDLER = None
WEB_ROOT = Path(__file__).with_name("web")


def set_avatar_mode(mode):
    global CURRENT_MODE
    with STATE_LOCK:
        CURRENT_MODE = mode.lower() if mode.lower() in {"girl", "boy"} else "girl"


def set_avatar_state(state):
    global CURRENT_STATE
    with STATE_LOCK:
        if state.lower() in {"listening", "speaking", "idle", "thinking"}:
            CURRENT_STATE = state.lower()


def set_message_handler(handler):
    global MESSAGE_HANDLER
    MESSAGE_HANDLER = handler


def _state_payload():
    with STATE_LOCK:
        return {"mode": CURRENT_MODE, "state": CURRENT_STATE}


class JarvisHandler(BaseHTTPRequestHandler):
    def log_message(self, format_string, *args):
        return

    def _send(self, status, body, content_type="application/json"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/state":
            self._send(200, json.dumps(_state_payload()))
            return

        filename = "index.html" if path == "/" else path.removeprefix("/")
        requested = (WEB_ROOT / filename).resolve()
        if WEB_ROOT not in requested.parents or not requested.is_file():
            self._send(404, "Not found", "text/plain")
            return
        content_types = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".gif": "image/gif",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        content_type = content_types.get(requested.suffix.lower(), "application/octet-stream")
        self._send(200, requested.read_bytes(), content_type)

    def do_POST(self):
        if urlparse(self.path).path != "/api/message":
            self._send(404, "Not found", "text/plain")
            return

        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length))
            message = str(payload.get("message", "")).strip()
        except (ValueError, TypeError, json.JSONDecodeError):
            self._send(400, json.dumps({"error": "Invalid request"}))
            return

        if not message:
            self._send(400, json.dumps({"error": "Message is empty"}))
            return
        if MESSAGE_HANDLER is None:
            self._send(503, json.dumps({"error": "Jarvis is still starting"}))
            return

        try:
            answer = MESSAGE_HANDLER(message)
            self._send(200, json.dumps({"answer": answer}))
        except Exception as error:
            self._send(500, json.dumps({"error": str(error)}))


def run_web_server():
    server = ThreadingHTTPServer(("127.0.0.1", 8765), JarvisHandler)
    print("Jarvis Python backend: http://127.0.0.1:8765")
    server.serve_forever()


def start_avatar_loop(mode="girl", message_handler=None):
    set_avatar_mode(mode)
    set_avatar_state("listening")
    set_message_handler(message_handler)
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    return web_thread


def start_avatar(mode="girl", message_handler=None):
    return start_avatar_loop(mode, message_handler)


def start_boy_avatar():
    return start_avatar_loop(mode="boy")


def start_girl_avatar():
    return start_avatar_loop(mode="girl")

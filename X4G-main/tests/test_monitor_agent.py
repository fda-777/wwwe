import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.monitor_agent import check_http_endpoint


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


class MonitorAgentTests(unittest.TestCase):
    def test_check_http_endpoint_returns_success_for_local_server(self) -> None:
        server = HTTPServer(("127.0.0.1", 0), HealthHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = check_http_endpoint(f"http://127.0.0.1:{port}/health")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status_code"], 200)


if __name__ == "__main__":
    unittest.main()

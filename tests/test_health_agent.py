import socket
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.health_agent import check_port_free, run_preflight_checks


class HealthAgentTests(unittest.TestCase):
    def test_check_port_free_accepts_an_available_port(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
            result = check_port_free(port)
        self.assertTrue(result["ok"])

    def test_run_preflight_checks_reports_project_files(self) -> None:
        root = Path(__file__).resolve().parents[1]
        results = run_preflight_checks(root=root)
        self.assertIn("required_files", results)
        self.assertTrue(results["required_files"]["ok"])


if __name__ == "__main__":
    unittest.main()

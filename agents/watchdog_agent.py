import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from agents.monitor_agent import MonitorAgent


class WatchdogAgent:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1]
        self.state_path = self.root / "reports" / "watchdog_state.json"
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {"restarts": 0, "last_restart": None}
        return {"restarts": 0, "last_restart": None}

    def _save_state(self) -> None:
        self.state_path.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    def _record_restart(self) -> None:
        self.state["restarts"] = int(self.state.get("restarts", 0)) + 1
        self.state["last_restart"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save_state()

    def run_once(self, port: int = 8000, endpoint_url: str | None = None) -> dict[str, Any]:
        monitor = MonitorAgent(self.root)
        port_check = monitor.check_port(port)
        endpoint_url = endpoint_url or f"http://127.0.0.1:{port}/health"
        endpoint_check = monitor.check_http_endpoint(endpoint_url)
        healthy = port_check.get("ok", False) and endpoint_check.get("ok", False)
        return {
            "ok": healthy,
            "port_check": port_check,
            "endpoint_check": endpoint_check,
            "restarts": self.state.get("restarts", 0),
            "last_restart": self.state.get("last_restart"),
        }

    def watch(self, interval: int = 30, port: int = 8000, endpoint_url: str | None = None) -> dict[str, Any]:
        while True:
            result = self.run_once(port=port, endpoint_url=endpoint_url)
            if not result["ok"]:
                self._record_restart()
                monitor = MonitorAgent(self.root)
                monitor.stop_service("python")
                monitor.start_service([sys.executable, str(self.root / "main.py")])
            time.sleep(interval)

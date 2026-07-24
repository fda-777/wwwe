import os
import platform
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class MonitorAgent:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1]

    def check_process(self, process_name: str) -> dict[str, Any]:
        if platform.system().lower() == "windows":
            try:
                output = subprocess.check_output(["tasklist", "/FO", "CSV"], text=True)
            except subprocess.CalledProcessError as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": process_name.lower() in output.lower(), "output": output}
        try:
            output = subprocess.check_output(["pgrep", "-af", process_name], text=True)
        except subprocess.CalledProcessError:
            return {"ok": False, "error": "Process not found"}
        return {"ok": True, "output": output}

    def check_port(self, port: int) -> dict[str, Any]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            try:
                sock.connect(("127.0.0.1", port))
            except OSError as exc:
                return {"ok": False, "error": str(exc), "port": port}
        return {"ok": True, "port": port}

    def check_http_endpoint(self, url: str) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                status_code = response.getcode()
            return {"ok": 200 <= status_code < 400, "status_code": status_code, "url": url}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return {"ok": False, "error": str(exc), "url": url}

    def collect_runtime_metrics(self) -> dict[str, Any]:
        metrics: dict[str, Any] = {}
        try:
            import psutil
        except ImportError:
            return {"ok": False, "error": "psutil not installed"}
        process = psutil.Process(os.getpid())
        metrics["cpu_percent"] = round(process.cpu_percent(interval=None), 2)
        metrics["memory_percent"] = round(process.memory_percent(), 2)
        return metrics

    def start_service(self, command: list[str]) -> dict[str, Any]:
        try:
            subprocess.Popen(command, cwd=self.root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
            return {"ok": True, "command": command}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}

    def stop_service(self, process_name: str) -> dict[str, Any]:
        if platform.system().lower() == "windows":
            try:
                subprocess.run(["taskkill", "/F", "/IM", process_name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as exc:
                return {"ok": False, "error": str(exc)}
            return {"ok": True, "process": process_name}
        try:
            subprocess.run(["pkill", "-f", process_name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as exc:
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "process": process_name}


def check_http_endpoint(url: str) -> dict[str, Any]:
    return MonitorAgent().check_http_endpoint(url)

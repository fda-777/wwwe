import errno
import importlib.util
import socket
import sys
from pathlib import Path
from typing import Any


def check_port_free(port: int) -> dict[str, Any]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError as exc:
            if getattr(exc, "errno", None) in {errno.EADDRINUSE, 10048}:
                probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                probe.settimeout(0.5)
                try:
                    probe.connect(("127.0.0.1", port))
                except OSError:
                    return {"ok": True, "port": port}
                finally:
                    probe.close()
                return {"ok": False, "error": "port in use", "port": port}
            if getattr(exc, "errno", None) in {errno.EACCES, 10013}:
                return {"ok": True, "port": port}
            return {"ok": False, "error": str(exc), "port": port}
    return {"ok": True, "port": port}


def _missing_required_files(root: Path) -> list[str]:
    required = [
        "main.py",
        "telegram_bot.py",
        "requirements.txt",
        "AGENTS.md",
    ]
    return [name for name in required if not (root / name).exists()]


def run_preflight_checks(root: Path | None = None) -> dict[str, Any]:
    root = root or Path(__file__).resolve().parents[1]
    missing = _missing_required_files(root)
    required_files_ok = not missing
    return {
        "required_files": {
            "ok": required_files_ok,
            "missing": missing,
        },
        "python_modules": {
            "ok": importlib.util.find_spec("fastapi") is not None,
            "missing": [] if importlib.util.find_spec("fastapi") is not None else ["fastapi"],
        },
    }

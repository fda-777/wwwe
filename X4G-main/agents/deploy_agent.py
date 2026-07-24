import subprocess
import sys
from pathlib import Path
from typing import Any


class DeployAgent:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1]

    def run(self, command: str) -> dict[str, Any]:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", *command.split()],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

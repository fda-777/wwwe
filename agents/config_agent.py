import json
import os
from pathlib import Path
from typing import Any


class ConfigAgent:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1]

    def load_environment(self) -> dict[str, Any]:
        env: dict[str, Any] = {}
        for key in ("PORT", "ADMIN_PASSWORD", "SECRET_KEY", "DATA_DIR", "RAILWAY_PUBLIC_DOMAIN"):
            value = os.environ.get(key)
            if value is not None:
                env[key] = value
        return env

    def save_report(self, report: dict[str, Any], path: str | None = None) -> Path:
        target = Path(path or self.root / "reports" / "config_report.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return target

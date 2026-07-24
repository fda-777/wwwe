import json
import sys
from pathlib import Path

from agents.health_agent import run_preflight_checks


def main() -> int:
    root = Path(__file__).resolve().parent
    report = run_preflight_checks(root)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    ok = report["required_files"]["ok"]
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

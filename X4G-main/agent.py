import argparse
import json
import sys
from pathlib import Path

from agents.config_agent import ConfigAgent
from agents.deploy_agent import DeployAgent
from agents.health_agent import check_port_free, run_preflight_checks
from agents.log_agent import LogAgent
from agents.monitor_agent import MonitorAgent
from agents.watchdog_agent import WatchdogAgent

ROOT = Path(__file__).resolve().parent


def build_report() -> dict[str, object]:
    checks = run_preflight_checks(ROOT)
    config_agent = ConfigAgent(ROOT)
    env = config_agent.load_environment()
    port = int(env.get("PORT", 8000))
    port_check = check_port_free(port)
    monitor = MonitorAgent(ROOT)
    runtime_metrics = monitor.collect_runtime_metrics()
    endpoint_url = env.get("HEALTH_URL") or "http://127.0.0.1:8000/health"
    endpoint_check = monitor.check_http_endpoint(endpoint_url)
    return {
        "root": str(ROOT),
        "environment": env,
        "checks": checks,
        "port_check": port_check,
        "runtime_metrics": runtime_metrics,
        "endpoint_check": endpoint_check,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="X4G management agent")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "check", "report", "restart", "start", "stop", "watch"])
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--endpoint", default=None)
    args = parser.parse_args()

    logger = LogAgent(ROOT)
    logger.info(f"Received command: {args.command}")

    if args.command == "status":
        report = build_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    if args.command == "check":
        report = build_report()
        ok = report["checks"]["required_files"]["ok"] and report["port_check"]["ok"]
        print(json.dumps({"ok": ok, "report": report}, indent=2, ensure_ascii=False))
        return 0 if ok else 1

    if args.command == "report":
        report = build_report()
        config_agent = ConfigAgent(ROOT)
        path = config_agent.save_report(report, str(ROOT / "reports" / "agent_report.json"))
        print(f"Report saved to {path}")
        return 0

    if args.command == "restart":
        deploy_agent = DeployAgent(ROOT)
        result = deploy_agent.run("main.py")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["ok"] else 1

    if args.command == "start":
        monitor = MonitorAgent(ROOT)
        result = monitor.start_service([sys.executable, str(ROOT / "main.py")])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["ok"] else 1

    if args.command == "stop":
        monitor = MonitorAgent(ROOT)
        result = monitor.stop_service("python")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["ok"] else 1

    if args.command == "watch":
        watchdog = WatchdogAgent(ROOT)
        print(json.dumps({"watching": True, "interval": args.interval, "port": args.port}, indent=2, ensure_ascii=False))
        watchdog.watch(interval=args.interval, port=args.port, endpoint_url=args.endpoint)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

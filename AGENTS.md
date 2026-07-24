# AGENTS.md

## Project overview
- This repository contains an X4G FastAPI-based VPN gateway service with VLESS/WebSocket and XHTTP support.
- The main application entrypoint is [main.py](main.py).
- The Telegram bot logic lives in [telegram_bot.py](telegram_bot.py).
- State is persisted to disk under the DATA_DIR path (default: /data) using x4g_state.json.

## Working conventions
- Prefer small, targeted changes that preserve the existing architecture.
- Keep the app behavior compatible with the current FastAPI startup/shutdown pattern.
- Avoid breaking the persistence logic in main.py unless the change explicitly requires it.
- Preserve Persian comments and existing naming patterns where possible.

## Validation
- After changing Python files, validate syntax with:
  - `python -m py_compile main.py telegram_bot.py relay_vless.py speed_limit.py xhttp_siz10.py pages.py agent.py`
- If you add a new runtime dependency, update [requirements.txt](requirements.txt) accordingly.

## Run locally
- Start the service with:
  - `python main.py`
- The app exposes the main dashboard and API routes through FastAPI.

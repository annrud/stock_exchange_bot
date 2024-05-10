from pathlib import Path

from aiohttp.web import run_app

from app.web.app import setup_app

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    run_app(setup_app(BASE_DIR / "local/config.yaml"))

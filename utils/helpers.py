import logging
import logging.handlers
from pathlib import Path


VERSION = "1.1.0"
LOG_DIR = Path.home() / "AppData" / "Roaming" / "Aether"


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "app.log"

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8")
    handler.setFormatter(fmt)

    console = logging.StreamHandler()
    console.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    root.addHandler(console)

    logging.getLogger("requests").setLevel(logging.WARNING)


def aeth_from_units(units: int) -> float:
    return units / 10_000_000_000


def units_from_aeth(aeth: float) -> int:
    return int(aeth * 10_000_000_000)


def shorten_hash(h: str, chars: int = 8) -> str:
    if len(h) <= chars * 2 + 2:
        return h
    return f"{h[:chars]}...{h[-chars:]}"


def check_for_update() -> dict | None:
    try:
        import requests as req
        resp = req.get("https://api.github.com/repos/dony971/aether-wallet/releases/latest", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        latest_tag = data.get("tag_name", "v0.0.0")
        latest_version = latest_tag.lstrip("v")

        def parse_ver(v):
            parts = v.split(".")
            return tuple(int(p) if p.isdigit() else 0 for p in parts)

        if parse_ver(latest_version) > parse_ver(VERSION):
            return {
                "tag": latest_tag,
                "version": latest_version,
                "body": data.get("body", "").strip()[:300],
                "url": "https://github.com/dony971/aether-wallet/releases/latest",
            }
    except Exception:
        pass
    return None

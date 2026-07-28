import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from core.config import config

AUDIT_FILE = config.data_dir / "audit.log"
_MAX_FILE_SIZE = 1_000_000
logger = logging.getLogger(__name__)

_EVENT_TYPES = {
    "WALLET_CREATE", "WALLET_LOAD", "WALLET_IMPORT", "WALLET_DELETE",
    "PIN_SET", "PIN_REMOVE", "PIN_VERIFY_OK", "PIN_VERIFY_FAIL",
    "PIN_LOCKOUT", "PIN_RESET",
    "NODE_START", "NODE_CRASH", "NODE_ERROR",
    "SESSION_LOCK", "SESSION_UNLOCK", "SESSION_TIMEOUT",
}


def _rotate():
    if AUDIT_FILE.exists() and AUDIT_FILE.stat().st_size > _MAX_FILE_SIZE:
        rotated = AUDIT_FILE.with_suffix(".log.1")
        AUDIT_FILE.rename(rotated)


def log(event: str, detail: str = "", **extra):
    if event not in _EVENT_TYPES:
        event = f"UNKNOWN_{event}"
    ts = datetime.now(timezone.utc).isoformat()
    entry = {"ts": ts, "event": event, "detail": detail}
    if extra:
        entry.update(extra)
    _rotate()
    try:
        AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning("Audit log write failed: %s", e)


def get_recent(n: int = 50) -> list[dict]:
    if not AUDIT_FILE.exists():
        return []
    try:
        lines = AUDIT_FILE.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(l) for l in lines[-n:]]
    except Exception as e:
        logger.warning("Audit log read failed: %s", e)
        return []

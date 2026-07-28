import hashlib
import json
import os
import time
from pathlib import Path

from core.config import config

PIN_FILE = config.data_dir / ".pin"
LOCKOUT_FILE = config.data_dir / ".pin_lockout"
_PBKDF2_ITERATIONS = 600_000
_MAX_ATTEMPTS = 5
_LOCKOUT_DURATION = 300  # 5 minutes


def _read() -> tuple[str, str] | None:
    if not PIN_FILE.exists():
        return None
    try:
        parts = PIN_FILE.read_text().strip().split(":")
        if len(parts) >= 2:
            return parts[0], parts[1]
    except Exception:
        return None
    return None


def _write(salt: str, pin_hash: str):
    PIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    PIN_FILE.write_text(f"{salt}:{pin_hash}")


def _hash(pin: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt.encode(), _PBKDF2_ITERATIONS).hex()


def _read_lockout() -> dict:
    try:
        if LOCKOUT_FILE.exists():
            return json.loads(LOCKOUT_FILE.read_text())
    except Exception:
        pass
    return {"attempts": 0, "until": 0}


def _write_lockout(data: dict):
    LOCKOUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCKOUT_FILE.write_text(json.dumps(data))


def _clear_lockout():
    _write_lockout({"attempts": 0, "until": 0})


def is_locked() -> bool:
    data = _read_lockout()
    if data["until"] and time.time() < data["until"]:
        return True
    if data["until"] and time.time() >= data["until"]:
        _clear_lockout()
    return False


def lockout_remaining() -> int:
    data = _read_lockout()
    if data["until"]:
        rem = int(data["until"] - time.time())
        return max(rem, 0)
    return 0


def is_set() -> bool:
    return PIN_FILE.exists()


def set_pin(pin: str):
    salt = os.urandom(16).hex()
    pin_hash = _hash(pin, salt)
    _write(salt, pin_hash)
    _clear_lockout()
    from utils.audit import log as audit_log
    audit_log("PIN_SET", "New PIN configured")


def verify(pin: str) -> bool:
    if is_locked():
        return False
    data = _read()
    if not data:
        return False
    salt, pin_hash = data
    ok = _hash(pin, salt) == pin_hash
    from utils.audit import log as audit_log
    if ok:
        _clear_lockout()
        audit_log("PIN_VERIFY_OK", "PIN verified successfully")
    else:
        lockout = _read_lockout()
        lockout["attempts"] += 1
        audit_log("PIN_VERIFY_FAIL", f"Wrong PIN (attempt {lockout['attempts']}/{_MAX_ATTEMPTS})")
        if lockout["attempts"] >= _MAX_ATTEMPTS:
            lockout["until"] = time.time() + _LOCKOUT_DURATION
            audit_log("PIN_LOCKOUT", f"Locked out for {_LOCKOUT_DURATION}s after {_MAX_ATTEMPTS} failures")
        _write_lockout(lockout)
    return ok


def remove_pin():
    try:
        PIN_FILE.unlink(missing_ok=True)
    except Exception:
        pass
    _clear_lockout()
    from utils.audit import log as audit_log
    audit_log("PIN_REMOVE", "PIN removed")

import hashlib
import os
from pathlib import Path

from core.config import config

PIN_FILE = config.data_dir / ".pin"
_PBKDF2_ITERATIONS = 600_000


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


def is_set() -> bool:
    return PIN_FILE.exists()


def set_pin(pin: str):
    salt = os.urandom(16).hex()
    pin_hash = _hash(pin, salt)
    _write(salt, pin_hash)


def verify(pin: str) -> bool:
    data = _read()
    if not data:
        return False
    salt, pin_hash = data
    return _hash(pin, salt) == pin_hash


def remove_pin():
    try:
        PIN_FILE.unlink(missing_ok=True)
    except Exception:
        pass

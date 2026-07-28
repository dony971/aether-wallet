import os
import json
import base64
import hashlib
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.config import config

_AES_KEY_SIZE = 32
_NONCE_SIZE = 12
_PIN_ITERATIONS = 600_000


def _derive_key(pin: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=_AES_KEY_SIZE, salt=salt, iterations=_PIN_ITERATIONS)
    return kdf.derive(pin.encode())


def _wallet_key_file() -> Path:
    return config.data_dir / ".wallet_key"


def _stored_key() -> bytes | None:
    kf = _wallet_key_file()
    if not kf.exists():
        return None
    try:
        return bytes.fromhex(kf.read_text().strip())
    except Exception:
        return None


def _store_key(key: bytes):
    kf = _wallet_key_file()
    kf.parent.mkdir(parents=True, exist_ok=True)
    kf.write_text(key.hex())


def _delete_key():
    kf = _wallet_key_file()
    if kf.exists():
        kf.unlink(missing_ok=True)


def encrypt_wallet(data: dict, pin: str | None = None, reuse_key: bytes | None = None) -> bytes:
    plain = json.dumps(data, indent=2).encode()
    nonce = os.urandom(_NONCE_SIZE)
    if pin:
        salt = os.urandom(16)
        key = _derive_key(pin, salt)
        blob = AESGCM(key).encrypt(nonce, plain, None)
        return json.dumps({"v": 1, "m": "pin", "salt": salt.hex(), "nonce": nonce.hex(), "data": blob.hex()}).encode()
    else:
        if reuse_key:
            key = reuse_key
        else:
            key = os.urandom(_AES_KEY_SIZE)
            _store_key(key)
        blob = AESGCM(key).encrypt(nonce, plain, None)
        return json.dumps({"v": 1, "m": "keyfile", "nonce": nonce.hex(), "data": blob.hex()}).encode()


def decrypt_wallet(raw: bytes, pin: str | None = None) -> dict:
    try:
        env = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return json.loads(raw.decode()) if isinstance(raw, bytes) else raw

    if not isinstance(env, dict) or "v" not in env:
        return env

    nonce = bytes.fromhex(env["nonce"])
    data = bytes.fromhex(env["data"])

    if env.get("m") == "pin":
        if not pin:
            raise ValueError("PIN required")
        salt = bytes.fromhex(env["salt"])
        key = _derive_key(pin, salt)
    elif env.get("m") == "keyfile":
        stored = _stored_key()
        if not stored:
            raise ValueError("Wallet key file missing")
        key = stored
    else:
        raise ValueError("Unknown encryption method")

    try:
        plain = AESGCM(key).decrypt(nonce, data, None)
    except InvalidTag:
        raise ValueError("Wallet key is invalid or the file is corrupted. Create a new wallet or import using your private key.")
    return json.loads(plain)


def is_encrypted(raw: bytes) -> bool:
    try:
        env = json.loads(raw)
        return isinstance(env, dict) and "v" in env and "m" in env
    except Exception:
        return False


def encrypt_file(path: Path, data: dict, pin: str | None = None):
    encrypted = encrypt_wallet(data, pin)
    path.write_bytes(encrypted)


def decrypt_file(path: Path, pin: str | None = None) -> dict:
    raw = path.read_bytes()
    if not is_encrypted(raw):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("Wallet file is corrupted")
    return decrypt_wallet(raw, pin)


def remove_pin_encryption(path: Path, pin: str | None = None):
    raw = path.read_bytes()
    if not is_encrypted(raw):
        return
    data = decrypt_wallet(raw, pin)
    encrypt_file(path, data, pin=None)

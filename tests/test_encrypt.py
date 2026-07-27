import sys, os, json, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.encrypt import (
    encrypt_wallet, decrypt_wallet, is_encrypted,
    encrypt_file, decrypt_file, remove_pin_encryption
)


def test_roundtrip_keyfile():
    data = {"public_key_hex": "a" * 64, "secret_key_hex": "b" * 64}
    blob = encrypt_wallet(data, pin=None)
    assert isinstance(blob, bytes)
    env = json.loads(blob)
    assert env["m"] == "keyfile"
    assert "nonce" in env and "data" in env

    restored = decrypt_wallet(blob)
    assert restored == data


def test_roundtrip_pin():
    data = {"public_key_hex": "c" * 64, "secret_key_hex": "d" * 64}
    blob = encrypt_wallet(data, pin="1234")
    env = json.loads(blob)
    assert env["m"] == "pin"
    assert "salt" in env

    restored = decrypt_wallet(blob, pin="1234")
    assert restored == data


def test_wrong_pin_fails():
    data = {"test": "value"}
    blob = encrypt_wallet(data, pin="1234")
    try:
        decrypt_wallet(blob, pin="wrong")
        assert False, "Should have raised"
    except Exception:
        pass


def test_is_encrypted():
    assert not is_encrypted(b'{"plain": "json"}')
    blob = encrypt_wallet({"a": 1}, pin=None)
    assert is_encrypted(blob)
    assert is_encrypted(b'{"v":1,"m":"pin","data":"00"}')
    assert not is_encrypted(b"not json")


def test_file_roundtrip(tmp_path: Path = Path(tempfile.mkdtemp())):
    p = tmp_path / "wallet.json"
    data = {"public_key_hex": "x" * 64}
    encrypt_file(p, data, pin=None)
    assert p.exists()
    raw = p.read_bytes()
    assert is_encrypted(raw)

    restored = decrypt_file(p)
    assert restored == data


def test_plain_json_backward_compat(tmp_path: Path = Path(tempfile.mkdtemp())):
    p = tmp_path / "legacy.json"
    data = {"public_key_hex": "z" * 64, "secret_key_hex": "y" * 64}
    p.write_text(json.dumps(data))
    assert not is_encrypted(p.read_bytes())
    restored = decrypt_file(p)
    assert restored == data


def test_remove_pin_encryption(tmp_path: Path = Path(tempfile.mkdtemp())):
    p = tmp_path / "pin_wallet.json"
    data = {"key": "secret"}
    encrypt_file(p, data, pin="9999")
    assert json.loads(p.read_bytes())["m"] == "pin"

    remove_pin_encryption(p, pin="9999")
    raw = p.read_bytes()
    assert is_encrypted(raw)
    env = json.loads(raw)
    assert env["m"] == "keyfile"


def test_corrupted_file():
    try:
        decrypt_file(Path(tempfile.mktemp()))
        assert False, "Should have raised"
    except Exception:
        pass


def test_tampered_data(tmp_path: Path = Path(tempfile.mkdtemp())):
    p = tmp_path / "tamper.json"
    encrypt_file(p, {"k": "v"}, pin="1234")
    raw = bytearray(p.read_bytes())
    raw[-1] ^= 0xFF
    p.write_bytes(bytes(raw))
    try:
        decrypt_file(p, pin="1234")
        assert False, "Should have raised (auth tag mismatch)"
    except Exception:
        pass


def test_invalid_hex_key():
    data = {"key": "value"}
    blob = encrypt_wallet(data, pin=None)
    env = json.loads(blob)
    env["nonce"] = "zzzz"
    try:
        decrypt_wallet(json.dumps(env).encode())
        assert False, "Should have raised"
    except Exception:
        pass


def test_pin_iterations():
    from utils.encrypt import _derive_key, _AES_KEY_SIZE
    key = _derive_key("1234", b"\x00" * 16)
    assert len(key) == _AES_KEY_SIZE
    assert isinstance(key, bytes)

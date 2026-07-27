import json
import logging
from pathlib import Path
from typing import Optional

from core.config import config
from utils.encrypt import encrypt_file, decrypt_file, is_encrypted

logger = logging.getLogger(__name__)


class WalletManager:
    def __init__(self):
        self._address: str = ""
        self._public_key: str = ""
        self._secret_key: str = ""
        self._wallet_path: Optional[Path] = None
        self._load_error: str = ""
        self._active_name: str = ""
        self._encrypted_pending: bytes | None = None
        self._wallets_dir.mkdir(parents=True, exist_ok=True)
        self._load()

    @property
    def _wallets_dir(self) -> Path:
        return config.data_dir / "wallets"

    @property
    def _active_file(self) -> Path:
        return config.data_dir / ".active_wallet"

    @property
    def has_wallet(self) -> bool:
        return bool(self._address)

    @property
    def address(self) -> str:
        return self._address

    @property
    def public_key(self) -> str:
        return self._public_key

    @property
    def secret_key(self) -> str:
        return self._secret_key

    @property
    def wallet_file(self) -> Optional[Path]:
        return self._wallet_path

    @property
    def load_error(self) -> str:
        return self._load_error

    @property
    def active_name(self) -> str:
        return self._active_name or "default"

    @property
    def wallet_data(self) -> dict:
        return {"address": self._address, "public_key_hex": self._public_key}

    @property
    def pin_required(self) -> bool:
        return self._encrypted_pending is not None

    def list_wallets(self) -> list[dict]:
        wallets = []
        for f in self._wallets_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                addr = data.get("public_key_hex", data.get("address", ""))
                wallets.append({
                    "name": f.stem,
                    "address": addr[:16] + "..." if len(addr) > 16 else addr,
                    "path": str(f),
                })
            except Exception:
                try:
                    raw = f.read_bytes()
                    if is_encrypted(raw):
                        wallets.append({
                            "name": f.stem,
                            "address": "(encrypted)",
                            "path": str(f),
                        })
                        continue
                except Exception:
                    pass
        return wallets

    @staticmethod
    def _sanitize_name(name: str) -> str:
        safe = "".join(c for c in name if c.isalnum() or c in " _-")
        return safe.strip() or "wallet"

    def create_wallet(self, name: str = "default") -> str:
        name = self._sanitize_name(name)
        import tempfile, os, json
        from PySide6.QtCore import QProcess
        p = self._wallets_dir / f"{name}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".json")
        tmp.close()
        try:
            proc = QProcess()
            binary = config.node_binary
            proc.start(str(binary), ["keygen", tmp.name])
            proc.waitForFinished(5000)
            if proc.exitCode() == 0:
                data = json.loads(Path(tmp.name).read_bytes())
                encrypt_file(p, data, pin=None)
                self._set_active(name)
                self._load_from(p)
                return f"Wallet '{name}' created!"
            err = proc.readAllStandardError().data().decode()
            return f"Failed: {err.strip() or 'unknown error'}"
        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

    def switch_wallet(self, name: str) -> str:
        name = self._sanitize_name(name)
        p = self._wallets_dir / f"{name}.json"
        if not p.exists():
            return f"Wallet '{name}' not found."
        self._set_active(name)
        self._load_from(p)
        return f"Switched to '{name}'"

    def import_wallet(self, private_key_hex: str, name: str = "imported") -> str:
        if len(private_key_hex) not in (64, 128):
            return "Invalid key length (need 64 or 128 hex chars)."
        name = self._sanitize_name(name)
        import tempfile, os
        from PySide6.QtCore import QProcess
        key_tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".key")
        key_tmp.write(private_key_hex)
        key_tmp.close()
        out_tmp = tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".json")
        out_tmp.close()
        try:
            p = self._wallets_dir / f"{name}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            proc = QProcess()
            binary = config.node_binary
            proc.start(str(binary), ["keygen", "--import-file", key_tmp.name, out_tmp.name])
            proc.waitForFinished(5000)
            if proc.exitCode() == 0:
                data = json.loads(Path(out_tmp.name).read_bytes())
                encrypt_file(p, data, pin=None)
                self._set_active(name)
                self._load_from(p)
                return f"Wallet '{name}' imported!"
            err = proc.readAllStandardError().data().decode()
            return f"Import failed: {err.strip() or 'unknown error'}"
        finally:
            try:
                os.unlink(key_tmp.name)
            except Exception:
                pass
            try:
                os.unlink(out_tmp.name)
            except Exception:
                pass

    def delete_wallet(self, name: str) -> str:
        name = self._sanitize_name(name)
        if name == self.active_name:
            return "Cannot delete active wallet."
        p = self._wallets_dir / f"{name}.json"
        if p.exists():
            p.unlink()
            return f"Wallet '{name}' deleted."
        return f"Wallet '{name}' not found."

    def export_private_key(self) -> str:
        if not self._secret_key:
            return ""
        return self._secret_key

    def decrypt_with_pin(self, pin: str) -> str | None:
        if self._encrypted_pending is None or not self._wallet_path:
            return None
        try:
            data = decrypt_file(self._wallet_path, pin)
            self._apply_data(data)
            self._encrypted_pending = None
            return None
        except ValueError as e:
            return str(e)

    def mark_pin_protected(self, protected: bool, pin: str | None = None):
        if not self._wallet_path or not self._wallet_path.exists():
            return
        try:
            data = decrypt_file(self._wallet_path, pin)
            data["pin_protected"] = protected
            encrypt_file(self._wallet_path, data, pin=pin if protected else None)
        except Exception as e:
            logger.warning("Failed to update encryption: %s", e)

    def is_pin_protected(self) -> bool:
        if not self._wallet_path or not self._wallet_path.exists():
            return False
        try:
            raw = self._wallet_path.read_bytes()
            if is_encrypted(raw):
                import json as _json
                env = _json.loads(raw)
                return env.get("m") == "pin"
            data = _json.loads(raw)
            return bool(data.get("pin_protected", False))
        except Exception:
            return False

    def _set_active(self, name: str):
        self._active_name = name
        try:
            self._active_file.write_text(name)
        except Exception as e:
            logger.warning(f"Could not write active wallet: {e}")

    def _get_active_name(self) -> str:
        try:
            if self._active_file.exists():
                return self._active_file.read_text().strip()
        except Exception:
            pass
        return "default"

    def _wallet_file_path(self) -> Path:
        name = self._get_active_name()
        return self._wallets_dir / f"{name}.json"

    def _load(self):
        self._load_from(self._wallet_file_path())

    def _load_from(self, p: Path):
        if not p.exists():
            return
        try:
            raw = p.read_bytes()
            if not is_encrypted(raw):
                data = json.loads(raw)
                self._apply_data(data, p)
                self._migrate_to_encrypted(p, data)
                return
            env = json.loads(raw)
            if env.get("m") == "keyfile":
                from utils.encrypt import decrypt_wallet
                data = decrypt_wallet(raw)
                self._apply_data(data, p)
            elif env.get("m") == "pin":
                self._encrypted_pending = raw
                self._wallet_path = p
                self._active_name = p.stem
                self._load_error = ""
                logger.info("Wallet is PIN-encrypted, awaiting PIN")
            else:
                self._load_error = "Unknown encryption format"
        except Exception as e:
            self._load_error = f"Failed to load wallet: {e}"
            logger.error(self._load_error)

    def _migrate_to_encrypted(self, p: Path, data: dict):
        from utils.encrypt import encrypt_file
        try:
            encrypt_file(p, data, pin=None)
            logger.info("Migrated unencrypted wallet to encrypted (keyfile)")
        except Exception as e:
            logger.warning("Migration to encrypted failed: %s", e)

    def upgrade_to_pin_encryption(self, pin: str):
        if not self._wallet_path or not self._wallet_path.exists():
            return
        try:
            data = decrypt_file(self._wallet_path, pin)
            encrypt_file(self._wallet_path, data, pin=pin)
            data["pin_protected"] = True
            logger.info("Upgraded wallet to PIN-based encryption")
        except Exception as e:
            logger.warning("Failed to upgrade to PIN encryption: %s", e)

    def _apply_data(self, data: dict, p: Path | None = None):
        self._public_key = data.get("public_key_hex", "")
        self._secret_key = data.get("secret_key_hex", "")
        if self._public_key:
            self._address = self._public_key
            if p:
                self._wallet_path = p
            self._load_error = ""
            if p:
                self._active_name = p.stem
        else:
            self._load_error = "Wallet file is missing public key."
            logger.warning(self._load_error)

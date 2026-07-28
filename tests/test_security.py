import sys, os, json, tempfile, time
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.pin_manager import set_pin, verify, is_set, remove_pin, is_locked, lockout_remaining
from utils.audit import log as audit_log, get_recent
from core.config import config


def test_pin_set_verify():
    remove_pin()
    assert not is_set()
    set_pin("1234")
    assert is_set()
    assert verify("1234")
    assert not verify("wrong")
    assert not verify("")
    remove_pin()
    assert not is_set()


def test_pin_file_location():
    remove_pin()
    expected = config.data_dir / ".pin"
    assert not expected.exists()
    set_pin("5678")
    assert expected.exists()
    assert verify("5678")
    remove_pin()
    assert not expected.exists()


def test_pin_lockout():
    remove_pin()
    set_pin("9999")
    assert not is_locked()
    for _ in range(4):
        verify("wrong")
    assert not is_locked()
    verify("wrong")
    assert is_locked()
    assert lockout_remaining() > 0
    assert not verify("9999")
    remove_pin()
    assert not is_locked()


def test_audit_log_basic():
    from utils.audit import AUDIT_FILE
    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()
    audit_log("WALLET_CREATE", "Test wallet", address="abc123")
    audit_log("PIN_VERIFY_FAIL", "Wrong PIN attempt")
    logs = get_recent(10)
    assert len(logs) == 2
    assert logs[0]["event"] == "WALLET_CREATE"
    assert logs[0]["detail"] == "Test wallet"
    assert logs[0]["address"] == "abc123"
    assert logs[1]["event"] == "PIN_VERIFY_FAIL"
    AUDIT_FILE.unlink(missing_ok=True)



def test_invalid_hex_validation():
    from utils.contacts import add_contact, delete_contact
    msg = add_contact("HexTest1", "xyz")
    assert "64" in msg or "hex" in msg
    msg = add_contact("HexTest2", "g" * 64)
    assert "64" in msg or "hex" in msg
    msg = add_contact("HexTest3", "a" * 64)
    assert "added" in msg
    delete_contact("HexTest3")


def test_csv_injection():
    from ui.pages.transactions import TransactionsPage
    safe = lambda v: TransactionsPage._sanitize_csv(None, v)
    assert safe("=SUM(A1:A10)") == "'=SUM(A1:A10)"
    assert safe("+cmd|dir") == "'+cmd|dir"
    assert safe("-script") == "'-script"
    assert safe("@RISK") == "'@RISK"
    assert safe("normal text") == "normal text"
    assert safe("") == ""


def test_wallet_name_sanitize():
    from wallet.wallet_manager import WalletManager
    assert WalletManager._sanitize_name("My Wallet!@#") == "My Wallet"
    assert WalletManager._sanitize_name("../../../etc") == "etc"
    assert WalletManager._sanitize_name("") == "wallet"
    assert WalletManager._sanitize_name("valid-name_123") == "valid-name_123"

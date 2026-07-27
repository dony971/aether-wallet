import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from unittest.mock import patch

from utils import contacts

_orig_file = contacts.CONTACTS_FILE


def setup_function():
    contacts.CONTACTS_FILE = Path(tempfile.mktemp(suffix=".json"))


def teardown_function():
    if contacts.CONTACTS_FILE.exists():
        contacts.CONTACTS_FILE.unlink()
    contacts.CONTACTS_FILE = _orig_file


def test_add_and_list():
    contacts.add_contact("Alice", "a" * 64)
    result = contacts.list_contacts()
    names = [c["name"] for c in result]
    assert "Alice" in names
    contacts.delete_contact("Alice")


def test_search():
    contacts.add_contact("Bob", "b" * 64)
    result = contacts.search_contacts("Bob")
    assert len(result) == 1
    assert result[0]["name"] == "Bob"
    contacts.delete_contact("Bob")


def test_add_invalid_address():
    msg = contacts.add_contact("Test", "short")
    assert "64" in msg

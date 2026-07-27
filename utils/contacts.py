import json
import logging
from pathlib import Path
from typing import Optional

from core.config import config

logger = logging.getLogger(__name__)

CONTACTS_FILE = config.data_dir / "contacts.json"


def _load() -> list[dict]:
    if not CONTACTS_FILE.exists():
        return []
    try:
        data = json.loads(CONTACTS_FILE.read_text())
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.warning("Failed to load contacts: %s", e)
        return []


def _save(contacts: list[dict]):
    try:
        CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONTACTS_FILE.write_text(json.dumps(contacts, indent=2))
    except Exception as e:
        logger.error("Failed to save contacts: %s", e)


def list_contacts() -> list[dict]:
    return _load()


def add_contact(name: str, address: str, notes: str = "") -> str:
    if not name.strip():
        return "Name is required."
    if len(address) != 64 or not all(c in "0123456789abcdefABCDEF" for c in address):
        return "Address must be 64 valid hex characters."
    contacts = _load()
    for c in contacts:
        if c["name"].lower() == name.strip().lower():
            return f"Contact '{name}' already exists."
    contacts.append({"name": name.strip(), "address": address.strip(), "notes": notes.strip()})
    _save(contacts)
    return f"Contact '{name}' added."


def edit_contact(old_name: str, new_name: str, new_address: str, new_notes: str = "") -> str:
    if not new_name.strip():
        return "Name is required."
    if len(new_address) != 64:
        return "Address must be 64 hex characters."
    contacts = _load()
    for c in contacts:
        if c["name"].lower() == old_name.lower():
            c["name"] = new_name.strip()
            c["address"] = new_address.strip()
            c["notes"] = new_notes.strip()
            _save(contacts)
            return f"Contact '{old_name}' updated."
    return f"Contact '{old_name}' not found."


def delete_contact(name: str) -> str:
    contacts = _load()
    filtered = [c for c in contacts if c["name"].lower() != name.lower()]
    if len(filtered) == len(contacts):
        return f"Contact '{name}' not found."
    _save(filtered)
    return f"Contact '{name}' deleted."


def search_contacts(query: str) -> list[dict]:
    q = query.strip().lower()
    if not q:
        return _load()
    contacts = _load()
    return [
        c for c in contacts
        if q in c["name"].lower() or q in c["address"].lower()
    ]

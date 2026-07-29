from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QClipboard
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QInputDialog, QApplication

from ui.theme import BG_PRIMARY, BG_CARD, BG_CARD_HOVER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT, BORDER, ERROR, SUCCESS
from utils import contacts
from utils.i18n import _


class AddressBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_address = ""

        self.setWindowTitle(_("Address Book"))
        self.setFixedSize(520, 520)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer = QFrame()
        outer.setStyleSheet(f"background-color: {BG_PRIMARY}; border-radius: 14px; border: 1px solid {BORDER};")
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel(_("Address Book"))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 700; background: transparent;")
        layout.addWidget(title)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(_("Search by name or address..."))
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 8px 12px; font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        self._search_input.textChanged.connect(self._refresh_list)
        layout.addWidget(self._search_input)

        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background-color: {BG_CARD}; border: 1px solid {BORDER};
                border-radius: 8px; padding: 4px; color: {TEXT_PRIMARY};
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 10px 12px; border-bottom: 1px solid {BORDER};
                border-radius: 6px;
            }}
            QListWidget::item:selected {{
                background-color: {ACCENT}33; color: {TEXT_PRIMARY};
            }}
            QListWidget::item:hover {{
                background-color: {BG_CARD_HOVER};
            }}
        """)
        self._list.itemDoubleClicked.connect(self._on_send_to)
        layout.addWidget(self._list, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._add_btn = QPushButton(_("+ Add"))
        self._add_btn.setStyleSheet(self._btn_style(ACCENT))
        self._add_btn.clicked.connect(self._on_add)
        btn_row.addWidget(self._add_btn)

        self._edit_btn = QPushButton(_("Edit"))
        self._edit_btn.setStyleSheet(self._btn_style(ACCENT))
        self._edit_btn.clicked.connect(self._on_edit)
        btn_row.addWidget(self._edit_btn)

        self._delete_btn = QPushButton(_("Delete"))
        self._delete_btn.setStyleSheet(self._btn_style(ERROR))
        self._delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(self._delete_btn)

        self._send_btn = QPushButton(_("Send To"))
        self._send_btn.setStyleSheet(self._btn_style(SUCCESS))
        self._send_btn.clicked.connect(self._on_send_to)
        btn_row.addWidget(self._send_btn)

        layout.addLayout(btn_row)

        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton(_("Close"))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #0A0A1A; font-weight: 700;
                border-radius: 8px; padding: 10px 24px; font-size: 13px; border: none;
            }}
            QPushButton:hover {{ background-color: #00EECC; }}
        """)
        close_btn.clicked.connect(self.accept)
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(outer)

        self._refresh_list()

    def _btn_style(self, color: str) -> str:
        return f"""
            QPushButton {{
                background-color: transparent; color: {color}; font-weight: 600;
                border-radius: 6px; padding: 8px 14px; font-size: 11px;
                border: 1px solid {color}44;
            }}
            QPushButton:hover {{ background-color: {color}22; border-color: {color}; }}
        """

    def _refresh_list(self):
        self._list.clear()
        query = self._search_input.text().strip()
        results = contacts.search_contacts(query) if query else contacts.list_contacts()
        for c in results:
            short = c["address"][:16] + "..."
            notes = f" — {c['notes'][:30]}" if c.get("notes") else ""
            text = f"{c['name']}  ({short}){notes}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, c["name"])
            self._list.addItem(item)

    def _get_selected_name(self) -> str:
        item = self._list.currentItem()
        return item.data(Qt.UserRole) if item else ""

    def _on_add(self):
        name, ok = QInputDialog.getText(self, _("Add Contact"), _("Name:"))
        if not ok or not name.strip():
            return
        addr, ok2 = QInputDialog.getText(self, _("Add Contact"), _("Address (64 hex):"))
        if not ok2 or len(addr.strip()) != 64:
            QMessageBox.warning(self, _("Invalid"), _("Address must be 64 hex characters."))
            return
        notes, ok3 = QInputDialog.getText(self, _("Add Contact"), _("Notes (optional):"))
        if not ok3:
            notes = ""
        msg = contacts.add_contact(name.strip(), addr.strip(), notes.strip())
        QMessageBox.information(self, "Contact", msg)
        self._refresh_list()

    def _on_edit(self):
        name = self._get_selected_name()
        if not name:
            return
        all_c = contacts.list_contacts()
        c = next((x for x in all_c if x["name"] == name), None)
        if not c:
            return
        new_name, ok = QInputDialog.getText(self, _("Edit Contact"), _("Name:"), text=c["name"])
        if not ok:
            return
        new_addr, ok2 = QInputDialog.getText(self, _("Edit Contact"), _("Address:"), text=c["address"])
        if not ok2 or len(new_addr.strip()) != 64:
            return
        new_notes, ok3 = QInputDialog.getText(self, _("Edit Contact"), _("Notes:"), text=c.get("notes", ""))
        if not ok3:
            new_notes = ""
        msg = contacts.edit_contact(name, new_name.strip(), new_addr.strip(), new_notes.strip())
        QMessageBox.information(self, "Contact", msg)
        self._refresh_list()

    def _on_delete(self):
        name = self._get_selected_name()
        if not name:
            return
        if QMessageBox.question(self, _("Confirm"), _("Delete '%s'?") % name,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            msg = contacts.delete_contact(name)
        QMessageBox.information(self, _("Contact"), msg)
        self._refresh_list()

    def _on_send_to(self):
        name = self._get_selected_name()
        if not name:
            return
        all_c = contacts.list_contacts()
        c = next((x for x in all_c if x["name"] == name), None)
        if c:
            self.selected_address = c["address"]
            self.accept()

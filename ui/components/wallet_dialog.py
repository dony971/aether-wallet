from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QInputDialog

from ui.theme import BG_PRIMARY, BG_CARD, BG_CARD_HOVER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT, BORDER, ERROR, SUCCESS
from wallet.wallet_manager import WalletManager
from utils.i18n import _


class ManageWalletsDialog(QDialog):
    def __init__(self, wallet_mgr: WalletManager, parent=None):
        super().__init__(parent)
        self._wm = wallet_mgr
        self.setWindowTitle(_("Manage Wallets"))
        self.setFixedSize(500, 500)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer = QFrame()
        outer.setStyleSheet(f"background-color: {BG_PRIMARY}; border-radius: 14px; border: 1px solid {BORDER};")
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel(_("Manage Wallets"))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 700; background: transparent;")
        layout.addWidget(title)

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
        layout.addWidget(self._list, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._create_btn = QPushButton(_("+ New"))
        self._create_btn.setStyleSheet(self._btn_style(ACCENT))
        self._create_btn.clicked.connect(self._on_create)
        btn_row.addWidget(self._create_btn)

        self._switch_btn = QPushButton(_("Switch"))
        self._switch_btn.setStyleSheet(self._btn_style(SUCCESS))
        self._switch_btn.clicked.connect(self._on_switch)
        btn_row.addWidget(self._switch_btn)

        self._import_btn = QPushButton(_("Import"))
        self._import_btn.setStyleSheet(self._btn_style(ACCENT))
        self._import_btn.clicked.connect(self._on_import)
        btn_row.addWidget(self._import_btn)

        self._delete_btn = QPushButton(_("Delete"))
        self._delete_btn.setStyleSheet(self._btn_style(ERROR))
        self._delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(self._delete_btn)

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
        for w in self._wm.list_wallets():
            item = QListWidgetItem(f"{w['name']}  —  {w['address']}")
            item.setData(Qt.UserRole, w["name"])
            if w["name"] == self._wm.active_name:
                item.setText(f"  \u25B6  {w['name']}  —  {w['address']}")
                item.setForeground(QColor(ACCENT))
            self._list.addItem(item)

    def _on_create(self):
        name, ok = QInputDialog.getText(self, _("New Wallet"), _("Wallet name:"), text=_("wallet2"))
        if not ok or not name.strip():
            return
        msg = self._wm.create_wallet(name.strip())
        QMessageBox.information(self, "Wallet", msg)
        self._refresh_list()

    def _on_switch(self):
        item = self._list.currentItem()
        if not item:
            return
        name = item.data(Qt.UserRole)
        if name == self._wm.active_name:
            return
        msg = self._wm.switch_wallet(name)
        QMessageBox.information(self, "Wallet", msg)
        self._refresh_list()
        self.accept()

    def _on_import(self):
        key, ok = QInputDialog.getText(
            self, _("Import Wallet"), _("Private key (64 or 128 hex chars):")
        )
        if not ok or not key.strip():
            return
        name, ok2 = QInputDialog.getText(self, _("Import Wallet"), _("Wallet name:"), text=_("imported"))
        if not ok2:
            return
        msg = self._wm.import_wallet(key.strip(), name.strip())
        QMessageBox.information(self, "Wallet", msg)
        self._refresh_list()

    def _on_delete(self):
        item = self._list.currentItem()
        if not item:
            return
        name = item.data(Qt.UserRole)
        if name == self._wm.active_name:
            QMessageBox.warning(self, _("Cannot Delete"), _("Switch to another wallet first."))
            return
        if QMessageBox.question(self, _("Confirm"), _("Delete wallet '%s'?") % name,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            msg = self._wm.delete_wallet(name)
        QMessageBox.information(self, _("Wallet"), msg)
        self._refresh_list()




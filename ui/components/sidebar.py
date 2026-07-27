from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QPainterPath, QLinearGradient, QBrush
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame

from ui.theme import BG_SIDEBAR, ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER


class SidebarButton(QPushButton):
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self._icon = icon
        self._text = text
        self._active = False
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setToolTip(text)

    def set_active(self, active: bool):
        self._active = active
        self.setChecked(active)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        if self._active:
            rect_path = QPainterPath()
            rect_path.addRoundedRect(6, 4, w - 12, h - 8, 10, 10)
            grad = QLinearGradient(0, 0, w, 0)
            grad.setColorAt(0.0, QColor(ACCENT + "18"))
            grad.setColorAt(1.0, QColor(ACCENT + "08"))
            painter.fillPath(rect_path, QBrush(grad))
            painter.setPen(QPen(QColor(ACCENT + "44"), 1))
            painter.drawPath(rect_path)

            accent_path = QPainterPath()
            accent_path.addRoundedRect(6, 12, 3, h - 24, 1.5, 1.5)
            painter.fillPath(accent_path, QColor(ACCENT))

            painter.setPen(QPen(QColor("#FFFFFF"), 1.2))
        elif self.underMouse():
            painter.fillRect(self.rect(), QColor("#FFFFFF0C"))
            painter.setPen(QPen(QColor(TEXT_SECONDARY), 1))
        else:
            painter.setPen(QPen(QColor(TEXT_MUTED), 1))

        icon_font = QFont("Segoe UI", 15)
        painter.setFont(icon_font)
        painter.drawText(16, 0, 28, h, Qt.AlignCenter, self._icon)

        text_font = QFont("Segoe UI", 12, QFont.Weight.Medium if self._active else QFont.Weight.Normal)
        painter.setFont(text_font)
        painter.drawText(52, 0, w - 62, h, Qt.AlignVCenter, self._text)

        painter.end()


class Sidebar(QFrame):
    page_changed = Signal(int)

    def __init__(self, wallet_mgr=None, parent=None):
        super().__init__(parent)
        self._wallet_mgr = wallet_mgr
        self.setFixedWidth(220)
        self.setStyleSheet(f"background-color: {BG_SIDEBAR}; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        logo = QLabel("  \u25C8  AETHER")
        logo.setStyleSheet(f"color: {ACCENT}; font-size: 20px; font-weight: 800; padding: 28px 18px 16px 18px; background: transparent; letter-spacing: 1px;")
        layout.addWidget(logo)

        subtitle = QLabel("  Wallet")
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 0 18px 4px 18px; background: transparent;")
        layout.addWidget(subtitle)

        self._wallet_label = QLabel("  loading...")
        self._wallet_label.setStyleSheet(f"color: {ACCENT}; font-size: 11px; font-weight: 600; padding: 0 18px 2px 18px; background: transparent;")
        layout.addWidget(self._wallet_label)

        self._manage_wallets_btn = QPushButton("  Manage Wallets")
        self._manage_wallets_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {TEXT_MUTED}; font-weight: 500;
                border-radius: 6px; padding: 4px 18px; font-size: 10px; border: none;
                text-align: left;
            }}
            QPushButton:hover {{ color: {ACCENT}; background-color: {ACCENT}11; }}
        """)
        self._manage_wallets_btn.clicked.connect(self._show_manage_wallets)
        layout.addWidget(self._manage_wallets_btn)

        self._address_book_btn = QPushButton("  Address Book")
        self._address_book_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {TEXT_MUTED}; font-weight: 500;
                border-radius: 6px; padding: 4px 18px; font-size: 10px; border: none;
                text-align: left;
            }}
            QPushButton:hover {{ color: {ACCENT}; background-color: {ACCENT}11; }}
        """)
        self._address_book_btn.clicked.connect(self._show_address_book)
        layout.addWidget(self._address_book_btn)

        self._buttons = []
        pages = [
            ("\u25A0", "Dashboard"),
            ("\u2197", "Send"),
            ("\u2199", "Receive"),
            ("\u2637", "Transactions"),
            ("\u2606", "Staking"),
            ("\u26CF", "Mining"),
            ("\u2699", "Settings"),
        ]

        for icon, text in pages:
            btn = SidebarButton(icon, text)
            btn.clicked.connect(lambda checked, i=len(self._buttons): self._select_page(i))
            layout.addWidget(btn)
            self._buttons.append(btn)

        layout.addStretch()

        ver = QLabel("v1.0.0  |  SEDC")
        ver.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; padding: 16px 20px 4px 20px; background: transparent;")
        layout.addWidget(ver)

        self._help_btn = QPushButton("?  Help")
        self._help_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {TEXT_MUTED}; font-weight: 500;
                border-radius: 6px; padding: 6px 18px; font-size: 11px; border: none;
                text-align: left;
            }}
            QPushButton:hover {{ color: {ACCENT}; background-color: {ACCENT}11; }}
        """)
        self._help_btn.clicked.connect(self._show_help)
        layout.addWidget(self._help_btn)

        self._select_page(0)

    def update_wallet_label(self):
        if self._wallet_mgr and self._wallet_mgr.has_wallet:
            self._wallet_label.setText(f"  {self._wallet_mgr.active_name}")
        else:
            self._wallet_label.setText("  No wallet")

    def _show_help(self):
        from ui.components.help_dialog import HelpDialog
        dlg = HelpDialog(self.window())
        dlg.exec()

    def _show_manage_wallets(self):
        if not self._wallet_mgr:
            return
        from ui.components.wallet_dialog import ManageWalletsDialog
        dlg = ManageWalletsDialog(self._wallet_mgr, self.window())
        if dlg.exec() == ManageWalletsDialog.Accepted:
            self.update_wallet_label()
            self._wallet_mgr._load()

    def _show_address_book(self):
        from ui.components.address_book_dialog import AddressBookDialog
        dlg = AddressBookDialog(self.window())
        if dlg.exec() == AddressBookDialog.Accepted and dlg.selected_address:
            self.page_changed.emit(1)
            win = self.window()
            if hasattr(win, '_send') and win._send._recipients:
                win._send._recipients[0].address.setText(dlg.selected_address)

    def _select_page(self, index: int):
        for i, btn in enumerate(self._buttons):
            btn.set_active(i == index)
        self.page_changed.emit(index)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(BG_SIDEBAR))
        painter.setPen(QPen(QColor(BORDER), 1))
        painter.drawLine(self.width() - 1, 60, self.width() - 1, self.height() - 20)
        painter.end()

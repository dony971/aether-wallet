from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import QUrl

from ui.theme import BG_PRIMARY, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT, BORDER


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.setFixedSize(480, 480)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer = QFrame()
        outer.setStyleSheet(f"background-color: {BG_PRIMARY}; border-radius: 14px; border: 1px solid {BORDER};")
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        title = QLabel("Help & Getting Started")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 700; background: transparent;")
        layout.addWidget(title)

        sections = [
            ("\u25A0  Dashboard", "View your balance, network stats, and live charts.\nTPS and balance history update automatically."),
            ("\u2197  Send", "Send AETH to one or multiple recipients.\nSelect fee (Low/Medium/High) and confirm."),
            ("\u2199  Receive", "Create a wallet, copy your address,\nscan QR code, or use Faucet to get test tokens."),
            ("\u2637  Transactions", "Browse all transactions, search by address/hash,\nclick for details, export to CSV."),
            ("\u2606  Staking", "Stake tokens to earn rewards.\nAPY 12.5%. Unstake anytime."),
            ("\u2699  Settings", "Node info, wallet backup, public key export,\ncheck for updates, data directory."),
        ]

        for heading, body in sections:
            s_title = QLabel(heading)
            s_title.setStyleSheet(f"color: {ACCENT}; font-size: 12px; font-weight: 600; background: transparent; margin-top: 4px;")
            layout.addWidget(s_title)
            s_body = QLabel(body)
            s_body.setWordWrap(True)
            s_body.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent; line-height: 1.5;")
            layout.addWidget(s_body)

        layout.addStretch()

        btn_row = QHBoxLayout()
        repo_btn = QPushButton("GitHub")
        repo_btn.setStyleSheet(self._btn_style())
        repo_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/dony971/aether")))
        btn_row.addWidget(repo_btn)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #0A0A1A; font-weight: 700;
                border-radius: 8px; padding: 10px 24px; font-size: 13px; border: none;
            }}
            QPushButton:hover {{ background-color: #00EECC; }}
        """)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(outer)

    def _btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: transparent; color: {ACCENT}; font-weight: 600;
                border-radius: 8px; padding: 10px 16px; font-size: 12px;
                border: 1px solid {ACCENT}44;
            }}
            QPushButton:hover {{ background-color: {ACCENT}22; border-color: {ACCENT}; }}
        """
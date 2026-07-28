from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame

from ui.theme import BG_PRIMARY, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT, BORDER
from utils.i18n import _


class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Welcome"))
        self.setFixedSize(520, 380)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer = QFrame()
        outer.setStyleSheet(f"background-color: {BG_PRIMARY}; border-radius: 16px; border: 1px solid {BORDER};")
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        icon = QLabel("\u25C8")
        icon.setStyleSheet(f"color: {ACCENT}; font-size: 36px; background: transparent;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel(_("Welcome to AETHER SEDC"))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: 700; background: transparent;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(
            _("You don't have a wallet yet.\n\n"
              "Create one to start sending, receiving,\n"
              "and staking AETH tokens.")
        )
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; background: transparent; line-height: 1.6;")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addStretch()

        self._create_btn = QPushButton(_("Create Wallet"))
        self._create_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #0A0A1A; font-weight: 700;
                border-radius: 8px; padding: 14px; font-size: 14px; border: none;
            }}
            QPushButton:hover {{ background-color: #00EECC; }}
        """)
        self._create_btn.clicked.connect(self.accept)
        layout.addWidget(self._create_btn)

        self._skip_btn = QPushButton(_("Skip for now"))
        self._skip_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {TEXT_MUTED}; font-weight: 500;
                border-radius: 8px; padding: 10px; font-size: 12px; border: none;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
        """)
        self._skip_btn.clicked.connect(self.reject)
        layout.addWidget(self._skip_btn)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(outer)
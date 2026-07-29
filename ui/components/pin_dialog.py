from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit

from ui.theme import BG_PRIMARY, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT, BORDER, ERROR
from utils.pin_manager import verify, set_pin, is_set
from utils.i18n import _


class PinDialog(QDialog):
    def __init__(self, mode: str = "unlock", parent=None):
        super().__init__(parent)
        self._mode = mode  # "unlock" | "set" | "confirm"
        self._pin = ""

    def get_pin(self) -> str:
        return self._pin

        self.setWindowTitle(_("PIN") if mode != "set" else _("Set PIN"))
        self.setFixedSize(380, 340)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer = QFrame()
        outer.setStyleSheet(f"background-color: {BG_PRIMARY}; border-radius: 16px; border: 1px solid {BORDER};")
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        icon = QLabel("\u26E8")
        icon.setStyleSheet(f"color: {ACCENT}; font-size: 32px; background: transparent;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        self._title = QLabel(
            _("Enter PIN") if mode != "set" else _("Create a PIN")
        )
        self._title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 700; background: transparent;")
        self._title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._title)

        self._sub = QLabel(
            _("PIN protects your wallet and transactions.") if mode == "set"
            else _("Enter your 4-6 digit PIN.")
        )
        self._sub.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        self._sub.setAlignment(Qt.AlignCenter)
        self._sub.setWordWrap(True)
        layout.addWidget(self._sub)

        self._input = QLineEdit()
        self._input.setEchoMode(QLineEdit.Password)
        self._input.setMaxLength(6)
        self._input.setAlignment(Qt.AlignCenter)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 12px; font-size: 24px; font-weight: 700;
                letter-spacing: 8px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        self._input.textChanged.connect(self._on_input)
        layout.addWidget(self._input)

        self._error = QLabel("")
        self._error.setStyleSheet(f"color: {ERROR}; font-size: 11px; background: transparent;")
        self._error.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._error)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if mode == "set" or mode == "unlock":
            self._skip_btn = QPushButton(_("Skip") if mode == "set" else _("Cancel"))
            self._skip_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent; color: {TEXT_MUTED}; font-weight: 500;
                    border-radius: 6px; padding: 8px 16px; font-size: 12px; border: none;
                }}
                QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
            """)
            self._skip_btn.clicked.connect(self.reject)
            btn_row.addWidget(self._skip_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(outer)

        self._input.setFocus()

    def _on_input(self, text: str):
        self._error.setText("")
        if len(text) < 4:
            return
        if self._mode == "unlock":
            if verify(text):
                self._pin = text
                self.accept()
            else:
                self._input.clear()
                self._error.setText(_("Incorrect PIN"))
        elif self._mode == "set":
            if len(text) >= 4:
                self._pin = text
                self._mode = "confirm"
                self._title.setText(_("Confirm PIN"))
                self._sub.setText(_("Re-enter your PIN to confirm."))
                self._input.clear()
        elif self._mode == "confirm":
            if text == self._pin:
                set_pin(text)
                self.accept()
            else:
                self._input.clear()
                self._error.setText(_("PINs don't match"))

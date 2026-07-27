from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit

from ui.theme import TEXT_PRIMARY, TEXT_SECONDARY, BG_CARD, BORDER, ACCENT, ERROR, SUCCESS, WARNING


class TransactionDetailDialog(QDialog):
    def __init__(self, tx: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transaction Details")
        self.setFixedSize(520, 460)
        self.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Transaction Details")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        fields = [
            ("Hash", self._hex(tx.get("tx_id", tx.get("hash", "")))),
            ("Status", tx.get("status", "unknown")),
            ("Amount", self._aeth(tx.get("amount", 0))),
            ("Fee", str(tx.get("fee", 0))),
            ("Timestamp", self._ts(tx.get("timestamp", 0))),
            ("Sender", self._hex(tx.get("sender", ""))),
            ("Receiver", self._hex(tx.get("receiver", ""))),
        ]

        parents = tx.get("parents", [])
        if isinstance(parents, list) and len(parents) > 0:
            p0 = self._hex(parents[0]) if len(parents) > 0 else "none"
            p1 = self._hex(parents[1]) if len(parents) > 1 else "none"
            fields.append(("Parent 1", p0))
            fields.append(("Parent 2", p1))

        for label, value in fields:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(label)
            lbl.setFixedWidth(90)
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
            row.addWidget(lbl)

            val = QTextEdit()
            val.setPlainText(value)
            val.setReadOnly(True)
            val.setMaximumHeight(32)
            val.setStyleSheet(f"""
                background-color: transparent; color: {TEXT_PRIMARY}; font-size: 11px;
                border: none; padding: 2px 0;
            """)
            row.addWidget(val, 1)
            layout.addLayout(row)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {ACCENT}; font-weight: 600;
                border-radius: 8px; padding: 10px; font-size: 13px;
                border: 1px solid {ACCENT}44;
            }}
            QPushButton:hover {{ background-color: {ACCENT}22; border-color: {ACCENT}; }}
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    @staticmethod
    def _hex(val) -> str:
        if isinstance(val, bytes):
            return val.hex()
        if isinstance(val, list):
            return bytes(val).hex()
        return str(val)

    @staticmethod
    def _aeth(val) -> str:
        if isinstance(val, (int, float)):
            return f"{val / 10_000_000_000:.6f} AETH"
        return str(val)

    @staticmethod
    def _ts(val) -> str:
        if isinstance(val, (int, float)) and val > 0:
            from datetime import datetime
            return datetime.fromtimestamp(val).strftime("%Y-%m-%d %H:%M:%S")
        return "-"

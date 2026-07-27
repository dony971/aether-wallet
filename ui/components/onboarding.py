from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QStackedWidget

from ui.theme import BG_PRIMARY, BG_CARD, BG_CARD_HOVER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT, BORDER, SUCCESS


ONBOARDING_FILE = Path.home() / "AppData" / "Roaming" / "Aether" / ".onboarding_done"


def is_first_run() -> bool:
    return not ONBOARDING_FILE.exists()


def mark_done():
    try:
        ONBOARDING_FILE.parent.mkdir(parents=True, exist_ok=True)
        ONBOARDING_FILE.write_text("done")
    except Exception:
        pass


class StepIndicator(QFrame):
    def __init__(self, total: int, current: int = 0):
        super().__init__()
        self._total = total
        self._current = current
        self.setFixedHeight(24)

    def set_current(self, i: int):
        self._current = i
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        spacing = w // self._total
        for i in range(self._total):
            cx = spacing // 2 + i * spacing
            r = 5 if i == self._current else 4
            color = QColor(ACCENT) if i <= self._current else QColor(BORDER)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(QRect(cx - r, h // 2 - r, r * 2, r * 2))
        painter.end()


class OnboardingWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to AETHER")
        self.setFixedSize(540, 480)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer = QFrame()
        outer.setStyleSheet(f"background-color: {BG_PRIMARY}; border-radius: 16px; border: 1px solid {BORDER};")
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self._stack, 1)

        self._steps = [
            self._make_page(
                "\u25C8",
                "Welcome to AETHER SEDC",
                "A next-generation DAG-based cryptocurrency wallet.\n\n"
                "Fast. Secure. Decentralized.\n\n"
                "This guide will help you get started in a few steps."
            ),
            self._make_page(
                "\u2699",
                "Step 1: Create a Wallet",
                "Your wallet is your identity on the AETHER network.\n\n"
                "Go to Receive to create a new wallet.\n"
                "Your address is a 64-character hex key.\n\n"
                "You can create multiple wallets and switch between them."
            ),
            self._make_page(
                "\u2197",
                "Step 2: Get AETH Tokens",
                "Use the Faucet in Receive to get free test tokens.\n\n"
                "Go to Send to transfer tokens to any address.\n"
                "You can send to multiple recipients at once."
            ),
            self._make_page(
                "\u2606",
                "Step 3: Stake & Mine",
                "Stake your tokens to earn 12.5% APY rewards.\n\n"
                "Enable mining in the Mining page to support the network\n"
                "and earn mining rewards."
            ),
            self._make_page(
                "\u2713",
                "You're All Set!",
                "Dashboard  \u2022  Send  \u2022  Receive\n"
                "Transactions  \u2022  Staking  \u2022  Mining  \u2022  Settings\n\n"
                "Use the sidebar to navigate.\n"
                "Help is always available at the bottom of the sidebar."
            ),
        ]

        for page in self._steps:
            self._stack.addWidget(page)

        self._indicator = StepIndicator(len(self._steps), 0)
        layout.addWidget(self._indicator)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self._back_btn = QPushButton("Back")
        self._back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {TEXT_SECONDARY}; font-weight: 600;
                border-radius: 8px; padding: 10px 20px; font-size: 13px;
                border: 1px solid {BORDER};
            }}
            QPushButton:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}
        """)
        self._back_btn.clicked.connect(self._prev_step)
        btn_row.addWidget(self._back_btn)

        btn_row.addStretch()

        self._next_btn = QPushButton("Next")
        self._next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #0A0A1A; font-weight: 700;
                border-radius: 8px; padding: 10px 24px; font-size: 13px; border: none;
            }}
            QPushButton:hover {{ background-color: #00EECC; }}
        """)
        self._next_btn.clicked.connect(self._next_step)
        btn_row.addWidget(self._next_btn)

        layout.addLayout(btn_row)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(outer)

        self._current_step = 0
        self._update_buttons()

    def _make_page(self, icon: str, title: str, body: str) -> QFrame:
        page = QFrame()
        page.setStyleSheet("background: transparent;")
        pl = QVBoxLayout(page)
        pl.setContentsMargins(0, 20, 0, 20)
        pl.setSpacing(16)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color: {ACCENT}; font-size: 42px; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        pl.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: 700; background: transparent;")
        title_lbl.setAlignment(Qt.AlignCenter)
        pl.addWidget(title_lbl)

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; background: transparent; line-height: 1.6;")
        body_lbl.setAlignment(Qt.AlignCenter)
        pl.addWidget(body_lbl)

        pl.addStretch()
        return page

    def _update_buttons(self):
        self._back_btn.setVisible(self._current_step > 0)
        is_last = self._current_step == len(self._steps) - 1
        self._next_btn.setText("Get Started" if is_last else "Next")
        self._indicator.set_current(self._current_step)

    def _next_step(self):
        if self._current_step == len(self._steps) - 1:
            mark_done()
            self.accept()
        else:
            self._current_step += 1
            self._stack.setCurrentIndex(self._current_step)
            self._update_buttons()

    def _prev_step(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._stack.setCurrentIndex(self._current_step)
            self._update_buttons()

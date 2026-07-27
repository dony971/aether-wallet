from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, Property
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtGui import QColor

from ui.theme import SUCCESS, ERROR, WARNING, ACCENT, TEXT_PRIMARY, TEXT_SECONDARY


class Toast(QFrame):
    def __init__(self, parent, message: str, type: str = "success", duration: int = 3000):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setMaximumWidth(420)

        bg = {"success": SUCCESS + "E6", "error": ERROR + "E6", "info": ACCENT + "E6", "warning": WARNING + "E6"}.get(type, ACCENT + "E6")
        icon_text = {"success": "\u2713", "error": "\u2717", "info": "\u24D8", "warning": "\u26A0"}.get(type, "\u24D8")

        self.setStyleSheet(f"""
            Toast {{
                background-color: {bg};
                border-radius: 10px;
                padding: 0;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        icon = QLabel(icon_text)
        icon.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; background: transparent;")
        layout.addWidget(icon)

        self._label = QLabel(message)
        self._label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: 600; background: transparent;")
        self._label.setWordWrap(False)
        layout.addWidget(self._label, 1)

        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity)

        QTimer.singleShot(duration, self._fade_out)

    def _fade_out(self):
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(300)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(self.deleteLater)
        anim.start()


class ToastManager(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background: transparent; border: none;")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(8)
        self._layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)

    def show_toast(self, message: str, type: str = "success", duration: int = 3000):
        toast = Toast(self, message, type, duration)
        self._layout.insertWidget(0, toast)
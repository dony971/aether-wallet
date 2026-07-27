from PySide6.QtCore import Qt, QTimer, Property, QEasingCurve, QPointF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

from ui.theme import BG_PRIMARY, ACCENT, TEXT_SECONDARY


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self._progress = 0.0
        self._angle = 0.0
        self._message = "Initializing..."
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(420, 520)

        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start(16)

        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._advance_progress)
        self._progress_timer.start(80)

    def set_message(self, msg: str):
        self._message = msg
        self.update()

    def _animate(self):
        self._angle += 2.0
        if self._angle >= 360:
            self._angle = 0
        self.update()

    def _advance_progress(self):
        if self._progress < 1.0:
            self._progress += 0.015
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        path = QPainterPath()
        path.addRoundedRect(10, 10, w - 20, h - 20, 24, 24)
        painter.fillPath(path, QColor("#1A1A2E"))

        painter.setPen(QPen(QColor("#2A2A3E"), 1))
        painter.drawPath(path)

        cx, cy = w // 2, 140

        grad = QLinearGradient(cx - 30, cy - 30, cx + 30, cy + 30)
        grad.setColorAt(0.0, QColor(ACCENT))
        grad.setColorAt(1.0, QColor("#0077FF"))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)

        painter.translate(cx, cy)
        painter.rotate(self._angle)
        num_spokes = 6
        for i in range(num_spokes):
            painter.rotate(360.0 / num_spokes)
            alpha = 100 + int(155 * (1.0 - i / num_spokes))
            c = QColor(ACCENT)
            c.setAlpha(alpha)
            painter.setBrush(QBrush(c))
            painter.drawRoundedRect(-3, -28, 6, 20, 3, 3)
        painter.resetTransform()

        painter.setPen(QColor(ACCENT))
        logo_font = QFont("Segoe UI", 32, QFont.Bold)
        painter.setFont(logo_font)
        painter.drawText(0, 200, w, 50, Qt.AlignCenter, "AETHER")

        painter.setPen(QColor(TEXT_SECONDARY))
        sub_font = QFont("Segoe UI", 12)
        painter.setFont(sub_font)
        painter.drawText(0, 235, w, 30, Qt.AlignCenter, "Self-Evolving DAG Consensus")

        painter.setPen(QColor("#FFFFFF"))
        msg_font = QFont("Segoe UI", 10)
        painter.setFont(msg_font)
        painter.drawText(0, 340, w, 30, Qt.AlignCenter, self._message)

        bar_x, bar_y, bar_w, bar_h = 60, 380, w - 120, 4
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#2A2A3E"))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 2, 2)

        if self._progress > 0:
            grad_bar = QLinearGradient(bar_x, 0, bar_x + int(bar_w * self._progress), 0)
            grad_bar.setColorAt(0.0, QColor(ACCENT))
            grad_bar.setColorAt(1.0, QColor("#0077FF"))
            painter.setBrush(QBrush(grad_bar))
            painter.drawRoundedRect(bar_x, bar_y, int(bar_w * self._progress), bar_h, 2, 2)

        painter.setPen(QColor(TEXT_SECONDARY))
        pct_font = QFont("Segoe UI", 9)
        painter.setFont(pct_font)
        painter.drawText(0, 395, w, 20, Qt.AlignCenter, f"{int(self._progress * 100)}%")

        painter.end()

    def closeEvent(self, event):
        self._anim_timer.stop()
        self._progress_timer.stop()
        super().closeEvent(event)

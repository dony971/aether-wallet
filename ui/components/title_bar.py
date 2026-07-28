from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QLinearGradient, QBrush, QMouseEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ui.theme import BG_SIDEBAR, ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, BORDER, ERROR
from utils.helpers import VERSION


class WindowButton(QPushButton):
    def __init__(self, label: str, color_hover: str, parent=None):
        super().__init__(parent)
        self._label = label
        self._color_hover = color_hover
        self._hovered = False
        self.setFixedSize(46, 32)
        self.setCursor(Qt.ArrowCursor)

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        if self._hovered:
            painter.fillRect(self.rect(), QColor(self._color_hover))

        painter.setPen(QPen(QColor(TEXT_PRIMARY), 1.5))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

        if self._label == "\u2014":
            # Minimize: small line
            painter.drawLine(14, h // 2 + 1, w - 14, h // 2 + 1)
        elif self._label == "\u25A1":
            # Maximize: small square
            margin = 11
            painter.drawRect(margin, margin + 1, w - 2 * margin, h - 2 * margin - 3)
        elif self._label == "\u2715":
            # Close: X
            margin = 13
            painter.drawLine(margin, margin + 1, w - margin, h - margin - 1)
            painter.drawLine(w - margin, margin + 1, margin, h - margin - 1)

        painter.end()


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self._pressed = False
        self._drag_pos = QPoint()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        icon = QLabel("\u25C8")
        icon.setStyleSheet(f"color: {ACCENT}; font-size: 14px; padding: 0 8px 0 14px; background: transparent;")
        layout.addWidget(icon)

        title = QLabel(f"AETHER SEDC v{VERSION}")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(title)

        layout.addStretch()

        self._min_btn = WindowButton("\u2014", "#FFFFFF22")
        self._min_btn.clicked.connect(lambda: self.window().showMinimized())
        layout.addWidget(self._min_btn)

        self._max_btn = WindowButton("\u25A1", "#FFFFFF22")
        self._max_btn.clicked.connect(self._toggle_maximize)
        layout.addWidget(self._max_btn)

        self._close_btn = WindowButton("\u2715", ERROR + "CC")
        self._close_btn.clicked.connect(lambda: self.window().close())
        layout.addWidget(self._close_btn)

        self.setMouseTracking(True)

    def _toggle_maximize(self):
        w = self.window()
        if w.isMaximized():
            w.showNormal()
        else:
            w.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._pressed:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._pressed = False
        event.accept()

    def mouseDoubleClickEvent(self, event):
        self._toggle_maximize()
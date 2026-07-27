from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QLinearGradient, QBrush
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel

from ui.theme import BG_CARD, BG_CARD_HOVER, BORDER, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT


class Card(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self._title = title
        self._hovered = False
        self.setFixedHeight(120)
        self.setCursor(Qt.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(20, 16, 20, 16)
        self.layout().setSpacing(6)

        if self._title:
            title_lbl = QLabel(self._title)
            title_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; background: transparent;")
            self.layout().addWidget(title_lbl)

        self._value_lbl = QLabel("--")
        self._value_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 26px; font-weight: 700; background: transparent;")
        self.layout().addWidget(self._value_lbl)

        self._subtitle_lbl = QLabel("")
        self._subtitle_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        self.layout().addWidget(self._subtitle_lbl)

    def set_value(self, value: str):
        self._value_lbl.setText(value)

    def set_subtitle(self, subtitle: str):
        self._subtitle_lbl.setText(subtitle)
        self._subtitle_lbl.setVisible(bool(subtitle))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        margin = 1
        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        path.addRoundedRect(rect, 12, 12)

        if self._hovered:
            grad = QLinearGradient(0, 0, 0, self.height())
            grad.setColorAt(0.0, QColor(BG_CARD_HOVER))
            grad.setColorAt(1.0, QColor(BG_CARD))
            painter.fillPath(path, QBrush(grad))
            painter.setPen(QPen(QColor(ACCENT + "77"), 1.5))
        else:
            painter.fillPath(path, QColor(BG_CARD))
            painter.setPen(QPen(QColor(BORDER), 1))

        painter.drawPath(path)
        painter.end()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)


class StatRow(QFrame):
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        self._val = QLabel(value)
        self._val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(lbl)
        layout.addStretch()
        layout.addWidget(self._val)

    def set_value(self, v: str):
        self._val.setText(v)

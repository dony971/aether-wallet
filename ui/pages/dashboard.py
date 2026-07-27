from PySide6.QtCore import Qt, QTimer, QRect, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QLinearGradient, QBrush
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QScrollArea

from ui.theme import BG_CARD, ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER, SUCCESS
from ui.components.card import Card, StatRow
from core.rpc_client import RpcClient


class NetworkChart(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(160)
        self.setFixedHeight(160)
        self._points = []
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(100)

    def add_point(self, value: float):
        self._points.append(value)
        if len(self._points) > 60:
            self._points.pop(0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        rect = self.rect().adjusted(1, 1, -1, -1)
        path.addRoundedRect(rect, 12, 12)
        painter.fillPath(path, QColor(BG_CARD))
        painter.setPen(QPen(QColor(BORDER), 1))
        painter.drawPath(path)

        if len(self._points) < 2:
            painter.setPen(QColor(TEXT_SECONDARY))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(rect, Qt.AlignCenter, "Waiting for data...")
            painter.end()
            return

        chart_rect = rect.adjusted(20, 20, -20, -30)
        cw, ch = chart_rect.width(), chart_rect.height()

        min_v = min(self._points)
        max_v = max(self._points)
        range_v = max_v - min_v if max_v != min_v else 1

        line_pen = QPen(QColor(ACCENT), 2, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(line_pen)

        step_x = cw / (len(self._points) - 1)
        poly = []
        for i, v in enumerate(self._points):
            x = chart_rect.left() + i * step_x
            y = chart_rect.bottom() - (v - min_v) / range_v * ch
            poly.append(QPointF(x, y))

        for i in range(len(poly) - 1):
            painter.drawLine(poly[i], poly[i + 1])

        fill_path = QPainterPath()
        fill_path.moveTo(poly[0])
        for p in poly[1:]:
            fill_path.lineTo(p)
        fill_path.lineTo(chart_rect.right(), chart_rect.bottom())
        fill_path.lineTo(chart_rect.left(), chart_rect.bottom())
        fill_path.closeSubpath()

        fill_grad = QLinearGradient(0, chart_rect.top(), 0, chart_rect.bottom())
        fill_grad.setColorAt(0.0, QColor(f"{ACCENT}30"))
        fill_grad.setColorAt(1.0, QColor("#0077FF10"))
        painter.fillPath(fill_path, QBrush(fill_grad))

        y_labels = 4
        for i in range(y_labels + 1):
            y = chart_rect.bottom() - ch * i / y_labels
            painter.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))
            painter.drawLine(chart_rect.left(), int(y), chart_rect.right(), int(y))
            val = min_v + range_v * i / y_labels
            painter.setPen(QColor(TEXT_MUTED))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(2, int(y - 8), 16, 16, Qt.AlignLeft, fmt_val(val))

        x_labels = 6
        for i in range(x_labels):
            x = chart_rect.left() + cw * i / x_labels
            painter.setPen(QColor(TEXT_MUTED))
            painter.setFont(QFont("Segoe UI", 9))
            secs = int((len(self._points) - 1) * i / x_labels)
            painter.drawText(int(x - 16), chart_rect.bottom() + 8, 32, 16, Qt.AlignCenter, f"-{secs}s")

        painter.end()


def fmt_val(v: float) -> str:
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.1f}K"
    return f"{v:.1f}"


class BalanceChart(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(130)
        self.setFixedHeight(130)
        self._points = []
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(100)

    def add_point(self, value: float):
        self._points.append(value)
        if len(self._points) > 120:
            self._points.pop(0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        rect = self.rect().adjusted(1, 1, -1, -1)
        path.addRoundedRect(rect, 12, 12)
        painter.fillPath(path, QColor(BG_CARD))
        painter.setPen(QPen(QColor(BORDER), 1))
        painter.drawPath(path)

        if len(self._points) < 2:
            painter.setPen(QColor(TEXT_SECONDARY))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(rect, Qt.AlignCenter, "Waiting for data...")
            painter.end()
            return

        chart_rect = rect.adjusted(20, 20, -20, -30)
        cw, ch = chart_rect.width(), chart_rect.height()

        min_v = min(self._points)
        max_v = max(self._points)
        range_v = max_v - min_v if max_v != min_v else 1

        line_pen = QPen(QColor(SUCCESS), 2, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(line_pen)

        step_x = cw / (len(self._points) - 1)
        poly = []
        for i, v in enumerate(self._points):
            x = chart_rect.left() + i * step_x
            y = chart_rect.bottom() - (v - min_v) / range_v * ch
            poly.append(QPointF(x, y))

        for i in range(len(poly) - 1):
            painter.drawLine(poly[i], poly[i + 1])

        fill_path = QPainterPath()
        fill_path.moveTo(poly[0])
        for p in poly[1:]:
            fill_path.lineTo(p)
        fill_path.lineTo(chart_rect.right(), chart_rect.bottom())
        fill_path.lineTo(chart_rect.left(), chart_rect.bottom())
        fill_path.closeSubpath()

        fill_grad = QLinearGradient(0, chart_rect.top(), 0, chart_rect.bottom())
        fill_grad.setColorAt(0.0, QColor(f"{SUCCESS}30"))
        fill_grad.setColorAt(1.0, QColor(f"{SUCCESS}05"))
        painter.fillPath(fill_path, QBrush(fill_grad))

        y_labels = 4
        for i in range(y_labels + 1):
            y = chart_rect.bottom() - ch * i / y_labels
            painter.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))
            painter.drawLine(chart_rect.left(), int(y), chart_rect.right(), int(y))
            val = min_v + range_v * i / y_labels
            painter.setPen(QColor(TEXT_MUTED))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(2, int(y - 8), 60, 16, Qt.AlignLeft, f"{val:.4f}")

        x_labels = 6
        for i in range(x_labels):
            x = chart_rect.left() + cw * i / x_labels
            painter.setPen(QColor(TEXT_MUTED))
            painter.setFont(QFont("Segoe UI", 9))
            secs = int((len(self._points) - 1) * i / x_labels * 3)
            if secs < 60:
                painter.drawText(int(x - 16), chart_rect.bottom() + 8, 32, 16, Qt.AlignCenter, f"-{secs}s")
            else:
                painter.drawText(int(x - 16), chart_rect.bottom() + 8, 32, 16, Qt.AlignCenter, f"-{secs//60}m")

        painter.end()


class DashboardPage(QWidget):
    def __init__(self, rpc: RpcClient, wallet_mgr=None, parent=None):
        super().__init__(parent)
        self._rpc = rpc
        self._wallet_mgr = wallet_mgr
        self._history = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(12)

        title = QLabel("Dashboard")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        self._balance_banner = QFrame()
        self._balance_banner.setFixedHeight(80)
        self._balance_banner.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {ACCENT}33;")
        banner_layout = QHBoxLayout(self._balance_banner)
        banner_layout.setContentsMargins(24, 0, 24, 0)

        self._banner_icon = QLabel("\u25C8")
        self._banner_icon.setStyleSheet(f"font-size: 28px; color: {ACCENT}; background: transparent;")
        banner_layout.addWidget(self._banner_icon)

        banner_layout.addSpacing(12)

        banner_text = QVBoxLayout()
        self._banner_title = QLabel("Wallet Balance")
        self._banner_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; background: transparent;")
        banner_text.addWidget(self._banner_title)

        self._banner_value = QLabel("-- AETH")
        self._banner_value.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 28px; font-weight: 800; background: transparent;")
        banner_text.addWidget(self._banner_value)

        banner_layout.addLayout(banner_text)
        banner_layout.addStretch()

        self._banner_sub = QLabel("")
        self._banner_sub.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        banner_layout.addWidget(self._banner_sub)

        layout.addWidget(self._balance_banner)

        self._grid = QGridLayout()
        self._grid.setSpacing(12)

        self._peers_card = Card("Peers")
        self._tx_card = Card("Transactions")
        self._hashrate_card = Card("Hashrate")
        self._difficulty_card = Card("Difficulty")
        self._status_card = Card("Status")

        self._grid.addWidget(self._peers_card, 0, 0)
        self._grid.addWidget(self._tx_card, 0, 1)
        self._grid.addWidget(self._hashrate_card, 0, 2)
        self._grid.addWidget(self._difficulty_card, 1, 0)
        self._grid.addWidget(self._status_card, 1, 1)

        layout.addLayout(self._grid)

        chart_section = QLabel("Network Activity (TPS)")
        chart_section.setStyleSheet(f"font-size: 14px; color: {TEXT_SECONDARY}; background: transparent; margin-top: 8px;")
        layout.addWidget(chart_section)

        self._chart = NetworkChart()
        layout.addWidget(self._chart)

        balance_chart_label = QLabel("Balance History")
        balance_chart_label.setStyleSheet(f"font-size: 14px; color: {TEXT_SECONDARY}; background: transparent; margin-top: 8px;")
        layout.addWidget(balance_chart_label)

        self._balance_chart = BalanceChart()
        layout.addWidget(self._balance_chart)

        details_frame = QFrame()
        details_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(20, 16, 20, 16)
        details_layout.setSpacing(0)

        details_title = QLabel("Node Details")
        details_title.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {TEXT_PRIMARY}; background: transparent; margin-bottom: 8px;")
        details_layout.addWidget(details_title)

        self._detail_rows = {}
        for key in ["Node Type", "P2P Port", "RPC Port", "Bootnode", "DAG Tips", "Mempool", "Total Supply", "Block Reward"]:
            row = StatRow(key, "--")
            details_layout.addWidget(row)
            self._detail_rows[key] = row

        layout.addWidget(details_frame)
        layout.addStretch()

    def refresh(self):
        try:
            stats = self._rpc.get_dag_stats()
            mining = self._rpc.get_mining_status()
            hashrate_resp = self._rpc.get_network_hashrate()

            peers = int(stats.get("connected_peers", 0))
            tps = float(stats.get("current_tps", 0))
            tx_count = int(stats.get("total_transactions", 0))
            tips = int(stats.get("tip_count", 0))

            difficulty = str(hashrate_resp.get("difficulty", "?"))
            hashrate_str = str(hashrate_resp.get("hashrate", "?"))

            is_mining = mining.get("is_mining", False)

            if self._wallet_mgr and self._wallet_mgr.has_wallet:
                try:
                    bal = self._rpc.get_balance(self._wallet_mgr.address)
                    aeth = bal.get("balance", 0) / 10_000_000_000
                    rewards = bal.get("mining_rewards", 0) / 10_000_000_000
                    self._banner_value.setText(f"{aeth:.6f} AETH")
                    self._banner_sub.setText(f"Mining rewards: {rewards:.6f} AETH")
                except Exception:
                    self._banner_value.setText("-- AETH")
                    self._banner_sub.setText("Balance unavailable")
            else:
                self._banner_value.setText("No wallet")
                self._banner_sub.setText("Create one in Receive")

            self._peers_card.set_value(str(peers))
            self._tx_card.set_value(str(tx_count))
            self._hashrate_card.set_value(hashrate_str)
            self._difficulty_card.set_value(difficulty)
            self._status_card.set_value("Mining" if is_mining else "Active")
            self._status_card.set_subtitle(f"{tps:.1f} TPS")

            self._chart.add_point(tps)

            if self._wallet_mgr and self._wallet_mgr.has_wallet:
                try:
                    bal = self._rpc.get_balance(self._wallet_mgr.address)
                    aeth = bal.get("balance", 0) / 10_000_000_000
                    self._balance_chart.add_point(aeth)
                except Exception:
                    pass

            self._detail_rows["DAG Tips"].set_value(str(tips))

        except Exception:
            self._banner_value.setText("Disconnected")
            for card in [self._peers_card, self._tx_card,
                         self._hashrate_card, self._difficulty_card, self._status_card]:
                card.set_value("Disconnected")

from PySide6.QtCore import Qt, QTimer, QRect, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QLinearGradient, QBrush
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea

from ui.theme import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BG_CARD, BG_CARD_HOVER, BORDER, ACCENT, ERROR, SUCCESS, WARNING, BG_PRIMARY
from ui.components.card import Card
from core.rpc_client import RpcClient, RpcError
from utils.i18n import _


class MiningChart(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.setFixedHeight(140)
        self._points = []
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(100)

    def add_point(self, val: float):
        self._points.append(val)
        if len(self._points) > 120:
            self._points.pop(0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin = 8

        painter.fillRect(self.rect(), QColor(BG_CARD))

        if not self._points:
            painter.setPen(QColor(TEXT_MUTED))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(self.rect(), Qt.AlignCenter, _("Waiting for mining data..."))
            painter.end()
            return

        max_val = max(self._points) or 1
        steps = len(self._points)
        plot_w = w - 2 * margin
        plot_h = h - 2 * margin

        path = QPainterPath()
        path.moveTo(margin, h - margin)
        for i, val in enumerate(self._points):
            x = margin + (i / max(steps - 1, 1)) * plot_w
            y = h - margin - (val / max_val) * plot_h * 0.85
            if i == 0:
                path.lineTo(x, y)
            else:
                path.lineTo(x, y)

        grad = QLinearGradient(0, margin, 0, h - margin)
        grad.setColorAt(0.0, QColor(ACCENT + "88"))
        grad.setColorAt(1.0, QColor(ACCENT + "08"))
        pen = QPen(QColor(ACCENT), 2)
        painter.setPen(pen)
        painter.setBrush(QBrush(grad))
        path.lineTo(margin + plot_w, h - margin)
        path.lineTo(margin, h - margin)
        path.closeSubpath()
        painter.drawPath(path)

        painter.setPen(QColor(TEXT_MUTED))
        painter.setFont(QFont("Segoe UI", 8))
        if self._points:
            painter.drawText(QRect(margin, 2, 80, 14), Qt.AlignLeft, _("{:.1f} H/s").format(max_val))
        painter.end()


class MiningPage(QWidget):
    def __init__(self, rpc: RpcClient, parent=None):
        super().__init__(parent)
        self._rpc = rpc

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
        layout.setSpacing(16)

        title = QLabel(_("Mining & Network"))
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        status_banner = QFrame()
        status_banner.setFixedHeight(80)
        status_banner.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {ACCENT}33;")
        banner_layout = QHBoxLayout(status_banner)
        banner_layout.setContentsMargins(24, 0, 24, 0)

        self._status_icon = QLabel("\u25CF")
        self._status_icon.setStyleSheet(f"color: {WARNING}; font-size: 24px; background: transparent;")
        banner_layout.addWidget(self._status_icon)

        status_text_col = QVBoxLayout()
        status_text_col.setSpacing(2)
        self._mining_status = QLabel(_("Checking..."))
        self._mining_status.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: 700; background: transparent;")
        status_text_col.addWidget(self._mining_status)

        self._mining_sub = QLabel("")
        self._mining_sub.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        status_text_col.addWidget(self._mining_sub)
        banner_layout.addLayout(status_text_col, 1)

        self._toggle_mining_btn = QPushButton(_("Start Mining"))
        self._toggle_mining_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #0A0A1A; font-weight: 700;
                border-radius: 8px; padding: 10px 20px; font-size: 13px; border: none;
            }}
            QPushButton:hover {{ background-color: #00EECC; }}
            QPushButton:disabled {{ background-color: #2A2A3E; color: #666; }}
        """)
        self._toggle_mining_btn.clicked.connect(self._toggle_mining)
        banner_layout.addWidget(self._toggle_mining_btn)

        layout.addWidget(status_banner)

        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(12)
        self._hashrate_card = Card(_("Hashrate"))
        stats_grid.addWidget(self._hashrate_card)
        self._difficulty_card = Card(_("Difficulty"))
        stats_grid.addWidget(self._difficulty_card)
        self._mined_card = Card(_("Total Mined"))
        stats_grid.addWidget(self._mined_card)
        self._net_hashrate_card = Card(_("Network Hashrate"))
        stats_grid.addWidget(self._net_hashrate_card)
        layout.addLayout(stats_grid)

        chart_label = QLabel(_("Mining Hashrate"))
        chart_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(chart_label)

        self._chart = MiningChart()
        self._chart.setStyleSheet(f"border: 1px solid {BORDER}; border-radius: 10px;")
        layout.addWidget(self._chart)

        net_frame = QFrame()
        net_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        net_layout = QVBoxLayout(net_frame)
        net_layout.setContentsMargins(24, 16, 24, 16)
        net_layout.setSpacing(8)

        net_title = QLabel(_("Network"))
        net_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        net_layout.addWidget(net_title)

        self._net_rows = {}
        for label in [_("Connected Peers"), _("TPS"), _("DAG Tips"), _("Epoch"), _("Total Transactions")]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
            row.addWidget(lbl)
            row.addStretch()
            val = QLabel("--")
            val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: 600; background: transparent;")
            row.addWidget(val)
            self._net_rows[label] = val
            net_layout.addLayout(row)

        layout.addWidget(net_frame)
        layout.addStretch()

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh)
        self._refresh_timer.start(3000)
        QTimer.singleShot(500, self._refresh)

    def refresh(self):
        self._refresh()

    def _refresh(self):
        try:
            stats = self._rpc.get_dag_stats()
            mining = self._rpc.get_mining_status()
            hashrate_resp = self._rpc.get_network_hashrate()

            is_mining = mining.get("is_mining", False)
            raw_hash = str(hashrate_resp.get("hashrate", "0"))
            hashrate = float(raw_hash.split()[0]) if raw_hash.split() else 0
            difficulty = str(hashrate_resp.get("difficulty", "?"))
            raw_net = str(hashrate_resp.get("network_hashrate", raw_hash))
            net_hashrate = float(raw_net.split()[0]) if raw_net.split() else 0
            total_mined = float(mining.get("total_mined", mining.get("mined", 0)))

            peers = int(stats.get("connected_peers", 0))
            tps = float(stats.get("current_tps", 0))
            tips = int(stats.get("tip_count", 0))
            epoch = int(stats.get("epoch", 0))
            tx_count = int(stats.get("total_transactions", 0))

            self._mining_status.setText(_("Mining") if is_mining else _("Not Mining"))
            self._mining_sub.setText(_("Hashrate: {:.2f} H/s").format(hashrate) if is_mining else _("Click Start to begin mining"))
            self._status_icon.setStyleSheet(f"color: {SUCCESS if is_mining else WARNING}; font-size: 24px; background: transparent;")
            self._toggle_mining_btn.setText(_("Stop Mining") if is_mining else _("Start Mining"))
            self._toggle_mining_btn.setEnabled(True)

            self._hashrate_card.set_value(_("{:.2f} H/s").format(hashrate))
            self._difficulty_card.set_value(str(difficulty))
            self._mined_card.set_value(f"{total_mined:.4f}")
            self._net_hashrate_card.set_value(_("{:.2f} H/s").format(net_hashrate))

            if is_mining:
                self._chart.add_point(hashrate)

            self._net_rows["Connected Peers"].set_value(str(peers))
            self._net_rows["TPS"].set_value(f"{tps:.1f}")
            self._net_rows["DAG Tips"].set_value(str(tips))
            self._net_rows["Epoch"].set_value(str(epoch))
            self._net_rows["Total Transactions"].set_value(str(tx_count))

        except RpcError:
            self._mining_status.setText(_("Node disconnected"))
            self._toggle_mining_btn.setEnabled(False)
            for card in [self._hashrate_card, self._difficulty_card, self._mined_card, self._net_hashrate_card]:
                card.set_value("--")
        except Exception:
            pass

    def _toggle_mining(self):
        self._toggle_mining_btn.setEnabled(False)
        try:
            mining = self._rpc.get_mining_status()
            if mining.get("is_mining"):
                self._rpc.stop_mining()
            else:
                self._rpc.start_mining()
            QTimer.singleShot(1000, self._refresh)
        except RpcError as e:
            self._mining_sub.setText(_("Error: {}").format(e))
        finally:
            self._toggle_mining_btn.setEnabled(True)
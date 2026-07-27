from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFileDialog, QMessageBox

from ui.theme import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BG_CARD, BORDER, ACCENT, SUCCESS, WARNING
from core.rpc_client import RpcClient, RpcError
from ui.pages.tx_detail import TransactionDetailDialog


def _hex(val) -> str:
    if isinstance(val, bytes):
        return val.hex()
    if isinstance(val, list):
        return bytes(val).hex()
    return str(val)


def _short(s: str, n=12) -> str:
    return s[:n] + "..." if len(s) > n else s


class TransactionsPage(QWidget):
    def __init__(self, rpc: RpcClient, parent=None):
        super().__init__(parent)
        self._rpc = rpc

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Transactions")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        header.addWidget(title)

        header.addStretch()

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {ACCENT}; font-weight: 600;
                border-radius: 6px; padding: 6px 16px; font-size: 12px;
                border: 1px solid {ACCENT}44;
            }}
            QPushButton:hover {{ background-color: {ACCENT}22; border-color: {ACCENT}; }}
        """)
        self._refresh_btn.clicked.connect(self.refresh)
        header.addWidget(self._refresh_btn)

        self._export_btn = QPushButton("Export CSV")
        self._export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {SUCCESS}; font-weight: 600;
                border-radius: 6px; padding: 6px 16px; font-size: 12px;
                border: 1px solid {SUCCESS}44;
            }}
            QPushButton:hover {{ background-color: {SUCCESS}22; border-color: {SUCCESS}; }}
        """)
        self._export_btn.clicked.connect(self._on_export_csv)
        header.addWidget(self._export_btn)

        layout.addLayout(header)

        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search by address, hash, or status...")
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 8px 14px; font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        self._search_input.textChanged.connect(self._filter_table)
        search_row.addWidget(self._search_input, 1)

        self._count_label = QLabel("0 tx")
        self._count_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        search_row.addWidget(self._count_label)

        layout.addLayout(search_row)

        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(["Hash", "From", "To", "Amount", "Fee", "Time", "Status"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)

        self._table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 4px;
                color: {TEXT_PRIMARY};
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {ACCENT}33;
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                padding: 10px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)

        self._table.cellClicked.connect(self._on_tx_click)
        self._tx_data_raw = []

        layout.addWidget(self._table)

        self.refresh()

    def refresh(self):
        self._refresh_btn.setEnabled(False)
        QTimer.singleShot(100, self._do_refresh)

    def _do_refresh(self):
        try:
            resp = self._rpc.get_recent_transactions(50)
            txs = resp.get("transactions", [])
            if not isinstance(txs, list):
                txs = []

            self._tx_data_raw = txs
            self._filter_table()
            if not txs:
                self._table.setRowCount(1)
                self._table.setItem(0, 0, QTableWidgetItem(""))
                self._table.setSpan(0, 0, 1, 7)
                empty = QLabel("\u25CB  No transactions yet\n\nSend or receive AETH to see your history here.")
                empty.setAlignment(Qt.AlignCenter)
                empty.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px; background: transparent; padding: 40px;")
                self._table.setCellWidget(0, 0, empty)
        except RpcError:
            self._tx_data_raw = []
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem(""))
            self._table.setSpan(0, 0, 1, 7)
            empty = QLabel("\u26A0  Node not connected\n\nStart the node to view transactions.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color: {WARNING}; font-size: 13px; background: transparent; padding: 40px;")
            self._table.setCellWidget(0, 0, empty)
        finally:
            self._refresh_btn.setEnabled(True)

    def _populate_table(self, txs: list):
        self._table.setRowCount(len(txs))
        for row, tx in enumerate(txs):
            tx_id = tx.get("tx_id", tx.get("hash", ""))
            tx_hash = _short(_hex(tx_id))

            sender = _short(_hex(tx.get("sender", "")))
            receiver = _short(_hex(tx.get("receiver", "")))

            raw_amount = tx.get("amount", 0)
            if isinstance(raw_amount, (int, float)):
                amount_str = f"{raw_amount / 10_000_000_000:.4f}"
            else:
                amount_str = str(raw_amount)

            raw_fee = tx.get("fee", 0)
            if isinstance(raw_fee, (int, float)):
                fee_str = f"{raw_fee}"
            else:
                fee_str = str(raw_fee)

            ts = tx.get("timestamp", 0)
            if isinstance(ts, (int, float)) and ts > 0:
                time_str = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            else:
                time_str = "-"

            status = tx.get("status", "unknown")

            self._table.setItem(row, 0, QTableWidgetItem(tx_hash))
            self._table.setItem(row, 1, QTableWidgetItem(sender))
            self._table.setItem(row, 2, QTableWidgetItem(receiver))
            self._table.setItem(row, 3, QTableWidgetItem(amount_str))
            self._table.setItem(row, 4, QTableWidgetItem(fee_str))
            self._table.setItem(row, 5, QTableWidgetItem(time_str))
            self._table.setItem(row, 6, QTableWidgetItem(status))

    def _filter_table(self):
        query = self._search_input.text().strip().lower()
        if not query:
            txs = self._tx_data_raw
        else:
            txs = [
                tx for tx in self._tx_data_raw
                if query in _hex(tx.get("tx_id", tx.get("hash", ""))).lower()
                or query in _hex(tx.get("sender", "")).lower()
                or query in _hex(tx.get("receiver", "")).lower()
                or query in tx.get("status", "").lower()
            ]
        self._populate_table(txs)
        self._count_label.setText(f"{len(txs)} tx")

    def _sanitize_csv(self, val: str) -> str:
        if val and val[0] in ("=", "+", "-", "@", "|", "%"):
            return "'" + val
        return val

    def _on_export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Transactions", "transactions.csv", "CSV Files (*.csv)")
        if not path:
            return
        import csv
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Hash", "Sender", "Receiver", "Amount", "Fee", "Timestamp", "Status"])
                for tx in self._tx_data_raw:
                    tx_id = self._sanitize_csv(_hex(tx.get("tx_id", tx.get("hash", ""))))
                    sender = self._sanitize_csv(_hex(tx.get("sender", "")))
                    receiver = self._sanitize_csv(_hex(tx.get("receiver", "")))
                    raw_amount = tx.get("amount", 0)
                    amount = f"{raw_amount / 10_000_000_000:.4f}" if isinstance(raw_amount, (int, float)) else str(raw_amount)
                    fee = tx.get("fee", 0)
                    ts = tx.get("timestamp", 0)
                    if isinstance(ts, (int, float)) and ts > 0:
                        ts = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                    status = self._sanitize_csv(tx.get("status", "unknown"))
                    writer.writerow([tx_id, sender, receiver, amount, fee, ts, status])
            QMessageBox.information(self, "Export", f"{len(self._tx_data_raw)} transactions exported to\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", str(e))

    def _on_tx_click(self, row: int, col: int):
        query = self._search_input.text().strip().lower()
        if not query:
            source = self._tx_data_raw
        else:
            source = [tx for tx in self._tx_data_raw
                      if query in _hex(tx.get("tx_id", tx.get("hash", ""))).lower()
                      or query in _hex(tx.get("sender", "")).lower()
                      or query in _hex(tx.get("receiver", "")).lower()
                      or query in tx.get("status", "").lower()]
        if row < len(source):
            dlg = TransactionDetailDialog(source[row], self)
            dlg.exec()

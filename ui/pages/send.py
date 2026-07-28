from PySide6.QtCore import Qt, QProcess, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, QComboBox, QScrollArea

from ui.theme import TEXT_PRIMARY, TEXT_SECONDARY, BG_CARD, BORDER, ACCENT, ERROR, SUCCESS, BG_PRIMARY
from core.rpc_client import RpcClient
from wallet.wallet_manager import WalletManager
from utils.pin_manager import is_set as pin_is_set
from utils.i18n import _


FEE_PRESETS = {_("Low"): "5", _("Medium"): "10", _("High"): "25"}


class RecipientRow(QFrame):
    def __init__(self, index: int, on_remove):
        super().__init__()
        self._index = index
        self._on_remove = on_remove

        self.setStyleSheet(f"background-color: {BG_PRIMARY}; border-radius: 8px; border: 1px solid {BORDER};")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        self.address = QLineEdit()
        self.address.setPlaceholderText(_("64 hex address"))
        self.address.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 6px;
                padding: 6px 10px; font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        layout.addWidget(self.address, 3)

        self.amount = QLineEdit()
        self.amount.setPlaceholderText(_("Amount (atomic)"))
        self.amount.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 6px;
                padding: 6px 10px; font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        layout.addWidget(self.amount, 1)

        remove_btn = QPushButton(_("X"))
        remove_btn.setFixedSize(28, 28)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {ERROR};
                border: 1px solid {ERROR}44; border-radius: 6px;
                font-size: 12px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {ERROR}22; }}
        """)
        remove_btn.clicked.connect(lambda: self._on_remove(self))
        layout.addWidget(remove_btn)

    def set_index(self, i: int):
        self._index = i


class SendPage(QWidget):
    def __init__(self, rpc: RpcClient, wallet_mgr: WalletManager, toast=None, parent=None):
        super().__init__(parent)
        self._rpc = rpc
        self._wallet_mgr = wallet_mgr
        self._toast = toast
        self._recipients: list[RecipientRow] = []
        self._send_queue: list[dict] = []
        self._queue_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        title = QLabel(_("Send AETHER"))
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        layout.addWidget(scroll, 1)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self._form_layout = QVBoxLayout(scroll_content)
        self._form_layout.setContentsMargins(0, 0, 0, 0)
        self._form_layout.setSpacing(12)
        scroll.setWidget(scroll_content)

        self._add_recipient_row()

        add_btn = QPushButton(_("+ Add Recipient"))
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {ACCENT}; font-weight: 600;
                border-radius: 6px; padding: 8px 16px; font-size: 12px;
                border: 1px dashed {ACCENT}66;
            }}
            QPushButton:hover {{ background-color: {ACCENT}11; border-color: {ACCENT}; }}
        """)
        add_btn.clicked.connect(self._add_recipient_row)
        self._form_layout.addWidget(add_btn)

        fee_row = QHBoxLayout()
        fee_row.setSpacing(12)
        self._form_layout.addLayout(fee_row)

        fee_row.addWidget(self._make_label(_("Fee:")))
        self._fee_combo = QComboBox()
        self._fee_combo.addItems(list(FEE_PRESETS.keys()))
        self._fee_combo.setCurrentText(_("Medium"))
        self._fee_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_CARD}; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 6px;
                padding: 6px 10px; font-size: 12px; min-width: 100px;
            }}
            QComboBox:hover {{ border-color: {ACCENT}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
        """)
        fee_row.addWidget(self._fee_combo)
        fee_row.addStretch()

        self._send_btn = QPushButton(_("Send All Transactions"))
        self._send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #0A0A1A; font-weight: 700;
                border-radius: 8px; padding: 14px; font-size: 14px; border: none;
            }}
            QPushButton:hover {{ background-color: #00EECC; }}
            QPushButton:disabled {{ background-color: #2A2A3E; color: #666; }}
        """)
        self._send_btn.clicked.connect(self._on_send)
        self._form_layout.addWidget(self._send_btn)

        self._result = QLabel("")
        self._result.setWordWrap(True)
        self._result.setStyleSheet("background: transparent; font-size: 12px; padding: 8px;")
        self._form_layout.addWidget(self._result)

        layout.addStretch()

    def _make_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        return lbl

    def _add_recipient_row(self):
        idx = len(self._recipients)
        row = RecipientRow(idx, self._remove_recipient_row)
        self._recipients.append(row)
        self._form_layout.insertWidget(len(self._recipients) - 1, row)

    def _remove_recipient_row(self, row: RecipientRow):
        if len(self._recipients) <= 1:
            return
        self._recipients.remove(row)
        self._form_layout.removeWidget(row)
        row.deleteLater()
        for i, r in enumerate(self._recipients):
            r.set_index(i)

    def _validate(self) -> list[dict] | None:
        txs = []
        for row in self._recipients:
            addr = row.address.text().strip()
            amt = row.amount.text().strip()
            if not addr or not amt:
                return None
            if len(addr) != 64 or not all(c in "0123456789abcdefABCDEF" for c in addr):
                return None
            try:
                int(amt)
            except ValueError:
                return None
            txs.append({"receiver": addr, "amount": amt})
        return txs

    def _on_send(self):
        if not self._wallet_mgr.has_wallet:
            if self._toast:
                self._toast.show_toast(_("No wallet found. Create one in Receive."), "error")
            else:
                QMessageBox.warning(self, _("No Wallet"), _("Create one in the Receive page first."))
            return

        if pin_is_set():
            from ui.components.pin_dialog import PinDialog
            if PinDialog("unlock", self).exec() != PinDialog.Accepted:
                return

        txs = self._validate()
        if txs is None:
            if self._toast:
                self._toast.show_toast(_("Check fields: 64-char hex address + numeric amount required."), "error")
            else:
                self._result.setStyleSheet(f"color: {ERROR}; background: transparent; padding: 8px;")
                self._result.setText(_("Check fields: 64-char hex address + numeric amount required."))
            return

        fee = FEE_PRESETS[self._fee_combo.currentText()]
        total_amount = sum(int(t["amount"]) for t in txs)
        total_fee = int(fee) * len(txs)

        msg = _("Send {} transaction(s)?\n\nTotal amount: {:.4f} AETH\nFee per tx: {}\nTotal fee: {}\nTotal cost: {:.4f} AETH").format(
            len(txs), total_amount / 10_000_000_000, fee, total_fee, (total_amount + total_fee) / 10_000_000_000
        )
        if not QMessageBox.question(self, _("Confirm"), msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            return

        self._send_queue = [{"receiver": t["receiver"], "amount": t["amount"], "fee": fee} for t in txs]
        self._queue_index = 0
        self._send_btn.setEnabled(False)
        self._send_next()

    def _send_next(self):
        if self._queue_index >= len(self._send_queue):
            if self._toast:
                self._toast.show_toast(_("All {} transaction(s) sent!").format(len(self._send_queue)), "success")
            self._send_btn.setEnabled(True)
            return

        tx = self._send_queue[self._queue_index]

        from core.config import config
        import tempfile, os, json
        binary = str(config.node_binary)
        rpc_url = f"http://127.0.0.1:{config.rpc_port}"

        tmp = tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".json")
        try:
            raw = self._wallet_mgr.wallet_file.read_bytes()
            env = json.loads(raw) if raw.startswith(b"{") else {"error": "encrypted"}
            if isinstance(env, dict) and "v" in env:
                from utils.pin_manager import verify as pin_verify
                from utils.encrypt import decrypt_wallet
                pin_candidate = getattr(self, "_last_pin", None)
                if pin_candidate and pin_verify(pin_candidate):
                    decrypted = decrypt_wallet(raw, pin_candidate)
                    tmp.write(json.dumps(decrypted, indent=2).encode())
                else:
                    self._toast.show_toast(_("Cannot send: wallet is PIN-encrypted"), "error")
                    self._send_btn.setEnabled(True)
                    return
            else:
                tmp.write(raw)
            tmp.close()

            proc = QProcess(self)
            proc.finished.connect(lambda code, p=proc, tx_data=tx, t=tmp: self._on_tx_result(p, code, tx_data, t))
            proc.start(binary, ["send", tx["receiver"], tx["amount"], tx["fee"],
                                "--wallet", tmp.name,
                                "--rpc-url", rpc_url])
        except Exception:
            self._toast.show_toast(_("Failed to prepare transaction"), "error")
            self._send_btn.setEnabled(True)

    def _on_tx_result(self, proc: QProcess, code: int, tx: dict, tmp_file=None):
        out = proc.readAllStandardOutput().data().decode().strip()
        err = proc.readAllStandardError().data().decode().strip()
        short_addr = tx["receiver"][:12]
        if code == 0:
            if self._toast:
                self._toast.show_toast(_("Tx to {}... sent ✓").format(short_addr), "success")
        else:
            if self._toast:
                self._toast.show_toast(_("Tx {} failed: {}").format(self._queue_index + 1, err[:80]), "error")
        if tmp_file:
            try:
                import os
                os.unlink(tmp_file.name)
            except Exception:
                pass
        self._queue_index += 1
        QTimer.singleShot(200, self._send_next)
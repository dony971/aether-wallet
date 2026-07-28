from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit, QApplication
from PySide6.QtGui import QPixmap

from ui.theme import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BG_CARD, BORDER, ERROR, SUCCESS, WARNING, ACCENT
from core.rpc_client import RpcClient, RpcError
from wallet.wallet_manager import WalletManager


class ReceivePage(QWidget):
    def __init__(self, rpc: RpcClient, wallet_mgr: WalletManager, parent=None):
        super().__init__(parent)
        self._rpc = rpc
        self._wallet_mgr = wallet_mgr

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        title = QLabel("Receive")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        self._card = QFrame()
        self._card.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        self._card_layout = QVBoxLayout(self._card)
        self._card_layout.setContentsMargins(24, 20, 24, 20)
        self._card_layout.setSpacing(14)

        self._rebuild()

        layout.addWidget(self._card)
        layout.addStretch()

    def _rebuild(self):
        while self._card_layout.count():
            item = self._card_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self._wallet_mgr.has_wallet:
            self._build_no_wallet()
        else:
            self._build_wallet_info()

    def _build_no_wallet(self):
        self._create_btn = QPushButton("Create Wallet")
        self._create_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #0A0A1A; font-weight: 700;
                border-radius: 8px; padding: 14px; font-size: 14px; border: none;
            }}
            QPushButton:hover {{ background-color: #00EECC; }}
        """)
        self._create_btn.clicked.connect(self._on_create_wallet)
        self._card_layout.addWidget(self._create_btn)

        self._status = QLabel("No wallet yet. Click above to create one.")
        self._status.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; font-size: 12px;")
        self._status.setWordWrap(True)
        self._card_layout.addWidget(self._status)

        self._result = QLabel("")
        self._result.setWordWrap(True)
        self._result.setStyleSheet("background: transparent; font-size: 12px; padding: 8px;")
        self._card_layout.addWidget(self._result)

    def _build_wallet_info(self):
        addr_row = QHBoxLayout()
        addr_input = QTextEdit()
        addr_input.setPlainText(self._wallet_mgr.address)
        addr_input.setReadOnly(True)
        addr_input.setMaximumHeight(60)
        addr_row.addWidget(addr_input, 1)

        copy_btn = QPushButton("Copy")
        copy_btn.setFixedWidth(70)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {ACCENT}; font-weight: 600;
                border-radius: 8px; font-size: 12px;
                border: 1px solid {ACCENT}44;
            }}
            QPushButton:hover {{ background-color: {ACCENT}22; border-color: {ACCENT}; }}
        """)
        copy_btn.clicked.connect(self._on_copy)
        addr_row.addWidget(copy_btn)

        self._card_layout.addWidget(self._make_label("Your Address"))
        self._card_layout.addLayout(addr_row)

        self._qr_label = QLabel()
        self._qr_label.setAlignment(Qt.AlignCenter)
        self._qr_label.setFixedHeight(140)
        self._generate_qr()
        self._card_layout.addWidget(self._qr_label)

        self._balance_btn = QPushButton("Check Balance")
        self._balance_btn.setStyleSheet(self._btn_style())
        self._balance_btn.clicked.connect(self._on_balance)
        self._card_layout.addWidget(self._balance_btn)

        self._faucet_btn = QPushButton("Request Faucet (10 AETH)")
        self._faucet_btn.setStyleSheet(self._btn_style())
        self._faucet_btn.clicked.connect(self._on_faucet)
        self._card_layout.addWidget(self._faucet_btn)

        self._result = QLabel("")
        self._result.setWordWrap(True)
        self._result.setStyleSheet("background: transparent; font-size: 12px; padding: 8px;")
        self._card_layout.addWidget(self._result)

    def _generate_qr(self):
        try:
            import qrcode
            from io import BytesIO
            qr = qrcode.QRCode(box_size=4, border=2)
            qr.add_data(self._wallet_mgr.address)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#00B4FF", back_color="#1A1A2E")
            buf = BytesIO()
            img.save(buf, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())
            self._qr_label.setPixmap(pixmap.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except ImportError:
            self._qr_label.setText("Install 'qrcode' for QR")
            self._qr_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent;")

    def _btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: transparent; color: {ACCENT}; font-weight: 600;
                border-radius: 8px; padding: 10px; font-size: 13px;
                border: 1px solid {ACCENT}44;
            }}
            QPushButton:hover {{ background-color: {ACCENT}22; border: 1px solid {ACCENT}; }}
        """

    def _make_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        return lbl

    def refresh(self):
        self._rebuild()

    def _on_create_wallet(self):
        self._result.setText("Creating wallet...")
        self._result.setStyleSheet("background: transparent; font-size: 12px; padding: 8px;")
        msg = self._wallet_mgr.create_wallet()
        if "successfully" in msg:
            self._result.setStyleSheet(f"color: {SUCCESS}; background: transparent; padding: 8px;")
            self._result.setText(msg)
            self._rebuild()
        else:
            self._result.setStyleSheet(f"color: {ERROR}; background: transparent; padding: 8px;")
            self._result.setText(msg)

    def _on_copy(self):
        QApplication.clipboard().setText(self._wallet_mgr.address)
        self._result.setStyleSheet(f"color: {SUCCESS}; background: transparent; padding: 8px;")
        self._result.setText("Address copied to clipboard!")
        QTimer.singleShot(2000, lambda: self._result.setText(""))

    def _on_balance(self):
        addr = self._wallet_mgr.address
        self._result.setText("Checking balance...")
        try:
            resp = self._rpc.get_balance(addr)
            bal = resp.get("balance", 0)
            rewards = resp.get("mining_rewards", 0)
            aeth = bal / 10_000_000_000
            reward_aeth = rewards / 10_000_000_000
            self._result.setStyleSheet(f"color: {SUCCESS}; background: transparent; padding: 8px;")
            self._result.setText(f"Balance: {aeth:.4f} AETH  |  Mining rewards: {reward_aeth:.4f} AETH")
        except RpcError as e:
            self._result.setStyleSheet(f"color: {ERROR}; background: transparent; padding: 8px;")
            self._result.setText(f"Balance error: {e}")

    def _on_faucet(self):
        addr = self._wallet_mgr.address
        self._result.setText("Requesting faucet...")
        QTimer.singleShot(50, lambda: self._do_faucet(addr))

    def _do_faucet(self, addr: str):
        try:
            resp = self._rpc.faucet(addr)
            self._result.setStyleSheet(f"color: {SUCCESS}; background: transparent; padding: 8px;")
            self._result.setText(f"Faucet: {resp.get('message', 'OK')}")
        except RpcError as e:
            self._result.setStyleSheet(f"color: {ERROR}; background: transparent; padding: 8px;")
            self._result.setText(f"Faucet error: {e}")

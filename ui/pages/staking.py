from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit, QScrollArea

from ui.theme import TEXT_PRIMARY, TEXT_SECONDARY, BG_CARD, BORDER, ACCENT, ERROR, SUCCESS, TEXT_MUTED
from ui.components.card import Card, StatRow
from core.rpc_client import RpcClient, RpcError
from wallet.wallet_manager import WalletManager


class StakingPage(QWidget):
    def __init__(self, rpc: RpcClient, wallet_mgr: WalletManager, parent=None):
        super().__init__(parent)
        self._rpc = rpc
        self._wallet_mgr = wallet_mgr

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

        title = QLabel("Staking")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        self._stats_card = Card()
        self._stats_layout = QVBoxLayout(self._stats_card)
        self._stats_layout.setContentsMargins(24, 20, 24, 20)
        self._stats_layout.setSpacing(12)

        self._stake_label = QLabel("Your Stake: —")
        self._stake_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 700; background: transparent;")
        self._stats_layout.addWidget(self._stake_label)

        self._rewards_label = QLabel("Rewards Earned: —")
        self._rewards_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        self._stats_layout.addWidget(self._rewards_label)

        self._apy_label = QLabel("APY: 12.5%")
        self._apy_label.setStyleSheet(f"color: {SUCCESS}; font-size: 13px; font-weight: 600; background: transparent;")
        self._stats_layout.addWidget(self._apy_label)

        self._total_staked_label = QLabel("Total Staked: —")
        self._total_staked_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; background: transparent;")
        self._stats_layout.addWidget(self._total_staked_label)

        layout.addWidget(self._stats_card)

        action_card = QFrame()
        action_card.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(24, 20, 24, 20)
        action_layout.setSpacing(12)

        action_layout.addWidget(self._make_label("Stake Amount (atomic units)"))
        self._stake_input = QLineEdit()
        self._stake_input.setPlaceholderText("e.g. 100000000000 = 10 AETH")
        self._stake_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 10px 14px; font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        action_layout.addWidget(self._stake_input)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self._stake_btn = QPushButton("Stake")
        self._stake_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS}; color: #0A0A1A; font-weight: 700;
                border-radius: 8px; padding: 12px 24px; font-size: 13px; border: none;
            }}
            QPushButton:hover {{ background-color: #00EECC; }}
            QPushButton:disabled {{ background-color: #2A2A3E; color: #666; }}
        """)
        self._stake_btn.clicked.connect(self._on_stake)
        btn_row.addWidget(self._stake_btn)

        self._unstake_btn = QPushButton("Unstake All")
        self._unstake_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {ERROR};
                font-weight: 600; border-radius: 8px; padding: 12px 24px;
                font-size: 13px; border: 1px solid {ERROR}44;
            }}
            QPushButton:hover {{ background-color: {ERROR}22; }}
            QPushButton:disabled {{ background-color: transparent; color: #444; border-color: #333; }}
        """)
        self._unstake_btn.clicked.connect(self._on_unstake)
        btn_row.addWidget(self._unstake_btn)

        action_layout.addLayout(btn_row)

        self._result = QLabel("")
        self._result.setWordWrap(True)
        self._result.setStyleSheet("background: transparent; font-size: 12px; padding: 8px;")
        action_layout.addWidget(self._result)

        layout.addWidget(action_card)
        layout.addStretch()

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh)
        self._refresh_timer.start(5000)
        QTimer.singleShot(500, self._refresh)

    def _make_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        return lbl

    def _refresh(self):
        if not self._wallet_mgr.has_wallet:
            self._stake_label.setText("Your Stake: — (no wallet)")
            self._rewards_label.setText("Rewards Earned: —")
            self._total_staked_label.setText("Total Staked: —")
            return
        try:
            addr = self._wallet_mgr.wallet_data.get("address", "")
            info = self._rpc.get_staking_info(addr)
            staked = info.get("staked_amount", info.get("staked", 0))
            rewards = info.get("rewards", info.get("reward", 0))
            total_staked = info.get("total_staked", info.get("total_staked_amount", 0))

            if isinstance(staked, (int, float)):
                self._stake_label.setText(f"Your Stake: {staked / 10_000_000_000:.4f} AETH")
            else:
                self._stake_label.setText(f"Your Stake: {staked}")

            if isinstance(rewards, (int, float)):
                self._rewards_label.setText(f"Rewards Earned: {rewards / 10_000_000_000:.4f} AETH")
            else:
                self._rewards_label.setText(f"Rewards Earned: {rewards}")

            if isinstance(total_staked, (int, float)):
                self._total_staked_label.setText(f"Total Staked: {total_staked / 10_000_000_000:.4f} AETH")
            else:
                self._total_staked_label.setText(f"Total Staked: {total_staked}")

            has_stake = isinstance(staked, (int, float)) and staked > 0
            self._unstake_btn.setEnabled(has_stake)

        except RpcError:
            pass

    def _on_stake(self):
        if not self._wallet_mgr.has_wallet:
            self._result.setStyleSheet(f"color: {ERROR}; background: transparent; padding: 8px;")
            self._result.setText("No wallet found.")
            return

        amt = self._stake_input.text().strip()
        if not amt:
            self._result.setStyleSheet(f"color: {ERROR}; background: transparent; padding: 8px;")
            self._result.setText("Enter an amount to stake.")
            return
        try:
            int(amt)
        except ValueError:
            self._result.setStyleSheet(f"color: {ERROR}; background: transparent; padding: 8px;")
            self._result.setText("Amount must be a number.")
            return

        self._stake_btn.setEnabled(False)
        self._result.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 8px;")
        self._result.setText("Staking...")

        try:
            addr = self._wallet_mgr.wallet_data.get("address", "")
            resp = self._rpc.stake_tokens(addr, int(amt))
            self._result.setStyleSheet(f"color: {SUCCESS}; background: transparent; padding: 8px;")
            self._result.setText(f"Staked! {resp}")
            QTimer.singleShot(1000, self._refresh)
        except RpcError as e:
            self._result.setStyleSheet(f"color: {ERROR}; background: transparent; padding: 8px;")
            self._result.setText(f"Error: {e}")
        finally:
            self._stake_btn.setEnabled(True)

    def _on_unstake(self):
        if not self._wallet_mgr.has_wallet:
            return

        from PySide6.QtWidgets import QMessageBox
        if not QMessageBox.question(
            self, "Confirm Unstake",
            "Unstake all tokens?\n\nRewards will be credited to your wallet.",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            return

        self._unstake_btn.setEnabled(False)
        self._result.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 8px;")
        self._result.setText("Unstaking...")

        try:
            addr = self._wallet_mgr.wallet_data.get("address", "")
            resp = self._rpc.unstake_tokens(addr)
            self._result.setStyleSheet(f"color: {SUCCESS}; background: transparent; padding: 8px;")
            self._result.setText(f"Unstaked! {resp}")
            QTimer.singleShot(1000, self._refresh)
        except RpcError as e:
            self._result.setStyleSheet(f"color: {ERROR}; background: transparent; padding: 8px;")
            self._result.setText(f"Error: {e}")
        finally:
            self._unstake_btn.setEnabled(True)
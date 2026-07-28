import logging
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
from PySide6.QtGui import QIcon, QAction, QMouseEvent, QCursor, QShortcut, QKeySequence
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QFrame, QSystemTrayIcon, QMenu, QSizeGrip

from ui.theme import BG_PRIMARY, BG_SIDEBAR, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, WARNING, ERROR, BORDER, ACCENT
from ui.components.sidebar import Sidebar
from ui.components.title_bar import TitleBar
from ui.components.toast import ToastManager
from ui.pages.dashboard import DashboardPage
from ui.pages.send import SendPage
from ui.pages.receive import ReceivePage
from ui.pages.transactions import TransactionsPage
from ui.pages.settings import SettingsPage
from ui.pages.staking import StakingPage
from ui.pages.mining import MiningPage
from core.rpc_client import RpcClient
from core.node_manager import NodeManager
from wallet.wallet_manager import WalletManager
from utils.pin_manager import is_set as is_pin_set, verify as verify_pin
from utils.helpers import VERSION, check_for_update
from utils.i18n import _


class MainWindow(QMainWindow):
    def __init__(self, splash=None, wallet_mgr=None):
        super().__init__()
        self._splash = splash
        self._rpc = RpcClient()
        self._node = NodeManager(self)
        self._wallet_mgr = wallet_mgr if wallet_mgr is not None else WalletManager()

        self.setWindowTitle(_("AETHER SEDC v{}").format(VERSION))
        self.setMinimumSize(960, 640)
        self.resize(1200, 780)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        outer = QFrame()
        outer.setStyleSheet(f"background-color: {BG_PRIMARY}; border: 1px solid {BORDER}; border-radius: 10px;")
        self.setCentralWidget(outer)

        root_layout = QVBoxLayout(outer)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._title_bar = TitleBar()
        root_layout.addWidget(self._title_bar)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._sidebar = Sidebar(wallet_mgr=self._wallet_mgr)
        content_layout.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent; border: none;")
        content_layout.addWidget(self._stack)

        root_layout.addWidget(content, 1)

        self._toast = ToastManager(content)
        self._toast.setGeometry(0, 0, content.width(), content.height())

        self._dashboard = DashboardPage(self._rpc, self._wallet_mgr)
        self._send = SendPage(self._rpc, self._wallet_mgr, self._toast)
        self._receive = ReceivePage(self._rpc, self._wallet_mgr)
        self._transactions = TransactionsPage(self._rpc)
        self._settings = SettingsPage(self._rpc, self._wallet_mgr)
        self._staking = StakingPage(self._rpc, self._wallet_mgr)
        self._mining = MiningPage(self._rpc)

        self._stack.addWidget(self._dashboard)
        self._stack.addWidget(self._send)
        self._stack.addWidget(self._receive)
        self._stack.addWidget(self._transactions)
        self._stack.addWidget(self._staking)
        self._stack.addWidget(self._mining)
        self._stack.addWidget(self._settings)

        self._sidebar.page_changed.connect(self._on_page_change)
        self._stack.currentChanged.connect(self._on_stack_changed)
        self._setup_shortcuts()

        self._node.status_changed.connect(self._on_node_status)
        self._node.error_occurred.connect(self._on_node_error)
        self._node.started.connect(self._on_node_started)

        self._status_bar = QFrame()
        self._status_bar.setFixedHeight(28)
        self._status_bar.setStyleSheet(f"background-color: {BG_SIDEBAR}; border-top: 1px solid {BORDER};")
        status_layout = QHBoxLayout(self._status_bar)
        status_layout.setContentsMargins(16, 0, 16, 0)
        status_layout.setSpacing(16)

        self._status_indicator = QLabel("\u25CF")
        self._status_indicator.setStyleSheet(f"color: {WARNING}; font-size: 10px; background: transparent;")
        status_layout.addWidget(self._status_indicator)

        self._status_text = QLabel(_("Starting..."))
        self._status_text.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
        status_layout.addWidget(self._status_text)

        status_layout.addStretch()

        self._status_peers = QLabel("")
        self._status_peers.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
        status_layout.addWidget(self._status_peers)

        self._status_height = QLabel("")
        self._status_height.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
        status_layout.addWidget(self._status_height)

        root_layout.addWidget(self._status_bar)

        grip = QSizeGrip(self._status_bar)
        grip.setStyleSheet("background: transparent;")

        self._prev_tx_count = 0
        self._resize_margin = 6
        self._resize_drag = False
        self._start_auto_backup()
        self._resize_edge = 0
        self._resize_start_pos = QPoint()
        self._resize_start_geo = QRect()
        self._setup_tray()

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh)

        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_status_bar)
        self._status_timer.start(5000)

        QTimer.singleShot(100, self._startup)

    def _setup_shortcuts(self):
        for i in range(7):
            sc = QShortcut(QKeySequence(f"Ctrl+{i + 1}"), self)
            sc.activated.connect(lambda idx=i: self._navigate_to(idx))
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.quit_app)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.close)

    def _navigate_to(self, index: int):
        if 0 <= index < len(self._stack):
            self._sidebar._select_page(index)

    def _setup_tray(self):
        self._tray = QSystemTrayIcon(self)
        icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
        try:
            import sys
            meipass = Path(sys._MEIPASS)
            icon_path = meipass / "assets" / "icon.ico"
        except AttributeError:
            pass
        icon = QIcon(str(icon_path))
        self._tray.setIcon(icon)
        self._tray.setToolTip(_("AETHER SEDC Wallet v{}").format(VERSION))

        menu = QMenu()
        show_action = QAction(_("Show"), self)
        show_action.triggered.connect(self.show_and_raise)
        menu.addAction(show_action)
        menu.addSeparator()
        quit_action = QAction(_("Quit"), self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def show_and_raise(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()
        self._check_pin()

    def _check_pin(self):
        if self._wallet_mgr.pin_required:
            from PySide6.QtWidgets import QInputDialog, QLineEdit
            attempts = 0
            while attempts < 3:
                ok, pin = QInputDialog.getText(self, _("Wallet Encrypted"), _("Enter PIN to unlock wallet:"), QLineEdit.Password)
                if not ok or not pin:
                    self.hide()
                    return
                err = self._wallet_mgr.decrypt_with_pin(pin)
                if err is None:
                    self._wallet_mgr.upgrade_to_pin_encryption(pin)
                    self._dashboard.refresh()
                    self._send.refresh()
                    self._receive.refresh()
                    self._sidebar.update_wallet_label()
                    return
                attempts += 1
            self._toast.show_toast(_("Wrong PIN after 3 attempts"), "error", 5000)
            self.hide()
            return

        needs_pin = is_pin_set() or self._wallet_mgr.is_pin_protected()
        if not needs_pin:
            return
        from ui.components.pin_dialog import PinDialog
        if is_pin_set():
            dlg = PinDialog("unlock", self)
            if dlg.exec() == PinDialog.Accepted:
                pin = dlg._input.text() or ""
                if verify_pin(pin) and not self._wallet_mgr.pin_required:
                    self._wallet_mgr.upgrade_to_pin_encryption(pin)
            else:
                self.hide()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, _("PIN Reset Detected"),
                _("Your PIN file was deleted or corrupted.\n"
                  "Set a new PIN in Settings to protect your wallet.")
            )
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.warning(
                self, _("PIN Reset Detected"),
                _("Your PIN file was deleted or corrupted.\n"
                  "The wallet is still encrypted with your PIN.\n\n"
                  "You must set a new PIN to unlock it."),
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if reply != QMessageBox.Ok:
                self.hide()
                return
            dlg = PinDialog("set", self)
            if dlg.exec() != PinDialog.Accepted:
                self.hide()
                return
            new_pin = dlg._pin
            err = self._wallet_mgr.decrypt_with_pin(new_pin)
            if err:
                self._toast.show_toast(_("Wrong PIN: {}").format(err), "error", 5000)
                self.hide()
                return
            self._dashboard.refresh()
            self._send.refresh()
            self._receive.refresh()
            self._sidebar.update_wallet_label()

    def _start_auto_backup(self):
        self._backup_timer = QTimer(self)
        self._backup_timer.timeout.connect(self._do_auto_backup)
        self._backup_timer.start(3600000)
        QTimer.singleShot(60000, self._do_auto_backup)

    def _do_auto_backup(self):
        from datetime import datetime
        if not self._wallet_mgr.wallet_file:
            return
        try:
            backup_dir = config.data_dir / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"wallet_{ts}.json.enc"
            raw = self._wallet_mgr.wallet_file.read_bytes()
            backup_path.write_bytes(raw)
            logger = logging.getLogger(__name__)
            logger.info("Auto-backup created: %s", backup_path)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning("Auto-backup failed: %s", e)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_and_raise()

    def quit_app(self):
        self._tray.hide()
        QTimer.singleShot(50, self.close)

    def _on_page_change(self, index: int):
        self._stack.setCurrentIndex(index)

    def _on_stack_changed(self, index: int):
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        content = self._stack.parent()
        if hasattr(self, '_toast'):
            self._toast.setGeometry(0, 0, content.width(), content.height())

    def _startup(self):
        if self._splash:
            self._splash.set_message(_("Starting node..."))
        self._node.start()
        QTimer.singleShot(500, self._watch_rpc_ready)

    def _watch_rpc_ready(self, attempt: int = 1):
        if self._rpc.is_ready():
            self._on_rpc_ready()
        elif attempt > 60:
            self._status_indicator.setStyleSheet(f"color: {WARNING}; font-size: 10px; background: transparent;")
            self._status_text.setText(_("Node not responding"))
            if self._splash:
                self._splash.close()
                self._splash = None
            self._toast.show_toast(_("Node not responding. Check that aether.exe is running."), "warning", 8000)
            self.show()
            self._check_pin()
            self._refresh_timer.start(5000)
            if self._wallet_mgr.load_error:
                self._toast.show_toast(_("Wallet issue: {}").format(self._wallet_mgr.load_error), "warning", 8000)
        else:
            QTimer.singleShot(500, lambda: self._watch_rpc_ready(attempt + 1))

    def _on_rpc_ready(self):
        self._status_indicator.setStyleSheet(f"color: {SUCCESS}; font-size: 10px; background: transparent;")
        self._status_text.setText(_("Connected"))
        if self._splash:
            self._splash.set_message(_("Connected to node"))
        self._refresh_timer.start(3000)
        self._refresh()
        if self._splash:
            self._splash.close()
            self._splash = None
        self.show()
        self._check_pin()
        QTimer.singleShot(5000, self._auto_check_update)
        if self._wallet_mgr.load_error:
            self._toast.show_toast(_("Wallet issue: {}").format(self._wallet_mgr.load_error), "warning", 8000)

    def _auto_check_update(self):
        result = check_for_update()
        if result:
            self._toast.show_toast(_("Update {} available! Check Settings > Updates.").format(result['tag']), "success", 10000)

    def _on_node_status(self, msg: str):
        self._status_text.setText(msg)
        if self._splash:
            self._splash.set_message(msg)

    def _on_node_error(self, msg: str):
        self._status_indicator.setStyleSheet(f"color: {ERROR}; font-size: 10px; background: transparent;")
        self._status_text.setText(_("Error: {}").format(msg.split(chr(10))[0]))
        if self._splash:
            self._splash.set_message(_("Error: {}").format(msg.split(chr(10))[0]))
        if hasattr(self, '_toast'):
            self._toast.show_toast(msg.split(chr(10))[0], "error", 5000)

    def _on_node_started(self):
        self._status_text.setText(_("Node started, connecting..."))
        if self._splash:
            self._splash.set_message(_("Node started, connecting..."))

    def _update_status_bar(self):
        try:
            stats = self._rpc.get_dag_stats()
            peers = stats.get("connected_peers", 0)
            txs = stats.get("total_transactions", 0)
            epoch = stats.get("epoch", 0)
            self._status_peers.setText(_("Peers: {}").format(peers))
            self._status_height.setText(_("Epoch: {}  |  TXs: {}").format(epoch, txs))
            self._status_indicator.setStyleSheet(f"color: {SUCCESS}; font-size: 10px; background: transparent;")
        except Exception:
            self._status_indicator.setStyleSheet(f"color: {WARNING}; font-size: 10px; background: transparent;")
            self._status_peers.setText("")

    def _refresh(self):
        self._dashboard.refresh()
        try:
            resp = self._rpc.get_recent_transactions(1)
            txs = resp.get("transactions", [])
            if isinstance(txs, list) and len(txs) > 0:
                count = len(txs)
                if self._prev_tx_count > 0 and count > self._prev_tx_count:
                    if not self.isVisible():
                        badge = self._transactions._count_label.text()
                        self._tray.showMessage(
                            _("New Transaction"),
                            _("Incoming transaction detected ({})").format(badge),
                            QSystemTrayIcon.MessageIcon.Information,
                            3000
                        )
                self._prev_tx_count = count
        except Exception:
            pass

    def closeEvent(self, event):
        if self._tray.isVisible():
            self.hide()
            self._tray.showMessage(_("AETHER Wallet"), _("Minimized to tray \u2014 wallet keeps running in background."), QSystemTrayIcon.MessageIcon.Information, 2000)
            event.ignore()
        else:
            self._tray.hide()
            self._refresh_timer.stop()
            self._status_timer.stop()
            self._node.cleanup()
            self._rpc.close()
            event.accept()

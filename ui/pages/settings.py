import sys
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit, QFileDialog, QMessageBox, QScrollArea, QDialog, QApplication, QComboBox
from PySide6.QtCore import QUrl

from ui.theme import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BG_CARD, BORDER, ACCENT, ERROR, WARNING
from core.rpc_client import RpcClient
from core.config import config
from wallet.wallet_manager import WalletManager
from utils.pin_manager import is_set as pin_is_set, set_pin, remove_pin
from utils.helpers import VERSION, check_for_update
from utils.i18n import _, set_language, get_language


class SettingsPage(QWidget):
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

        title = QLabel(_("Settings"))
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        # Node section
        node_frame = QFrame()
        node_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        node_layout = QVBoxLayout(node_frame)
        node_layout.setContentsMargins(24, 20, 24, 20)
        node_layout.setSpacing(10)

        node_title = QLabel(_("Node Configuration"))
        node_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        node_layout.addWidget(node_title)

        self._node_info = QLabel(_("Loading..."))
        self._node_info.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        self._node_info.setWordWrap(True)
        node_layout.addWidget(self._node_info)

        layout.addWidget(node_frame)

        # Wallet section
        wallet_frame = QFrame()
        wallet_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        wallet_layout = QVBoxLayout(wallet_frame)
        wallet_layout.setContentsMargins(24, 20, 24, 20)
        wallet_layout.setSpacing(10)

        wallet_title = QLabel(_("Wallet"))
        wallet_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        wallet_layout.addWidget(wallet_title)

        self._wallet_status = QLabel("")
        self._wallet_status.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        wallet_layout.addWidget(self._wallet_status)

        btn_row = QHBoxLayout()

        self._backup_btn = QPushButton(_("Backup Wallet"))
        self._backup_btn.setStyleSheet(self._btn_style())
        self._backup_btn.clicked.connect(self._on_backup)
        btn_row.addWidget(self._backup_btn)

        self._export_pk_btn = QPushButton(_("Export Public Key"))
        self._export_pk_btn.setStyleSheet(self._btn_style())
        self._export_pk_btn.clicked.connect(self._on_export_pk)
        btn_row.addWidget(self._export_pk_btn)

        self._export_sk_btn = QPushButton(_("Export Private Key"))
        self._export_sk_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {WARNING}; font-weight: 600;
                border-radius: 8px; padding: 10px 16px; font-size: 12px;
                border: 1px solid {WARNING}44;
            }}
            QPushButton:hover {{ background-color: {WARNING}22; border-color: {WARNING}; }}
        """)
        self._export_sk_btn.clicked.connect(self._on_export_sk)
        btn_row.addWidget(self._export_sk_btn)

        wallet_layout.addLayout(btn_row)

        layout.addWidget(wallet_frame)

        # Updates section
        update_frame = QFrame()
        update_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        update_layout = QVBoxLayout(update_frame)
        update_layout.setContentsMargins(24, 20, 24, 20)
        update_layout.setSpacing(10)

        update_title = QLabel(_("Updates"))
        update_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        update_layout.addWidget(update_title)

        self._update_status = QLabel(_("Local version: v{}").format(VERSION))
        self._update_status.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; background: transparent;")
        update_layout.addWidget(self._update_status)

        self._check_update_btn = QPushButton(_("Check for Updates"))
        self._check_update_btn.setStyleSheet(self._btn_style())
        self._check_update_btn.clicked.connect(self._on_check_update)
        update_layout.addWidget(self._check_update_btn)

        layout.addWidget(update_frame)

        # Data section
        data_frame = QFrame()
        data_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        data_layout = QVBoxLayout(data_frame)
        data_layout.setContentsMargins(24, 20, 24, 20)
        data_layout.setSpacing(10)

        data_title = QLabel(_("Data Directory"))
        data_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        data_layout.addWidget(data_title)

        data_path = QTextEdit()
        data_path.setPlainText(str(config.data_dir))
        data_path.setReadOnly(True)
        data_path.setMaximumHeight(40)
        data_layout.addWidget(data_path)

        layout.addWidget(data_frame)

        appearance_frame = QFrame()
        appearance_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        appearance_layout = QVBoxLayout(appearance_frame)
        appearance_layout.setContentsMargins(24, 20, 24, 20)
        appearance_layout.setSpacing(10)

        appearance_title = QLabel(_("Appearance"))
        appearance_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        appearance_layout.addWidget(appearance_title)

        self._theme_btn = QPushButton(_("Switch to Light Theme") if self._is_dark() else _("Switch to Dark Theme"))
        self._theme_btn.setStyleSheet(self._btn_style())
        self._theme_btn.clicked.connect(self._on_toggle_theme)
        appearance_layout.addWidget(self._theme_btn)

        theme_note = QLabel(_("Theme change applies after restart"))
        theme_note.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
        appearance_layout.addWidget(theme_note)

        layout.addWidget(appearance_frame)

        lang_frame = QFrame()
        lang_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        lang_layout = QVBoxLayout(lang_frame)
        lang_layout.setContentsMargins(24, 20, 24, 20)
        lang_layout.setSpacing(10)

        lang_title = QLabel(_("Language"))
        lang_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        lang_layout.addWidget(lang_title)

        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["English", "Fran\u00e7ais"])
        self._lang_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: transparent; color: {TEXT_PRIMARY};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 8px 12px; font-size: 13px;
            }}
            QComboBox:focus {{ border-color: {ACCENT}; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox::down-arrow {{ image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid {TEXT_PRIMARY}; margin-right: 8px; }}
        """)
        self._lang_combo.currentTextChanged.connect(self._on_language_changed)
        lang_layout.addWidget(self._lang_combo)

        layout.addWidget(lang_frame)

        security_frame = QFrame()
        security_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        security_layout = QVBoxLayout(security_frame)
        security_layout.setContentsMargins(24, 20, 24, 20)
        security_layout.setSpacing(10)

        security_title = QLabel(_("Security"))
        security_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        security_layout.addWidget(security_title)

        self._pin_btn = QPushButton(_("Set PIN") if not pin_is_set() else _("Change PIN"))
        self._pin_btn.setStyleSheet(self._btn_style())
        self._pin_btn.clicked.connect(self._on_pin)
        security_layout.addWidget(self._pin_btn)

        if pin_is_set():
            self._pin_remove_btn = QPushButton(_("Remove PIN"))
            self._pin_remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent; color: {ERROR}; font-weight: 600;
                    border-radius: 6px; padding: 8px 14px; font-size: 11px;
                    border: 1px solid {ERROR}44;
                }}
                QPushButton:hover {{ background-color: {ERROR}22; border-color: {ERROR}; }}
            """)
            self._pin_remove_btn.clicked.connect(self._on_remove_pin)
            security_layout.addWidget(self._pin_remove_btn)

        pin_note = QLabel(_("PIN protects your wallet and transactions.\nYou'll be asked for it on app startup and before sending."))
        pin_note.setWordWrap(True)
        pin_note.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
        security_layout.addWidget(pin_note)

        layout.addWidget(security_frame)

        startup_frame = QFrame()
        startup_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        startup_layout = QVBoxLayout(startup_frame)
        startup_layout.setContentsMargins(24, 20, 24, 20)
        startup_layout.setSpacing(10)

        startup_title = QLabel(_("Startup"))
        startup_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        startup_layout.addWidget(startup_title)

        self._autostart_btn = QPushButton(_("Disable Auto-Start") if self._is_autostart() else _("Enable Auto-Start"))
        self._autostart_btn.setStyleSheet(self._btn_style())
        self._autostart_btn.clicked.connect(self._on_toggle_autostart)
        startup_layout.addWidget(self._autostart_btn)

        autostart_note = QLabel(_("Automatically launch AETHER Wallet when you log into Windows."))
        autostart_note.setWordWrap(True)
        autostart_note.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
        startup_layout.addWidget(autostart_note)

        layout.addWidget(startup_frame)

        about_frame = QFrame()
        about_frame.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px; border: 1px solid {BORDER};")
        about_layout = QVBoxLayout(about_frame)
        about_layout.setContentsMargins(24, 20, 24, 20)
        about_layout.setSpacing(10)

        about_title = QLabel(_("About"))
        about_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
        about_layout.addWidget(about_title)

        about_lines = [
            (_("Version"), "1.0.0"),
            (_("Protocol"), "AETHER SEDC"),
            (_("Backend"), "aether.exe Rust v1.0.0"),
            (_("RPC Port"), str(config.rpc_port)),
            (_("P2P Port"), str(config.p2p_port)),
            (_("Bootnode"), config.bootnodes[0] if config.bootnodes else "—"),
            (_("Source"), "github.com/dony971/aether"),
        ]
        for label, value in about_lines:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent;")
            lbl.setFixedWidth(100)
            row.addWidget(lbl)
            val = QLabel(value)
            val.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent;")
            val.setWordWrap(True)
            row.addWidget(val, 1)
            about_layout.addLayout(row)

        license_lbl = QLabel(_("MIT License — 2026 AETHER SEDC"))
        license_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
        about_layout.addWidget(license_lbl)

        layout.addWidget(about_frame)
        layout.addStretch()

    def _on_language_changed(self, lang: str):
        code = "fr" if lang == "Fran\u00e7ais" else "en"
        set_language(code)
        QMessageBox.information(self, _("Language Changed"), _("Restart the wallet to apply the language change."))

    def _btn_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: transparent; color: {ACCENT}; font-weight: 600;
                border-radius: 8px; padding: 10px 16px; font-size: 12px;
                border: 1px solid {ACCENT}44;
            }}
            QPushButton:hover {{ background-color: {ACCENT}22; border-color: {ACCENT}; }}
        """

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()

    def _refresh(self):
        wallet_ok = self._wallet_mgr.has_wallet
        wallet_status = _("Active") if wallet_ok else _("None")
        addr_display = self._wallet_mgr.address[:16] + '...' if wallet_ok else '--'
        self._wallet_status.setText(_("Wallet: {}  |  Address: {}").format(wallet_status, addr_display))
        self._backup_btn.setEnabled(wallet_ok)
        self._export_pk_btn.setEnabled(wallet_ok)
        self._export_sk_btn.setEnabled(wallet_ok)

        try:
            stats = self._rpc.get_dag_stats()
            mining = self._rpc.get_mining_status()
            hashrate = self._rpc.get_network_hashrate()
            tips = self._rpc.get_tips()

            mining_status = _("Mining") if mining.get('is_mining') else _("Active")
            bootnode_val = config.bootnodes[0] if config.bootnodes else _("none")
            info = (
                _("Status: {}").format(mining_status) + "\n"
                + _("Peers: {}").format(stats.get('connected_peers', '?')) + "\n"
                + _("Epoch: {}").format(stats.get('epoch', '?')) + "\n"
                + _("TPS: {:.1f}").format(stats.get('current_tps', 0)) + "\n"
                + _("Difficulty: {}").format(hashrate.get('difficulty', '?')) + "\n"
                + _("Hashrate: {}").format(hashrate.get('hashrate', '?')) + "\n"
                + _("Transactions: {}").format(stats.get('total_transactions', 0)) + "\n"
                + _("DAG Tips: {}").format(stats.get('tip_count', 0)) + "\n"
                + _("Bootnode: {}").format(bootnode_val) + "\n"
                + _("P2P Port: {}").format(config.p2p_port) + "\n"
                + _("RPC Port: {}").format(config.rpc_port)
            )
            self._node_info.setText(info)
        except Exception:
            self._node_info.setText(_("Node not connected"))

    def _is_dark(self) -> bool:
        try:
            pref = (Path.home() / "AppData" / "Roaming" / "Aether" / "theme_pref")
            return pref.read_text().strip() != "light" if pref.exists() else True
        except Exception:
            return True

    def _on_toggle_theme(self):
        pref_file = Path.home() / "AppData" / "Roaming" / "Aether" / "theme_pref"
        is_dark = self._is_dark()
        new_theme = "light" if is_dark else "dark"
        try:
            pref_file.parent.mkdir(parents=True, exist_ok=True)
            pref_file.write_text(new_theme)
        except Exception:
            pass
        theme_name = _("Light") if new_theme == "light" else _("Dark")
        QMessageBox.information(
            self, _("Theme Changed"),
            _("Switch to {} theme.\n\nRestart the wallet to apply.").format(theme_name)
        )
        self._theme_btn.setText(_("Switch to Light Theme") if is_dark else _("Switch to Dark Theme"))

    def _on_pin(self):
        from ui.components.pin_dialog import PinDialog
        pin = ""
        if pin_is_set():
            dlg = PinDialog("unlock", self)
            if dlg.exec() == PinDialog.Accepted:
                dlg2 = PinDialog("set", self)
                if dlg2.exec() == PinDialog.Accepted:
                    pin = dlg2._pin
                else:
                    return
        else:
            dlg = PinDialog("set", self)
            if dlg.exec() == PinDialog.Accepted:
                pin = dlg._pin
            else:
                return

        has_pin = bool(pin) or pin_is_set()
        self._wallet_mgr.mark_pin_protected(has_pin, pin if has_pin else None)
        self._pin_btn.setText(_("Change PIN") if has_pin else _("Set PIN"))

        if has_pin and not hasattr(self, "_pin_remove_btn"):
            btn = QPushButton(_("Remove PIN"))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent; color: {ERROR}; font-weight: 600;
                    border-radius: 6px; padding: 8px 14px; font-size: 11px;
                    border: 1px solid {ERROR}44;
                }}
                QPushButton:hover {{ background-color: {ERROR}22; border-color: {ERROR}; }}
            """)
            btn.clicked.connect(self._on_remove_pin)
            self._pin_btn.parent().layout().insertWidget(
                self._pin_btn.parent().layout().indexOf(self._pin_btn) + 1, btn
            )
            self._pin_remove_btn = btn

        self._refresh_pin_ui()

    def _on_remove_pin(self):
        from ui.components.pin_dialog import PinDialog
        dlg = PinDialog("unlock", self)
        if dlg.exec() == PinDialog.Accepted:
            remove_pin()
            self._wallet_mgr.mark_pin_protected(False)
            self._pin_btn.setText(_("Set PIN"))
            self._refresh_pin_ui()

    def _refresh_pin_ui(self):
        if hasattr(self, "_pin_remove_btn"):
            self._pin_remove_btn.setVisible(pin_is_set())

    def _is_autostart(self) -> bool:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, "AETHERWallet")
                return Path(val.strip('"')).resolve() == Path(sys.executable).resolve()
        except (FileNotFoundError, OSError):
            return False

    def _on_toggle_autostart(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            if self._is_autostart():
                winreg.DeleteValue(key, "AETHERWallet")
                self._autostart_btn.setText(_("Enable Auto-Start"))
            else:
                exe = f'"{sys.executable}"'
                winreg.SetValueEx(key, "AETHERWallet", 0, winreg.REG_SZ, exe)
                self._autostart_btn.setText(_("Disable Auto-Start"))
            winreg.CloseKey(key)
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not toggle auto-start:\n{}").format(e))

    def _on_check_update(self):
        self._check_update_btn.setEnabled(False)
        self._update_status.setText(_("Checking for updates..."))
        QTimer.singleShot(100, self._do_check_update)

    def _do_check_update(self):
        try:
            result = check_for_update()
            if result:
                self._update_status.setStyleSheet(f"color: {SUCCESS}; font-size: 12px; background: transparent; font-weight: 700;")
                self._update_status.setText(_("Update available: {} (local: v{})").format(result['tag'], VERSION))
                btn = QMessageBox(
                    QMessageBox.Information,
                    _("Update Available"),
                    _("AETHER SEDC {} is available!\n\n"
                      "{}...\n\n"
                      "Auto-download and install?").format(result['tag'], result['body']),
                    QMessageBox.Yes | QMessageBox.No,
                    self
                )
                if btn.exec() == QMessageBox.Yes:
                    if result.get("setup_url"):
                        self._update_status.setText(_("Downloading update..."))
                        temp_dir = Path.home() / "AppData" / "Local" / "Temp" / "AETHER_Update"
                        temp_dir.mkdir(parents=True, exist_ok=True)
                        setup_path = temp_dir / "AETHER_Wallet_Setup.exe"
                        from utils.helpers import download_update
                        if download_update(result["setup_url"], setup_path):
                            self._update_status.setText(_("Download complete. Launching installer..."))
                            import subprocess
                            subprocess.Popen([str(setup_path)])
                            QTimer.singleShot(500, self.window().close)
                        else:
                            self._update_status.setText(_("Download failed. Try again."))
            else:
                self._update_status.setText(_("You're up to date (v{})").format(VERSION))
                QMessageBox.information(self, _("Up to Date"), _("Current version v{} is the latest.").format(VERSION))
        except Exception as e:
            self._update_status.setText(_("Update check failed: {}").format(e))
        finally:
            self._check_update_btn.setEnabled(True)

    def _on_backup(self):
        if not self._wallet_mgr.wallet_file:
            return
        path, _ = QFileDialog.getSaveFileName(self, _("Backup Wallet"), "wallet_backup.json", "JSON (*.json)")
        if path:
            try:
                import shutil
                shutil.copy2(str(self._wallet_mgr.wallet_file), path)
                QMessageBox.information(self, _("Backup"), _("Wallet backed up to:\n{}").format(path))
            except Exception as e:
                QMessageBox.critical(self, _("Error"), _("Backup failed: {}").format(e))

    def _on_export_pk(self):
        if not self._wallet_mgr.has_wallet:
            return
        QMessageBox.information(
            self, _("Public Key"),
            _("Address / Public Key:\n\n{}").format(self._wallet_mgr.address)
        )

    def _on_export_sk(self):
        if not self._wallet_mgr.has_wallet:
            return
        sk = self._wallet_mgr.export_private_key()
        if not sk:
            QMessageBox.warning(self, _("Error"), _("No private key available."))
            return
        if QMessageBox.warning(
            self, _("WARNING: Private Key Export"),
            _("Anyone with your private key can control your funds.\n\n"
              "Only export if you know what you're doing.\n\n"
              "Continue?"),
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        from PySide6.QtGui import QClipboard
        from PySide6.QtCore import QTimer
        dlg = QDialog(self)
        dlg.setWindowTitle(_("Private Key"))
        dlg.setFixedSize(520, 260)
        dlg.setStyleSheet(f"background-color: {BG_CARD}; border-radius: 12px;")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 20, 24, 20)
        warn = QLabel(_("\u26A0 Keep this secret! Anyone with this key controls your funds."))
        warn.setWordWrap(True)
        warn.setStyleSheet(f"color: {WARNING}; font-size: 12px; background: transparent; font-weight: 600;")
        layout.addWidget(warn)
        key_field = QTextEdit()
        key_field.setPlainText(sk)
        key_field.setReadOnly(True)
        key_field.setMaximumHeight(80)
        key_field.setStyleSheet(f"color: {TEXT_PRIMARY}; background: {BG_PRIMARY}; border: 1px solid {BORDER}; border-radius: 6px; padding: 8px; font-size: 11px;")
        layout.addWidget(key_field)
        btn_layout = QHBoxLayout()
        copy_btn = QPushButton(_("Copy to Clipboard"))
        copy_btn.setStyleSheet(self._btn_style())
        btn_layout.addWidget(copy_btn)
        close_btn = QPushButton(_("Close"))
        close_btn.setStyleSheet(self._btn_style())
        close_btn.clicked.connect(dlg.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        note = QLabel(_("Clipboard will auto-clear after 30 seconds."))
        note.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; background: transparent;")
        layout.addWidget(note)

        def _copy_and_clear():
            clip = QApplication.clipboard()
            clip.setText(sk)
            copy_btn.setText(_("Copied!"))
            copy_btn.setEnabled(False)
            QTimer.singleShot(30000, lambda: clip.clear() if clip.text() == sk else None)

        copy_btn.clicked.connect(_copy_and_clear)
        dlg.exec()

import sys
import traceback
import logging
from pathlib import Path

from PySide6.QtCore import Qt, QSharedMemory
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow
from ui.theme import apply_theme
from ui.components.welcome_dialog import WelcomeDialog
from utils.helpers import setup_logging
from core.config import config

logger = logging.getLogger(__name__)


def _crash_handler(exc_type, exc_value, exc_tb):
    logger.critical(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_tb)
    )
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        QMessageBox.critical(
            None, "AETHER Wallet — Unexpected Error",
            f"An unexpected error occurred.\n\n"
            f"{exc_type.__name__}: {exc_value}\n\n"
            f"Log saved to %APPDATA%/Aether/app.log\n\n"
            f"Please restart the wallet."
        )
    except Exception:
        pass


def _check_single_instance() -> bool:
    mem = QSharedMemory("aether-wallet-single-instance")
    if not mem.create(1):
        if mem.attach():
            mem.detach()
        if not mem.create(1):
            logger.warning("Another instance is already running")
            QMessageBox.warning(None, "Already Running", "AETHER Wallet is already running.")
            return False
    return True


def _check_node_binary() -> bool:
    if not config.node_binary or not config.node_binary.exists():
        logger.error("aether.exe not found at %s", config.node_binary)
        QMessageBox.critical(
            None, "Missing Node Binary",
            f"aether.exe not found.\n\nExpected at:\n{config.node_binary}\n\n"
            "Please reinstall the wallet."
        )
        return False
    return True


if __name__ == "__main__":
    setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("AETHER SEDC")
    app.setOrganizationName("AETHER")
    app.setWindowIcon(QIcon(str(Path(__file__).parent / "assets" / "icon.ico")))

    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("aether.wallet")
    except Exception:
        pass

    if not _check_single_instance():
        sys.exit(1)

    if not _check_node_binary():
        sys.exit(1)

    sys.excepthook = _crash_handler

    apply_theme(app)

    splash = SplashScreen()
    splash.set_message("Starting AETHER node...")
    splash.show()
    app.processEvents()

    from wallet.wallet_manager import WalletManager
    wm = WalletManager()

    win = MainWindow(splash=splash, wallet_mgr=wm)
    app.processEvents()

    splash.close()
    win.show()

    from ui.components.onboarding import is_first_run, OnboardingWizard, mark_done
    if is_first_run():
        wizard = OnboardingWizard(win)
        wizard.exec()

    if not wm.has_wallet:
        dialog = WelcomeDialog(win)
        if dialog.exec() == WelcomeDialog.Accepted:
            win._sidebar._select_page(2)

    sys.exit(app.exec())

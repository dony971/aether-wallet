import logging
import signal
import sys
from pathlib import Path
from PySide6.QtCore import QObject, QProcess, Signal, QTimer

from core.config import config
from utils.audit import log as audit_log

logger = logging.getLogger(__name__)


class NodeManager(QObject):
    started = Signal()
    stopped = Signal()
    error_occurred = Signal(str)
    status_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process: QProcess = QProcess(self)
        self._process.setProcessChannelMode(QProcess.SeparateChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.started.connect(self._on_started)
        self._process.finished.connect(self._on_finished)
        self._restart_timer = QTimer(self)
        self._restart_timer.setSingleShot(True)
        self._restart_timer.timeout.connect(self.start)
        self._restart_count = 0
        self._shutting_down = False
        self._stderr_buf = ""

    @property
    def is_running(self) -> bool:
        return self._process.state() == QProcess.Running

    def start(self):
        if self.is_running:
            return

        binary = config.node_binary
        if not binary.exists():
            self.error_occurred.emit(f"Binary not found: {binary}")
            return

        args = [
            "--daemon",
            "--data-dir", str(config.data_dir),
            "--p2p-port", str(config.p2p_port),
            "--rpc-port", str(config.rpc_port),
        ]
        if config.bootnodes:
            args += ["--bootnodes", ",".join(config.bootnodes)]

        logger.info(f"Starting node: {binary} {' '.join(args)}")
        audit_log("NODE_START", f"Starting node on ports {config.p2p_port}/{config.rpc_port}")
        self.status_changed.emit("Starting node...")
        self._process.start(str(binary), args)

    def stop(self):
        self._shutting_down = True
        self._restart_timer.stop()
        if self.is_running:
            logger.info("Stopping node...")
            self.status_changed.emit("Stopping node...")
            if sys.platform == "win32":
                self._process.terminate()
                QTimer.singleShot(3000, self._kill_if_needed)
            else:
                pid = self._process.processId()
                try:
                    os_kill(pid, signal.SIGINT)
                except (ProcessLookupError, PermissionError):
                    self._process.terminate()
                QTimer.singleShot(5000, self._kill_if_needed)

    def _kill_if_needed(self):
        if self._process.state() == QProcess.Running:
            logger.warning("Force killing node")
            self._process.kill()
            self._process.waitForFinished(2000)

    def _on_started(self):
        self._restart_count = 0
        logger.info("Node process started")
        self.status_changed.emit("Node started")
        self.started.emit()

    def _on_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        logger.info(f"Node exited with code {exit_code} (status {exit_status})")
        self.stopped.emit()

        stderr = self._stderr_buf
        self._stderr_buf = ""

        if "could not acquire lock" in stderr.lower() and "sled" in stderr.lower():
            sled_path = config.data_dir / "sled_db"
            if sled_path.exists():
                import shutil
                shutil.rmtree(str(sled_path), ignore_errors=True)
                logger.warning("Sled DB was locked — deleted stale lock")
                self.status_changed.emit("Resetting database lock...")
                self._restart_count = 0
                QTimer.singleShot(1000, self.start)
                return

        if self._shutting_down:
            return

        if ("address already in use" in stderr.lower()
                or ("port" in stderr.lower() and "in use" in stderr.lower())):
            msg = f"Port {config.rpc_port} or {config.p2p_port} is already in use.\nClose other applications and restart."
            self.error_occurred.emit(msg)
            return

        if exit_code != 0:
            self._restart_count += 1
            audit_log("NODE_CRASH", f"Node exited with code {exit_code}, restart {self._restart_count}/3")
            if self._restart_count <= 3:
                delay = min(2 ** self._restart_count, 10)
                logger.warning(f"Restarting in {delay}s (attempt {self._restart_count}/3)")
                self.status_changed.emit(f"Restarting in {delay}s...")
                self._restart_timer.start(delay * 1000)
            else:
                self.error_occurred.emit("Node crashed too many times. Check logs in %APPDATA%/Aether/app.log")
                audit_log("NODE_ERROR", "Node crashed too many times, giving up")
        else:
            self._restart_count = 0

    def _on_stdout(self):
        data = self._process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        for line in data.splitlines():
            if line.strip():
                logger.debug(f"[node] {line}")

    def _on_stderr(self):
        data = self._read_stderr()
        if data:
            self._stderr_buf += data
            for line in data.splitlines():
                logger.error(f"[node stderr] {line}")

    def _read_stderr(self) -> str:
        raw = self._process.readAllStandardError().data()
        return raw.decode("utf-8", errors="replace") if raw else ""

    def cleanup(self):
        self._shutting_down = True
        self._restart_timer.stop()
        if self.is_running:
            self._process.terminate()
            self._process.waitForFinished(5000)


def os_kill(pid: int, sig):
    if sys.platform == "win32":
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
        ctypes.windll.kernel32.TerminateProcess(handle, 0)
        ctypes.windll.kernel32.CloseHandle(handle)
    else:
        import os as real_os
        real_os.kill(pid, sig)

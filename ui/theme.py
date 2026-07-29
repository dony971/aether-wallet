from PySide6.QtGui import QColor, QPalette, QFont
from pathlib import Path

DARK = {
    "BG_PRIMARY": "#121212",
    "BG_SECONDARY": "#1E1E2E",
    "BG_CARD": "#1A1A2E",
    "BG_CARD_HOVER": "#22223A",
    "BG_SIDEBAR": "#16162A",
    "BG_INPUT": "#2A2A3E",
    "TEXT_PRIMARY": "#FFFFFF",
    "TEXT_SECONDARY": "#9E9EB8",
    "TEXT_MUTED": "#6B6B8A",
    "ACCENT": "#00B4FF",
    "ACCENT_HOVER": "#33C5FF",
    "ACCENT_PRESSED": "#0099DD",
    "ACCENT_DIM": "#0077AA",
    "SUCCESS": "#00D4A0",
    "WARNING": "#FFB800",
    "ERROR": "#FF4757",
    "INFO": "#00B4FF",
    "BORDER": "#2A2A3E",
    "BORDER_LIGHT": "#3A3A52",
}

LIGHT = {
    "BG_PRIMARY": "#F5F5F8",
    "BG_SECONDARY": "#FFFFFF",
    "BG_CARD": "#FFFFFF",
    "BG_CARD_HOVER": "#EEF2FF",
    "BG_SIDEBAR": "#FFFFFF",
    "BG_INPUT": "#F0F0F5",
    "TEXT_PRIMARY": "#1A1A2E",
    "TEXT_SECONDARY": "#6B6B8A",
    "TEXT_MUTED": "#9E9EB8",
    "ACCENT": "#0066FF",
    "ACCENT_HOVER": "#3388FF",
    "ACCENT_PRESSED": "#0055CC",
    "ACCENT_DIM": "#99BBFF",
    "SUCCESS": "#00AA77",
    "WARNING": "#CC8800",
    "ERROR": "#DD3344",
    "INFO": "#0066FF",
    "BORDER": "#D0D0E0",
    "BORDER_LIGHT": "#E0E0F0",
}

CURRENT = DARK.copy()

FONT_FAMILY = "Segoe UI, Inter, Roboto, sans-serif"

_theme_pref_file = Path.home() / "AppData" / "Roaming" / "Aether" / "theme_pref"


def _save_theme_pref(name: str):
    try:
        _theme_pref_file.parent.mkdir(parents=True, exist_ok=True)
        _theme_pref_file.write_text(name)
    except Exception:
        pass


def _load_theme_pref() -> str:
    try:
        if _theme_pref_file.exists():
            return _theme_pref_file.read_text().strip()
    except Exception:
        pass
    return "dark"


def apply_theme(app, theme_name: str = ""):
    if not theme_name:
        theme_name = _load_theme_pref()
    palette_data = DARK if theme_name == "dark" else LIGHT
    CURRENT.clear()
    CURRENT.update(palette_data)

    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(CURRENT["BG_PRIMARY"]))
    palette.setColor(QPalette.WindowText, QColor(CURRENT["TEXT_PRIMARY"]))
    palette.setColor(QPalette.Base, QColor(CURRENT["BG_SECONDARY"]))
    palette.setColor(QPalette.AlternateBase, QColor(CURRENT["BG_CARD"]))
    palette.setColor(QPalette.ToolTipBase, QColor(CURRENT["BG_CARD"]))
    palette.setColor(QPalette.ToolTipText, QColor(CURRENT["TEXT_PRIMARY"]))
    palette.setColor(QPalette.Text, QColor(CURRENT["TEXT_PRIMARY"]))
    palette.setColor(QPalette.Button, QColor(CURRENT["BG_SECONDARY"]))
    palette.setColor(QPalette.ButtonText, QColor(CURRENT["TEXT_PRIMARY"]))
    palette.setColor(QPalette.BrightText, QColor(CURRENT["TEXT_PRIMARY"]))
    palette.setColor(QPalette.Link, QColor(CURRENT["ACCENT"]))
    palette.setColor(QPalette.Highlight, QColor(CURRENT["ACCENT"]))
    palette.setColor(QPalette.HighlightedText, QColor(CURRENT["BG_PRIMARY"]))
    app.setPalette(palette)
    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    stylesheet = f"""
    QWidget {{
        background-color: {CURRENT['BG_PRIMARY']};
        color: {CURRENT['TEXT_PRIMARY']};
        font-family: {FONT_FAMILY};
    }}
    QMainWindow {{
        background-color: {CURRENT['BG_PRIMARY']};
    }}
    QPushButton {{
        background-color: {CURRENT['ACCENT']};
        color: #000000;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {CURRENT['ACCENT_HOVER']};
    }}
    QPushButton:pressed {{
        background-color: {CURRENT['ACCENT_PRESSED']};
    }}
    QPushButton:disabled {{
        background-color: {CURRENT['BORDER']};
        color: {CURRENT['TEXT_MUTED']};
    }}
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {CURRENT['BG_INPUT']};
        color: {CURRENT['TEXT_PRIMARY']};
        border: 1px solid {CURRENT['BORDER']};
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        selection-background-color: {CURRENT['ACCENT_DIM']};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {CURRENT['ACCENT']};
    }}
    QLabel {{
        color: {CURRENT['TEXT_PRIMARY']};
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {CURRENT['BORDER']};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {CURRENT['TEXT_MUTED']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 6px;
    }}
    QScrollBar::handle:horizontal {{
        background: {CURRENT['BORDER']};
        border-radius: 3px;
        min-width: 30px;
    }}
    QMessageBox {{
        background-color: {CURRENT['BG_PRIMARY']};
        color: {CURRENT['TEXT_PRIMARY']};
    }}
    QMessageBox QLabel {{
        color: {CURRENT['TEXT_PRIMARY']};
    }}
    QMessageBox QPushButton {{
        background-color: {CURRENT['ACCENT']};
        color: #000000;
        border: none;
        border-radius: 6px;
        padding: 6px 20px;
        font-size: 12px;
        font-weight: 600;
        min-width: 80px;
    }}
    """
    app.setStyleSheet(stylesheet)

    _save_theme_pref(theme_name)


def __getattr__(name):
    if name in CURRENT:
        return CURRENT[name]
    raise AttributeError(f"module 'ui.theme' has no attribute '{name}'")

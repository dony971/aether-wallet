from dataclasses import dataclass, field
from pathlib import Path
import os
import sys


def default_data_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", ".")) / "Aether"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Aether"
    else:
        return Path.home() / ".aether"


def find_node_binary() -> Path:
    paths = [
        Path.cwd() / "aether.exe",
        Path.cwd() / "aether",
        Path.cwd() / "target" / "release" / "aether.exe",
        Path.cwd() / "target" / "release" / "aether",
        default_data_dir() / "aether.exe",
        default_data_dir() / "aether",
    ]
    try:
        import sys
        meipass = Path(sys._MEIPASS)
        paths.insert(0, meipass / "aether.exe")
        paths.insert(0, meipass / "aether")
    except AttributeError:
        pass
    for p in paths:
        if p.exists():
            return p.resolve()
        if sys.platform == "win32":
            alt = p.with_suffix(".exe")
            if alt.exists():
                return alt.resolve()
    return paths[0]


@dataclass
class AppConfig:
    data_dir: Path = field(default_factory=default_data_dir)
    node_binary: Path = field(default_factory=find_node_binary)
    p2p_port: int = 25565
    rpc_port: int = 9933
    bootnodes: list[str] = field(default_factory=lambda: ["103.102.135.123:25565"])
    node_type: str = "miner"


config = AppConfig()

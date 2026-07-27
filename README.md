# AETHER SEDC Wallet

A full-featured desktop wallet for the AETHER Self-Evolving DAG cryptocurrency.

![AETHER Wallet](assets/icon.ico)

## Features

- **Dashboard** — Live network stats, balance chart, TPS graph
- **Send** — Single or multi-recipient transactions with fee selection
- **Receive** — Wallet creation, QR code, address copy, faucet
- **Transactions** — Searchable history, CSV export, detail dialog
- **Staking** — Stake tokens, track rewards, 12.5% APY
- **Mining** — Start/stop mining, hashrate chart, network stats
- **Settings** — Node info, wallet backup, PIN security, theme, auto-updater
- **Multi-Wallet** — Create, import, switch between wallets
- **Address Book** — Save contacts, quick-send to saved addresses
- **Security** — PIN lock (app startup + send protection)
- **System Tray** — Minimize to tray, background operation, transaction notifications
- **Themes** — Dark (default) and Light mode
- **Auto-Backup** — Hourly wallet backup to `%APPDATA%/Aether/backups/`

## Requirements

- Windows 10/11 (64-bit)
- No dependencies — everything is bundled

## Installation

### Option 1: Portable ZIP

1. Download `AETHER_Wallet_v1.0.0_Portable.zip`
2. Extract anywhere
3. Run `AETHER_Wallet.exe`

### Option 2: Inno Setup Installer

1. Download `AETHER_Wallet_v1.0.0_Setup.exe`
2. Run the installer
3. Launch from Start Menu or Desktop shortcut

## First Run

1. On first launch, an onboarding wizard guides you through setup
2. Create a wallet in the **Receive** tab
3. Get test tokens via the **Faucet** button
4. Start sending, staking, or mining

## Configuration

All data is stored in `%APPDATA%/Aether/`:
- `wallets/` — Wallet files (JSON)
- `backups/` — Automatic wallet backups
- `contacts.json` — Address book
- `app.log` — Application logs (rotated, 3 × 2MB)
- `.pin` — PIN hash (if set)
- `theme_pref` — Theme preference

## Building from Source

```bash
pip install -r requirements.txt
python -m PyInstaller --noconsole --onedir --name "AETHER_Wallet" ^
    --icon "assets\icon.ico" ^
    --add-data "aether.exe;." ^
    --add-data "assets\icon.ico;assets" ^
    main.py
```

Output: `dist/AETHER_Wallet/AETHER_Wallet.exe`

## Running Tests

```bash
pip install pytest
pytest tests/
```

## Architecture

```
main.py                    Entry point (single instance, crash handler, onboarding)
core/
  config.py                AppConfig, paths, ports, bootnode
  rpc_client.py            Synchronous JSON-RPC client (requests)
  node_manager.py          QProcess wrapper for aether.exe
wallet/
  wallet_manager.py        Multi-wallet management, import/export
ui/
  theme.py                 Dark/Light theme engine, palette
  main_window.py           Frameless window, tray, timers, PIN lock
  components/
    sidebar.py             7-page sidebar with wallet label
    title_bar.py           Custom Fluent Design title bar
    card.py                Hover-glow stat cards
    toast.py               Non-blocking toast notifications
    welcome_dialog.py      First-run wallet creation prompt
    onboarding.py          5-step onboarding wizard
    wallet_dialog.py       Multi-wallet management dialog
    address_book_dialog.py Contacts management dialog
    pin_dialog.py          PIN entry/setup dialog
    help_dialog.py         Help & getting started
  pages/
    dashboard.py           Stats, balance banner, 2 live charts
    send.py                Transaction builder (multi-recipient)
    receive.py             Wallet, QR, faucet, copy
    transactions.py        Table, search, CSV export, empty states
    staking.py             Stake/unstake, rewards, APY
    mining.py              Mining controls, hashrate chart, network
    settings.py            Node, wallet, theme, PIN, auto-updater, about
    tx_detail.py           Transaction detail dialog
utils/
  helpers.py               Logging setup, AETH conversion
  contacts.py              Address book storage (JSON)
  pin_manager.py           PIN hashing/verification (SHA-256 + salt)
```

## License

MIT License — 2026 AETHER SEDC

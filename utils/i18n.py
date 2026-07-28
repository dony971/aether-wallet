import json
from pathlib import Path
from core.config import config

_current_lang = "fr"

TRANSLATIONS = {
    "en": {
        # Sidebar
        "  AETHER": "  AETHER",
        "  Wallet": "  Wallet",
        "  loading...": "  loading...",
        "  No wallet": "  No wallet",
        "  Manage Wallets": "  Manage Wallets",
        "  Address Book": "  Address Book",
        "Dashboard": "Dashboard",
        "Send": "Send",
        "Receive": "Receive",
        "Transactions": "Transactions",
        "Staking": "Staking",
        "Mining": "Mining",
        "Settings": "Settings",
        "?  Help": "?  Help",
        # Dashboard
        "Your Balance": "Your Balance",
        "Peers": "Peers",
        "Hashrate": "Hashrate",
        "Difficulty": "Difficulty",
        "Status": "Status",
        "Total Mined": "Total Mined",
        "Network Hashrate": "Network Hashrate",
        "Network Activity (TPS)": "Network Activity (TPS)",
        "No wallet yet": "No wallet yet",
        "Create a wallet to start using the AETHER network.": "Create a wallet to start using the AETHER network.",
        # Receive
        "Receive": "Receive",
        "Your Address": "Your Address",
        "Copy": "Copy",
        "Check Balance": "Check Balance",
        "Request Faucet (10 AETH)": "Request Faucet (10 AETH)",
        "Create Wallet": "Create Wallet",
        "No wallet yet. Click above to create one.": "No wallet yet. Click above to create one.",
        "Address copied to clipboard!": "Address copied to clipboard!",
        "Install 'qrcode' for QR": "Install 'qrcode' for QR",
        # Send
        "Send AETHER": "Send AETHER",
        "From": "From",
        "To": "To",
        "Amount (atomic units)": "Amount (atomic units)",
        "Add Recipient": "Add Recipient",
        "Send All": "Send All",
        "Network Fee": "Network Fee",
        "Total": "Total",
        "Send Now": "Send Now",
        "No wallet": "No wallet",
        # Transactions
        "Recent Transactions": "Recent Transactions",
        "No transactions yet": "No transactions yet",
        "Confirming...": "Confirming...",
        "Confirmed": "Confirmed",
        # Settings
        "Node": "Node",
        "Wallet": "Wallet",
        "Updates": "Updates",
        "Data": "Data",
        "Appearance": "Appearance",
        "Security": "Security",
        "Startup": "Startup",
        "About": "About",
        "Local version": "Local version",
        "Check for Updates": "Check for Updates",
        "Export Private Key": "Export Private Key",
        "Backup Wallet": "Backup Wallet",
        "Data Directory": "Data Directory",
        "Open Data Dir": "Open Data Dir",
        "Theme": "Theme",
        "Dark": "Dark",
        "Light": "Light",
        "PIN Code": "PIN Code",
        "Set PIN": "Set PIN",
        "Change PIN": "Change PIN",
        "Remove PIN": "Remove PIN",
        "Auto-start on login": "Auto-start on login",
        # Staking
        "Staking": "Staking",
        "Your Stake: —": "Your Stake: —",
        "Rewards Earned: —": "Rewards Earned: —",
        "APY: 12.5%": "APY: 12.5%",
        "Total Staked: —": "Total Staked: —",
        "Stake Amount (atomic units)": "Stake Amount (atomic units)",
        "Stake": "Stake",
        "Unstake All": "Unstake All",
        # Mining
        "Mining & Network": "Mining & Network",
        "Checking...": "Checking...",
        "Start Mining": "Start Mining",
        "Stop Mining": "Stop Mining",
        "Mining Hashrate": "Mining Hashrate",
        "Network": "Network",
        "Connected Peers": "Connected Peers",
        "TPS": "TPS",
        "DAG Tips": "DAG Tips",
        "Epoch": "Epoch",
        "Total Transactions": "Total Transactions",
        "Waiting for mining data...": "Waiting for mining data...",
        # General
        "Search contacts or paste address...": "Search contacts or paste address...",
        "Node not responding": "Node not responding",
        "Starting...": "Starting...",
        "Connected": "Connected",
        "Update available": "Update available",
        "You're up to date": "You're up to date",
        "Update check failed": "Update check failed",
    },
    "fr": {
        # Sidebar
        "  AETHER": "  AETHER",
        "  Wallet": "  Portefeuille",
        "  loading...": "  chargement...",
        "  No wallet": "  Aucun wallet",
        "  Manage Wallets": "  Gérer les wallets",
        "  Address Book": "  Carnet d'adresses",
        "Dashboard": "Tableau de bord",
        "Send": "Envoyer",
        "Receive": "Recevoir",
        "Transactions": "Transactions",
        "Staking": "Staking",
        "Mining": "Minage",
        "Settings": "Paramètres",
        "?  Help": "?  Aide",
        # Dashboard
        "Your Balance": "Votre Solde",
        "Peers": "Pairs",
        "Hashrate": "Taux de hachage",
        "Difficulty": "Difficulté",
        "Status": "Statut",
        "Total Mined": "Total Miné",
        "Network Hashrate": "Taux de hachage réseau",
        "Network Activity (TPS)": "Activité réseau (TPS)",
        "No wallet yet": "Aucun wallet",
        "Create a wallet to start using the AETHER network.": "Créez un wallet pour utiliser le réseau AETHER.",
        # Receive
        "Receive": "Recevoir",
        "Your Address": "Votre Adresse",
        "Copy": "Copier",
        "Check Balance": "Voir le solde",
        "Request Faucet (10 AETH)": "Demander au Faucet (10 AETH)",
        "Create Wallet": "Créer un wallet",
        "No wallet yet. Click above to create one.": "Pas encore de wallet. Cliquez ci-dessus pour en créer un.",
        "Address copied to clipboard!": "Adresse copiée !",
        "Install 'qrcode' for QR": "Installez 'qrcode' pour le QR",
        # Send
        "Send AETHER": "Envoyer AETHER",
        "From": "De",
        "To": "À",
        "Amount (atomic units)": "Montant (unités atomiques)",
        "Add Recipient": "Ajouter un destinataire",
        "Send All": "Tout envoyer",
        "Network Fee": "Frais réseau",
        "Total": "Total",
        "Send Now": "Envoyer",
        "No wallet": "Aucun wallet",
        # Transactions
        "Recent Transactions": "Transactions récentes",
        "No transactions yet": "Aucune transaction",
        "Confirming...": "Confirmation...",
        "Confirmed": "Confirmé",
        # Settings
        "Node": "Nœud",
        "Wallet": "Portefeuille",
        "Updates": "Mises à jour",
        "Data": "Données",
        "Appearance": "Apparence",
        "Security": "Sécurité",
        "Startup": "Démarrage",
        "About": "À propos",
        "Local version": "Version locale",
        "Check for Updates": "Vérifier les mises à jour",
        "Export Private Key": "Exporter la clé privée",
        "Backup Wallet": "Sauvegarder le wallet",
        "Data Directory": "Dossier de données",
        "Open Data Dir": "Ouvrir le dossier",
        "Theme": "Thème",
        "Dark": "Sombre",
        "Light": "Clair",
        "PIN Code": "Code PIN",
        "Set PIN": "Définir le PIN",
        "Change PIN": "Changer le PIN",
        "Remove PIN": "Supprimer le PIN",
        "Auto-start on login": "Démarrage auto",
        # Staking
        "Staking": "Staking",
        "Your Stake: —": "Votre mise : —",
        "Rewards Earned: —": "Récompenses : —",
        "APY: 12.5%": "APY : 12,5 %",
        "Total Staked: —": "Total misé : —",
        "Stake Amount (atomic units)": "Montant à miser (unités atomiques)",
        "Stake": "Miser",
        "Unstake All": "Tout retirer",
        # Mining
        "Mining & Network": "Minage & Réseau",
        "Checking...": "Vérification...",
        "Start Mining": "Démarrer le minage",
        "Stop Mining": "Arrêter le minage",
        "Mining Hashrate": "Taux de hachage minage",
        "Network": "Réseau",
        "Connected Peers": "Pairs connectés",
        "TPS": "TPS",
        "DAG Tips": "Pointes DAG",
        "Epoch": "Époque",
        "Total Transactions": "Total transactions",
        "Waiting for mining data...": "Données de minage...",
        # General
        "Search contacts or paste address...": "Rechercher ou coller une adresse...",
        "Node not responding": "Nœud ne répond pas",
        "Starting...": "Démarrage...",
        "Connected": "Connecté",
        "Update available": "Mise à jour disponible",
        "You're up to date": "Vous êtes à jour",
        "Update check failed": "Échec de la vérification",
    },
}

def _(text: str) -> str:
    return TRANSLATIONS.get(_current_lang, {}).get(text, text)

def set_language(lang: str):
    global _current_lang
    if lang in TRANSLATIONS:
        _current_lang = lang
        _save_pref()

def get_language() -> str:
    return _current_lang

def _pref_file() -> Path:
    return config.data_dir / "lang_pref"

def _save_pref():
    try:
        _pref_file().write_text(_current_lang)
    except Exception:
        pass

def _load_pref():
    global _current_lang
    try:
        if _pref_file().exists():
            lang = _pref_file().read_text().strip()
            if lang in TRANSLATIONS:
                _current_lang = lang
    except Exception:
        pass

_load_pref()

import logging
import requests

logger = logging.getLogger(__name__)


class RpcError(Exception):
    pass


class RpcClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 9933):
        self._url = f"http://{host}:{port}"
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def _call(self, method: str, params=None) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or [],
        }
        try:
            resp = self._session.post(self._url, json=payload, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data and data["error"] is not None:
                raise RpcError(data["error"].get("message", str(data["error"])))
            return data.get("result", data)
        except requests.ConnectionError:
            raise RpcError("Cannot connect to node")
        except requests.Timeout:
            raise RpcError("RPC request timed out")
        except requests.RequestException as e:
            raise RpcError(f"RPC error: {e}")

    def get_balance(self, address: str) -> dict:
        return self._call("aether_getBalance", [address])

    def send_transaction(self, tx_hex: str) -> dict:
        return self._call("aether_sendTransaction", [tx_hex])

    def get_dag_stats(self) -> dict:
        return self._call("aether_getDagStats")

    def get_network_hashrate(self) -> dict:
        return self._call("aether_getNetworkHashrate")

    def get_transaction_status(self, hash_hex: str) -> dict:
        return self._call("aether_getTransactionStatus", [hash_hex])

    def get_recent_transactions(self, limit: int = 10) -> dict:
        return self._call("aether_getRecentTransactions", [limit])

    def get_transaction_history(self, address: str) -> dict:
        return self._call("aether_getTransactionHistory", [address])

    def get_mining_status(self) -> dict:
        return self._call("aether_getMiningStatus")

    def start_mining(self) -> dict:
        return self._call("aether_startMining")

    def stop_mining(self) -> dict:
        return self._call("aether_stopMining")

    def faucet(self, address: str) -> dict:
        return self._call("aether_faucet", [address])

    def create_account(self) -> dict:
        return self._call("aether_createAccount")

    def get_tips(self) -> dict:
        return self._call("aether_getTips")

    def get_dag_snapshot(self) -> dict:
        return self._call("aether_getDagSnapshot")

    def get_staking_info(self, address: str) -> dict:
        return self._call("aether_getStakingInfo", [address])

    def stake_tokens(self, address: str, amount: int) -> dict:
        return self._call("aether_stakeTokens", [address, amount])

    def unstake_tokens(self, address: str) -> dict:
        return self._call("aether_unstakeTokens", [address])

    def get_account_nonce(self, address: str) -> dict:
        return self._call("aether_getAccountNonce", [address])

    def is_ready(self) -> bool:
        try:
            self.get_mining_status()
            return True
        except RpcError:
            return False

    def close(self):
        self._session.close()

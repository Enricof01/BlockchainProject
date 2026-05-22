"""
wallet_node.py
==============
WalletNode – erbt von Node, ergänzt Wallet-Funktionalität.
Kann TXs erstellen, signieren und einreichen.
"""

from node import Node
from wallet.wallet import Wallet
from p2p import sync_chain, discover_peers


class WalletNode(Node):
    def __init__(self, node_name: str, port: int, blockchain, wallet: Wallet):
        super().__init__(node_name=node_name, port=port, blockchain=blockchain)
        self.wallet = wallet
        self._setup_wallet_routes()

    # --------------------------------------------------
    # WALLET-AKTIONEN
    # --------------------------------------------------

    def send(self, recipient: str, amount: float) -> tuple[bool, str]:
        """
        Erstellt eine signierte TX und reicht sie beim eigenen Mempool ein.
        Broadcastet sie danach an alle Peers.
        """
        # Zuerst Chain synchronisieren damit Balance aktuell ist
        sync_chain(self)

        available = self.get_available_balance(self.wallet.address)
        if available < amount:
            return False, f"Nicht genug Coins. Verfügbar: {available:.2f}"

        tx_dict = self.wallet.create_transaction(recipient=recipient, amount=amount)
        accepted, message = self.add_transaction_to_mempool(tx_dict)

        if accepted:
            self.broadcast_transaction(tx_dict)

        return accepted, message

    # --------------------------------------------------
    # ZUSÄTZLICHE ROUTES
    # --------------------------------------------------

    def _setup_wallet_routes(self):

        @self.app.route("/wallet/info", methods=["GET"])
        def wallet_info():
            from flask import jsonify
            return jsonify({
                "address":           self.wallet.address,
                "confirmed_balance": self.get_balance(self.wallet.address),
                "available_balance": self.get_available_balance(self.wallet.address),
            })

        @self.app.route("/wallet/send", methods=["POST"])
        def wallet_send():
            from flask import jsonify, request
            data      = request.get_json()
            recipient = data.get("recipient")
            amount    = data.get("amount")

            if not recipient or amount is None:
                return jsonify({"message": "recipient und amount erforderlich."}), 400

            accepted, message = self.send(recipient=recipient, amount=float(amount))
            return jsonify({"accepted": accepted, "message": message})

        @self.app.route("/wallet/sync", methods=["POST"])
        def wallet_sync():
            from flask import jsonify
            replaced = sync_chain(self)
            return jsonify({
                "synced":       replaced,
                "chain_length": len(self.blockchain.chain),
            })
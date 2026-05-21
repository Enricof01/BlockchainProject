"""
node.py
=======
Node – orchestriert Blockchain, Mempool, P2P-Netzwerk und API.
Hat-eine Blockchain (Aggregation).
"""

import json
import hashlib

import requests
from flask import Flask, jsonify, request
from cryptography.hazmat.primitives import serialization

from wallet import verify_transaction, public_key_to_address


class Node:
    def __init__(self, node_name: str, port: int, blockchain=None):
        self.node_name  = node_name
        self.port       = port
        self.app        = Flask(node_name)
        self.blockchain = blockchain   # has-a Beziehung
        self.mempool    = []
        self.peers      = set()
        self.setup_routes()

    # --------------------------------------------------
    # HILFSFUNKTIONEN
    # --------------------------------------------------

    def transaction_to_string(self, transaction: dict) -> str:
        return json.dumps(transaction, sort_keys=True)

    def get_transaction_id(self, transaction: dict) -> str:
        return hashlib.sha256(
            self.transaction_to_string(transaction).encode("utf-8")
        ).hexdigest()

    # --------------------------------------------------
    # BALANCE
    # Die Node fragt die Blockchain – sie berechnet nicht selbst.
    # --------------------------------------------------

    def get_balance(self, address: str) -> float:
        """
        Delegiert an blockchain.get_balance().
        Node entscheidet was sie mit dem Ergebnis macht (z.B. TX ablehnen).
        """
        if self.blockchain is None:
            return 0.0
        return self.blockchain.get_balance(address)

    def get_pending_spent_amount(self, address: str) -> float:
        """
        Coins die bereits im Mempool ausgegeben werden (noch nicht bestätigt).
        Das prüft die Node selbst – die Blockchain kennt den Mempool nicht.
        """
        spent = 0.0
        for tx in self.mempool:
            if tx.get("sender") == address:
                spent += float(tx.get("amount", 0))
        return spent

    def get_available_balance(self, address: str) -> float:
        """Bestätigte Balance minus wartende Ausgaben im Mempool."""
        return self.get_balance(address) - self.get_pending_spent_amount(address)

    # --------------------------------------------------
    # TRANSAKTIONSVALIDIERUNG
    # --------------------------------------------------

    def validate_transaction_format(self, transaction: dict):
        required = ["sender", "recipient", "amount", "timestamp", "public_key", "signature"]
        for field in required:
            if field not in transaction:
                return False, f"Feld fehlt: {field}"
        return True, "Format gültig."

    def is_duplicate_transaction(self, transaction: dict) -> bool:
        new_id = self.get_transaction_id(transaction)
        return any(self.get_transaction_id(tx) == new_id for tx in self.mempool)

    def public_key_matches_sender(self, transaction: dict) -> bool:
        """
        Verhindert Angriff: Jemand signiert mit eigenem Key,
        schreibt aber Alices Adresse als Sender rein.
        """
        try:
            public_key = serialization.load_pem_public_key(
                transaction["public_key"].encode("utf-8")
            )
            return public_key_to_address(public_key) == transaction["sender"]
        except Exception:
            return False

    def validate_transaction(self, transaction: dict):
        """Komplette Prüfkette – Node entscheidet ob TX in den Mempool darf."""

        # Coinbase-TXs lehnt die Node immer ab (nur Blockchain/Miner darf die erstellen)
        if transaction.get("sender") == "COINBASE":
            return False, "Externe Coinbase-Transaktionen sind nicht erlaubt."

        format_valid, message = self.validate_transaction_format(transaction)
        if not format_valid:
            return False, message

        try:
            sender    = transaction["sender"]
            recipient = transaction["recipient"]
            amount    = float(transaction["amount"])

            if not sender:
                return False, "Sender fehlt."
            if not recipient:
                return False, "Empfänger fehlt."
            if amount <= 0:
                return False, "Betrag muss größer als 0 sein."
            if self.is_duplicate_transaction(transaction):
                return False, "Transaktion bereits im Mempool."
            if not verify_transaction(transaction):
                return False, "Signatur ungültig."
            if not self.public_key_matches_sender(transaction):
                return False, "Public Key passt nicht zur Sender-Adresse."

            # Node fragt Blockchain nach verfügbarer Balance
            available = self.get_available_balance(sender)
            if available < amount:
                return False, f"Nicht genug Coins. Verfügbar: {available:.2f}, benötigt: {amount:.2f}"

            return True, "Transaktion gültig."

        except ValueError:
            return False, "Amount ist keine gültige Zahl."
        except Exception as e:
            return False, f"Fehler bei Validierung: {e}"

    def add_transaction_to_mempool(self, transaction: dict):
        is_valid, message = self.validate_transaction(transaction)
        if not is_valid:
            return False, message
        self.mempool.append(transaction)
        return True, "Transaktion in Mempool aufgenommen."

    def remove_transactions_from_mempool(self, transactions: list):
        ids_to_remove = {self.get_transaction_id(tx) for tx in transactions}
        self.mempool = [
            tx for tx in self.mempool
            if self.get_transaction_id(tx) not in ids_to_remove
        ]

    # --------------------------------------------------
    # PEER-TO-PEER
    # --------------------------------------------------

    def add_peer(self, peer_url: str):
        self.peers.add(peer_url)

    def broadcast_transaction(self, transaction: dict):
        for peer in self.peers:
            try:
                requests.post(f"{peer}/receive_transaction", json=transaction, timeout=3)
            except requests.RequestException:
                print(f"[{self.node_name}] Peer nicht erreichbar: {peer}")

    def broadcast_block(self, block):
        block_data = block.to_dict() if hasattr(block, "to_dict") else block
        for peer in self.peers:
            try:
                requests.post(f"{peer}/receive_block", json=block_data, timeout=3)
            except requests.RequestException:
                print(f"[{self.node_name}] Peer nicht erreichbar: {peer}")

    # --------------------------------------------------
    # BLOCK-ÜBERGABE AN BLOCKCHAIN
    # --------------------------------------------------

    def add_received_block(self, block_data: dict):
        """
        Node empfängt Block vom Netzwerk und reicht ihn an die Blockchain weiter.
        Blockchain entscheidet ob er gültig ist (Validierungslogik bleibt dort).
        """
        if self.blockchain is None:
            return False, "Keine Blockchain verbunden."

        accepted = self.blockchain.add_block(block_data)

        if accepted:
            transactions = block_data.get("transactions", [])
            self.remove_transactions_from_mempool(transactions)
            return True, "Block akzeptiert, Mempool aktualisiert."

        return False, "Block von Blockchain abgelehnt."

    # --------------------------------------------------
    # ROUTES / API
    # --------------------------------------------------

    def setup_routes(self):

        @self.app.route("/status", methods=["GET"])
        def status():
            return jsonify({
                "node_name":    self.node_name,
                "port":         self.port,
                "peers":        list(self.peers),
                "mempool_size": len(self.mempool),
                "chain_length": len(self.blockchain.chain) if self.blockchain else None,
            })

        @self.app.route("/chain", methods=["GET"])
        def get_chain():
            if self.blockchain is None:
                return jsonify({"message": "Keine Blockchain verbunden."}), 400
            chain_data = [
                block.to_dict() if hasattr(block, "to_dict") else block.__dict__
                for block in self.blockchain.chain
            ]
            return jsonify({"length": len(chain_data), "chain": chain_data})

        @self.app.route("/mempool", methods=["GET"])
        def get_mempool():
            return jsonify({"mempool_size": len(self.mempool), "mempool": self.mempool})

        @self.app.route("/balance/<address>", methods=["GET"])
        def get_balance_route(address):
            return jsonify({
                "address":           address,
                "confirmed_balance": self.get_balance(address),
                "pending_spent":     self.get_pending_spent_amount(address),
                "available_balance": self.get_available_balance(address),
            })

        @self.app.route("/receive_transaction", methods=["POST"])
        def receive_transaction():
            """Empfängt TX von Peers – kein Re-Broadcast."""
            tx = request.get_json()
            accepted, message = self.add_transaction_to_mempool(tx)
            print(f"[{self.node_name}] TX empfangen: {message}")
            return jsonify({"accepted": accepted, "message": message})

        @self.app.route("/submit_transaction", methods=["POST"])
        def submit_transaction():
            """Empfängt TX von Wallet/Frontend – broadcastet bei Erfolg."""
            tx = request.get_json()
            accepted, message = self.add_transaction_to_mempool(tx)
            if accepted:
                self.broadcast_transaction(tx)
            return jsonify({"accepted": accepted, "message": message})

        @self.app.route("/add_peer", methods=["POST"])
        def add_peer_route():
            data = request.get_json()
            peer = data.get("peer")
            if not peer:
                return jsonify({"message": "Peer fehlt."}), 400
            self.add_peer(peer)
            return jsonify({"message": "Peer hinzugefügt.", "peers": list(self.peers)})

        @self.app.route("/peers", methods=["GET"])
        def get_peers():
            return jsonify({"peers": list(self.peers)})

        @self.app.route("/receive_block", methods=["POST"])
        def receive_block():
            block_data = request.get_json()
            accepted, message = self.add_received_block(block_data)
            return jsonify({"accepted": accepted, "message": message}), 200 if accepted else 400
        @self.app.route("/sync", methods=["POST"])
        def sync():
            from p2p import sync_chain
            replaced = sync_chain(self)
            return jsonify({
                "synced":       replaced,
                "chain_length": len(self.blockchain.chain),
                "peers":        list(self.peers),
            })

    def run(self, debug=False):
        print(f"[{self.node_name}] Starte auf Port {self.port}...")
        self.app.run(host="0.0.0.0", port=self.port, debug=debug)
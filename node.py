import json
import hashlib

import requests
from flask import Flask, jsonify, request
from cryptography.hazmat.primitives import serialization

from wallet.transaction import verify_transaction
from wallet.address import public_key_to_address


class Node:
    def __init__(self, node_name, port, blockchain=None):
        self.node_name = node_name
        self.port = port
        self.app = Flask(node_name)

        # Die Blockchain wird von außen übergeben.
        # In blockchain.py liegen Block, Chain, Mining usw.
        self.blockchain = blockchain

        # Mempool = gültige, aber noch nicht geminte Transaktionen
        self.mempool = []

        # Andere bekannte Nodes
        self.peers = set()

        self.setup_routes()

    # --------------------------------------------------
    # HILFSFUNKTIONEN
    # --------------------------------------------------

    def transaction_to_string(self, transaction: dict) -> str:
        """
        Wandelt eine Transaktion stabil in einen String um.
        Wird genutzt, um doppelte Transaktionen zu erkennen.
        """
        return json.dumps(transaction, sort_keys=True)

    def get_transaction_id(self, transaction: dict) -> str:
        """
        Erstellt eine eindeutige ID für eine Transaktion.
        """
        tx_string = self.transaction_to_string(transaction)
        return hashlib.sha256(tx_string.encode("utf-8")).hexdigest()

    def get_confirmed_transactions(self):
        """
        Holt alle Transaktionen aus der Blockchain.
        Diese Funktion ist flexibel, damit sie mit verschiedenen Block-Strukturen funktioniert.
        """
        if self.blockchain is None:
            return []

        confirmed_transactions = []

        if not hasattr(self.blockchain, "chain"):
            return []

        for block in self.blockchain.chain:
            # Variante 1: block ist ein Objekt mit .transactions
            if hasattr(block, "transactions"):
                confirmed_transactions.extend(block.transactions)

            # Variante 2: block ist ein Dictionary mit ["transactions"]
            elif isinstance(block, dict) and "transactions" in block:
                confirmed_transactions.extend(block["transactions"])

        return confirmed_transactions

    def public_key_matches_sender(self, transaction: dict) -> bool:
        """
        Prüft:
        Gehört der mitgeschickte Public Key wirklich zur Sender-Adresse?

        Wichtig gegen diesen Angriff:
        Jemand signiert mit seinem eigenen Key,
        schreibt aber als sender die Adresse von Alice rein.
        """
        try:
            sender_address = transaction["sender"]
            public_key_pem = transaction["public_key"]

            public_key = serialization.load_pem_public_key(
                public_key_pem.encode("utf-8")
            )

            calculated_address = public_key_to_address(public_key)

            return calculated_address == sender_address

        except Exception:
            return False

    # --------------------------------------------------
    # BALANCE
    # --------------------------------------------------

    def get_balance(self, address: str) -> float:
        """
        Berechnet den Kontostand einer Adresse aus allen bestätigten Transaktionen
        in der Blockchain.

        Wichtig:
        Die Wallet speichert keine Coins.
        Die Balance ergibt sich aus der Blockchain-Historie.
        """
        balance = 0.0

        confirmed_transactions = self.get_confirmed_transactions()

        for tx in confirmed_transactions:
            # Normales Format aus deinem wallet.transaction.py:
            # {
            #   "sender": "...",
            #   "recipient": "...",
            #   "amount": 10,
            #   "timestamp": ...,
            #   "public_key": "...",
            #   "signature": "..."
            # }

            sender = tx.get("sender")
            recipient = tx.get("recipient")
            amount = float(tx.get("amount", 0))

            if recipient == address:
                balance += amount

            if sender == address:
                balance -= amount

        return balance

    def get_pending_spent_amount(self, address: str) -> float:
        """
        Berechnet, wie viele Coins eine Adresse bereits im Mempool ausgeben möchte.
        Das verhindert einfaches Double-Spending vor dem Mining.
        """
        spent = 0.0

        for tx in self.mempool:
            sender = tx.get("sender")
            amount = float(tx.get("amount", 0))

            if sender == address:
                spent += amount

        return spent

    def get_available_balance(self, address: str) -> float:
        """
        Balance minus bereits wartende Ausgaben im Mempool.
        """
        confirmed_balance = self.get_balance(address)
        pending_spent = self.get_pending_spent_amount(address)

        return confirmed_balance - pending_spent

    # --------------------------------------------------
    # TRANSAKTIONSVALIDIERUNG
    # --------------------------------------------------

    def validate_transaction_format(self, transaction: dict):
        """
        Prüft, ob alle wichtigen Felder vorhanden sind.
        """
        required_fields = [
            "sender",
            "recipient",
            "amount",
            "timestamp",
            "public_key",
            "signature",
        ]

        for field in required_fields:
            if field not in transaction:
                return False, f"Feld fehlt: {field}"

        return True, "Format ist gültig."

    def is_duplicate_transaction(self, transaction: dict) -> bool:
        """
        Prüft, ob die Transaktion bereits im Mempool liegt.
        """
        new_tx_id = self.get_transaction_id(transaction)

        for existing_tx in self.mempool:
            existing_tx_id = self.get_transaction_id(existing_tx)

            if existing_tx_id == new_tx_id:
                return True

        return False

    def validate_transaction(self, transaction: dict):
        """
        Komplette Prüfung einer Transaktion durch die Node.
        """
        format_valid, message = self.validate_transaction_format(transaction)

        if not format_valid:
            return False, message

        try:
            sender = transaction["sender"]
            recipient = transaction["recipient"]
            amount = float(transaction["amount"])

            if not sender:
                return False, "Sender fehlt."

            if not recipient:
                return False, "Empfänger fehlt."

            if amount <= 0:
                return False, "Betrag muss größer als 0 sein."

            if self.is_duplicate_transaction(transaction):
                return False, "Transaktion ist bereits im Mempool."

            if not verify_transaction(transaction):
                return False, "Signatur ist ungültig."

            if not self.public_key_matches_sender(transaction):
                return False, "Public Key passt nicht zur Sender-Adresse."

            available_balance = self.get_available_balance(sender)

            if available_balance < amount:
                return False, (
                    f"Nicht genug Coins. "
                    f"Verfügbar: {available_balance}, benötigt: {amount}"
                )

            return True, "Transaktion ist gültig."

        except ValueError:
            return False, "Amount ist keine gültige Zahl."

        except Exception as error:
            return False, f"Fehler bei der Validierung: {error}"

    def add_transaction_to_mempool(self, transaction: dict):
        """
        Validiert eine Transaktion und legt sie in den Mempool.
        """
        is_valid, message = self.validate_transaction(transaction)

        if not is_valid:
            return False, message

        self.mempool.append(transaction)

        return True, "Transaktion wurde in den Mempool aufgenommen."

    def remove_transactions_from_mempool(self, transactions):
        """
        Entfernt Transaktionen aus dem Mempool,
        wenn sie in einen Block aufgenommen wurden.
        """
        transaction_ids_to_remove = {
            self.get_transaction_id(tx) for tx in transactions
        }

        self.mempool = [
            tx for tx in self.mempool
            if self.get_transaction_id(tx) not in transaction_ids_to_remove
        ]

    # --------------------------------------------------
    # PEER-TO-PEER
    # --------------------------------------------------

    def add_peer(self, peer_url: str):
        """
        Fügt eine andere Node hinzu.
        Beispiel:
        http://127.0.0.1:5001
        """
        self.peers.add(peer_url)

    def broadcast_transaction(self, transaction: dict):
        """
        Sendet eine Transaktion an alle bekannten Peers.
        """
        for peer in self.peers:
            try:
                requests.post(
                    f"{peer}/receive_transaction",
                    json=transaction,
                    timeout=3
                )
            except requests.RequestException:
                print(f"[{self.node_name}] Peer nicht erreichbar: {peer}")

    def broadcast_block(self, block):
        """
        Sendet einen Block an alle bekannten Peers.
        Der Block kommt normalerweise aus blockchain.py.
        """
        if hasattr(block, "to_dict"):
            block_data = block.to_dict()
        else:
            block_data = block

        for peer in self.peers:
            try:
                requests.post(
                    f"{peer}/receive_block",
                    json=block_data,
                    timeout=3
                )
            except requests.RequestException:
                print(f"[{self.node_name}] Peer nicht erreichbar: {peer}")

    # --------------------------------------------------
    # BLOCK-ÜBERGABE AN BLOCKCHAIN
    # --------------------------------------------------

    def add_received_block(self, block_data: dict):
        """
        Übergibt einen empfangenen Block an blockchain.py.
        Die Node macht nicht selbst die komplette Blockprüfung.
        Sie delegiert an die Blockchain-Klasse.
        """
        if self.blockchain is None:
            return False, "Keine Blockchain mit dieser Node verbunden."

        if not hasattr(self.blockchain, "add_block"):
            return False, "Blockchain hat keine add_block()-Methode."

        accepted = self.blockchain.add_block(block_data)

        if accepted:
            transactions = block_data.get("transactions", [])
            self.remove_transactions_from_mempool(transactions)

            return True, "Block wurde akzeptiert und Mempool aktualisiert."

        return False, "Block wurde von der Blockchain abgelehnt."

    # --------------------------------------------------
    # ROUTES / API
    # --------------------------------------------------

    def setup_routes(self):

        @self.app.route("/status", methods=["GET"])
        def status():
            chain_length = None

            if self.blockchain is not None and hasattr(self.blockchain, "chain"):
                chain_length = len(self.blockchain.chain)

            return jsonify({
                "node_name": self.node_name,
                "port": self.port,
                "peers": list(self.peers),
                "mempool_size": len(self.mempool),
                "chain_length": chain_length,
            })

        @self.app.route("/mempool", methods=["GET"])
        def get_mempool():
            return jsonify({
                "mempool_size": len(self.mempool),
                "mempool": self.mempool,
            })

        @self.app.route("/balance/<address>", methods=["GET"])
        def get_balance_route(address):
            return jsonify({
                "address": address,
                "confirmed_balance": self.get_balance(address),
                "pending_spent": self.get_pending_spent_amount(address),
                "available_balance": self.get_available_balance(address),
            })

        @self.app.route("/receive_transaction", methods=["POST"])
        def receive_transaction_route():
            transaction = request.get_json()

            accepted, message = self.add_transaction_to_mempool(transaction)

            print(f"[{self.node_name}] Neue Transaktion: {message}")

            return jsonify({
                "accepted": accepted,
                "message": message,
                "mempool_size": len(self.mempool),
            })

        @self.app.route("/submit_transaction", methods=["POST"])
        def submit_transaction_route():
            """
            Diese Route ist für eine Wallet oder ein Frontend gedacht.
            Unterschied zu receive_transaction:
            Wenn akzeptiert, wird die Transaktion auch an Peers weitergeleitet.
            """
            transaction = request.get_json()

            accepted, message = self.add_transaction_to_mempool(transaction)

            if accepted:
                self.broadcast_transaction(transaction)

            return jsonify({
                "accepted": accepted,
                "message": message,
                "mempool_size": len(self.mempool),
            })

        @self.app.route("/add_peer", methods=["POST"])
        def add_peer_route():
            data = request.get_json()
            peer = data.get("peer")

            if not peer:
                return jsonify({"message": "Peer fehlt."}), 400

            self.add_peer(peer)

            return jsonify({
                "message": "Peer hinzugefügt.",
                "peers": list(self.peers),
            })

        @self.app.route("/peers", methods=["GET"])
        def get_peers():
            return jsonify({
                "peers": list(self.peers),
            })

        @self.app.route("/receive_block", methods=["POST"])
        def receive_block_route():
            block_data = request.get_json()

            accepted, message = self.add_received_block(block_data)

            return jsonify({
                "accepted": accepted,
                "message": message,
            }), 200 if accepted else 400

        @self.app.route("/chain", methods=["GET"])
        def get_chain_route():
            """
            Gibt die Blockchain aus, falls eine Blockchain verbunden ist.
            """
            if self.blockchain is None:
                return jsonify({
                    "message": "Keine Blockchain verbunden."
                }), 400

            if not hasattr(self.blockchain, "chain"):
                return jsonify({
                    "message": "Blockchain hat keine chain."
                }), 400

            chain_data = []

            for block in self.blockchain.chain:
                if hasattr(block, "to_dict"):
                    chain_data.append(block.to_dict())
                elif isinstance(block, dict):
                    chain_data.append(block)
                else:
                    chain_data.append(block.__dict__)

            return jsonify({
                "length": len(chain_data),
                "chain": chain_data,
            })

    def run(self, debug=False):
        print(f"Starte Node '{self.node_name}' auf Port {self.port}...")
        self.app.run(host="0.0.0.0", port=self.port, debug=debug)
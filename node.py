import json
from base64 import b64encode
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from flask import Flask, jsonify, request


class Node:

    def __init__(self, node_name, port):
        self.node_name = node_name
        self.port = port
        self.app = Flask(node_name)

        # 1. Jede Node generiert ihr eigenes Schlüsselpaar (Wallet)
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.verifying_key

        # Der Public Key (als Hex-String) ist gleichzeitig die Adresse
        self.wallet_address = self.public_key.to_string().hex()

        self.mempool = []  # Der lokale Warteraum für Transaktionen
        self.setup_routes()

    def setup_routes(self):

        # Route, um Transaktionen von anderen Nodes zu empfangen
        @self.app.route("/receive_transaction", methods=["POST"])
        def receive_tx():
            tx_data = request.get_json()

            # Hier würde die mathematische Prüfung stattfinden (Verif)
            # Wenn valide, ab in den Mempool
            self.mempool.append(tx_data)
            print(
                f"[{self.node_name}] Neue Transaktion im Mempool! Größe: {len(self.mempool)}"
            )
            return jsonify({"status": "accepted", "mempool_size": len(self.mempool)})

    # 2. Die Wallet-Funktion zum VERSCHICKEN von Bitcoin
    def send_transaction(self, recipient_address, amount):
        # Das unverschlüsselte Datenpaket (Nachricht)
        tx_body = {
            "sender": self.wallet_address,
            "recipient": recipient_address,
            "amount": amount,
        }

        # Nachricht für die Signierung in Bytes umwandeln
        tx_bytes = json.dumps(tx_body, sort_keys=True).encode()

        # Mit dem eigenen Private Key signieren
        signature = self.private_key.sign(tx_bytes)

        # Das fertige Paket zum Senden (inklusive Signatur & Public Key für die Nodes)
        complete_transaction = {
            "body": tx_body,
            "signature": b64encode(signature).decode(
                "utf-8"
            ),  # Für JSON lesbar machen
            "sender_public_key": self.wallet_address,
        }

        return complete_transaction
    
        # Füge diese Methode einfach unten in deine Node-Klasse ein:

    def run(self, debug=False):
        print(f"🚀 Starte {self.node_name} auf Port {self.port}...")
        # Hier wird der Port an Flask übergeben und nach außen geöffnet (exposed)
        self.app.run(host="0.0.0.0", port=self.port, debug=debug)
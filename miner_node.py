"""
miner_node.py
=============
MinerNode – erbt von Node, ergänzt Mining-Loop.
Holt TXs aus dem Mempool, mint einen Block, broadcastet ihn.
"""

import threading
import time

from node import Node
from blockchain_core import Block
from consensus import mine_block, create_coinbase_tx, adjust_difficulty
from p2p import sync_chain


class MinerNode(Node):
    def __init__(self, node_name: str, port: int, blockchain, miner_address: str, wallet=None):
        super().__init__(node_name=node_name, port=port, blockchain=blockchain, wallet=wallet)
        self.miner_address = miner_address   # Adresse die den Block-Reward bekommt
        self.mining        = False
        self._setup_miner_routes()

    # --------------------------------------------------
    # MINING
    # --------------------------------------------------

    def mine_next_block(self) -> Block | None:
        """
        Holt TXs aus dem Mempool, hängt Coinbase-TX an,
        mint den Block und gibt ihn zurück.
        """
        # Zuerst mit Peers synchronisieren (längste Chain gewinnt)
        sync_chain(self)

        # Coinbase-TX (Mining-Reward) + Mempool-TXs
        coinbase = create_coinbase_tx(self.miner_address)

        from transaction import Transaction
        mempool_txs = [Transaction.from_dict(tx) for tx in self.mempool]
        transactions = [coinbase] + mempool_txs

        # Neuen Block vorbereiten
        candidate = Block(
            index         = len(self.blockchain.chain),
            transactions  = transactions,
            previous_hash = self.blockchain.last_block.hash,
            difficulty    = self.blockchain.difficulty,   # ← aktuelle Difficulty
        )

        # PoW – das eigentliche Mining
        mined_block = mine_block(candidate, self.blockchain.difficulty)

        # Block an eigene Blockchain übergeben
        accepted = self.blockchain.add_block(mined_block)

        if accepted:
            # Geminte TXs aus Mempool entfernen
            self.remove_transactions_from_mempool(self.mempool.copy())
            # Block an alle Peers broadcasten
            self.broadcast_block(mined_block)
            print(f"[{self.node_name}] Block #{mined_block.index} gemint und gesendet ✅")
            return mined_block

        print(f"[{self.node_name}] Geminter Block abgelehnt ❌")
        return None

    def start_mining_loop(self, interval: float = 0.0):
        """
        Startet den Mining-Loop in einem Background-Thread.
        interval: Pause zwischen Blöcken in Sekunden (0 = sofort wieder minen).
        """
        self.mining = True

        def loop():
            while self.mining:
                self.mine_next_block()
                if interval > 0:
                    time.sleep(interval)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        print(f"[{self.node_name}] Mining-Loop gestartet (Miner: {self.miner_address[:20]}...)")

    def stop_mining_loop(self):
        self.mining = False
        print(f"[{self.node_name}] Mining gestoppt.")

    # --------------------------------------------------
    # ZUSÄTZLICHE ROUTES
    # --------------------------------------------------

    def _setup_miner_routes(self):

        @self.app.route("/mine", methods=["POST"])
        def mine_once():
            """Mined manuell einen Block (z.B. aus dem Frontend auslösen)."""
            from flask import jsonify
            block = self.mine_next_block()
            if block:
                return jsonify({
                    "message": "Block gemint.",
                    "block":   block.to_dict(),
                })
            return jsonify({"message": "Mining fehlgeschlagen."}), 500

        @self.app.route("/mining/start", methods=["POST"])
        def start_mining():
            from flask import jsonify
            self.start_mining_loop()
            return jsonify({"message": "Mining-Loop gestartet."})

        @self.app.route("/mining/stop", methods=["POST"])
        def stop_mining():
            from flask import jsonify
            self.stop_mining_loop()
            return jsonify({"message": "Mining gestoppt."})

        @self.app.route("/mining/status", methods=["GET"])
        def mining_status():
            from flask import jsonify
            return jsonify({
                "mining":     self.mining,
                "difficulty": self.blockchain.difficulty,
                "miner":      self.miner_address,
                "reward":     50.0,
            })
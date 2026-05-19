"""
Blockchain MVP mit eigenem Coin
- Blocks
- Proof of Work Mining
- Mempool
- Coinbase Reward
- einfache Balance-Berechnung
"""

import hashlib
import json
from datetime import datetime
from typing import Any


MINING_REWARD = 50


class Block:
    def __init__(self, index: int, data: list[dict[str, Any]] | str, previous_hash: str):
        self.index = index
        self.timestamp = datetime.utcnow().isoformat()
        self.data = data  # bei euch: Liste von Transaktionen
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_content = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "data": self.data,
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_content.encode()).hexdigest()

    def __repr__(self) -> str:
        return (
            f"\n┌─ Block #{self.index} ─────────────────────────────────\n"
            f"│  Timestamp    : {self.timestamp}\n"
            f"│  Nonce        : {self.nonce}\n"
            f"│  Data         : {self.data}\n"
            f"│  Previous Hash: {self.previous_hash[:20]}...\n"
            f"│  Hash         : {self.hash[:20]}...\n"
            f"└──────────────────────────────────────────────────"
        )


class Mempool:
    def __init__(self):
        self.pending_transactions: list[dict[str, Any]] = []

    def add_transaction(self, transaction: dict[str, Any]) -> None:
        self.pending_transactions.append(transaction)

    def get_pending_transactions(self) -> list[dict[str, Any]]:
        return self.pending_transactions.copy()

    def clear(self) -> None:
        self.pending_transactions.clear()


class Blockchain:
    def __init__(self, difficulty: int = 3):
        self.chain: list[Block] = []
        self.mempool = Mempool()
        self.difficulty = difficulty
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        genesis = Block(
            index=0,
            data="Genesis Block",
            previous_hash="0" * 64,
        )
        self.chain.append(genesis)
        print(f"[Blockchain] Genesis Block erstellt: {genesis.hash[:20]}...")

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    # ─────────────────────────────────────────────
    # Transaktionen & Coin-Logik
    # ─────────────────────────────────────────────

    def create_transaction(self, sender: str, recipient: str, amount: float) -> bool:
        transaction = {
            "type": "TRANSFER",
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        }

        if not self.is_valid_transaction(transaction):
            print("[Mempool] ❌ Transaktion ungültig")
            return False

        self.mempool.add_transaction(transaction)
        print(f"[Mempool] ✅ Transaktion hinzugefügt: {sender} -> {recipient}: {amount}")
        return True

    def create_coinbase_transaction(self, miner_address: str) -> dict[str, Any]:
        return {
            "type": "COINBASE",
            "sender": "SYSTEM",
            "recipient": miner_address,
            "amount": MINING_REWARD,
        }

    def get_balance(self, address: str) -> float:
        balance = 0.0

        for block in self.chain:
            if not isinstance(block.data, list):
                continue

            for tx in block.data:
                if tx.get("sender") == address:
                    balance -= float(tx.get("amount", 0))
                if tx.get("recipient") == address:
                    balance += float(tx.get("amount", 0))

        return balance

    def is_valid_transaction(self, transaction: dict[str, Any]) -> bool:
        required_fields = {"type", "sender", "recipient", "amount"}
        if not required_fields.issubset(transaction.keys()):
            return False

        if transaction["amount"] <= 0:
            return False

        # Coinbase darf Coins erzeugen, normale Transfers nicht.
        if transaction["type"] == "COINBASE":
            return transaction["sender"] == "SYSTEM"

        sender_balance = self.get_balance(transaction["sender"])
        return sender_balance >= transaction["amount"]

    # ─────────────────────────────────────────────
    # Proof of Work & Mining
    # ─────────────────────────────────────────────

    def is_valid_proof(self, block_hash: str) -> bool:
        return block_hash.startswith("0" * self.difficulty)

    def mine_block(self, block: Block) -> Block:
        print(f"[Mining] Starte Mining für Block #{block.index}...")

        while True:
            block.hash = block.compute_hash()

            if self.is_valid_proof(block.hash):
                print(f"[Mining] ✅ Block gefunden: {block.hash}")
                return block

            block.nonce += 1

    def mine_pending_transactions(self, miner_address: str) -> Block:
        coinbase_tx = self.create_coinbase_transaction(miner_address)
        transactions = [coinbase_tx] + self.mempool.get_pending_transactions()

        # Sicherheit: Nur gültige Transaktionen in den Block lassen.
        for tx in transactions:
            if not self.is_valid_transaction(tx):
                raise ValueError(f"Ungültige Transaktion im Mempool: {tx}")

        new_block = Block(
            index=len(self.chain),
            data=transactions,
            previous_hash=self.last_block.hash,
        )

        mined_block = self.mine_block(new_block)

        if not self.validate_block(mined_block, self.last_block):
            raise ValueError("Geminter Block ist ungültig")

        self.chain.append(mined_block)
        self.mempool.clear()
        return mined_block

    def validate_block(self, block: Block, previous_block: Block) -> bool:
        if block.previous_hash != previous_block.hash:
            print(f"[Validation] ❌ Block #{block.index}: previous_hash falsch")
            return False

        if block.hash != block.compute_hash():
            print(f"[Validation] ❌ Block #{block.index}: Hash falsch")
            return False

        if not self.is_valid_proof(block.hash):
            print(f"[Validation] ❌ Block #{block.index}: Proof of Work fehlt")
            return False

        if isinstance(block.data, list):
            for tx in block.data:
                # Bei historischer Chain müsste man Balances vor dem Block prüfen.
                # Für MVP reicht hier Formatprüfung + Coinbase-Regel.
                if tx.get("amount", 0) <= 0:
                    return False

        return True

    def is_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if not self.validate_block(current, previous):
                return False

        return True

    def __repr__(self) -> str:
        return "".join(str(block) for block in self.chain)

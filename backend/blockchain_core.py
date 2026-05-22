"""
blockchain_core.py
==================
Block, Blockchain, Genesis Block mit Coinbase-TX.
add_block() prüft jetzt Proof of Work.
"""

import hashlib
import json
from datetime import datetime, timezone

from transaction import Transaction

FOUNDER_ADDRESS = "FOUNDER_PLACEHOLDER_REPLACE_AFTER_WALLET"
GENESIS_REWARD  = 1_000_000


# ─────────────────────────────────────────────
#  BLOCK
# ─────────────────────────────────────────────

class Block:
    def __init__(
        self,
        index: int,
        transactions: list,
        previous_hash: str,
        nonce: int = 0,
        timestamp: str = "",
        difficulty: int = 3,   # ← hinzufügen
    ):
        self.index         = index
        self.transactions  = transactions
        self.previous_hash = previous_hash
        self.nonce         = nonce
        self.timestamp     = timestamp or datetime.now(timezone.utc).isoformat()
        self.hash          = self.compute_hash()
        self.difficulty    = difficulty 

    def compute_hash(self) -> str:
        block_content = json.dumps({
            "index":         self.index,
            "timestamp":     self.timestamp,
            "transactions":  [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(block_content.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "index":         self.index,
            "timestamp":     self.timestamp,
            "transactions":  [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
            "hash":          self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        transactions = [Transaction.from_dict(tx) for tx in data.get("transactions", [])]
        block = cls(
            index         = data["index"],
            transactions  = transactions,
            previous_hash = data["previous_hash"],
            nonce         = data.get("nonce", 0),
            timestamp     = data.get("timestamp", ""),
        )
        block.hash = data.get("hash", block.compute_hash())
        return block

    def __repr__(self) -> str:
        tx_lines = "\n".join(f"│    {tx}" for tx in self.transactions)
        return (
            f"\n┌─ Block #{self.index} ─────────────────────────────────\n"
            f"│  Timestamp    : {self.timestamp}\n"
            f"│  Transaktionen:\n{tx_lines}\n"
            f"│  Nonce        : {self.nonce}\n"
            f"│  Previous Hash: {self.previous_hash[:20]}...\n"
            f"│  Hash         : {self.hash[:20]}...\n"
            f"└──────────────────────────────────────────────────"
        )


# ─────────────────────────────────────────────
#  BLOCKCHAIN
# ─────────────────────────────────────────────

class Blockchain:
    def __init__(self, founder_address: str = FOUNDER_ADDRESS, difficulty: int = 3):
        self.chain:      list[Block] = []
        self.difficulty              = difficulty
        self.founder_address         = founder_address
        self._create_genesis_block()

    def _create_genesis_block(self):
        coinbase = Transaction(
            sender    = "COINBASE",
            recipient = self.founder_address,
            amount    = GENESIS_REWARD,
            timestamp = "2026-01-01T00:00:00+00:00", 
        )
        genesis = Block(
            index         = 0,
            transactions  = [coinbase],
            previous_hash = "0" * 64,
            timestamp     = "2026-01-01T00:00:00+00:00",  # ← fest!
            difficulty    = self.difficulty,
    )        # Genesis Block muss auch PoW erfüllen
        from consensus import mine_block
        genesis = mine_block(genesis, self.difficulty)
        self.chain.append(genesis)
        print(f"[Blockchain] Genesis Block | {GENESIS_REWARD:,} Coins → {self.founder_address[:24]}...")

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, block_data, skip_pow_check: bool = False) -> bool:
        """
        Nimmt Block als Objekt oder dict entgegen.
        Prüft: previous_hash, Hash-Integrität, PoW.
        skip_pow_check=True nur für Tests ohne Mining.
        """
        if isinstance(block_data, dict):
            block = Block.from_dict(block_data)
        elif isinstance(block_data, Block):
            block = block_data
        else:
            print("[Blockchain] add_block: unbekannter Typ")
            return False

        if block.previous_hash != self.last_block.hash:
            print(f"[Blockchain] Block #{block.index} abgelehnt: previous_hash stimmt nicht")
            return False

        if block.hash != block.compute_hash():
            print(f"[Blockchain] Block #{block.index} abgelehnt: Hash ungültig")
            return False

        if not skip_pow_check and not block.hash.startswith("0" * self.difficulty):
            print(f"[Blockchain] Block #{block.index} abgelehnt: PoW nicht erfüllt")
            return False

        # Difficulty nach jedem Block ggf. anpassen
        from consensus import adjust_difficulty
        self.difficulty = adjust_difficulty(self.chain, self.difficulty)

        self.chain.append(block)
        print(f"[Blockchain] Block #{block.index} akzeptiert | {len(block.transactions)} TX(s)")
        return True

    def get_balance(self, address: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        return balance

    def is_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current  = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                print(f"[Validation] ❌ Block #{i}: Hash ungültig")
                return False

            if current.previous_hash != previous.hash:
                print(f"[Validation] ❌ Block #{i}: Verkettung gebrochen")
                return False

            if not current.hash.startswith("0" * self.difficulty):
                print(f"[Validation] ❌ Block #{i}: PoW nicht erfüllt")
                return False

            coinbase_count = sum(1 for tx in current.transactions if tx.is_coinbase())
            if coinbase_count > 1:
                print(f"[Validation] ❌ Block #{i}: mehr als eine Coinbase-TX")
                return False

        return True

    def __repr__(self) -> str:
        return "".join(str(block) for block in self.chain)
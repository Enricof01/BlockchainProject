"""
blockchain_core.py
==================
Phase 1 - Blockchain Fundament
Enthält: Transaction, Block, Blockchain, Genesis Block mit Coinbase-TX
"""

import hashlib
import json
from datetime import datetime, timezone


# ─────────────────────────────────────────────
#  TRANSACTION
#  Wird später nach transaction.py ausgelagert
# ─────────────────────────────────────────────

class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float, signature: str = ""):
        self.sender    = sender       # Public-Key-Adresse oder "COINBASE"
        self.recipient = recipient    # Public-Key-Adresse des Empfängers
        self.amount    = amount
        self.signature = signature    # wird in Phase Wallet befüllt (ECDSA)
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "sender":    self.sender,
            "recipient": self.recipient,
            "amount":    self.amount,
            "timestamp": self.timestamp,
        }

    def compute_hash(self) -> str:
        """TX-Hash (ohne Signatur) – wird später für ECDSA-Signierung gebraucht."""
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()

    def is_coinbase(self) -> bool:
        return self.sender == "COINBASE"

    def __repr__(self) -> str:
        tag = "[COINBASE]" if self.is_coinbase() else ""
        return f"TX {tag} {self.sender[:12]}... → {self.recipient[:12]}... | {self.amount} Coins"


# ─────────────────────────────────────────────
#  BLOCK
# ─────────────────────────────────────────────

class Block:
    def __init__(self, index: int, transactions: list, previous_hash: str):
        self.index        = index
        self.timestamp    = datetime.now(timezone.utc).isoformat()
        self.transactions = transactions   # list[Transaction]
        self.previous_hash = previous_hash
        self.nonce        = 0              # Proof of Work (Phase 3)
        self.hash         = self.compute_hash()

    def compute_hash(self) -> str:
        """SHA-256 über alle Felder inklusive serialisierter Transaktionen."""
        block_content = json.dumps({
            "index":         self.index,
            "timestamp":     self.timestamp,
            "transactions":  [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(block_content.encode()).hexdigest()

    def __repr__(self) -> str:
        tx_lines = "\n".join(f"│    {tx}" for tx in self.transactions)
        return (
            f"\n┌─ Block #{self.index} ─────────────────────────────────\n"
            f"│  Timestamp    : {self.timestamp}\n"
            f"│  Transaktionen:\n{tx_lines}\n"
            f"│  Previous Hash: {self.previous_hash[:20]}...\n"
            f"│  Hash         : {self.hash[:20]}...\n"
            f"└──────────────────────────────────────────────────"
        )


# ─────────────────────────────────────────────
#  BLOCKCHAIN
# ─────────────────────────────────────────────

# Founder-Adresse: wird ersetzt sobald Wallet-Modul fertig ist
# → dann: from wallet import Wallet; FOUNDER_ADDRESS = Wallet().address
FOUNDER_ADDRESS = "FOUNDER_PLACEHOLDER_REPLACE_AFTER_WALLET"
GENESIS_REWARD  = 1_000_000  # initiale Coins


class Blockchain:
    def __init__(self):
        self.chain: list[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """
        Genesis Block mit Coinbase-Transaktion.
        Sender = 'COINBASE' (keine echte Adresse nötig).
        Empfänger = FOUNDER_ADDRESS bekommt die initialen Coins.
        """
        coinbase_tx = Transaction(
            sender    = "COINBASE",
            recipient = FOUNDER_ADDRESS,
            amount    = GENESIS_REWARD,
        )
        genesis = Block(
            index        = 0,
            transactions = [coinbase_tx],
            previous_hash = "0" * 64,
        )
        self.chain.append(genesis)
        print(f"[Blockchain] Genesis Block erstellt | {GENESIS_REWARD:,} Coins → {FOUNDER_ADDRESS[:20]}...")

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, transactions: list) -> Block:
        """Hängt einen neuen Block mit einer Liste von Transaktionen an."""
        new_block = Block(
            index         = len(self.chain),
            transactions  = transactions,
            previous_hash = self.last_block.hash,
        )
        self.chain.append(new_block)
        return new_block

    def get_balance(self, address: str) -> float:
        """
        Berechnet den Kontostand einer Adresse
        indem alle Transaktionen aller Blöcke gescannt werden.
        """
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        return balance

    def is_valid(self) -> bool:
        """
        Prüft die gesamte Chain:
        1. Hash jedes Blocks korrekt?
        2. Verkettung (previous_hash) intakt?
        3. Kein doppelter Coinbase (außer Genesis)?
        """
        for i in range(1, len(self.chain)):
            current  = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                print(f"[Validation] ❌ Block #{i}: Hash ungültig!")
                return False

            if current.previous_hash != previous.hash:
                print(f"[Validation] ❌ Block #{i}: Verkettung gebrochen!")
                return False

            # Kein Coinbase erlaubt außer im Genesis Block
            for tx in current.transactions:
                if tx.is_coinbase():
                    print(f"[Validation] ❌ Block #{i}: unerlaubte Coinbase-TX!")
                    return False

        return True

    def __repr__(self) -> str:
        return "".join(str(block) for block in self.chain)


# ─────────────────────────────────────────────
#  CLI / DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 52)
    print("  Blockchain Demo - Phase 1 (mit Transaktionen)")
    print("=" * 52)

    bc = Blockchain()

    # Transaktionen simulieren
    tx1 = Transaction(sender=FOUNDER_ADDRESS, recipient="alice_adresse_xyz", amount=100)
    tx2 = Transaction(sender="alice_adresse_xyz", recipient="bob_adresse_abc", amount=30)

    bc.add_block([tx1])
    bc.add_block([tx2])

    print(bc)

    # Kontostand prüfen
    print("\n[Balances]")
    print(f"  Founder : {bc.get_balance(FOUNDER_ADDRESS):>10,.2f} Coins")
    print(f"  Alice   : {bc.get_balance('alice_adresse_xyz'):>10,.2f} Coins")
    print(f"  Bob     : {bc.get_balance('bob_adresse_abc'):>10,.2f} Coins")

    # Validierung
    print("\n[Test 1] Chain-Validierung:")
    print("  Ergebnis:", "✅ Gültig" if bc.is_valid() else "❌ Ungültig")

    # Manipulation simulieren
    print("\n[Test 2] Manipulation von Block #1:")
    bc.chain[1].transactions[0].amount = 9999
    bc.chain[1].hash = bc.chain[1].compute_hash()  # Hash neu berechnen = Angriff
    print("  Ergebnis:", "✅ Gültig" if bc.is_valid() else "❌ Manipulation erkannt!")
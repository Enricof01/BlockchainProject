"""
blockchain_core.py
==================
Phase 1 - Blockchain Fundament
Enthält: Block, Blockchain, Genesis Block, CLI-Test
"""

import hashlib
import json
from datetime import datetime


# ─────────────────────────────────────────────
#  BLOCK
# ─────────────────────────────────────────────

class Block:
    def __init__(self, index: int, data: str, previous_hash: str):
        self.index         = index
        self.timestamp     = datetime.utcnow().isoformat()
        self.data          = data          # später: Liste von Transaktionen
        self.previous_hash = previous_hash
        self.nonce         = 0             # wird für Proof of Work gebraucht (Phase 3)
        self.hash          = self.compute_hash()

    def compute_hash(self) -> str:
        """Erstellt den SHA-256 Hash des Blocks aus allen Feldern."""
        block_content = json.dumps({
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
        }, sort_keys=True)

        return hashlib.sha256(block_content.encode()).hexdigest()

    def __repr__(self) -> str:
        return (
            f"\n┌─ Block #{self.index} ─────────────────────────────────\n"
            f"│  Timestamp    : {self.timestamp}\n"
            f"│  Data         : {self.data}\n"
            f"│  Previous Hash: {self.previous_hash[:20]}...\n"
            f"│  Hash         : {self.hash[:20]}...\n"
            f"└──────────────────────────────────────────────────"
        )


# ─────────────────────────────────────────────
#  BLOCKCHAIN
# ─────────────────────────────────────────────

class Blockchain:
    def __init__(self):
        self.chain: list[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Der erste Block – hard-coded, kein vorheriger Hash."""
        genesis = Block(
            index=0,
            data="Genesis Block",
            previous_hash="0" * 64   # Platzhalter: 64 Nullen
        )
        self.chain.append(genesis)
        print(f"[Blockchain] Genesis Block erstellt: {genesis.hash[:20]}...")

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: str) -> Block:
        """Hängt einen neuen Block an die Chain."""
        new_block = Block(
            index=len(self.chain),
            data=data,
            previous_hash=self.last_block.hash
        )
        self.chain.append(new_block)
        return new_block

    def is_valid(self) -> bool:
        """
        Prüft die gesamte Chain auf Integrität:
        1. Hash jedes Blocks muss korrekt berechnet sein
        2. previous_hash muss mit Hash des Vorgängers übereinstimmen
        """
        for i in range(1, len(self.chain)):
            current  = self.chain[i]
            previous = self.chain[i - 1]

            # Wurde der Block nachträglich verändert?
            if current.hash != current.compute_hash():
                print(f"[Validation] ❌ Block #{i}: Hash ungültig!")
                return False

            # Stimmt die Verkettung?
            if current.previous_hash != previous.hash:
                print(f"[Validation] ❌ Block #{i}: Verkettung gebrochen!")
                return False

        return True

    def __repr__(self) -> str:
        return "".join(str(block) for block in self.chain)


# ─────────────────────────────────────────────
#  CLI / DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 52)
    print("  Blockchain Demo - Phase 1")
    print("=" * 52)

    bc = Blockchain()

    # Blöcke hinzufügen
    bc.add_block("TX: Alice sendet 10 Coins an Bob")
    bc.add_block("TX: Bob sendet 3 Coins an Carol")
    bc.add_block("TX: Carol sendet 1 Coin an Dave")

    # Chain ausgeben
    print(bc)

    # Validierung
    print("\n[Test 1] Chain-Validierung:")
    print("  Ergebnis:", "✅ Gültig" if bc.is_valid() else "❌ Ungültig")

    # Manipulation simulieren
    print("\n[Test 2] Manipulation von Block #1:")
    bc.chain[1].data = "TX: Alice sendet 9999 Coins an Hacker"
    print("  Ergebnis:", "✅ Gültig" if bc.is_valid() else "❌ Manipulation erkannt!")

    print("\nFertig. Nächster Schritt: Proof of Work (Phase 3) oder P2P-Netzwerk (Phase 2).")
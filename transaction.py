"""
transaction.py
==============
Transaction-Klasse – gemeinsame Datenstruktur für Node, Blockchain und Wallet.
Wird als dict über das Netzwerk übertragen, als Objekt intern verarbeitet.
"""

import hashlib
import json
from datetime import datetime, timezone


class Transaction:
    def __init__(
        self,
        sender: str,
        recipient: str,
        amount: float,
        public_key: str = "",
        signature: str = "",
        timestamp: str = "",
    ):
        self.sender     = sender        # Adresse oder "COINBASE"
        self.recipient  = recipient     # Adresse des Empfängers
        self.amount     = float(amount)
        self.public_key = public_key    # PEM-String, leer bei COINBASE
        self.signature  = signature     # ECDSA-Signatur, leer bis Wallet signiert
        self.timestamp  = timestamp or datetime.now(timezone.utc).isoformat()

    # ── Serialisierung ──────────────────────────────

    def to_dict(self) -> dict:
        """Vollständiges dict – wird über Netzwerk gesendet."""
        return {
            "sender":     self.sender,
            "recipient":  self.recipient,
            "amount":     self.amount,
            "timestamp":  self.timestamp,
            "public_key": self.public_key,
            "signature":  self.signature,
        }

    def to_signable_dict(self) -> dict:
        """Dict OHNE Signatur – wird für ECDSA-Signierung gehasht."""
        return {
            "sender":     self.sender,
            "recipient":  self.recipient,
            "amount":     self.amount,
            "timestamp":  self.timestamp,
            "public_key": self.public_key,
        }

    def compute_hash(self) -> str:
        """SHA-256 des signierbaren Dicts – Input für ECDSA."""
        return hashlib.sha256(
            json.dumps(self.to_signable_dict(), sort_keys=True).encode()
        ).hexdigest()

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Erstellt ein Transaction-Objekt aus einem dict (z.B. aus dem Netzwerk)."""
        return cls(
            sender     = data["sender"],
            recipient  = data["recipient"],
            amount     = float(data["amount"]),
            public_key = data.get("public_key", ""),
            signature  = data.get("signature", ""),
            timestamp  = data.get("timestamp", ""),
        )

    # ── Hilfsmethoden ───────────────────────────────

    def is_coinbase(self) -> bool:
        return self.sender == "COINBASE"

    def get_id(self) -> str:
        """Eindeutige TX-ID (über vollständiges dict inkl. Signatur)."""
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()

    def __repr__(self) -> str:
        tag = "[COINBASE] " if self.is_coinbase() else ""
        s = self.sender[:16] if len(self.sender) > 16 else self.sender
        r = self.recipient[:16] if len(self.recipient) > 16 else self.recipient
        return f"TX {tag}{s}... → {r}... | {self.amount} Coins"
"""
wallet/wallet.py
================
Wallet – ECDSA-Schlüsselpaar, Adresse, Signierung und Verifikation.
Nutzt secp256k1 (wie Bitcoin) via cryptography-Lib.
"""

import hashlib
import base58
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
   decode_dss_signature,
    encode_dss_signature,
)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


# ─────────────────────────────────────────────
#  ADRESS-ABLEITUNG
# ─────────────────────────────────────────────

def public_key_to_address(public_key) -> str:
    """
    Leitet eine Wallet-Adresse aus einem Public Key ab.
    Ablauf (vereinfacht nach Bitcoin):
      1. Public Key → DER-Bytes
      2. SHA-256 → RIPEMD-160  (= Hash160)
      3. Version-Byte voranstellen (0x00)
      4. Base58Check kodieren
    """
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    sha256_hash   = hashlib.sha256(pub_bytes).digest()
    ripemd160     = hashlib.new("ripemd160", sha256_hash).digest()
    versioned     = b"\x00" + ripemd160          # Mainnet-Prefix

    # Checksum = erste 4 Bytes von SHA256(SHA256(versioned))
    checksum      = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    address_bytes = versioned + checksum

    return base58.b58encode(address_bytes).decode("utf-8")


# ─────────────────────────────────────────────
#  SIGNIERUNG / VERIFIKATION
# ─────────────────────────────────────────────

def sign_transaction(private_key, tx_hash: str) -> str:
    """
    Signiert einen TX-Hash mit dem Private Key (ECDSA, SHA-256).
    Gibt die Signatur als Hex-String zurück.
    """
    signature = private_key.sign(
        tx_hash.encode(),
        ec.ECDSA(hashes.SHA256()),
    )
    return signature.hex()


def verify_transaction(transaction: dict) -> bool:
    """
    Prüft die ECDSA-Signatur einer Transaktion.
    Erwartet im dict: sender, recipient, amount, timestamp, public_key, signature.
    Coinbase-Transaktionen werden automatisch als gültig durchgelassen.
    """
    if transaction.get("sender") == "COINBASE":
        return True

    try:
        public_key_pem = transaction.get("public_key", "")
        signature_hex  = transaction.get("signature", "")

        if not public_key_pem or not signature_hex:
            return False

        public_key = serialization.load_pem_public_key(
            public_key_pem.encode("utf-8"),
            backend=default_backend(),
        )

        # Signierbares dict (ohne Signatur) – muss identisch mit Wallet.sign() sein
        import json
        signable = json.dumps({
            "sender":     transaction["sender"],
            "recipient":  transaction["recipient"],
            "amount":     float(transaction["amount"]),
            "timestamp":  transaction["timestamp"],
            "public_key": transaction["public_key"],
        }, sort_keys=True).encode()

        public_key.verify(
            bytes.fromhex(signature_hex),
            signable,
            ec.ECDSA(hashes.SHA256()),
        )
        return True

    except Exception:
        return False


# ─────────────────────────────────────────────
#  WALLET KLASSE
# ─────────────────────────────────────────────

class Wallet:
    def __init__(self, private_key=None):
        """
        Erstellt ein neues Wallet oder lädt ein bestehendes.
        private_key: ec.EllipticCurvePrivateKey (optional, für Import)
        """
        if private_key:
            self._private_key = private_key
        else:
            self._private_key = ec.generate_private_key(
                ec.SECP256K1(),
                default_backend(),
            )

        self._public_key = self._private_key.public_key()
        self.address     = public_key_to_address(self._public_key)

    # ── Key-Export ──────────────────────────────────

    @property
    def private_key_pem(self) -> str:
        """Private Key als PEM-String (GEHEIM halten, nie ins Repo!)."""
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

    @property
    def public_key_pem(self) -> str:
        """Public Key als PEM-String (kann geteilt werden)."""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    # ── Import ──────────────────────────────────────

    @classmethod
    def from_pem(cls, pem_string: str) -> "Wallet":
        """Lädt ein Wallet aus einem gespeicherten PEM-Private-Key."""
        private_key = serialization.load_pem_private_key(
            pem_string.encode("utf-8"),
            password=None,
            backend=default_backend(),
        )
        return cls(private_key=private_key)

    # ── Signierung ──────────────────────────────────

    def sign(self, tx_hash: str) -> str:
        """Signiert einen TX-Hash. Gibt Hex-String zurück."""
        return sign_transaction(self._private_key, tx_hash)

    def create_transaction(self, recipient: str, amount: float) -> dict:
        """
        Erstellt eine vollständig signierte Transaktion als dict.
        Direkt verwendbar für Node.add_transaction_to_mempool().
        """
        from datetime import datetime, timezone
        import json

        timestamp = datetime.now(timezone.utc).isoformat()

        # Signierbares dict (ohne Signatur)
        signable = json.dumps({
            "sender":     self.address,
            "recipient":  recipient,
            "amount":     float(amount),
            "timestamp":  timestamp,
            "public_key": self.public_key_pem,
        }, sort_keys=True).encode()

        signature = self._private_key.sign(
            signable,
            ec.ECDSA(hashes.SHA256()),
        ).hex()

        return {
            "sender":     self.address,
            "recipient":  recipient,
            "amount":     float(amount),
            "timestamp":  timestamp,
            "public_key": self.public_key_pem,
            "signature":  signature,
        }

    def __repr__(self) -> str:
        return f"Wallet(address={self.address})"
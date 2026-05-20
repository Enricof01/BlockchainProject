import hashlib
import base58
from cryptography.hazmat.primitives import serialization


def public_key_to_bytes(public_key) -> bytes:
    """
    Wandelt den Public Key in Bytes um.
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def public_key_to_address(public_key) -> str:
    """
    Erstellt aus einem Public Key eine einfache Wallet-Adresse.
    """
    public_key_bytes = public_key_to_bytes(public_key)

    sha256_hash = hashlib.sha256(public_key_bytes).digest()

    # Für unser Projekt reicht eine kurze Adresse aus den ersten 20 Bytes.
    short_hash = sha256_hash[:20]

    address = base58.b58encode(short_hash).decode("utf-8")

    return address

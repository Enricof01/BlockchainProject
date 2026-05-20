import json
import time
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature


def create_transaction_payload(sender: str, recipient: str, amount: float, timestamp: float) -> dict:
    """
    Das ist der Teil der Transaktion, der signiert wird.
    Die Signatur selbst darf hier NICHT enthalten sein.
    """
    return {
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
        "timestamp": timestamp
    }


def payload_to_bytes(payload: dict) -> bytes:
    """
    Wandelt den Payload stabil in Bytes um.
    sort_keys=True ist wichtig, damit die Reihenfolge immer gleich bleibt.
    """
    return json.dumps(payload, sort_keys=True).encode("utf-8")


def sign_transaction(private_key, sender: str, recipient: str, amount: float) -> dict:
    """
    Erstellt und signiert eine Transaktion.
    """
    timestamp = time.time()

    payload = create_transaction_payload(
        sender=sender,
        recipient=recipient,
        amount=amount,
        timestamp=timestamp
    )

    signature = private_key.sign(
        payload_to_bytes(payload),
        ec.ECDSA(hashes.SHA256())
    )

    public_key = private_key.public_key()

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    return {
        **payload,
        "public_key": public_key_pem,
        "signature": base64.b64encode(signature).decode("utf-8")
    }


def verify_transaction(transaction: dict) -> bool:
    """
    Prüft, ob die Signatur einer Transaktion gültig ist.
    """
    try:
        public_key = serialization.load_pem_public_key(
            transaction["public_key"].encode("utf-8")
        )

        signature = base64.b64decode(transaction["signature"])

        payload = create_transaction_payload(
            sender=transaction["sender"],
            recipient=transaction["recipient"],
            amount=transaction["amount"],
            timestamp=transaction["timestamp"]
        )

        public_key.verify(
            signature,
            payload_to_bytes(payload),
            ec.ECDSA(hashes.SHA256())
        )

        return True

    except InvalidSignature:
        return False
    except Exception:
        return False
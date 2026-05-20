from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


def generate_private_key():
    """
    Erstellt einen neuen privaten ECDSA-Key mit secp256k1.
    """
    return ec.generate_private_key(ec.SECP256K1())


def save_private_key(private_key, filename="wallet_private.pem"):
    """
    Speichert den privaten Key als PEM-Datei.
    """
    pem_data = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(filename, "wb") as file:
        file.write(pem_data)


def load_private_key(filename="wallet_private.pem"):
    """
    Lädt einen privaten Key aus einer PEM-Datei.
    """
    with open(filename, "rb") as file:
        return serialization.load_pem_private_key(
            file.read(),
            password=None
        )


def get_public_key(private_key):
    """
    Gibt den Public Key zu einem Private Key zurück.
    """
    return private_key.public_key()
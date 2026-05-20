import argparse
import json
import os
import time

from wallet.keys import generate_private_key, save_private_key, load_private_key
from wallet.address import public_key_to_address
from wallet.transaction import sign_transaction, verify_transaction


WALLET_DIR = "wallets"
TRANSACTION_DIR = "transactions"


def get_wallet_file(name: str) -> str:
    """
    Gibt den Dateipfad für eine Wallet zurück.
    Beispiel: wallets/alice_private.pem
    """
    os.makedirs(WALLET_DIR, exist_ok=True)
    return os.path.join(WALLET_DIR, f"{name}_private.pem")


def get_transaction_file(sender_name: str, recipient: str) -> str:
    """
    Gibt den Dateipfad für eine Transaktion zurück.
    Beispiel: transactions/transaction_alice_to_empfaenger_1710000000.json
    """
    os.makedirs(TRANSACTION_DIR, exist_ok=True)

    safe_recipient = recipient.replace("/", "_").replace("\\", "_")
    timestamp = int(time.time())

    filename = f"transaction_{sender_name}_to_{safe_recipient}_{timestamp}.json"

    return os.path.join(TRANSACTION_DIR, filename)


def create_wallet(name: str):
    wallet_file = get_wallet_file(name)

    if os.path.exists(wallet_file):
        print(f"Wallet '{name}' existiert bereits.")
        print(f"Datei: {wallet_file}")
        return

    private_key = generate_private_key()
    save_private_key(private_key, wallet_file)

    address = public_key_to_address(private_key.public_key())

    print(f"Wallet '{name}' wurde erstellt.")
    print("Adresse:", address)
    print("Private Key gespeichert in:", wallet_file)


def show_address(name: str):
    wallet_file = get_wallet_file(name)

    if not os.path.exists(wallet_file):
        print(f"Wallet '{name}' existiert nicht.")
        return

    private_key = load_private_key(wallet_file)
    address = public_key_to_address(private_key.public_key())

    print(f"Adresse von Wallet '{name}':")
    print(address)


def create_signed_transaction(sender_name: str, recipient: str, amount: float):
    sender_wallet_file = get_wallet_file(sender_name)

    if not os.path.exists(sender_wallet_file):
        print(f"Wallet '{sender_name}' existiert nicht.")
        return

    if amount <= 0:
        print("Der Betrag muss größer als 0 sein.")
        return

    private_key = load_private_key(sender_wallet_file)
    sender_address = public_key_to_address(private_key.public_key())

    transaction = sign_transaction(
        private_key=private_key,
        sender=sender_address,
        recipient=recipient,
        amount=amount
    )

    filename = get_transaction_file(sender_name, recipient)

    with open(filename, "w") as file:
        json.dump(transaction, file, indent=4)

    print("Transaktion wurde erstellt und signiert.")
    print("Von Wallet:", sender_name)
    print("Sender-Adresse:", sender_address)
    print("Empfänger-Adresse:", recipient)
    print("Betrag:", amount)
    print("Gespeichert in:", filename)


def verify_transaction_file(filename: str):
    if not os.path.exists(filename):
        print(f"Datei '{filename}' wurde nicht gefunden.")
        return

    with open(filename, "r") as file:
        transaction = json.load(file)

    is_valid = verify_transaction(transaction)

    if is_valid:
        print("Signatur ist gültig.")
    else:
        print("Signatur ist ungültig.")


def list_wallets():
    os.makedirs(WALLET_DIR, exist_ok=True)

    files = os.listdir(WALLET_DIR)
    wallet_files = [file for file in files if file.endswith("_private.pem")]

    if not wallet_files:
        print("Es wurden noch keine Wallets erstellt.")
        return

    print("Gespeicherte Wallets:")

    for wallet_file in wallet_files:
        name = wallet_file.replace("_private.pem", "")
        private_key = load_private_key(os.path.join(WALLET_DIR, wallet_file))
        address = public_key_to_address(private_key.public_key())

        print(f"- {name}: {address}")


def list_transactions():
    os.makedirs(TRANSACTION_DIR, exist_ok=True)

    files = os.listdir(TRANSACTION_DIR)
    transaction_files = [file for file in files if file.endswith(".json")]

    if not transaction_files:
        print("Es wurden noch keine Transaktionen erstellt.")
        return

    print("Gespeicherte Transaktionen:")

    for transaction_file in transaction_files:
        print(f"- {os.path.join(TRANSACTION_DIR, transaction_file)}")


def main():
    parser = argparse.ArgumentParser(description="Wallet CLI")

    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--name", required=True)

    address_parser = subparsers.add_parser("address")
    address_parser.add_argument("--name", required=True)

    send_parser = subparsers.add_parser("send")
    send_parser.add_argument("--from", dest="sender_name", required=True)
    send_parser.add_argument("--to", required=True)
    send_parser.add_argument("--amount", required=True, type=float)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--file", required=True)

    subparsers.add_parser("list")
    subparsers.add_parser("transactions")

    args = parser.parse_args()

    if args.command == "create":
        create_wallet(args.name)

    elif args.command == "address":
        show_address(args.name)

    elif args.command == "send":
        create_signed_transaction(args.sender_name, args.to, args.amount)

    elif args.command == "verify":
        verify_transaction_file(args.file)

    elif args.command == "list":
        list_wallets()

    elif args.command == "transactions":
        list_transactions()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
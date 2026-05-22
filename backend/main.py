"""
main.py
=======
Testet das komplette System:
Wallet → Blockchain → Node → Transaktionen → Validierung
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from wallet import Wallet, verify_transaction
from transaction import Transaction
from blockchain_core import Blockchain, Block


def separator(title: str):
    print(f"\n{'=' * 52}")
    print(f"  {title}")
    print('=' * 52)


def main():

    # ─────────────────────────────────────────────
    #  SCHRITT 1: Wallets erstellen
    # ─────────────────────────────────────────────
    separator("1. Wallets erstellen")

    founder = Wallet()
    alice   = Wallet()
    bob     = Wallet()

    print(f"  Founder : {founder.address}")
    print(f"  Alice   : {alice.address}")
    print(f"  Bob     : {bob.address}")

    # ─────────────────────────────────────────────
    #  SCHRITT 2: Blockchain starten
    # ─────────────────────────────────────────────
    separator("2. Blockchain starten (Genesis Block)")

    bc = Blockchain(founder_address=founder.address)
    print(bc)

    # ─────────────────────────────────────────────
    #  SCHRITT 3: Balances nach Genesis
    # ─────────────────────────────────────────────
    separator("3. Balances nach Genesis Block")

    print(f"  Founder : {bc.get_balance(founder.address):>12,.2f} Coins")
    print(f"  Alice   : {bc.get_balance(alice.address):>12,.2f} Coins")
    print(f"  Bob     : {bc.get_balance(bob.address):>12,.2f} Coins")

    # ─────────────────────────────────────────────
    #  SCHRITT 4: Founder → Alice (500 Coins)
    # ─────────────────────────────────────────────
    separator("4. Founder sendet 500 Coins an Alice")

    tx1_dict = founder.create_transaction(recipient=alice.address, amount=500)

    print(f"  Signatur gültig : {verify_transaction(tx1_dict)}")

    tx1 = Transaction.from_dict(tx1_dict)
    block1 = Block(
        index         = len(bc.chain),
        transactions  = [tx1],
        previous_hash = bc.last_block.hash,
    )
    bc.add_block(block1)
    print(bc.chain[-1])

    # ─────────────────────────────────────────────
    #  SCHRITT 5: Alice → Bob (200 Coins)
    # ─────────────────────────────────────────────
    separator("5. Alice sendet 200 Coins an Bob")

    tx2_dict = alice.create_transaction(recipient=bob.address, amount=200)

    print(f"  Signatur gültig : {verify_transaction(tx2_dict)}")

    tx2 = Transaction.from_dict(tx2_dict)
    block2 = Block(
        index         = len(bc.chain),
        transactions  = [tx2],
        previous_hash = bc.last_block.hash,
    )
    bc.add_block(block2)
    print(bc.chain[-1])

    # ─────────────────────────────────────────────
    #  SCHRITT 6: Mehrere TXs in einem Block
    # ─────────────────────────────────────────────
    separator("6. Mehrere TXs in einem Block")

    tx3_dict = founder.create_transaction(recipient=bob.address,   amount=1000)
    tx4_dict = bob.create_transaction(recipient=alice.address, amount=100)

    tx3 = Transaction.from_dict(tx3_dict)
    tx4 = Transaction.from_dict(tx4_dict)

    block3 = Block(
        index         = len(bc.chain),
        transactions  = [tx3, tx4],
        previous_hash = bc.last_block.hash,
    )
    bc.add_block(block3)
    print(bc.chain[-1])

    # ─────────────────────────────────────────────
    #  SCHRITT 7: Balances nach allen TXs
    # ─────────────────────────────────────────────
    separator("7. Balances nach allen Transaktionen")

    print(f"  Founder : {bc.get_balance(founder.address):>12,.2f} Coins")
    print(f"  Alice   : {bc.get_balance(alice.address):>12,.2f} Coins")
    print(f"  Bob     : {bc.get_balance(bob.address):>12,.2f} Coins")

    total = (
        bc.get_balance(founder.address) +
        bc.get_balance(alice.address) +
        bc.get_balance(bob.address)
    )
    print(f"\n  Gesamt (muss 1.000.000 sein): {total:,.2f} Coins  {'✅' if total == 1_000_000 else '❌'}")

    # ─────────────────────────────────────────────
    #  SCHRITT 8: Chain validieren
    # ─────────────────────────────────────────────
    separator("8. Chain-Validierung")

    result = bc.is_valid()
    print(f"  Ergebnis: {'✅ Gültig' if result else '❌ Ungültig'}")

    # ─────────────────────────────────────────────
    #  SCHRITT 9: Manipulationsversuch
    # ─────────────────────────────────────────────
    separator("9. Manipulationsversuch")

    print("  Ändere Block #1: Alice bekommt statt 500 → 99.999 Coins...")
    bc.chain[1].transactions[0].amount = 99_999
    result = bc.is_valid()
    print(f"  Ergebnis: {'✅ Gültig' if result else '❌ Manipulation erkannt!'}")

    # ─────────────────────────────────────────────
    #  SCHRITT 10: Wallet speichern & laden
    # ─────────────────────────────────────────────
    separator("10. Wallet speichern & laden (PEM)")

    pem = alice.private_key_pem
    alice_restored = Wallet.from_pem(pem)

    print(f"  Original-Adresse  : {alice.address}")
    print(f"  Restored-Adresse  : {alice_restored.address}")
    print(f"  Identisch         : {'✅' if alice.address == alice_restored.address else '❌'}")

    # TX mit wiederhergestelltem Wallet signieren
    tx_test_dict = alice_restored.create_transaction(recipient=bob.address, amount=10)
    print(f"  TX mit restored Wallet gültig: {'✅' if verify_transaction(tx_test_dict) else '❌'}")

    # ─────────────────────────────────────────────
    #  SCHRITT 11: Ungültige TX (gefälschte Signatur)
    # ─────────────────────────────────────────────
    separator("11. Sicherheitstest: gefälschte Signatur")

    fake_tx = founder.create_transaction(recipient=bob.address, amount=100)
    fake_tx["amount"] = 999_999   # Betrag nachträglich manipulieren
    print(f"  Manipulierte TX erkannt: {'✅' if not verify_transaction(fake_tx) else '❌'}")

    separator("Fertig ✅")
    print("  Nächste Schritte:")
    print("  → consensus.py  : Proof of Work, Mining-Loop")
    print("  → p2p.py        : Peer-Discovery, Broadcast")
    print("  → main_node.py  : Node starten und per HTTP testen")
    print()


if __name__ == "__main__":
    main()
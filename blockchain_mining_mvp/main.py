from blockchain import Blockchain


def main():
    # Difficulty 3 ist für eine lokale Demo schnell genug.
    blockchain = Blockchain(difficulty=3)

    chris = "CHRIS_WALLET"
    marvin = "MARVIN_WALLET"

    print("\n--- 1. Mining: Chris erzeugt neue Coins ---")
    blockchain.mine_pending_transactions(miner_address=chris)
    print("Chris Balance:", blockchain.get_balance(chris))

    print("\n--- 2. Chris sendet 10 Coins an Marvin ---")
    blockchain.create_transaction(sender=chris, recipient=marvin, amount=10)

    print("\n--- 3. Mining: offene Transaktion wird bestätigt ---")
    blockchain.mine_pending_transactions(miner_address=chris)

    print("\n--- Balances ---")
    print("Chris Balance:", blockchain.get_balance(chris))
    print("Marvin Balance:", blockchain.get_balance(marvin))

    print("\n--- Chain gültig? ---")
    print("✅ Ja" if blockchain.is_valid() else "❌ Nein")

    print("\n--- Blockchain ---")
    print(blockchain)


if __name__ == "__main__":
    main()

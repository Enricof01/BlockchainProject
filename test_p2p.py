"""
test_p2p.py
===========
Testet automatisch:
1. P2P Chain-Sync (longest chain rule)
2. Fork-Handling (zwei Miner gleichzeitig)
3. Double-Spend-Schutz

Voraussetzung: zwei Nodes laufen bereits
  Terminal 1: uv run main_node.py --type miner --port 5000 --name miner_1
  Terminal 2: uv run main_node.py --type miner --port 5001 --name miner_2 --peers http://127.0.0.1:5000
"""

import time
import requests
from wallet.wallet import Wallet

NODE_1 = "http://127.0.0.1:5001"
NODE_2 = "http://127.0.0.1:5002"


# ─────────────────────────────────────────────
#  HILFSFUNKTIONEN
# ─────────────────────────────────────────────

def separator(title: str):
    print(f"\n{'=' * 52}")
    print(f"  {title}")
    print('=' * 52)


def get_chain_length(node_url: str) -> int:
    try:
        r = requests.get(f"{node_url}/status", timeout=3)
        return r.json().get("chain_length", 0)
    except Exception:
        return -1


def get_balance(node_url: str, address: str) -> float:
    try:
        r = requests.get(f"{node_url}/balance/{address}", timeout=3)
        return r.json().get("confirmed_balance", 0.0)
    except Exception:
        return 0.0


def get_mempool_size(node_url: str) -> int:
    try:
        r = requests.get(f"{node_url}/mempool", timeout=3)
        return r.json().get("mempool_size", 0)
    except Exception:
        return -1


def mine_block(node_url: str) -> bool:
    try:
        r = requests.post(f"{node_url}/mine", timeout=60)
        return r.status_code == 200
    except Exception:
        return False


def submit_tx(node_url: str, tx: dict) -> tuple[bool, str]:
    try:
        r = requests.post(
            f"{node_url}/submit_transaction",
            json=tx,
            timeout=5,
        )
        data = r.json()
        return data.get("accepted", False), data.get("message", "")
    except Exception as e:
        return False, str(e)


def check_nodes_reachable():
    for url in [NODE_1, NODE_2]:
        try:
            requests.get(f"{url}/status", timeout=2)
        except Exception:
            print(f"❌ Node nicht erreichbar: {url}")
            print("   Starte zuerst:")
            print("   Terminal 1: uv run main_node.py --type miner --port 5000 --name miner_1")
            print("   Terminal 2: uv run main_node.py --type miner --port 5001 --name miner_2 --peers http://127.0.0.1:5000")
            exit(1)
    print("✅ Beide Nodes erreichbar")


# ─────────────────────────────────────────────
#  TEST 1: P2P CHAIN-SYNC
# ─────────────────────────────────────────────

def test_chain_sync():
    separator("TEST 1: P2P Chain-Sync (Longest Chain Rule)")

    len1_before = get_chain_length(NODE_1)
    len2_before = get_chain_length(NODE_2)
    print(f"  Chain-Länge vorher → Node 1: {len1_before} | Node 2: {len2_before}")

    # Node 1 mined 2 Blöcke
    print("\n  Node 1 mined 2 Blöcke...")
    mine_block(NODE_1)
    mine_block(NODE_1)

    len1_after = get_chain_length(NODE_1)
    print(f"  Node 1 Chain-Länge jetzt: {len1_after}")

    # Node 2 sync triggern
    print("\n  Node 2 sync triggern (POST /wallet/sync oder manuell mine)...")
    try:
        requests.post(f"{NODE_2}/sync", timeout=5)
    except Exception:
        pass

    # kurz warten
    time.sleep(1)

    len2_after = get_chain_length(NODE_2)
    print(f"  Node 2 Chain-Länge nach Sync: {len2_after}")

    if len2_after == len1_after:
        print("\n  Ergebnis: ✅ Chain-Sync funktioniert!")
    else:
        print("\n  Ergebnis: ❌ Chain-Sync fehlgeschlagen")
        print("  Hinweis: Sync passiert bei MinerNode automatisch vor dem nächsten Mine.")
        print("  Teste manuell: mine einen Block auf Node 2 → er synct vorher.")


# ─────────────────────────────────────────────
#  TEST 2: FORK-HANDLING
# ─────────────────────────────────────────────

def test_fork_handling():
    separator("TEST 2: Fork-Handling (zwei Miner gleichzeitig)")

    import threading

    len1_before = get_chain_length(NODE_1)
    len2_before = get_chain_length(NODE_2)
    print(f"  Chain-Länge vorher → Node 1: {len1_before} | Node 2: {len2_before}")

    results = {}

    def mine_on(node_url, key):
        success = mine_block(node_url)
        results[key] = success

    # Beide Nodes minen gleichzeitig
    print("\n  Beide Nodes minen gleichzeitig...")
    t1 = threading.Thread(target=mine_on, args=(NODE_1, "node1"))
    t2 = threading.Thread(target=mine_on, args=(NODE_2, "node2"))
    t1.start()
    t2.start()
    t1.join(timeout=120)
    t2.join(timeout=120)

    len1_after = get_chain_length(NODE_1)
    len2_after = get_chain_length(NODE_2)
    print(f"\n  Node 1 gemint: {results.get('node1')} | Chain-Länge: {len1_after}")
    print(f"  Node 2 gemint: {results.get('node2')} | Chain-Länge: {len2_after}")

    # Jetzt nochmal minen – der nächste Block löst den Fork auf
    print("\n  Node 1 mined weiteren Block → Fork sollte aufgelöst werden...")
    mine_block(NODE_1)
    time.sleep(1)

    len1_final = get_chain_length(NODE_1)
    len2_final = get_chain_length(NODE_2)
    print(f"  Finale Chain-Länge → Node 1: {len1_final} | Node 2: {len2_final}")

    if len1_final == len2_final:
        print("\n  Ergebnis: ✅ Fork aufgelöst, beide Nodes einig!")
    else:
        print("\n  Ergebnis: ⚠️  Nodes haben unterschiedliche Chain-Längen")
        print("  Das ist normal wenn der Broadcast noch nicht angekommen ist.")
        print("  → Mined einen weiteren Block auf Node 2, dann synct er.")


# ─────────────────────────────────────────────
#  TEST 3: DOUBLE-SPEND-SCHUTZ
# ─────────────────────────────────────────────

def test_double_spend():
    separator("TEST 3: Double-Spend-Schutz")

    # Frisches Wallet erstellen
    attacker = Wallet()
    victim   = Wallet()

    print(f"  Angreifer: {attacker.address[:30]}...")
    print(f"  Opfer    : {victim.address[:30]}...")

    # Zuerst: Angreifer muss Coins bekommen
    # Wir schauen ob er schon Balance hat (aus Mining-Rewards)
    balance = get_balance(NODE_1, attacker.address)
    print(f"\n  Angreifer-Balance: {balance} Coins")

    if balance == 0:
        print("  ℹ️  Angreifer hat keine Coins – Test mit verfügbarer Wallet")
        print("  Hinweis: Für diesen Test brauchst du eine Adresse mit Coins.")
        print("  Entweder den Miner-Node stoppen und dessen Wallet-Adresse nutzen,")
        print("  oder zuerst einige Blöcke minen lassen damit Rewards ankommen.")
        return

    # TX 1: legitime Transaktion
    tx1 = attacker.create_transaction(recipient=victim.address, amount=balance)
    accepted1, msg1 = submit_tx(NODE_1, tx1)
    print(f"\n  TX 1 (legitim, {balance} Coins) → Node 1: {accepted1} | {msg1}")

    # TX 2: gleiche Coins nochmal ausgeben (Double-Spend Versuch)
    tx2 = attacker.create_transaction(recipient=victim.address, amount=balance)
    accepted2, msg2 = submit_tx(NODE_1, tx2)
    print(f"  TX 2 (double-spend) → Node 1: {accepted2} | {msg2}")

    # TX 3: gleiche Coins an andere Node schicken
    accepted3, msg3 = submit_tx(NODE_2, tx1)
    print(f"  TX 1 nochmal → Node 2: {accepted3} | {msg3}")

    print()
    if accepted1 and not accepted2:
        print("  Ergebnis: ✅ Double-Spend auf gleicher Node erkannt!")
    else:
        print("  Ergebnis: ⚠️  Prüfe Mempool-Logik")

    if accepted1 and not accepted3:
        print("  Ergebnis: ✅ Duplicate TX auf anderer Node erkannt!")
    else:
        print("  Ergebnis: ⚠️  Gleiche TX auf Node 2 akzeptiert (Broadcast-Sync prüfen)")

    print(f"\n  Mempool Node 1: {get_mempool_size(NODE_1)} TXs")
    print(f"  Mempool Node 2: {get_mempool_size(NODE_2)} TXs")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 52)
    print("  P2P & Consensus Test Suite")
    print("=" * 52)
    print()
    print("  Voraussetzung:")
    print("  Terminal 1: uv run main_node.py --type miner --port 5000 --name miner_1")
    print("  Terminal 2: uv run main_node.py --type miner --port 5001 --name miner_2 --peers http://127.0.0.1:5000")
    print()

    check_nodes_reachable()

    test_chain_sync()
    test_fork_handling()
    test_double_spend()

    separator("Test Suite abgeschlossen")
    print()
    print("  Manuell prüfen kannst du außerdem:")
    print(f"  curl {NODE_1}/chain | python3 -m json.tool")
    print(f"  curl {NODE_2}/chain | python3 -m json.tool")
    print(f"  curl {NODE_1}/status")
    print(f"  curl {NODE_2}/status")
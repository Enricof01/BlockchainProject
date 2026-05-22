"""
main_node.py
============
Startskript für eine Node.
Unterstützt Miner-Node und Wallet-Node.

Verwendung:
  python main_node.py --type miner  --port 5000 --name miner_1
  python main_node.py --type wallet --port 5001 --name wallet_1
  python main_node.py --type miner  --port 5002 --name miner_2 --peers http://127.0.0.1:5000

Founder-Wallet:
  Beim ersten Start wird eine founder.pem erstellt.
  Diese NICHT ins Git-Repo committen (.gitignore).
"""

import argparse
import os

from blockchain_core import Blockchain
from wallet.wallet import Wallet
from miner_node import MinerNode
from wallet_node import WalletNode
from p2p import discover_peers


# ─────────────────────────────────────────────
#  FOUNDER WALLET
# ─────────────────────────────────────────────

FOUNDER_PEM_PATH = "keys/founder.pem"

def load_or_create_founder_wallet() -> Wallet:
    """
    Lädt das Founder-Wallet aus founder.pem oder erstellt es einmalig neu.
    """
    if os.path.exists(FOUNDER_PEM_PATH):
        with open(FOUNDER_PEM_PATH, "r") as f:
            wallet = Wallet.from_pem(f.read())
        print(f"[Setup] Founder-Wallet geladen: {wallet.address}")
    else:
        wallet = Wallet()
        with open(FOUNDER_PEM_PATH, "w") as f:
            f.write(wallet.private_key_pem)
        print(f"[Setup] Neues Founder-Wallet erstellt: {wallet.address}")
        print(f"[Setup] Private Key gespeichert in: {FOUNDER_PEM_PATH}")
        print(f"[Setup] ⚠️  NICHT ins Git-Repo committen!")

    return wallet


# ─────────────────────────────────────────────
#  NODE WALLET
# ─────────────────────────────────────────────

def load_or_create_node_wallet(name: str) -> Wallet:
    """Jede Node hat ihr eigenes Wallet (eigene Adresse für Rewards)."""
    pem_path = f"keys/{name}.pem"

    if os.path.exists(pem_path):
        with open(pem_path, "r") as f:
            wallet = Wallet.from_pem(f.read())
        print(f"[Setup] Node-Wallet geladen: {wallet.address}")
    else:
        wallet = Wallet()
        with open(pem_path, "w") as f:
            f.write(wallet.private_key_pem)
        print(f"[Setup] Neues Node-Wallet erstellt: {wallet.address}")

    return wallet


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Blockchain Node starten")
    parser.add_argument("--type",   choices=["miner", "wallet"], default="miner",
                        help="Node-Typ: miner oder wallet")
    parser.add_argument("--port",   type=int, default=5000,
                        help="Port der Node (default: 5000)")
    parser.add_argument("--name",   type=str, default="node_1",
                        help="Name der Node (default: node_1)")
    parser.add_argument("--peers",  type=str, default="",
                        help="Kommagetrennte Liste von Bootstrap-Peers, z.B. http://127.0.0.1:5001")
    parser.add_argument("--difficulty", type=int, default=3,
                        help="PoW Difficulty (default: 3)")
    args = parser.parse_args()

    print("=" * 52)
    print(f"  Blockchain Node  |  {args.type.upper()}  |  Port {args.port}")
    print("=" * 52)

    # ── Founder-Wallet & Blockchain ─────────────────
    founder_wallet = load_or_create_founder_wallet()
    blockchain     = Blockchain(
        founder_address = founder_wallet.address,
        difficulty      = args.difficulty,
    )

    # ── Node-Wallet ─────────────────────────────────
    node_wallet = load_or_create_node_wallet(args.name)

    # ── Node erstellen ───────────────────────────────
    if args.type == "miner":
        node = MinerNode(
            node_name      = args.name,
            port           = args.port,
            blockchain     = blockchain,
            miner_address  = node_wallet.address,
            wallet         = node_wallet,   # ← Wallet mitgeben
        )
        print(f"[Setup] Miner-Adresse: {node_wallet.address}")

    else:
        node = WalletNode(
            node_name  = args.name,
            port       = args.port,
            blockchain = blockchain,
            wallet     = node_wallet,
        )
        print(f"[Setup] Wallet-Adresse: {node_wallet.address}")

    # ── Peers verbinden ──────────────────────────────
    if args.peers:
        bootstrap = [p.strip() for p in args.peers.split(",") if p.strip()]
        discover_peers(node, bootstrap)

    # ── Infos ────────────────────────────────────────
    print()
    print(f"  Node-Typ   : {args.type}")
    print(f"  Port       : {args.port}")
    print(f"  Difficulty : {args.difficulty}")
    print(f"  Peers      : {list(node.peers) or 'keine'}")
    print()
    print("  Verfügbare Endpunkte:")
    print(f"    GET  http://127.0.0.1:{args.port}/status")
    print(f"    GET  http://127.0.0.1:{args.port}/chain")
    print(f"    GET  http://127.0.0.1:{args.port}/mempool")
    print(f"    POST http://127.0.0.1:{args.port}/submit_transaction")
    print(f"    GET  http://127.0.0.1:{args.port}/balance/<address>")
    if args.type == "miner":
        print(f"    POST http://127.0.0.1:{args.port}/mine")
        print(f"    POST http://127.0.0.1:{args.port}/mining/start")
        print(f"    POST http://127.0.0.1:{args.port}/mining/stop")
        print(f"    GET  http://127.0.0.1:{args.port}/mining/status")
    else:
        print(f"    GET  http://127.0.0.1:{args.port}/wallet/info")
        print(f"    POST http://127.0.0.1:{args.port}/wallet/send")
        print(f"    POST http://127.0.0.1:{args.port}/wallet/sync")
    print()

    # ── Node starten ─────────────────────────────────
    node.run(debug=False)


if __name__ == "__main__":
    main()
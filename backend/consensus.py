"""
consensus.py
============
Proof of Work – Mining-Loop, Difficulty Adjustment, Block-Reward.
Wird vom MinerNode verwendet.
"""

import time
from transaction import Transaction
from blockchain_core import Block

# ── Konstanten ───────────────────────────────────────────────────
INITIAL_DIFFICULTY      = 3       # Hash muss mit "000..." anfangen
BLOCK_REWARD            = 50.0    # Coins pro geminetem Block
ADJUSTMENT_INTERVAL     = 10      # alle N Blöcke Difficulty anpassen
TARGET_BLOCK_TIME       = 10.0    # Ziel: 10 Sekunden pro Block


# ─────────────────────────────────────────────
#  PROOF OF WORK
# ─────────────────────────────────────────────

def mine_block(block: Block, difficulty: int) -> Block:
    """
    Mining-Loop: Nonce hochzählen bis Hash mit N Nullen anfängt.
    Verändert block.nonce und block.hash in-place, gibt Block zurück.
    """
    target  = "0" * difficulty
    started = time.time()

    print(f"[Mining] Starte Mining für Block #{block.index} | Difficulty: {difficulty}...")

    while not block.hash.startswith(target):
        block.nonce += 1
        block.hash   = block.compute_hash()

    elapsed = time.time() - started
    print(
        f"[Mining] ✅ Block #{block.index} gefunden! "
        f"Nonce: {block.nonce} | Hash: {block.hash[:20]}... | {elapsed:.2f}s"
    )
    return block


def valid_proof(block: Block, difficulty: int) -> bool:
    """Prüft ob ein Block den PoW erfüllt."""
    return block.hash.startswith("0" * difficulty) and block.hash == block.compute_hash()


# ─────────────────────────────────────────────
#  DIFFICULTY ADJUSTMENT
# ─────────────────────────────────────────────

def adjust_difficulty(chain: list, current_difficulty: int) -> int:
    """
    Passt die Difficulty alle ADJUSTMENT_INTERVAL Blöcke an.
    Ziel: TARGET_BLOCK_TIME Sekunden pro Block.

    Zu schnell → Difficulty hoch
    Zu langsam → Difficulty runter (minimum 1)
    """
    if len(chain) % ADJUSTMENT_INTERVAL != 0 or len(chain) < ADJUSTMENT_INTERVAL:
        return current_difficulty

    # Zeitspanne der letzten N Blöcke berechnen
    last_block  = chain[-1]
    first_block = chain[-ADJUSTMENT_INTERVAL]

    try:
        from datetime import datetime, timezone
        fmt = "%Y-%m-%dT%H:%M:%S.%f+00:00"

        t_last  = datetime.fromisoformat(last_block.timestamp)
        t_first = datetime.fromisoformat(first_block.timestamp)
        elapsed = (t_last - t_first).total_seconds()
    except Exception:
        return current_difficulty

    expected = TARGET_BLOCK_TIME * ADJUSTMENT_INTERVAL
    ratio    = elapsed / expected if expected > 0 else 1.0

    if ratio < 0.5:
        new_difficulty = current_difficulty + 1
        print(f"[Difficulty] ⬆️  Blöcke zu schnell ({elapsed:.1f}s) → {current_difficulty} → {new_difficulty}")
    elif ratio > 2.0:
        new_difficulty = max(1, current_difficulty - 1)
        print(f"[Difficulty] ⬇️  Blöcke zu langsam ({elapsed:.1f}s) → {current_difficulty} → {new_difficulty}")
    else:
        new_difficulty = current_difficulty
        print(f"[Difficulty] ✅ Difficulty bleibt bei {current_difficulty} ({elapsed:.1f}s)")

    return new_difficulty


# ─────────────────────────────────────────────
#  MINING-REWARD (Coinbase-TX)
# ─────────────────────────────────────────────

def create_coinbase_tx(miner_address: str) -> Transaction:
    """
    Erstellt die Belohnungs-Transaktion für den Miner.
    Sender = 'COINBASE', kein Private Key nötig.
    """
    return Transaction(
        sender    = "COINBASE",
        recipient = miner_address,
        amount    = BLOCK_REWARD,
    )
def is_valid_proof(block_hash: str, difficulty: int) -> bool:
    return block_hash.startswith("0" * difficulty)

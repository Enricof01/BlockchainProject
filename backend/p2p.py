"""
p2p.py
======
P2P-Hilfsfunktionen für Node-Synchronisation und Chain-Auswahl.
Wird vom Node verwendet – kein eigener Server, nur HTTP-Logik.
"""

import requests
from blockchain_core import Blockchain, Block
from transaction import Transaction


# ─────────────────────────────────────────────
#  CHAIN SYNC  (longest chain rule)
# ─────────────────────────────────────────────

def fetch_chain_from_peer(peer_url: str) -> list[dict] | None:
    """
    Holt die Chain eines Peers als Liste von Block-dicts.
    Gibt None zurück wenn Peer nicht erreichbar.
    """
    try:
        response = requests.get(f"{peer_url}/chain", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("chain", [])
    except requests.RequestException:
        print(f"[P2P] Peer nicht erreichbar: {peer_url}")
    return None


def sync_chain(node) -> bool:
    """
    Longest-Chain-Rule: Vergleicht die eigene Chain mit allen Peers.
    Übernimmt die längste valide Chain.
    Gibt True zurück wenn die eigene Chain ersetzt wurde.
    """
    best_chain  = node.blockchain.chain
    best_length = len(best_chain)
    replaced    = False

    for peer in node.peers:
        chain_data = fetch_chain_from_peer(peer)
        if chain_data is None:
            continue

        if len(chain_data) <= best_length:
            continue

        # Candidate Chain aufbauen und validieren
        candidate = _build_chain_from_data(chain_data, node.blockchain.difficulty)
        if candidate and _is_valid_chain(candidate, node.blockchain.difficulty):
            best_chain  = candidate
            best_length = len(candidate)
            replaced    = True
            print(f"[P2P] Chain von {peer} übernommen | Länge: {best_length}")

    if replaced:
        node.blockchain.chain = best_chain
        print(f"[P2P] Eigene Chain ersetzt. Neue Länge: {best_length}")

    return replaced


def _build_chain_from_data(chain_data: list[dict], difficulty: int) -> list[Block] | None:
    """Baut eine Block-Liste aus rohen dicts auf."""
    try:
        return [Block.from_dict(b) for b in chain_data]
    except Exception as e:
        print(f"[P2P] Chain konnte nicht rekonstruiert werden: {e}")
        return None


def _is_valid_chain(chain: list[Block], difficulty: int) -> bool:
    """
    Validiert eine fremde Chain komplett:
    Hash-Integrität, Verkettung, PoW.
    """
    for i in range(1, len(chain)):
        current  = chain[i]
        previous = chain[i - 1]

        if current.hash != current.compute_hash():
            return False

        if current.previous_hash != previous.hash:
            return False

        if not current.hash.startswith("0" * difficulty):
            return False

    return True


# ─────────────────────────────────────────────
#  PEER DISCOVERY
# ─────────────────────────────────────────────

def discover_peers(node, bootstrap_peers: list[str]):
    """
    Verbindet sich mit Bootstrap-Peers und holt deren Peer-Listen.
    Registriert die eigene Node bei jedem Peer.
    Startet außerdem einen Background-Thread der sich nach dem
    Flask-Start nochmal bei allen Peers registriert (Timing-Fix).
    """
    import threading

    own_url = f"http://127.0.0.1:{node.port}"

    for peer in bootstrap_peers:
        if peer == own_url:
            continue

        node.add_peer(peer)
        _register_at_peer(peer, own_url)

        # Peer-Liste des Peers holen
        try:
            resp = requests.get(f"{peer}/peers", timeout=3)
            if resp.status_code == 200:
                known_peers = resp.json().get("peers", [])
                for p in known_peers:
                    if p != own_url and p not in node.peers:
                        node.add_peer(p)
                        _register_at_peer(p, own_url)
        except requests.RequestException:
            pass

    print(f"[P2P] Bekannte Peers: {list(node.peers)}")

    # Nach dem Flask-Start nochmal registrieren (Timing-Fix)
    # Flask braucht ~1s bis er wirklich erreichbar ist
    def delayed_register():
        import time
        time.sleep(2)
        for peer in list(node.peers):
            _register_at_peer(peer, own_url)
            print(f"[P2P] Re-registriert bei: {peer}")
        # Direkt beim Start auch Chain syncen
        replaced = sync_chain(node)
        if replaced:
            print(f"[P2P] Chain beim Start synchronisiert.")

    thread = threading.Thread(target=delayed_register, daemon=True)
    thread.start()


def _register_at_peer(peer_url: str, own_url: str):
    """Meldet die eigene Node bei einem Peer an."""
    try:
        requests.post(
            f"{peer_url}/add_peer",
            json={"peer": own_url},
            timeout=3,
        )
    except requests.RequestException:
        pass
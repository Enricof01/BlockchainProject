import { createContext, useState, useCallback, useEffect } from 'react';

export const BlockchainContext = createContext(null);

const BASE_PORT = 5001;

export async function api(port, path, opts = {}) {
  const r = await fetch(`http://127.0.0.1:${port}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export function BlockchainProvider({ children }) {
  const [nodes, setNodes]           = useState([BASE_PORT]);
  const [activeNode, setActiveNode] = useState(BASE_PORT);
  const [chain, setChain]           = useState([]);
  const [mempool, setMempool]       = useState([]);
  const [walletInfo, setWalletInfo] = useState(null);
  const [nodeStatus, setNodeStatus] = useState({});

  const addNode = () => {
    const next = Math.max(...nodes) + 1;
    setNodes(n => [...n, next]);
  };

  const removeNode = (port) => {
    setNodes(n => n.filter(p => p !== port));
    if (activeNode === port) setActiveNode(nodes.find(p => p !== port));
  };

  const fetchAll = useCallback(async () => {
    // Chain
    try {
      const d = await api(activeNode, '/chain');
      setChain((d.chain || []).slice().reverse());
    } catch { setChain([]); }

    // Mempool
    try {
      const d = await api(activeNode, '/mempool');
      setMempool(d.mempool || []);
    } catch { setMempool([]); }

    // Wallet
    try {
      setWalletInfo(await api(activeNode, '/wallet/info'));
    } catch { setWalletInfo(null); }

    // Node-Status für alle Nodes
    const results = {};
    await Promise.all(nodes.map(async port => {
      try {
        const r = await fetch(`http://127.0.0.1:${port}/status`);
        results[port] = { ...(await r.json()), online: true };
      } catch {
        results[port] = { online: false };
      }
    }));
    setNodeStatus(results);
  }, [activeNode, nodes.join(',')]);

  useEffect(() => {
    fetchAll();
    const t = setInterval(fetchAll, 4000);
    return () => clearInterval(t);
  }, [fetchAll]);

  return (
    <BlockchainContext.Provider value={{
      nodes, activeNode, setActiveNode, addNode, removeNode,
      chain, mempool, walletInfo, nodeStatus, setWalletInfo,
      refresh: fetchAll,
    }}>
      {children}
    </BlockchainContext.Provider>
  );
}

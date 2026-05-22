import { useContext } from 'react';
import { BlockchainContext } from '../context/BlockchainContext';
import { Card, Badge } from './ui';
import { Server, Plus, X, Network } from 'lucide-react';
import axios from "axios";

export default function NetworkView() {
  const { nodes, activeNode, setActiveNode, addNode, removeNode, nodeStatus } = useContext(BlockchainContext);

  const onlineCount = Object.values(nodeStatus).filter(d => d.online).length;

  async function mine(port) {
    await axios.post(`http://127.0.0.1:${port}/mine`)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <p style={{ fontSize: 13, color: '#6b7280' }}>
          <span style={{ color: '#4ade80', fontWeight: 700 }}>{onlineCount}</span>/{nodes.length} Nodes online
        </p>
        <button
          onClick={addNode}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            fontSize: 12, color: '#f3ba2f',
            background: 'rgba(243,186,47,0.1)', border: '1px solid rgba(243,186,47,0.2)',
            padding: '7px 14px', borderRadius: 10,
          }}
        >
          <Plus size={12} /> Node hinzufügen
        </button>
      </div>

      {nodes.map(port => {
        const d = nodeStatus[port] || {};
        return (
          <div
            key={port}
            onClick={() => setActiveNode(port)}
            style={{
              background: '#0d0d12',
              border: `1px solid ${activeNode === port ? 'rgba(243,186,47,0.4)' : '#1f1f29'}`,
              borderRadius: 16, padding: '1.25rem',
              cursor: 'pointer', transition: 'border-color 0.15s',

            }}
          >
            <button onClick = {() => mine(port)}>mine</button>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: d.online ? 16 : 0 }}>
              <div>
                <p style={{ fontWeight: 700, color: '#fff', fontSize: 14, marginBottom: 4 }}>
                  {d.node_name || `Node :${port}`}
                </p>
                <p style={{ fontFamily: 'monospace', fontSize: 10, color: '#6b7280' }}>127.0.0.1:{port}</p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {activeNode === port && <Badge color="amber">aktiv</Badge>}
                <Badge color={d.online ? 'green' : 'red'}>{d.online ? 'online' : 'offline'}</Badge>
                {nodes.length > 1 && (
                  <button
                    onClick={e => { e.stopPropagation(); removeNode(port); }}
                    style={{ background: 'none', border: 'none', color: '#4b5563', display: 'flex', padding: 4 }}
                  >
                    <X size={14} />
                  </button>
                )}
              </div>
            </div>

            {d.online && (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, marginBottom: 12 }}>
                  {[['Blöcke', d.chain_length], ['Mempool', `${d.mempool_size} TXs`], ['Peers', d.peers?.length]].map(([l, v]) => (
                    <div key={l} style={{ background: '#13131c', padding: '10px 12px', borderRadius: 10 }}>
                      <p style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1, marginBottom: 4 }}>{l}</p>
                      <p style={{ color: '#fff', fontWeight: 700, fontFamily: 'monospace' }}>{v}</p>
                    </div>
                  ))}
                </div>
                {d.peers?.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {d.peers.map(p => <Badge key={p} color="blue">{p}</Badge>)}
                  </div>
                )}
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}

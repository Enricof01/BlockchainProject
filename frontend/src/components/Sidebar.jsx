import { useContext } from 'react';
import { BlockchainContext } from '../context/BlockchainContext';
import {
  LayoutDashboard, Database, Activity, Wallet,
  Network, Server, ShieldCheck, Plus, X,
} from 'lucide-react';

const VIEWS = [
  { id: 'dashboard', label: 'Dashboard',      icon: LayoutDashboard },
  { id: 'explorer',  label: 'Block Explorer', icon: Database },
  { id: 'mempool',   label: 'Mempool',        icon: Activity },
  { id: 'wallet',    label: 'Wallet',         icon: Wallet },
  { id: 'network',   label: 'Netzwerk',       icon: Network },
];

export default function Sidebar({ view, setView }) {
  const { nodes, activeNode, setActiveNode, addNode, removeNode } = useContext(BlockchainContext);

  return (
    <aside style={{
      width: 240, background: '#0d0d12',
      borderRight: '1px solid #1f1f29',
      padding: '1.5rem',
      display: 'flex', flexDirection: 'column',
      justifyContent: 'space-between',
      flexShrink: 0, height: '100vh',
      position: 'sticky', top: 0,
    }}>
      <div>
        {/* Logo */}
        <div style={{ marginBottom: '2.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: 22, fontWeight: 900, color: '#f3ba2f', letterSpacing: '-0.5px' }}>
            ◈ NuggetChain
          </div>
          <div style={{ fontSize: 10, color: '#4b5563', marginTop: 4, letterSpacing: 2, textTransform: 'uppercase' }}>
            Blockchain Explorer
          </div>
        </div>

        {/* Navigation */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {VIEWS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setView(id)}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '10px 14px', borderRadius: 12,
                fontSize: 13, fontWeight: 700,
                border: '1px solid',
                background: view === id ? 'rgba(243,186,47,0.1)' : 'transparent',
                color: view === id ? '#f3ba2f' : '#6b7280',
                borderColor: view === id ? 'rgba(243,186,47,0.2)' : 'transparent',
                transition: 'all 0.15s', textAlign: 'left',
              }}
            >
              <Icon size={15} /> {label}
            </button>
          ))}
        </nav>

        {/* Node-Selector */}
        <div style={{ marginTop: 24, padding: '12px 14px', background: '#13131c', borderRadius: 12, border: '1px solid #1f1f29' }}>
          <p style={{ fontSize: 10, color: '#6b7280', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1, fontWeight: 700 }}>
            Nodes
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {nodes.map(port => (
              <div key={port} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <button
                  onClick={() => setActiveNode(port)}
                  style={{
                    flex: 1, fontSize: 11, fontFamily: 'monospace',
                    padding: '5px 8px', borderRadius: 8,
                    border: '1px solid',
                    background: activeNode === port ? 'rgba(243,186,47,0.1)' : 'transparent',
                    color: activeNode === port ? '#f3ba2f' : '#6b7280',
                    borderColor: activeNode === port ? 'rgba(243,186,47,0.2)' : 'transparent',
                    textAlign: 'left',
                  }}
                >
                  :{port}
                </button>
                {nodes.length > 1 && (
                  <button
                    onClick={() => removeNode(port)}
                    style={{ background: 'none', border: 'none', color: '#4b5563', padding: 4, display: 'flex' }}
                  >
                    <X size={12} />
                  </button>
                )}
              </div>
            ))}
          </div>
          <button
            onClick={addNode}
            style={{
              marginTop: 8, fontSize: 10, color: '#6b7280',
              background: 'none', border: 'none',
              display: 'flex', alignItems: 'center', gap: 4,
              padding: '4px 0',
            }}
          >
            <Plus size={10} /> Node hinzufügen
          </button>
        </div>
      </div>

      {/* Footer */}
      <div style={{ background: '#13131c', padding: '1rem', borderRadius: 12, border: '1px solid #1f1f29' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, fontWeight: 700, color: '#4ade80', marginBottom: 6 }}>
          <Server size={11} /> Node online
        </div>
        <div style={{ fontSize: 10, color: '#6b7280', fontFamily: 'monospace' }}>
          <p>127.0.0.1:{activeNode}</p>
          <p style={{ marginTop: 2 }}>NuggetChain v1.0</p>
        </div>
        <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 6, fontSize: 10, color: '#6b7280' }}>
          <ShieldCheck size={10} style={{ color: '#f3ba2f' }} /> System: Validiert
        </div>
      </div>
    </aside>
  );
}

import { useContext } from 'react';
import { BlockchainContext } from '../context/BlockchainContext';
import { StatCard, Card, Badge } from './ui';
import { Layers, Activity, Users, Cpu, Wallet, Key, Database, Clock, ArrowRight, Server } from 'lucide-react';

export default function DashboardView() {
  const { chain, mempool, walletInfo, nodeStatus, nodes, activeNode } = useContext(BlockchainContext);

  const latestBlock   = chain[0];
  const onlineCount   = Object.values(nodeStatus).filter(d => d.online).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14 }}>
        <StatCard icon={Layers}   label="Aktuelle Blockhöhe" value={`#${latestBlock?.index ?? 0}`}      color="yellow" />
        <StatCard icon={Activity} label="Mempool"            value={`${mempool.length} TXs`}            color="red" />
        <StatCard icon={Users}    label="Nodes online"       value={`${onlineCount}/${nodes.length}`}   color="green" />
        <StatCard icon={Cpu}      label="Difficulty"         value={latestBlock?.difficulty ?? '—'}     color="purple" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '5fr 7fr', gap: 24 }}>
        {/* Wallet */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {walletInfo ? (
            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
                <div style={{ background: 'rgba(243,186,47,0.1)', padding: 12, borderRadius: 12, color: '#f3ba2f', display: 'flex' }}>
                  <Wallet size={24} />
                </div>
                <Badge color="gray">Secp256k1</Badge>
              </div>
              <p style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1 }}>
                Verfügbares Guthaben
              </p>
              <h2 style={{ fontSize: 38, fontWeight: 900, color: '#fff', margin: '8px 0', letterSpacing: '-1px' }}>
                {walletInfo.available_balance?.toLocaleString()}
                <span style={{ color: '#f3ba2f', fontWeight: 300, fontSize: 24, marginLeft: 8 }}>◈</span>
              </h2>
              <div style={{ borderTop: '1px solid #1f1f29', paddingTop: 16, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                {[['Bestätigt', walletInfo.confirmed_balance], ['Ausstehend', walletInfo.pending_spent]].map(([l, v]) => (
                  <div key={l}>
                    <p style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1 }}>{l}</p>
                    <p style={{ color: '#fff', fontWeight: 700, marginTop: 4 }}>{v?.toLocaleString()} ◈</p>
                  </div>
                ))}
              </div>
              <div style={{ borderTop: '1px solid #1f1f29', paddingTop: 12, display: 'flex', alignItems: 'center', gap: 8, fontSize: 10, color: '#6b7280' }}>
                <Key size={11} style={{ color: '#9ca3af', flexShrink: 0 }} />
                <span style={{ fontFamily: 'monospace', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {walletInfo.address}
                </span>
              </div>
            </Card>
          ) : (
            <Card style={{ textAlign: 'center', padding: '3rem', color: '#4b5563', fontSize: 13 }}>
              Kein Wallet auf dieser Node
            </Card>
          )}

          {/* Node-Liste */}
          <Card>
            <h3 style={{ fontSize: 12, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Server size={12} /> Netzwerk-Nodes
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {nodes.map(port => {
                const d = nodeStatus[port] || {};
                return (
                  <div key={port} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #1f1f29' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 6, height: 6, borderRadius: '50%', background: d.online ? '#4ade80' : '#ef4444', flexShrink: 0 }} />
                      <span style={{ fontFamily: 'monospace', fontSize: 12, color: '#d1d5db' }}>{d.node_name || `:${port}`}</span>
                    </div>
                    <div style={{ display: 'flex', gap: 12, fontSize: 11, color: '#6b7280' }}>
                      <span>{d.chain_length ?? '—'} Blöcke</span>
                      <span>{d.mempool_size ?? '—'} TXs</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>

        {/* Rechte Spalte */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Letzte Blöcke */}
          <Card>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Database size={14} style={{ color: '#f3ba2f' }} /> Letzte Blöcke
              </h3>
              <span style={{ fontSize: 10, color: '#6b7280', fontFamily: 'monospace', background: '#13131c', padding: '3px 8px', borderRadius: 6 }}>live</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {chain.slice(0, 3).map(b => (
                <div key={b.index} style={{ padding: 14, background: '#13131c', borderRadius: 12, border: '1px solid #1f1f29' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ background: 'rgba(243,186,47,0.1)', color: '#f3ba2f', fontSize: 11, fontWeight: 900, padding: '4px 10px', borderRadius: 8 }}>
                        #{b.index}
                      </span>
                      <span style={{ fontSize: 10, color: '#6b7280', fontFamily: 'monospace', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Clock size={10} /> {b.timestamp?.slice(0, 19).replace('T', ' ')}
                      </span>
                    </div>
                    <span style={{ fontSize: 10, fontWeight: 700, color: '#4ade80', background: 'rgba(74,222,128,0.05)', border: '1px solid rgba(74,222,128,0.1)', padding: '2px 8px', borderRadius: 20 }}>
                      Nonce: {b.nonce?.toLocaleString()}
                    </span>
                  </div>
                  <p style={{ fontFamily: 'monospace', fontSize: 10, color: '#6b7280', background: 'rgba(0,0,0,0.2)', padding: '6px 10px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.03)', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    <span style={{ color: '#374151', fontFamily: 'sans-serif', fontWeight: 700 }}>HASH: </span>{b.hash}
                  </p>
                </div>
              ))}
              {chain.length === 0 && <p style={{ textAlign: 'center', color: '#4b5563', padding: '2rem', fontSize: 13 }}>Keine Blöcke</p>}
            </div>
          </Card>

          {/* Mempool */}
          <Card>
            <h3 style={{ fontSize: 14, fontWeight: 700, color: '#fff', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Activity size={14} style={{ color: '#f87171' }} /> Mempool
            </h3>
            {mempool.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#4b5563', padding: '1.5rem', fontSize: 13 }}>Mempool leer</p>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {mempool.slice(0, 4).map((tx, i) => (
                  <div key={i} style={{ padding: '10px 12px', background: '#13131c', border: '1px solid #1f1f29', borderRadius: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                      <div style={{ fontFamily: 'monospace', fontSize: 10, color: '#9ca3af', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ color: '#60a5fa' }}>{tx.sender?.slice(0, 8)}…</span>
                        <ArrowRight size={8} style={{ color: '#4b5563' }} />
                        <span style={{ color: '#a78bfa' }}>{tx.recipient?.slice(0, 8)}…</span>
                      </div>
                      <span style={{ fontSize: 11, fontWeight: 900, color: '#f87171' }}>+{tx.amount} ◈</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

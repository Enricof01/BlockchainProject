import { useState, useContext } from 'react';
import { BlockchainContext } from '../context/BlockchainContext';
import { Card, Badge, HashChip } from './ui';
import { Database, Clock, Cpu, Layers, CheckCircle2, Search, RefreshCw } from 'lucide-react';

export default function BlockExplorerView() {
  const { chain, refresh } = useContext(BlockchainContext);
  const [search, setSearch]   = useState('');
  const [selected, setSelected] = useState(null);

  const filtered = chain.filter(b =>
    search === '' ||
    b.index.toString() === search ||
    b.hash?.toLowerCase().includes(search.toLowerCase())
  );

  const block = selected != null ? chain.find(b => b.index === selected) : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Suchleiste */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, background: '#0d0d12', border: '1px solid #1f1f29', padding: '1rem 1.25rem', borderRadius: 16 }}>
        <div style={{ position: 'relative', flex: 1, maxWidth: 420 }}>
          <Search size={13} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Nach Block-Index oder Hash suchen…"
            style={{ paddingLeft: 36, fontFamily: 'monospace' }}
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 12, color: '#6b7280', fontFamily: 'monospace', flexShrink: 0 }}>
          <span>Blöcke: <span style={{ color: '#f3ba2f', fontWeight: 700 }}>{chain.length}</span></span>
          <button onClick={refresh} style={{ background: 'none', border: 'none', color: '#6b7280', display: 'flex' }}>
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Block-Liste */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {filtered.map(b => (
            <div
              key={b.index}
              onClick={() => setSelected(selected === b.index ? null : b.index)}
              style={{
                background: '#0d0d12',
                border: `1px solid ${selected === b.index ? 'rgba(243,186,47,0.4)' : '#1f1f29'}`,
                borderRadius: 16, padding: '1.25rem',
                cursor: 'pointer', transition: 'border-color 0.15s',
              }}
            >
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ background: 'rgba(243,186,47,0.1)', color: '#f3ba2f', fontSize: 11, fontWeight: 900, padding: '4px 10px', borderRadius: 8, display: 'flex', alignItems: 'center', gap: 5 }}>
                    <Database size={11} /> #{b.index}
                  </span>
                  <span style={{ fontSize: 10, color: '#6b7280', fontFamily: 'monospace', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Clock size={10} /> {b.timestamp?.slice(0, 19).replace('T', ' ')}
                  </span>
                </div>
                <span style={{ fontSize: 10, fontWeight: 700, color: '#4ade80', background: 'rgba(74,222,128,0.05)', border: '1px solid rgba(74,222,128,0.1)', padding: '2px 8px', borderRadius: 20, display: 'flex', alignItems: 'center', gap: 4 }}>
                  <CheckCircle2 size={10} /> Validiert
                </span>
              </div>

              {/* Metadaten */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, background: '#13131c', padding: '10px 12px', borderRadius: 10, border: '1px solid rgba(31,31,41,0.5)', marginBottom: 10 }}>
                {[
                  [<Cpu size={10} />, 'Nonce', b.nonce?.toLocaleString()],
                  [<Layers size={10} />, 'Difficulty', b.difficulty],
                  [null, 'TXs', b.transactions?.length],
                ].map(([icon, label, val]) => (
                  <div key={label}>
                    <p style={{ fontSize: 10, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 3, marginBottom: 4 }}>{icon} {label}</p>
                    <p style={{ fontFamily: 'monospace', color: '#fff', fontWeight: 700, fontSize: 12 }}>{val}</p>
                  </div>
                ))}
              </div>

              {/* Hash */}
              <div>
                <p style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1, marginBottom: 4 }}>Hash</p>
                <p style={{ fontFamily: 'monospace', fontSize: 10, color: '#f3ba2f', background: 'rgba(0,0,0,0.3)', padding: '6px 10px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.03)', margin: 0, wordBreak: 'break-all' }}>
                  {b.hash}
                </p>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#4b5563', fontSize: 13 }}>Keine Blöcke gefunden</div>
          )}
        </div>

        {/* Detail-Panel */}
        <div style={{ position: 'sticky', top: 0, alignSelf: 'start' }}>
          {block ? (
            <Card gold>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: '#fff', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Database size={14} style={{ color: '#f3ba2f' }} /> Block #{block.index}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 20 }}>
                {[
                  ['Hash',       block.hash],
                  ['Prev Hash',  block.previous_hash],
                  ['Timestamp',  block.timestamp?.slice(0, 19).replace('T', ' ')],
                  ['Nonce',      block.nonce?.toLocaleString()],
                  ['Difficulty', block.difficulty],
                ].map(([k, v]) => (
                  <div key={k} style={{ background: '#13131c', border: '1px solid #1f1f29', borderRadius: 10, padding: '10px 12px' }}>
                    <p style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1, marginBottom: 4 }}>{k}</p>
                    <p style={{ fontFamily: 'monospace', fontSize: 10, color: '#d1d5db', wordBreak: 'break-all', margin: 0 }}>{v}</p>
                  </div>
                ))}
              </div>

              <p style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1, marginBottom: 10 }}>
                Transaktionen
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {block.transactions?.map((tx, i) => (
                  <div key={i} style={{ background: '#13131c', border: '1px solid #232333', borderRadius: 12, padding: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <Badge color={tx.sender === 'COINBASE' ? 'amber' : 'blue'}>
                        {tx.sender === 'COINBASE' ? 'COINBASE' : 'TX'}
                      </Badge>
                      <span style={{ fontWeight: 900, color: '#f3ba2f', fontSize: 13 }}>{tx.amount} ◈</span>
                    </div>
                    <div style={{ fontFamily: 'monospace', fontSize: 10, color: '#6b7280', display: 'flex', flexDirection: 'column', gap: 3 }}>
                      <p style={{ margin: 0 }}>Von: {tx.sender === 'COINBASE' ? '—' : tx.sender?.slice(0, 26) + '…'}</p>
                      <p style={{ margin: 0 }}>An:  {tx.recipient?.slice(0, 26)}…</p>
                    </div>
                  </div>
                ))}
                {block.transactions?.length === 0 && (
                  <p style={{ fontSize: 12, color: '#4b5563', fontStyle: 'italic' }}>Keine Transaktionen</p>
                )}
              </div>
            </Card>
          ) : (
            <Card style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 200, color: '#4b5563', gap: 10 }}>
              <Database size={32} />
              <p style={{ fontSize: 13 }}>Block auswählen für Details</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

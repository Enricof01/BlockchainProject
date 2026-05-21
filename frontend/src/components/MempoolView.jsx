import { useContext } from 'react';
import { BlockchainContext } from '../context/BlockchainContext';
import { Card, Badge } from './ui';
import { Activity, Clock, ArrowRight, Inbox } from 'lucide-react';

export default function MempoolView() {
  const { mempool } = useContext(BlockchainContext);

  return (
    <Card>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h3 style={{ fontSize: 14, fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: 8 }}>
          <Activity size={14} style={{ color: '#f87171' }} /> Transaktions-Mempool
        </h3>
        <Badge color={mempool.length > 0 ? 'amber' : 'gray'}>{mempool.length} wartend</Badge>
      </div>

      {mempool.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#4b5563', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
          <Inbox size={32} />
          <p style={{ fontSize: 13 }}>Mempool leer – keine unbestätigten Transaktionen</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          {mempool.map((tx, i) => (
            <div key={i} style={{ padding: '14px', background: '#13131c', border: '1px solid #1f1f29', borderRadius: 12, transition: 'border-color 0.15s' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <div style={{ fontFamily: 'monospace', fontSize: 10, color: '#9ca3af', display: 'flex', alignItems: 'center', gap: 5 }}>
                  <span style={{ color: '#60a5fa' }}>{tx.sender?.slice(0, 10)}…</span>
                  <ArrowRight size={10} style={{ color: '#4b5563' }} />
                  <span style={{ color: '#a78bfa' }}>{tx.recipient?.slice(0, 10)}…</span>
                </div>
                <span style={{ fontSize: 12, fontWeight: 900, color: '#f87171', background: 'rgba(239,68,68,0.05)', padding: '3px 8px', borderRadius: 8 }}>
                  +{tx.amount} ◈
                </span>
              </div>
              <p style={{ fontSize: 10, color: '#4b5563', display: 'flex', alignItems: 'center', gap: 4, margin: 0 }}>
                <Clock size={10} /> {tx.timestamp?.slice(0, 19).replace('T', ' ')}
              </p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

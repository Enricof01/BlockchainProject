export function Badge({ children, color = 'gray' }) {
  const map = {
    green:  { bg: 'rgba(74,222,128,0.1)',  color: '#4ade80',  border: 'rgba(74,222,128,0.2)' },
    red:    { bg: 'rgba(239,68,68,0.1)',   color: '#f87171',  border: 'rgba(239,68,68,0.2)' },
    amber:  { bg: 'rgba(243,186,47,0.1)',  color: '#f3ba2f',  border: 'rgba(243,186,47,0.2)' },
    blue:   { bg: 'rgba(96,165,250,0.1)',  color: '#60a5fa',  border: 'rgba(96,165,250,0.2)' },
    purple: { bg: 'rgba(167,139,250,0.1)', color: '#a78bfa',  border: 'rgba(167,139,250,0.2)' },
    gray:   { bg: '#13131c',               color: '#6b7280',  border: '#1f1f29' },
  };
  const c = map[color] || map.gray;
  return (
    <span style={{
      fontSize: 10, fontWeight: 700, padding: '2px 8px',
      borderRadius: 6, border: `1px solid ${c.border}`,
      background: c.bg, color: c.color,
    }}>
      {children}
    </span>
  );
}

export function Card({ children, style = {}, gold = false }) {
  return (
    <div style={{
      background: '#0d0d12',
      border: `1px solid ${gold ? 'rgba(243,186,47,0.3)' : '#1f1f29'}`,
      borderRadius: 16, padding: '1.5rem',
      ...style,
    }}>
      {children}
    </div>
  );
}

export function StatCard({ icon: Icon, label, value, color = 'yellow' }) {
  const colors = {
    yellow: { bg: 'rgba(243,186,47,0.1)', color: '#f3ba2f' },
    blue:   { bg: 'rgba(96,165,250,0.1)', color: '#60a5fa' },
    purple: { bg: 'rgba(167,139,250,0.1)', color: '#a78bfa' },
    green:  { bg: 'rgba(74,222,128,0.1)', color: '#4ade80' },
    red:    { bg: 'rgba(239,68,68,0.1)',  color: '#f87171' },
  };
  const c = colors[color] || colors.yellow;
  return (
    <div style={{ background: '#0d0d12', border: '1px solid #1f1f29', padding: '1.25rem', borderRadius: 16, display: 'flex', alignItems: 'center', gap: 14 }}>
      <div style={{ padding: 10, borderRadius: 12, background: c.bg, color: c.color, display: 'flex' }}>
        <Icon size={20} />
      </div>
      <div>
        <p style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1, margin: 0 }}>{label}</p>
        <p style={{ fontSize: 18, fontWeight: 900, color: '#fff', margin: '2px 0 0' }}>{value}</p>
      </div>
    </div>
  );
}

export function HashChip({ hash }) {
  if (!hash) return null;
  return (
    <span style={{ fontFamily: 'monospace', fontSize: 10, background: 'rgba(0,0,0,0.3)', padding: '2px 8px', borderRadius: 6, color: '#f3ba2f', wordBreak: 'break-all' }}>
      {hash}
    </span>
  );
}

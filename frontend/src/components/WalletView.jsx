import { useState, useContext } from 'react';
import { BlockchainContext } from '../context/BlockchainContext';
import { api } from '../context/BlockchainContext';
import { Card } from './ui';
import { Wallet, Key, Send, ArrowUpRight } from 'lucide-react';

export default function WalletView() {
  const { walletInfo, activeNode, refresh, setActiveNode, nodes, setWalletInfo } = useContext(BlockchainContext);
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount]       = useState('');
  const [status, setStatus]       = useState(null);
  const [sending, setSending]     = useState(false);
  const [nodeIterator, setNodeIterator] = useState(0);

  const send = async () => {
    if (!recipient || !amount) return;
    setSending(true); setStatus(null);
    try {
      const r = await api(activeNode, '/wallet/send', {
        method: 'POST',
        body: JSON.stringify({ recipient, amount: parseFloat(amount) }),
      });
      setStatus(r);
      if (r.accepted) { setRecipient(''); setAmount(''); refresh(); }
    } catch (e) {
      setStatus({ accepted: false, message: String(e) });
    }
    setSending(false);
  };

  if (!walletInfo) {
    return (
      <Card style={{ textAlign: 'center', padding: '3rem', color: '#4b5563', fontSize: 13 }}>
        Kein Wallet auf dieser Node verfügbar
      </Card>
    );
  }

  async function changeWalletInfo(){

  setWalletInfo(await api(activeNode, '/wallet/info'));
   console.log(`was changed to ${activeNode}`)
   console.log(walletInfo)
  }

  function changeNode() {
    if(nodes.length - 1 == nodeIterator) {
      setNodeIterator(0)
    }

    else{
      setNodeIterator(prev => prev + 1)
    }
    setActiveNode(nodes[nodeIterator])
    changeWalletInfo()

  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
      {/* Balance Card */}
      
      <Card>
        <button onClick={() => changeNode()}>wallet change</button>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
          <div style={{ background: 'rgba(243,186,47,0.1)', padding: 12, borderRadius: 12, color: '#f3ba2f', display: 'flex' }}>
            <Wallet size={24} />
          </div>
          <span style={{ fontSize: 10, fontWeight: 700, color: '#6b7280', background: '#13131c', padding: '3px 10px', borderRadius: 6, border: '1px solid #1f1f29' }}>
            Secp256k1 Address
          </span>
        </div>

        <p style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1 }}>
          Verfügbares Guthaben
        </p>
        <h2 style={{ fontSize: 42, fontWeight: 900, color: '#fff', margin: '8px 0', letterSpacing: '-1px' }}>
          {walletInfo.available_balance?.toLocaleString()}
          <span style={{ color: '#f3ba2f', fontWeight: 300, fontSize: 26, marginLeft: 10 }}>◈</span>
        </h2>

        <div style={{ borderTop: '1px solid #1f1f29', paddingTop: 16, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          {[
            ['Bestätigt', walletInfo.confirmed_balance],
            ['Ausstehend', walletInfo.pending_spent],
          ].map(([l, v]) => (
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

      {/* Send Card */}
      <Card>
        <h3 style={{ fontSize: 14, fontWeight: 700, color: '#fff', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Send size={14} style={{ color: '#f3ba2f' }} /> Coins transferieren
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1, display: 'block', marginBottom: 6 }}>
              Empfänger-Adresse
            </label>
            <input
              value={recipient}
              onChange={e => setRecipient(e.target.value)}
              placeholder="1ABC…"
              style={{ fontFamily: 'monospace' }}
            />
          </div>

          <div>
            <label style={{ fontSize: 10, color: '#6b7280', textTransform: 'uppercase', fontWeight: 700, letterSpacing: 1, display: 'block', marginBottom: 6 }}>
              Betrag (◈)
            </label>
            <input
              type="number"
              value={amount}
              onChange={e => setAmount(e.target.value)}
              placeholder="0.00"
              min="0"
            />
          </div>

          <button
            onClick={send}
            disabled={sending || !recipient || !amount}
            style={{
              width: '100%', background: sending || !recipient || !amount ? '#2a2a1a' : '#f3ba2f',
              color: sending || !recipient || !amount ? '#6b7280' : '#000',
              fontWeight: 900, padding: '14px', borderRadius: 12,
              border: 'none', fontSize: 13, display: 'flex',
              justifyContent: 'center', alignItems: 'center', gap: 8,
              cursor: sending || !recipient || !amount ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s',
            }}
          >
            {sending ? 'Sendet…' : <><span>Zahlung anweisen</span><ArrowUpRight size={16} /></>}
          </button>

          {status && (
            <div style={{
              padding: '10px 14px', borderRadius: 10, fontSize: 12, fontWeight: 700,
              background: status.accepted ? 'rgba(74,222,128,0.1)' : 'rgba(239,68,68,0.1)',
              color: status.accepted ? '#4ade80' : '#f87171',
              border: `1px solid ${status.accepted ? 'rgba(74,222,128,0.2)' : 'rgba(239,68,68,0.2)'}`,
            }}>
              {status.accepted ? '✓ ' : '✗ '}{status.message}
            </div>
          )}
        </div>
      </Card>

    </div>
  );
}

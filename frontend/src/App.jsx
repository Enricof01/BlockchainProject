import { useState } from 'react';
import { BlockchainProvider } from './context/BlockchainContext';
import Sidebar from './components/Sidebar';
import DashboardView    from './components/DashboardView';
import BlockExplorerView from './components/BlockExplorerView';
import MempoolView      from './components/MempoolView';
import WalletView       from './components/WalletView';
import NetworkView      from './components/NetworkView';
import { ShieldCheck } from 'lucide-react';

const VIEW_LABELS = {
  dashboard: { title: 'Krypto-Zentrale',   sub: 'Ganzheitliche Netzwerk-Überwachung und Wallet-Verwaltung.' },
  explorer:  { title: 'Blockchain Ledger', sub: 'Detaillierter Einblick in verifizierte Blöcke, Hashes und Validierungsmetriken.' },
  mempool:   { title: 'Transaktions-Pool', sub: 'Unbestätigte Transaktionen die auf Mining warten.' },
  wallet:    { title: 'Wallet',            sub: 'Guthaben verwalten und Coins transferieren.' },
  network:   { title: 'Netzwerk',          sub: 'Verbundene Nodes, Peers und Netzwerk-Status.' },
};

function AppContent() {
  const [view, setView] = useState('dashboard');
  const { title, sub } = VIEW_LABELS[view];

  return (
    <div style={{ minHeight: '100vh', background: '#070709', color: '#f3f4f6', display: 'flex' }}>
      <Sidebar view={view} setView={setView} />

      <main style={{ flex: 1, padding: '2.5rem', overflowY: 'auto', height: '100vh', boxSizing: 'border-box' }}>
        {/* Header */}
        <header style={{ marginBottom: '2rem', borderBottom: '1px solid #1f1f29', paddingBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 900, color: '#fff', margin: 0, letterSpacing: '-0.5px' }}>
              {title}
            </h1>
            <p style={{ color: '#6b7280', fontSize: 13, marginTop: 6 }}>{sub}</p>
          </div>
          <div style={{ background: '#13131c', border: '1px solid #1f1f29', padding: '6px 14px', borderRadius: 12, fontSize: 11, fontFamily: 'monospace', color: '#6b7280', display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
            <ShieldCheck size={12} style={{ color: '#f3ba2f' }} /> System-Status: Validiert
          </div>
        </header>

        {/* Views */}
        {view === 'dashboard' && <DashboardView />}
        {view === 'explorer'  && <BlockExplorerView />}
        {view === 'mempool'   && <MempoolView />}
        {view === 'wallet'    && <WalletView />}
        {view === 'network'   && <NetworkView />}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BlockchainProvider>
      <AppContent />
    </BlockchainProvider>
  );
}

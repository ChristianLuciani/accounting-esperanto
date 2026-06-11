import React, { useState, useEffect } from 'react';
import { Activity, Globe, AlertCircle, Search, Layers, RefreshCcw, Server } from 'lucide-react';
import { motion } from 'framer-motion';

// Configurable at build/deploy time (Vite). Falls back to the local dev API.
// Never hardcode a deployed URL here — the dashboard is a local demo only
// (see CLAUDE.md: do not deploy the frontend publicly).
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Static, clearly-labelled illustrative mappings. These are NOT live API
// results — they exist to show the dashboard layout and the Co-responsibility
// inconsistency flag. The banner in the UI states this explicitly.
const SAMPLE_MAPPINGS = [
  {
    code: '101.01', name: 'Petty Cash Fund', jurisdiction: 'MX',
    match: 'asset.noncurrent.ppe', score: 0.3, method: 'illustrative',
    inconsistent: true,
    note: 'Deterministic Violation: liquid asset mapped to a Non-Current node (caught by the Co-responsibility boundary check).'
  },
  { code: '101', name: 'Caja', jurisdiction: 'MX', match: 'asset.current.cash', score: 1.0, method: 'illustrative', inconsistent: false },
  { code: '105', name: 'Clientes', jurisdiction: 'MX', match: 'asset.current.receivables', score: 1.0, method: 'illustrative', inconsistent: false },
  { code: '201', name: 'Proveedores', jurisdiction: 'MX', match: 'liability.current.payables', score: 1.0, method: 'illustrative', inconsistent: false },
];

const App = () => {
  const [loading, setLoading] = useState(true);
  const [apiOnline, setApiOnline] = useState(null); // null = unknown, then bool
  const [ontologyNodes, setOntologyNodes] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const healthRes = await fetch(`${API_BASE_URL}/health`);
      const isHealthy = healthRes.ok;

      let total = null;
      if (isHealthy) {
        const accountsRes = await fetch(`${API_BASE_URL}/accounts`);
        if (accountsRes.ok) {
          const accountsData = await accountsRes.json();
          total = typeof accountsData.total === 'number' ? accountsData.total : null;
        }
      }
      setApiOnline(isHealthy);
      setOntologyNodes(total);
    } catch (error) {
      // Graceful degradation: the dashboard renders with an Offline status
      // instead of crashing or showing fabricated metrics.
      console.error('API connection failed:', error);
      setApiOnline(false);
      setOntologyNodes(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Only real, API-derived values here — no fabricated coverage/entity counts.
  const stats = [
    {
      label: 'System Status',
      value: apiOnline === null ? '—' : apiOnline ? 'Healthy' : 'Offline',
      icon: Activity,
      color: apiOnline ? '#10b981' : '#ef4444',
    },
    {
      label: 'Ontology Nodes (live)',
      value: ontologyNodes === null ? '—' : ontologyNodes.toString(),
      icon: Layers,
      color: '#a855f7',
    },
    {
      label: 'API Endpoint',
      value: API_BASE_URL.replace(/^https?:\/\//, ''),
      icon: Server,
      color: '#6366f1',
    },
    {
      label: 'Mode',
      value: 'Local demo',
      icon: Globe,
      color: '#94a3b8',
    },
  ];

  return (
    <div className="dashboard-container">
      <header className="header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="title-badge">kontablo</div>
          <button
            onClick={fetchData}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}
            title="Refresh Data"
            aria-label="Refresh data"
          >
            <RefreshCcw size={18} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
        <div className="search-bar glass-card" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Search size={18} color="#94a3b8" />
          <input
            type="text"
            placeholder="Search accounts or IDs..."
            style={{ background: 'transparent', border: 'none', color: 'white', outline: 'none', width: '200px' }}
          />
        </div>
      </header>

      {/* Honest banner: distinguishes live data from illustrative samples. */}
      <div role="note" className="glass-card" style={{ padding: '0.75rem 1rem', marginBottom: '1rem', fontSize: '0.8rem', color: '#cbd5e1', borderLeft: '3px solid #6366f1' }}>
        Local demonstration dashboard. <strong>System Status</strong> and <strong>Ontology Nodes</strong> are live from the API at
        {' '}<code>{API_BASE_URL}</code>. The mapping list and per-jurisdiction figures below are <strong>illustrative samples</strong>, not live results.
        {apiOnline === false && ' — API is currently unreachable; live values show “—”.'}
      </div>

      <div className="stats-grid">
        {stats.map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="glass-card stat-item"
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h3>{stat.label}</h3>
              <stat.icon size={20} color={stat.color} />
            </div>
            <div className="value">{stat.value}</div>
          </motion.div>
        ))}
      </div>

      <div className="chart-section">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card"
          style={{ position: 'relative' }}
        >
          {loading && (
            <div style={{ position: 'absolute', top: '1rem', right: '1rem', fontSize: '0.75rem', color: '#6366f1' }}>
              Fetching...
            </div>
          )}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', alignItems: 'center' }}>
            <h2 style={{ fontSize: '1.25rem' }}>Account Mapping (illustrative)</h2>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <span className="badge badge-warning">Sample data</span>
            </div>
          </div>

          <div className="mapping-list">
            {SAMPLE_MAPPINGS.map((m, i) => (
              <div key={i} className={`list-item ${m.inconsistent ? 'inconsistent-item' : ''}`}>
                <div style={{ marginRight: '1rem' }}>
                  <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {m.code}
                    {m.inconsistent && <AlertCircle size={14} color="#ef4444" className="animate-warning" />}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{m.jurisdiction}</div>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>{m.name}</div>
                  <div style={{ fontSize: '0.75rem', color: '#6366f1', fontFamily: 'monospace' }}>{m.match}</div>
                  {m.inconsistent && <div className="audit-note">{m.note}</div>}
                </div>
                <div>
                  <div style={{ textAlign: 'right', fontWeight: 600, color: m.inconsistent ? '#ef4444' : '#10b981' }}>
                    {(m.score * 100).toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8', textAlign: 'right' }}>{m.method}</div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card"
        >
          <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Status by Jurisdiction</h2>
          <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginBottom: '1rem' }}>Illustrative — not live API data</div>
          {[
            { j: 'MX', p: 98 },
            { j: 'BR', p: 92 },
            { j: 'FR', p: 88 },
            { j: 'RU', p: 85 },
            { j: 'IL', p: 91 },
            { j: 'IN', p: 89 }
          ].map((item, i) => (
            <div key={i} style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                <span>{item.j}</span>
                <span>{item.p}%</span>
              </div>
              <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.p}%` }}
                  transition={{ duration: 1, delay: i * 0.1 }}
                  style={{ height: '100%', background: '#6366f1', borderRadius: '2px' }}
                ></motion.div>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

export default App;

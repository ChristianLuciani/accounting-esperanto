import React, { useState, useEffect } from 'react';
import { LayoutGrid, PieChart, Activity, Globe, CheckCircle2, AlertCircle, Search, Layers, RefreshCcw } from 'lucide-react';
import { motion } from 'framer-motion';

const API_BASE_URL = "http://localhost:8000";

const App = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState([
    { label: 'Coverage', value: '0%', icon: CheckCircle2, color: '#10b981' },
    { label: 'Entities', value: '0', icon: Globe, color: '#6366f1' },
    { label: 'Ontology Nodes', value: '0', icon: Layers, color: '#a855f7' },
    { label: 'System Status', value: 'Offline', icon: Activity, color: '#ef4444' },
  ]);
  const [recentMappings, setRecentMappings] = useState([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Fetch Health
      const healthRes = await fetch(`${API_BASE_URL}/health`);
      const isHealthy = healthRes.ok;
      
      // 2. Fetch Accounts (Ontology)
      const accountsRes = await fetch(`${API_BASE_URL}/accounts`);
      const accountsData = await accountsRes.json();
      
      setStats([
        { label: 'Coverage', value: '94.2%', icon: CheckCircle2, color: '#10b981' },
        { label: 'Entities', value: '12', icon: Globe, color: '#6366f1' },
        { label: 'Ontology Nodes', value: accountsData.total.toString(), icon: Layers, color: '#a855f7' },
        { label: 'System Status', value: isHealthy ? 'Healthy' : 'Error', icon: Activity, color: isHealthy ? '#10b981' : '#ef4444' },
      ]);

      // Mock some recent mappings from the data we just got
      if (accountsData.accounts && accountsData.accounts.length > 0) {
        const samples = [
          {
            code: '101.01',
            name: 'Petty Cash Fund',
            jurisdiction: 'MX',
            match: 'asset.noncurrent.ppe',
            score: 0.3,
            method: 'semantic_ai',
            inconsistent: true,
            note: 'Deterministic Violation: Liquid asset mapped to Non-Current node.'
          },
          ...accountsData.accounts.slice(0, 4).map(acc => ({
            code: acc.local_codes?.mx || 'SYNC',
            name: acc.label_en,
            jurisdiction: 'MX',
            match: acc.id,
            score: 0.98,
            method: 'exact_lookup',
            inconsistent: false
          }))
        ];
        setRecentMappings(samples);
      }

    } catch (error) {
      console.error("API connection failed:", error);
      setStats(prev => prev.map(s => s.label === 'System Status' ? {...s, value: 'Offline', color: '#ef4444'} : s));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="dashboard-container">
      <header className="header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="title-badge">kontablo</div>
            <button 
                onClick={fetchData} 
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}
                title="Refresh Data"
            >
                <RefreshCcw size={18} className={loading ? "animate-spin" : ""} />
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
            <h2 style={{ fontSize: '1.25rem' }}>Global Account Mapping</h2>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <span className="badge badge-success">Live Sync</span>
              <span className="badge badge-warning">Audit Active</span>
            </div>
          </div>
          
          <div className="mapping-list">
            {recentMappings.length > 0 ? recentMappings.map((m, i) => (
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
                  <div style={{ 
                    textAlign: 'right', 
                    fontWeight: 600, 
                    color: m.inconsistent ? '#ef4444' : '#10b981' 
                  }}>
                    {(m.score * 100).toFixed(0)}%
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8', textAlign: 'right' }}>{m.method}</div>
                </div>
              </div>
            )) : (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>
                {loading ? "Initializing..." : "No mapping data available. Check API connection."}
              </div>
            )}
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card"
        >
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>Status by Jurisdiction</h2>
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

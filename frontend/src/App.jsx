import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AboutView from './components/AboutView';
import CorridorTrends from './components/CorridorTrends';
import ShippingAlertsTable from './components/ShippingAlertsTable';
import ChatAssistantView from './components/ChatAssistantView';
import { API_BASE } from './config';

export default function App() {
  const [activeTab, setActiveTab] = useState('about');
  const [summary, setSummary] = useState(null);
  const [corridors, setCorridors] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState('Mumbai-Pune');
  const [chatInitialQuery, setChatInitialQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/summary`).then((r) => r.json()),
      fetch(`${API_BASE}/api/corridors`).then((r) => r.json()),
      fetch(`${API_BASE}/api/anomalies`).then((r) => r.json()),
    ])
      .then(([sumData, corrData, anomData]) => {
        setSummary(sumData);
        setCorridors(corrData);
        setAnomalies(anomData);
        if (corrData && corrData.length > 0) {
          setSelectedRoute(corrData[0].route);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load API data:', err);
        setLoading(false);
      });
  }, []);

  const handleAskAboutAlert = (query) => {
    setChatInitialQuery(query);
    setActiveTab('chat');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-canvas)' }}>
      {/* Clean Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main Container */}
      <main style={{ maxWidth: '1280px', margin: '0 auto', width: '100%', padding: '28px 24px 64px 24px', flex: 1 }}>
        {/* Tab 1: About & Guide (Home) */}
        {activeTab === 'about' && (
          <div className="fade-in">
            <AboutView onNavigate={(tab) => setActiveTab(tab)} />
          </div>
        )}

        {/* Tab 2: Corridor Trends (The Trajectory Graph) */}
        {activeTab === 'trends' && (
          <div className="fade-in">
            <CorridorTrends
              corridors={corridors}
              selectedRoute={selectedRoute}
              onSelectRoute={setSelectedRoute}
            />

            {/* Simple Corridors Summary Grid */}
            <div className="minimal-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '6px' }}>
                All Monitored Corridors
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
                Click any corridor to view its 104-week cost trajectory in the graph above
              </p>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                gap: '12px'
              }}>
                {corridors.map((c) => (
                  <div
                    key={c.route}
                    onClick={() => {
                      setSelectedRoute(c.route);
                      window.scrollTo({ top: 80, behavior: 'smooth' });
                    }}
                    style={{
                      padding: '14px',
                      border: selectedRoute === c.route ? '1px solid #18181B' : '1px solid var(--border-light)',
                      borderRadius: '4px',
                      background: selectedRoute === c.route ? 'var(--bg-subtle)' : '#FFFFFF',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{c.route}</span>
                      <span className="badge badge-neutral mono" style={{ fontSize: '0.65rem' }}>{c.route_type}</span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Avg Rate: <strong className="mono" style={{ color: 'var(--text-main)' }}>₹{c.avg_cost_per_tonne_km.toFixed(2)}</strong> / t-km
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {c.shipment_count} shipments • {c.unjustified_anomalies_count + c.justified_anomalies_count} rate alerts
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Shipping Cost Alerts */}
        {activeTab === 'alerts' && (
          <div className="fade-in">
            <ShippingAlertsTable
              anomalies={anomalies}
              onAskAboutAlert={handleAskAboutAlert}
            />
          </div>
        )}

        {/* Tab 4: AI Freight Assistant */}
        {activeTab === 'chat' && (
          <div className="fade-in">
            <ChatAssistantView initialQuery={chatInitialQuery} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-light)',
        padding: '18px 24px',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        backgroundColor: '#FFFFFF'
      }}>
        <span>FreightTiger Shipping Rate Watchdog • Road Logistics Intelligence</span>
      </footer>
    </div>
  );
}

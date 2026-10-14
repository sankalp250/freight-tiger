import React from 'react';

export default function Navbar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'about', label: 'About & Guide' },
    { id: 'trends', label: 'Corridor Trends' },
    { id: 'alerts', label: 'Shipping Cost Alerts' },
    { id: 'chat', label: 'AI Assistant' },
  ];

  return (
    <header style={{
      borderBottom: '1px solid var(--border-light)',
      backgroundColor: '#FFFFFF',
      position: 'sticky',
      top: 0,
      zIndex: 40
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '0 24px',
        height: '60px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Brand */}
        <div
          onClick={() => setActiveTab('about')}
          style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}
        >
          <div style={{
            width: '28px',
            height: '28px',
            background: '#18181B',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            fontWeight: 700,
            fontSize: '0.85rem'
          }}>
            FT
          </div>
          <div>
            <span style={{ fontWeight: 600, fontSize: '0.95rem', letterSpacing: '-0.01em' }}>
              FreightTiger
            </span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginLeft: '6px' }}>
              / Rate Watchdog
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '6px' }}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: 'none',
                border: 'none',
                padding: '8px 14px',
                fontSize: '0.85rem',
                fontWeight: activeTab === tab.id ? 600 : 400,
                color: activeTab === tab.id ? 'var(--text-main)' : 'var(--text-muted)',
                cursor: 'pointer',
                borderRadius: '4px',
                borderBottom: activeTab === tab.id ? '2px solid #18181B' : '2px solid transparent',
                transition: 'all 0.15s ease'
              }}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Quick CTA */}
        <div>
          <button
            onClick={() => setActiveTab('chat')}
            className="btn-primary"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.8rem',
              padding: '6px 14px'
            }}
          >
            <span>Ask AI Assistant</span>
          </button>
        </div>
      </div>
    </header>
  );
}

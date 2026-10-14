import React from 'react';

export default function AboutView({ onNavigate }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Hero Welcome Card */}
      <div className="minimal-card" style={{ padding: '36px', background: '#FFFFFF' }}>
        <div style={{ maxWidth: '800px' }}>
          <span className="badge badge-neutral mono" style={{ marginBottom: '12px', fontSize: '0.75rem' }}>
            Freight Logistics Rate Intelligence
          </span>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 600, letterSpacing: '-0.02em', color: '#18181B', lineHeight: 1.25, marginBottom: '12px' }}>
            Smart Shipping Cost Watchdog
          </h1>
          <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '24px' }}>
            In road logistics across India, shipping rates can quietly creep up on key corridors. 
            Sometimes the increase has a legitimate real-world cause — such as monsoon flooding forcing detours, 
            regional festival surcharges, or nationwide diesel price increases. Other times, the cost rise is unjustified.
            This watchdog tracks rates week-by-week, flags suspicious spikes, and explains why in plain English.
          </p>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={() => onNavigate('trends')}
              className="btn-primary"
              style={{ padding: '8px 18px', fontSize: '0.85rem' }}
            >
              View Corridor Graphs →
            </button>
            <button
              onClick={() => onNavigate('alerts')}
              className="btn-secondary"
              style={{ padding: '8px 18px', fontSize: '0.85rem' }}
            >
              View Flagged Rate Alerts
            </button>
            <button
              onClick={() => onNavigate('chat')}
              className="btn-secondary"
              style={{ padding: '8px 18px', fontSize: '0.85rem' }}
            >
              Ask AI Assistant
            </button>
          </div>
        </div>
      </div>

      {/* Explanatory 3-Column Bento Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '20px'
      }}>
        {/* Card 1: The Metric */}
        <div className="minimal-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '4px',
            background: 'var(--bg-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 600,
            fontSize: '0.85rem'
          }}>
            1
          </div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Fair Normalized Cost</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Total trip cost can be misleading because trucks carry different weights over different distances.
            We normalize every shipment into <strong>Cost per Tonne-Kilometer (₹/t-km)</strong>:
          </p>
          <div className="mono" style={{
            background: 'var(--bg-subtle)',
            padding: '10px 14px',
            borderRadius: '4px',
            fontSize: '0.75rem',
            border: '1px solid var(--border-light)'
          }}>
            Total Freight Cost ÷ (Tonnes × Distance in Km)
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            All shipments are grouped into standard Monday-to-Sunday calendar weeks.
          </p>
        </div>

        {/* Card 2: The Two Baselines */}
        <div className="minimal-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '4px',
            background: 'var(--bg-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 600,
            fontSize: '0.85rem'
          }}>
            2
          </div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Two Strict Baselines</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            To know if a price is unusual, the system compares it against two exact standards:
          </p>
          <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <li>
              <strong>Against Own Past History</strong>: The route's rolling average over the prior 8 weeks (no future data peek).
            </li>
            <li>
              <strong>Against Similar Routes</strong>: The average cost of other routes with similar length (Short, Medium, or Long) during the same week.
            </li>
          </ul>
        </div>

        {/* Card 3: The AI Assistant */}
        <div className="minimal-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '4px',
            background: 'var(--bg-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 600,
            fontSize: '0.85rem'
          }}>
            3
          </div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Grounded AI Assistant</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            When a route spikes, our AI assistant checks real context notes (fuel price updates, weather disruptions, festival surcharges).
          </p>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            If a legitimate note explains the rise, it marks it as <strong>Legitimate</strong> with the exact reason. 
            If no valid reason exists, it flags it as <strong>Needs Human Review</strong>.
          </p>
          <div style={{ marginTop: 'auto' }}>
            <span className="badge badge-blue mono" style={{ fontSize: '0.7rem' }}>
              Powered by Live Google Gemini AI
            </span>
          </div>
        </div>
      </div>

      {/* Corridors Monitored Overview */}
      <div className="minimal-card" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '6px' }}>
          Corridors Monitored Across India
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          7 representative freight lanes tracked over 104 weeks (January 2024 to December 2025):
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '12px'
        }}>
          {[
            { route: 'Mumbai - Pune', type: 'Short Corridor', dist: '~150 km' },
            { route: 'Delhi - Jaipur', type: 'Short Corridor', dist: '~280 km' },
            { route: 'Chennai - Bangalore', type: 'Medium Corridor', dist: '~350 km' },
            { route: 'Kolkata - Bhubaneswar', type: 'Medium Corridor', dist: '~440 km' },
            { route: 'Ahmedabad - Mumbai', type: 'Medium Corridor', dist: '~530 km' },
            { route: 'Mumbai - Delhi', type: 'Long Corridor', dist: '~1,400 km' },
            { route: 'Delhi - Chennai', type: 'Long Corridor', dist: '~2,200 km' },
          ].map((corridor, i) => (
            <div
              key={i}
              style={{
                padding: '12px 14px',
                border: '1px solid var(--border-light)',
                borderRadius: '4px',
                background: 'var(--bg-subtle)'
              }}
            >
              <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{corridor.route}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                {corridor.type} • {corridor.dist}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';

export default function ShippingAlertsTable({ anomalies, onAskAboutAlert }) {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  if (!anomalies) return null;

  const filtered = anomalies.filter((item) => {
    if (filter === 'unexplained' && item.flagged !== 'Yes') return false;
    if (filter === 'justified' && item.flagged !== 'No (justified)') return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        item.route.toLowerCase().includes(q) ||
        item.week_of.includes(q) ||
        item.reason.toLowerCase().includes(q) ||
        item.matched_note_id.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const unexplainedCount = anomalies.filter((a) => a.flagged === 'Yes').length;
  const justifiedCount = anomalies.filter((a) => a.flagged === 'No (justified)').length;

  return (
    <div className="minimal-card" style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, letterSpacing: '-0.01em' }}>
            Shipping Cost Alerts & Flagged Routes
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Routes where weekly cost per tonne-km rose significantly above past average or similar-length routes
          </p>
        </div>

        {/* Search & Filter Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input
            type="text"
            placeholder="Search route or date..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              padding: '6px 12px',
              fontSize: '0.8rem',
              border: '1px solid var(--border-light)',
              borderRadius: '4px',
              outline: 'none',
              width: '180px'
            }}
          />

          <div style={{ display: 'flex', gap: '4px' }}>
            <button
              onClick={() => setFilter('all')}
              className={`btn-secondary ${filter === 'all' ? 'active' : ''}`}
              style={{ fontSize: '0.75rem', padding: '5px 10px' }}
            >
              All Alerts ({anomalies.length})
            </button>
            <button
              onClick={() => setFilter('unexplained')}
              className={`btn-secondary ${filter === 'unexplained' ? 'active' : ''}`}
              style={{ fontSize: '0.75rem', padding: '5px 10px' }}
            >
              Needs Review ({unexplainedCount})
            </button>
            <button
              onClick={() => setFilter('justified')}
              className={`btn-secondary ${filter === 'justified' ? 'active' : ''}`}
              style={{ fontSize: '0.75rem', padding: '5px 10px' }}
            >
              Legitimate ({justifiedCount})
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>Corridor</th>
              <th>Week Of</th>
              <th>Actual Rate</th>
              <th>vs. Past 8-Wk Avg</th>
              <th>vs. Similar Routes</th>
              <th>Status</th>
              <th>Note ID</th>
              <th>Reason & Context</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                  No shipping alerts match your filter.
                </td>
              </tr>
            ) : (
              filtered.map((row, idx) => {
                const isNeedsReview = row.flagged === 'Yes';
                return (
                  <tr key={idx}>
                    <td>
                      <span style={{ fontWeight: 600 }}>{row.route}</span>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: '6px' }}>
                        ({row.route_type})
                      </span>
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem' }}>{row.week_of}</td>
                    <td className="mono" style={{ fontWeight: 600 }}>
                      ₹{parseFloat(row.cost_per_tonne_km).toFixed(2)}/t-km
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem', color: '#B91C1C' }}>
                      {row.vs_own_history}
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem', color: '#B91C1C' }}>
                      {row.vs_similar_routes}
                    </td>
                    <td>
                      <span className={`badge ${isNeedsReview ? 'badge-red' : 'badge-blue'} mono`}>
                        {isNeedsReview ? 'Needs Review' : 'Legitimate Rise'}
                      </span>
                    </td>
                    <td>
                      {row.matched_note_id ? (
                        <span className="badge badge-neutral mono" style={{ fontWeight: 600 }}>
                          {row.matched_note_id}
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>—</span>
                      )}
                    </td>
                    <td style={{ fontSize: '0.8rem', lineHeight: '1.4', maxWidth: '360px' }}>
                      {row.reason}
                    </td>
                    <td>
                      <button
                        onClick={() => onAskAboutAlert && onAskAboutAlert(`Why did ${row.route} have a cost rise on ${row.week_of}?`)}
                        className="btn-secondary"
                        style={{ fontSize: '0.7rem', padding: '3px 8px', whiteSpace: 'nowrap' }}
                      >
                        Ask AI 💬
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

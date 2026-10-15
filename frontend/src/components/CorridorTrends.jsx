import React, { useState, useEffect } from 'react';
import { API_BASE } from '../config';

export default function CorridorTrends({ corridors, selectedRoute, onSelectRoute }) {
  const [trendsData, setTrendsData] = useState(null);
  const [hoveredWeek, setHoveredWeek] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedRoute) return;
    setLoading(true);
    fetch(`${API_BASE}/api/trends?route=${encodeURIComponent(selectedRoute)}`)
      .then((res) => res.json())
      .then((data) => {
        setTrendsData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching trends:', err);
        setLoading(false);
      });
  }, [selectedRoute]);

  if (!corridors || corridors.length === 0) return null;

  const weeks = trendsData?.weeks || [];
  const minCost = weeks.length > 0 ? Math.min(...weeks.map((w) => w.cost_per_tonne_km)) * 0.85 : 0;
  const maxCost = weeks.length > 0 ? Math.max(...weeks.map((w) => w.cost_per_tonne_km)) * 1.15 : 5;

  // Chart coordinate mapping
  const chartWidth = 960;
  const chartHeight = 260;
  const padding = { top: 20, right: 30, bottom: 30, left: 50 };
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  const getX = (idx) => padding.left + (idx / Math.max(weeks.length - 1, 1)) * innerWidth;
  const getY = (val) => {
    if (val === null || val === undefined) return null;
    const ratio = (val - minCost) / Math.max(maxCost - minCost, 0.01);
    return padding.top + innerHeight - ratio * innerHeight;
  };

  // Generate SVG path points
  const actualPoints = weeks.map((w, i) => `${getX(i)},${getY(w.cost_per_tonne_km)}`).join(' ');
  const histPoints = weeks
    .map((w, i) => (w.hist_avg !== null ? `${getX(i)},${getY(w.hist_avg)}` : null))
    .filter(Boolean)
    .join(' ');
  const peerPoints = weeks
    .map((w, i) => (w.peer_avg !== null ? `${getX(i)},${getY(w.peer_avg)}` : null))
    .filter(Boolean)
    .join(' ');

  return (
    <div className="minimal-card" style={{ padding: '24px', marginBottom: '24px' }}>
      {/* Header & Corridor Switcher */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 600, letterSpacing: '-0.01em' }}>
            Corridor Shipping Cost Trajectory
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Comparing Actual Weekly Cost per Tonne-Km against the Past 8-Week Average and Similar Routes
          </p>
        </div>

        {/* Corridor Pill Selectors */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {corridors.map((c) => (
            <button
              key={c.route}
              onClick={() => onSelectRoute(c.route)}
              className={`btn-secondary ${selectedRoute === c.route ? 'active' : ''}`}
              style={{ fontSize: '0.75rem', padding: '5px 10px' }}
            >
              {c.route}
              <span style={{ opacity: 0.65, marginLeft: '4px', fontSize: '0.65rem' }}>
                ({c.route_type})
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* SVG Chart */}
      {loading ? (
        <div style={{ height: '260px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Loading corridor time-series...
        </div>
      ) : weeks.length > 0 ? (
        <div style={{ position: 'relative' }}>
          <svg
            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
            style={{ width: '100%', height: 'auto', overflow: 'visible', display: 'block' }}
          >
            {/* Grid Lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
              const y = padding.top + innerHeight * (1 - pct);
              const val = minCost + pct * (maxCost - minCost);
              return (
                <g key={i}>
                  <line
                    x1={padding.left}
                    y1={y}
                    x2={padding.left + innerWidth}
                    y2={y}
                    stroke="#F0F0EE"
                    strokeWidth="1"
                  />
                  <text
                    x={padding.left - 8}
                    y={y + 4}
                    textAnchor="end"
                    fontSize="10"
                    fill="#A1A1AA"
                    className="mono"
                  >
                    ₹{val.toFixed(2)}
                  </text>
                </g>
              );
            })}

            {/* Peer Baseline (Dotted blue) */}
            {peerPoints && (
              <polyline
                fill="none"
                stroke="#93C5FD"
                strokeWidth="1.5"
                strokeDasharray="3 3"
                points={peerPoints}
              />
            )}

            {/* Historical 8-Week Baseline (Dashed gray) */}
            {histPoints && (
              <polyline
                fill="none"
                stroke="#A1A1AA"
                strokeWidth="1.5"
                strokeDasharray="4 4"
                points={histPoints}
              />
            )}

            {/* Actual Cost per Tonne-Km (Solid dark) */}
            <polyline
              fill="none"
              stroke="#18181B"
              strokeWidth="2"
              points={actualPoints}
            />

            {/* Anomaly & Data Points */}
            {weeks.map((w, i) => {
              const cx = getX(i);
              const cy = getY(w.cost_per_tonne_km);
              const isFlagged = w.flagged === 'Yes';
              const isJustified = w.flagged === 'No (justified)';

              if (isFlagged || isJustified) {
                return (
                  <circle
                    key={i}
                    cx={cx}
                    cy={cy}
                    r={isFlagged ? 5.5 : 4.5}
                    fill={isFlagged ? '#EF4444' : '#3B82F6'}
                    stroke="#FFFFFF"
                    strokeWidth="2"
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={() => setHoveredWeek(w)}
                  />
                );
              }
              return null;
            })}

            {/* Date labels on X-Axis */}
            {[0, 26, 52, 78, 103].map((idx) => {
              if (!weeks[idx]) return null;
              return (
                <text
                  key={idx}
                  x={getX(idx)}
                  y={chartHeight - 8}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#71717A"
                  className="mono"
                >
                  {weeks[idx].week_of}
                </text>
              );
            })}
          </svg>

          {/* Chart Legend */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '24px',
            marginTop: '16px',
            fontSize: '0.75rem',
            color: 'var(--text-muted)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '16px', height: '2px', background: '#18181B' }}></div>
              <span>Actual Cost / t-km</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '16px', height: '2px', borderTop: '2px dashed #A1A1AA' }}></div>
              <span>Trailing 8-Wk Historical Baseline</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '16px', height: '2px', borderTop: '2px dotted #93C5FD' }}></div>
              <span>Peer Corridor Baseline (Same Type)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#EF4444' }}></div>
              <span>Unexplained Spike (Flagged)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#3B82F6' }}></div>
              <span>Justified Rise (Verified Note)</span>
            </div>
          </div>

          {/* Hover Tooltip Card */}
          {hoveredWeek && (
            <div style={{
              marginTop: '14px',
              padding: '12px 16px',
              backgroundColor: 'var(--bg-subtle)',
              border: '1px solid var(--border-light)',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '0.8rem'
            }}>
              <div>
                <span className="mono" style={{ fontWeight: 600 }}>Week of {hoveredWeek.week_of}: </span>
                <span>Actual ₹{hoveredWeek.cost_per_tonne_km.toFixed(2)} / t-km</span>
                <span style={{ color: 'var(--text-muted)', marginLeft: '8px' }}>
                  (Hist: {hoveredWeek.hist_pct > 0 ? `+${hoveredWeek.hist_pct}%` : `${hoveredWeek.hist_pct}%`}, Peers: {hoveredWeek.peer_pct > 0 ? `+${hoveredWeek.peer_pct}%` : `${hoveredWeek.peer_pct}%`})
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className={`badge ${hoveredWeek.flagged === 'Yes' ? 'badge-red' : 'badge-blue'} mono`}>
                  {hoveredWeek.flagged}
                </span>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {hoveredWeek.reason}
                </span>
              </div>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}

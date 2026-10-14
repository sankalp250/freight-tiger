import React, { useState } from 'react';

export default function ChatAssistantView({ initialQuery }) {
  const [query, setQuery] = useState(initialQuery || '');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hello! I am your FreightTiger Shipping Rate Assistant. Ask me any question in plain English about corridor rates, price spikes, or real-world justifications (e.g., diesel price increases, flood detours, festival surcharges).",
      provider: 'Google Gemini'
    }
  ]);
  const [loading, setLoading] = useState(false);

  const sampleQuestions = [
    "Why did Chennai-Bangalore freight cost spike in late February 2025?",
    "Explain what caused the rate increase on Ahmedabad-Mumbai in January 2025.",
    "Did nationwide diesel price increases impact freight rates in May 2025?",
    "Which routes had unexplained cost spikes in late 2025?",
    "What is the average shipping rate on Mumbai-Delhi?"
  ];

  const handleSend = async (customText) => {
    const textToSend = customText || query;
    if (!textToSend.trim() || loading) return;

    const newHistory = [...messages, { role: 'user', text: textToSend }];
    setMessages(newHistory);
    setQuery('');
    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: textToSend })
      });
      const data = await res.json();
      setMessages([
        ...newHistory,
        {
          role: 'assistant',
          text: data.answer,
          citations: data.citations || [],
          provider: data.provider || 'Google Gemini'
        }
      ]);
    } catch (err) {
      setMessages([
        ...newHistory,
        { role: 'assistant', text: 'Error connecting to the Freight Assistant service. Please verify the backend server is running.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header Banner */}
      <div className="minimal-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 600, letterSpacing: '-0.01em' }}>
              AI Freight Rate Assistant
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Ask natural language questions about shipping rates, route spikes, and verified context notes
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <span className="badge badge-blue mono" style={{ fontSize: '0.75rem' }}>
              Primary: Google Gemini 2.5 Flash
            </span>
            <span className="badge badge-neutral mono" style={{ fontSize: '0.75rem' }}>
              Fallback: Groq
            </span>
          </div>
        </div>

        {/* Quick Suggestion Pills */}
        <div style={{ marginTop: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase', fontWeight: 500 }}>
            Click to Ask Suggested Questions:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {sampleQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSend(q)}
                className="btn-secondary"
                style={{ fontSize: '0.75rem', padding: '6px 12px', textAlign: 'left' }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Messages Container */}
      <div className="minimal-card" style={{ padding: '24px', minHeight: '420px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '20px' }}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '85%'
              }}
            >
              <div style={{
                fontSize: '0.7rem',
                color: 'var(--text-muted)',
                marginBottom: '4px',
                textAlign: msg.role === 'user' ? 'right' : 'left'
              }}>
                {msg.role === 'user' ? 'You' : `Freight Watchdog AI • ${msg.provider || 'Gemini'}`}
              </div>
              <div style={{
                padding: '12px 18px',
                borderRadius: '6px',
                fontSize: '0.88rem',
                lineHeight: 1.6,
                background: msg.role === 'user' ? '#18181B' : 'var(--bg-subtle)',
                color: msg.role === 'user' ? '#FFFFFF' : 'var(--text-main)',
                border: msg.role === 'user' ? 'none' : '1px solid var(--border-light)',
                whiteSpace: 'pre-wrap'
              }}>
                {msg.text}
              </div>
              {msg.citations && msg.citations.length > 0 && (
                <div style={{ marginTop: '6px', display: 'flex', gap: '6px' }}>
                  {msg.citations.map((c) => (
                    <span key={c} className="badge badge-neutral mono" style={{ fontSize: '0.7rem' }}>
                      Verified Ground Truth Note: {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ alignSelf: 'flex-start', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Investigating route records & consulting Gemini AI...
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          style={{ display: 'flex', gap: '10px' }}
        >
          <input
            type="text"
            placeholder="Ask a question about shipping rates (e.g. 'Why did Delhi-Jaipur spike in November?')..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              padding: '10px 16px',
              fontSize: '0.88rem',
              border: '1px solid var(--border-light)',
              borderRadius: '4px',
              outline: 'none'
            }}
          />
          <button type="submit" className="btn-primary" disabled={loading} style={{ padding: '10px 20px' }}>
            Send Question
          </button>
        </form>
      </div>
    </div>
  );
}

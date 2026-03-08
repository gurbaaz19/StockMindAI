import { useState, useEffect } from 'react';

const API_BASE = "http://localhost:8000/api";

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedRec, setSelectedRec] = useState(null);

  const fetchRecommendations = async () => {
    try {
      const res = await fetch(`${API_BASE}/recommendations`);
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data);
      }
    } catch (err) {
      console.error("Failed to fetch recommendations", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Trigger re-analysis for one selected or just refresh the list. 
    // Here we just refresh the static list from DB.
    await fetchRecommendations();
  };

  const getTagClass = (action) => {
    const act = action.toLowerCase();
    if (act.includes('buy')) return 'buy';
    if (act.includes('sell')) return 'sell';
    return 'hold';
  };

  return (
    <div className="container">
      <div className="header-actions">
        <div>
          <h1 className="title" style={{ background: 'linear-gradient(135deg, #fff 0%, #cbd5e1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>StockMind AI</h1>
          <p className="subtitle" style={{ margin: 0, marginTop: '0.5rem' }}>Long-term AI Recommendation Engine</p>
        </div>
        
        <button className="refresh-btn glass" onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? <span className="loader"></span> : "🔄 Refresh"}
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', marginTop: '4rem', color: 'white' }}>
          <div className="loader" style={{ width: 40, height: 40 }}></div>
          <p style={{ marginTop: '1rem' }}>Analyzing Market Data...</p>
        </div>
      ) : (
        <div className="dashboard-grid">
          {recommendations.length > 0 ? recommendations.map((rec) => (
            <div key={rec.id} className="card glass" onClick={() => setSelectedRec(rec)}>
              <div className="card-header">
                <div>
                  <div className="ticker">{rec.country_flag} {rec.ticker}</div>
                  <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.2rem'}}>{rec.market_name}</div>
                  <div className="price">${rec.current_price.toFixed(2)}</div>
                </div>
                <div className={`tag ${getTagClass(rec.action)}`}>
                  {rec.action}
                </div>
              </div>
              
              <div className="confidence">
                 <span style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Confidence: {Math.round(rec.confidence * 100)}%</span>
                 <div className="confidence-bar">
                    <div className="confidence-fill" style={{ width: `${rec.confidence * 100}%` }}></div>
                 </div>
              </div>

              <div className="reasoning">
                {rec.reasoning}
              </div>
            </div>
          )) : (
            <div style={{color: 'white', gridColumn: '1 / -1', textAlign: 'center'}}>
              No tracking data found. Watchlist processing might be in progress!
            </div>
          )}
        </div>
      )}

      {selectedRec && (
        <div className="modal-overlay" onClick={() => setSelectedRec(null)}>
          <div className="modal-content glass" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedRec(null)}>×</button>
            <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{selectedRec.country_flag} {selectedRec.ticker} Report</h2>
            <div style={{fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1rem'}}>Market: {selectedRec.market_name}</div>
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', alignItems: 'center' }}>
              <span style={{ fontSize: '1.5rem', fontWeight: 600 }}>${selectedRec.current_price.toFixed(2)}</span>
              <span className={`tag ${getTagClass(selectedRec.action)}`} style={{ fontSize: '1rem', padding: '0.5rem 1rem' }}>
                {selectedRec.action}
              </span>
              <span style={{color: 'var(--text-secondary)'}}>Conf: {Math.round(selectedRec.confidence * 100)}%</span>
            </div>
            <div style={{ lineHeight: 1.8, color: '#e2e8f0', background: 'rgba(0,0,0,0.2)', padding: '1.5rem', borderRadius: '12px' }}>
              <h4 style={{ marginBottom: '1rem', color: 'var(--primary)' }}>AI Analyst Reasoning</h4>
              <div style={{ whiteSpace: 'pre-wrap' }}>{selectedRec.reasoning}</div>
              
              <div style={{ marginTop: '2rem', fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
                Last updated: {new Date(selectedRec.timestamp).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

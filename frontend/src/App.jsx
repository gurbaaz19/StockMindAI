import { useState, useEffect, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';

const API_BASE = "http://localhost:8000/api";
const WS_BASE = "ws://localhost:8000/ws";

const PERIODS = [
  { value: '1mo', label: '1M' },
  { value: '3mo', label: '3M' },
  { value: '6mo', label: '6M' },
  { value: '1y',  label: '1Y' },
  { value: '5y',  label: '5Y' },
];

const CURRENCIES = [
  'USD', 'EUR', 'GBP', 'JPY', 'INR', 'CNY', 'HKD', 'AUD',
  'CAD', 'CHF', 'SGD', 'KRW', 'TWD', 'BRL', 'MXN', 'ZAR',
  'SEK', 'NOK', 'DKK', 'NZD', 'TRY', 'AED', 'SAR', 'ILS',
  'THB', 'IDR', 'MYR', 'PHP', 'PLN', 'CZK', 'HUF',
];

const formatPrice = (price, currency = 'USD', symbol = '$') => {
  if (price == null || isNaN(price)) return '—';
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency,
      maximumFractionDigits: price >= 100 ? 2 : 4,
    }).format(price);
  } catch {
    return `${symbol}${Number(price).toFixed(2)}`;
  }
};

function PriceChart({ data, currency, symbol, height = 240 }) {
  if (!data || data.length === 0) {
    return <div className="chart-empty">No data available</div>;
  }
  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            tickFormatter={(d) => d.slice(5)}
            minTickGap={24}
          />
          <YAxis
            domain={['auto', 'auto']}
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            width={70}
            tickFormatter={(v) => formatPrice(v, currency, symbol)}
          />
          <Tooltip
            contentStyle={{
              background: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid rgba(255,255,255,0.15)',
              borderRadius: 8,
              color: '#f8fafc',
            }}
            labelStyle={{ color: '#cbd5e1' }}
            formatter={(value) => [formatPrice(value, currency, symbol), 'Close']}
          />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#6366f1"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#ec4899' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function HistoryPanel({ ticker, currency, symbol }) {
  const [period, setPeriod] = useState('1mo');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setErr(null);
      try {
        const res = await fetch(`${API_BASE}/history/${encodeURIComponent(ticker)}?period=${period}`);
        const data = await res.json();
        if (cancelled) return;
        if (data.error) {
          setErr(data.error);
          setHistory([]);
        } else {
          setHistory(data.history || []);
        }
      } catch (e) {
        if (!cancelled) setErr(String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [ticker, period]);

  return (
    <div className="history-panel">
      <div className="period-row">
        {PERIODS.map(p => (
          <button
            key={p.value}
            className={`period-btn ${period === p.value ? 'active' : ''}`}
            onClick={() => setPeriod(p.value)}
            type="button"
          >
            {p.label}
          </button>
        ))}
      </div>
      {loading ? (
        <div className="chart-loading"><div className="loader" style={{ width: 32, height: 32 }} /></div>
      ) : err ? (
        <div className="chart-empty">Could not load history: {err}</div>
      ) : (
        <PriceChart data={history} currency={currency} symbol={symbol} />
      )}
    </div>
  );
}

function FxConverter() {
  const [base, setBase] = useState('USD');
  const [quote, setQuote] = useState('INR');
  const [amount, setAmount] = useState('100');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  const fetchRate = async (b = base, q = quote) => {
    setLoading(true);
    setErr(null);
    try {
      const res = await fetch(`${API_BASE}/forex/${b}/${q}`);
      const json = await res.json();
      if (json.error) {
        setErr(json.error);
        setData(null);
      } else {
        setData(json);
      }
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRate('USD', 'INR');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchRate();
  };

  const handleSwap = () => {
    const newBase = quote;
    const newQuote = base;
    setBase(newBase);
    setQuote(newQuote);
    fetchRate(newBase, newQuote);
  };

  const converted = useMemo(() => {
    if (!data?.rate) return null;
    const n = parseFloat(amount);
    if (isNaN(n)) return null;
    return n * data.rate;
  }, [amount, data]);

  return (
    <div className="glass" style={{ padding: '2rem', marginTop: '1rem' }}>
      <h2 style={{ marginBottom: '0.5rem' }}>FX Converter</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Live currency rates from Yahoo Finance, with a 1-month rate history chart.
      </p>

      <form onSubmit={handleSubmit} className="fx-form">
        <input
          type="number"
          className="glass fx-input"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          step="any"
          min="0"
          placeholder="Amount"
        />
        <select className="glass fx-select" value={base} onChange={(e) => setBase(e.target.value)}>
          {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <button type="button" className="refresh-btn glass fx-swap" onClick={handleSwap} title="Swap">⇄</button>
        <select className="glass fx-select" value={quote} onChange={(e) => setQuote(e.target.value)}>
          {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <button type="submit" className="refresh-btn glass" disabled={loading}>
          {loading ? <span className="loader" style={{ width: 15, height: 15, borderWidth: 2 }} /> : 'Convert'}
        </button>
      </form>

      {err && <div className="chart-empty">Error: {err}</div>}

      {data && !err && (
        <>
          <div className="fx-result glass">
            <div className="fx-amount">
              {formatPrice(parseFloat(amount) || 0, base, base)} = <strong>{converted != null ? formatPrice(converted, quote, quote) : '—'}</strong>
            </div>
            <div className="fx-rate">1 {base} = {data.rate?.toFixed(6)} {quote}</div>
          </div>
          <div style={{ marginTop: '1.5rem' }}>
            <h4 style={{ marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>1M rate history ({base}/{quote})</h4>
            <PriceChart data={data.history || []} currency={quote} symbol={quote} height={260} />
          </div>
        </>
      )}
    </div>
  );
}

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedRec, setSelectedRec] = useState(null);

  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);

  const [basketCountry, setBasketCountry] = useState('');
  const [basket, setBasket] = useState([]);
  const [basketLoading, setBasketLoading] = useState(false);

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
    const ws = new WebSocket(WS_BASE);
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === "new_recommendation") {
          const newRec = message.data;
          setRecommendations(prev => {
            const idx = prev.findIndex(r => r.ticker === newRec.ticker);
            if (idx !== -1) {
              const updated = [...prev];
              updated[idx] = newRec;
              return updated;
            }
            return [newRec, ...prev];
          });
        }
      } catch (e) {
        console.error("WS parse error", e);
      }
    };
    ws.onclose = () => console.log("WebSocket Disconnected");
    return () => ws.close();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchRecommendations();
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      await fetch(`${API_BASE}/analyze/${encodeURIComponent(searchQuery.trim())}`, { method: 'POST' });
      setSearchQuery('');
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  const handleGenerateBasket = async (e) => {
    e.preventDefault();
    if (!basketCountry.trim()) return;
    setBasketLoading(true);
    try {
      const res = await fetch(`${API_BASE}/basket/${encodeURIComponent(basketCountry.trim())}`);
      if (res.ok) {
        const data = await res.json();
        setBasket(data.basket || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setBasketLoading(false);
    }
  };

  const getTagClass = (action) => {
    if (!action) return 'hold';
    const act = action.toLowerCase();
    if (act.includes('buy')) return 'buy';
    if (act.includes('sell')) return 'sell';
    return 'hold';
  };

  return (
    <div className="container">
      <div className="header-actions" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '1rem', marginBottom: '1rem' }}>
        <div>
          <h1 className="title" style={{ background: 'linear-gradient(135deg, #fff 0%, #cbd5e1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>StockMind AI</h1>
          <p className="subtitle" style={{ margin: 0, marginTop: '0.5rem' }}>Long-term AI Recommendation Engine — Global Markets</p>
        </div>

        <div className="tabs" style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
          <button className={`tag glass ${activeTab === 'dashboard' ? 'buy' : ''}`} style={{cursor: 'pointer'}} onClick={() => setActiveTab('dashboard')}>Real-Time Dashboard</button>
          <button className={`tag glass ${activeTab === 'baskets' ? 'buy' : ''}`} style={{cursor: 'pointer'}} onClick={() => setActiveTab('baskets')}>Curated Baskets</button>
          <button className={`tag glass ${activeTab === 'fx' ? 'buy' : ''}`} style={{cursor: 'pointer'}} onClick={() => setActiveTab('fx')}>FX Converter</button>
        </div>
      </div>

      {activeTab === 'dashboard' && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem', flex: 1, maxWidth: '500px' }}>
              <input
                type="text"
                placeholder="Search any ticker (AAPL, RELIANCE.NS, BARC.L, BTC-USD…)"
                className="glass"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ flex: 1, padding: '0.75rem 1rem', color: 'white', border: '1px solid var(--glass-border)', outline: 'none' }}
              />
              <button type="submit" className="refresh-btn glass" disabled={searching}>
                {searching ? <span className="loader" style={{ width: 15, height: 15, borderWidth: '2px' }}></span> : "Analyze"}
              </button>
            </form>

            <button className="refresh-btn glass" onClick={handleRefresh} disabled={refreshing}>
              {refreshing ? <span className="loader" style={{ width: 15, height: 15, borderWidth: '2px' }}></span> : "🔄 Refresh List"}
            </button>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', marginTop: '4rem', color: 'white' }}>
              <div className="loader" style={{ width: 40, height: 40 }}></div>
              <p style={{ marginTop: '1rem' }}>Connecting to data streams...</p>
            </div>
          ) : (
            <div className="dashboard-grid">
              {recommendations.length > 0 ? recommendations.map((rec) => (
                <div key={`${rec.id}-${rec.ticker}`} className="card glass" onClick={() => setSelectedRec(rec)}>
                  <div className="card-header">
                    <div>
                      <div className="ticker">{rec.country_flag} {rec.ticker}</div>
                      <div style={{fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.2rem'}}>{rec.market_name}</div>
                      <div className="price">{formatPrice(rec.current_price, rec.currency, rec.currency_symbol)}</div>
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
                  No tracking data found yet.
                </div>
              )}
            </div>
          )}
        </>
      )}

      {activeTab === 'baskets' && (
        <div className="glass" style={{ padding: '2rem', marginTop: '1rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>Country-Specific AI Baskets</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            Ask our AI to curate a specialized basket of top stocks or ETFs specifically from a requested country or region to diversify your long-term portfolio.
          </p>

          <form onSubmit={handleGenerateBasket} style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', maxWidth: '600px', flexWrap: 'wrap' }}>
            <input
              type="text"
              placeholder="Enter a country (e.g. India, Germany, China, Brazil)..."
              className="glass"
              value={basketCountry}
              onChange={(e) => setBasketCountry(e.target.value)}
              style={{ flex: 1, padding: '1rem', color: 'white', border: '1px solid var(--glass-border)', outline: 'none', fontSize: '1.1rem', minWidth: '300px' }}
            />
            <button type="submit" className="refresh-btn glass" style={{ padding: '0 2rem', fontSize: '1.1rem', background: 'rgba(99, 102, 241, 0.5)' }} disabled={basketLoading}>
              {basketLoading ? <span className="loader"></span> : "Curate Basket"}
            </button>
          </form>

          {basketLoading && (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'white' }}>
              <div className="loader" style={{ width: 50, height: 50 }}></div>
              <p style={{ marginTop: '1rem' }}>Our AI is researching appropriate assets in {basketCountry}...</p>
            </div>
          )}

          {basket.length > 0 && !basketLoading && (
            <div className="dashboard-grid">
              {basket.map((item, idx) => (
                <div key={idx} className="card glass">
                  <div className="card-header" style={{ alignItems: 'flex-start', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>
                    <div>
                      <div className="ticker">{item.ticker}</div>
                      <div style={{ fontSize: '0.9rem', color: '#e2e8f0', marginTop: '0.2rem' }}>{item.name}</div>
                      {item.currency && (
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>Listed in {item.currency}</div>
                      )}
                    </div>
                  </div>
                  <div className="reasoning" style={{ WebkitLineClamp: 'unset', maxHeight: 'none' }}>
                    {item.reasoning}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'fx' && <FxConverter />}

      {selectedRec && (
        <div className="modal-overlay" onClick={() => setSelectedRec(null)}>
          <div className="modal-content glass" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedRec(null)}>×</button>
            <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{selectedRec.country_flag} {selectedRec.ticker} Report</h2>
            <div style={{fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1rem'}}>
              Market: {selectedRec.market_name} · Currency: {selectedRec.currency || 'USD'}
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '1.5rem', fontWeight: 600 }}>
                {formatPrice(selectedRec.current_price, selectedRec.currency, selectedRec.currency_symbol)}
              </span>
              <span className={`tag ${getTagClass(selectedRec.action)}`} style={{ fontSize: '1rem', padding: '0.5rem 1rem' }}>
                {selectedRec.action}
              </span>
              <span style={{color: 'var(--text-secondary)'}}>Conf: {Math.round(selectedRec.confidence * 100)}%</span>
            </div>

            <HistoryPanel
              ticker={selectedRec.ticker}
              currency={selectedRec.currency || 'USD'}
              symbol={selectedRec.currency_symbol || '$'}
            />

            <div style={{ lineHeight: 1.8, color: '#e2e8f0', background: 'rgba(0,0,0,0.2)', padding: '1.5rem', borderRadius: '12px', marginTop: '1.5rem' }}>
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

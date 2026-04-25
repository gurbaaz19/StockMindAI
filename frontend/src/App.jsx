import { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
const WS_BASE = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

const PERIODS = [
  { value: '1mo', label: '1M' },
  { value: '3mo', label: '3M' },
  { value: '6mo', label: '6M' },
  { value: '1y',  label: '1Y' },
  { value: '5y',  label: '5Y' },
];

const CURRENCIES = [
  { code: 'USD', flag: '🇺🇸', name: 'US Dollar' },
  { code: 'EUR', flag: '🇪🇺', name: 'Euro' },
  { code: 'GBP', flag: '🇬🇧', name: 'British Pound' },
  { code: 'JPY', flag: '🇯🇵', name: 'Japanese Yen' },
  { code: 'INR', flag: '🇮🇳', name: 'Indian Rupee' },
  { code: 'CNY', flag: '🇨🇳', name: 'Chinese Yuan' },
  { code: 'HKD', flag: '🇭🇰', name: 'Hong Kong Dollar' },
  { code: 'AUD', flag: '🇦🇺', name: 'Australian Dollar' },
  { code: 'CAD', flag: '🇨🇦', name: 'Canadian Dollar' },
  { code: 'CHF', flag: '🇨🇭', name: 'Swiss Franc' },
  { code: 'SGD', flag: '🇸🇬', name: 'Singapore Dollar' },
  { code: 'KRW', flag: '🇰🇷', name: 'South Korean Won' },
  { code: 'TWD', flag: '🇹🇼', name: 'New Taiwan Dollar' },
  { code: 'BRL', flag: '🇧🇷', name: 'Brazilian Real' },
  { code: 'MXN', flag: '🇲🇽', name: 'Mexican Peso' },
  { code: 'ZAR', flag: '🇿🇦', name: 'South African Rand' },
  { code: 'SEK', flag: '🇸🇪', name: 'Swedish Krona' },
  { code: 'NOK', flag: '🇳🇴', name: 'Norwegian Krone' },
  { code: 'DKK', flag: '🇩🇰', name: 'Danish Krone' },
  { code: 'NZD', flag: '🇳🇿', name: 'New Zealand Dollar' },
  { code: 'TRY', flag: '🇹🇷', name: 'Turkish Lira' },
  { code: 'AED', flag: '🇦🇪', name: 'UAE Dirham' },
  { code: 'SAR', flag: '🇸🇦', name: 'Saudi Riyal' },
  { code: 'ILS', flag: '🇮🇱', name: 'Israeli New Shekel' },
  { code: 'THB', flag: '🇹🇭', name: 'Thai Baht' },
  { code: 'IDR', flag: '🇮🇩', name: 'Indonesian Rupiah' },
  { code: 'MYR', flag: '🇲🇾', name: 'Malaysian Ringgit' },
  { code: 'PHP', flag: '🇵🇭', name: 'Philippine Peso' },
  { code: 'PLN', flag: '🇵🇱', name: 'Polish Zloty' },
  { code: 'CZK', flag: '🇨🇿', name: 'Czech Koruna' },
  { code: 'HUF', flag: '🇭🇺', name: 'Hungarian Forint' },
  { code: 'RUB', flag: '🇷🇺', name: 'Russian Ruble' },
  { code: 'VND', flag: '🇻🇳', name: 'Vietnamese Dong' },
  { code: 'ISK', flag: '🇮🇸', name: 'Icelandic Króna' },
  { code: 'EGP', flag: '🇪🇬', name: 'Egyptian Pound' },
  { code: 'CLP', flag: '🇨🇱', name: 'Chilean Peso' },
  { code: 'COP', flag: '🇨🇴', name: 'Colombian Peso' },
  { code: 'PEN', flag: '🇵🇪', name: 'Peruvian Sol' },
  { code: 'ARS', flag: '🇦🇷', name: 'Argentine Peso' },
  { code: 'QAR', flag: '🇶🇦', name: 'Qatari Riyal' },
  { code: 'KWD', flag: '🇰🇼', name: 'Kuwaiti Dinar' },
  { code: 'OMR', flag: '🇴🇲', name: 'Omani Rial' },
  { code: 'BHD', flag: '🇧🇭', name: 'Bahraini Dinar' },
  { code: 'PKR', flag: '🇵🇰', name: 'Pakistani Rupee' },
  { code: 'BDT', flag: '🇧🇩', name: 'Bangladeshi Taka' },
  { code: 'LKR', flag: '🇱🇰', name: 'Sri Lankan Rupee' },
  { code: 'UAH', flag: '🇺🇦', name: 'Ukrainian Hryvnia' },
  { code: 'RON', flag: '🇷🇴', name: 'Romanian Leu' },
  { code: 'BGN', flag: '🇧🇬', name: 'Bulgarian Lev' },
  { code: 'NGN', flag: '🇳🇬', name: 'Nigerian Naira' },
  { code: 'KES', flag: '🇰🇪', name: 'Kenyan Shilling' },
  { code: 'GHS', flag: '🇬🇭', name: 'Ghanaian Cedi' },
  { code: 'KZT', flag: '🇰🇿', name: 'Kazakhstani Tenge' },
  { code: 'MAD', flag: '🇲🇦', name: 'Moroccan Dirham' },
  { code: 'DZD', flag: '🇩🇿', name: 'Algerian Dinar' },
  { code: 'AOA', flag: '🇦🇴', name: 'Angolan Kwanza' },
  { code: 'AMD', flag: '🇦🇲', name: 'Armenian Dram' },
  { code: 'AZN', flag: '🇦🇿', name: 'Azerbaijani Manat' },
  { code: 'BAM', flag: '🇧🇦', name: 'Bosnia-Herzegovina Mark' },
  { code: 'BBD', flag: '🇧🇧', name: 'Barbadian Dollar' },
  { code: 'BIF', flag: '🇧🇮', name: 'Burundian Franc' },
  { code: 'BMD', flag: '🇧🇲', name: 'Bermudian Dollar' },
  { code: 'BND', flag: '🇧🇳', name: 'Brunei Dollar' },
  { code: 'BOB', flag: '🇧🇴', name: 'Bolivian Boliviano' },
  { code: 'BSD', flag: '🇧🇸', name: 'Bahamian Dollar' },
  { code: 'BTN', flag: '🇧🇹', name: 'Bhutanese Ngultrum' },
  { code: 'BWP', flag: '🇧🇼', name: 'Botswanan Pula' },
  { code: 'BYN', flag: '🇧🇾', name: 'Belarusian Ruble' },
  { code: 'BZD', flag: '🇧🇿', name: 'Belize Dollar' },
  { code: 'CDF', flag: '🇨🇩', name: 'Congolese Franc' },
  { code: 'CRC', flag: '🇨🇷', name: 'Costa Rican Colón' },
  { code: 'CUP', flag: '🇨🇺', name: 'Cuban Peso' },
  { code: 'CVE', flag: '🇨🇻', name: 'Cape Verdean Escudo' },
  { code: 'DJF', flag: '🇩🇯', name: 'Djiboutian Franc' },
  { code: 'DOP', flag: '🇩🇴', name: 'Dominican Peso' },
  { code: 'ERN', flag: '🇪🇷', name: 'Eritrean Nakfa' },
  { code: 'ETB', flag: '🇪🇹', name: 'Ethiopian Birr' },
  { code: 'FJD', flag: '🇫🇯', name: 'Fijian Dollar' },
  { code: 'GEL', flag: '🇬🇪', name: 'Georgian Lari' },
  { code: 'GIP', flag: '🇬🇮', name: 'Gibraltar Pound' },
  { code: 'GMD', flag: '🇬🇲', name: 'Gambian Dalasi' },
  { code: 'GNF', flag: '🇬🇳', name: 'Guinean Franc' },
  { code: 'GTQ', flag: '🇬🇹', name: 'Guatemalan Quetzal' },
  { code: 'GYD', flag: '🇬🇾', name: 'Guyanese Dollar' },
  { code: 'HNL', flag: '🇭🇳', name: 'Honduran Lempira' },
  { code: 'HTG', flag: '🇭🇹', name: 'Haitian Gourde' },
  { code: 'IQD', flag: '🇮🇶', name: 'Iraqi Dinar' },
  { code: 'IRR', flag: '🇮🇷', name: 'Iranian Rial' },
  { code: 'JMD', flag: '🇯🇲', name: 'Jamaican Dollar' },
  { code: 'JOD', flag: '🇯🇴', name: 'Jordanian Dinar' },
  { code: 'KGS', flag: '🇰🇬', name: 'Kyrgystani Som' },
  { code: 'KHR', flag: '🇰🇭', name: 'Cambodian Riel' },
  { code: 'KMF', flag: '🇰🇲', name: 'Comorian Franc' },
  { code: 'KPW', flag: '🇰🇵', name: 'North Korean Won' },
  { code: 'KYD', flag: '🇰🇾', name: 'Cayman Islands Dollar' },
  { code: 'LAK', flag: '🇱🇦', name: 'Laotian Kip' },
  { code: 'LBP', flag: '🇱🇧', name: 'Lebanese Pound' },
  { code: 'LRD', flag: '🇱🇷', name: 'Liberian Dollar' },
  { code: 'LSL', flag: '🇱🇸', name: 'Lesotho Loti' },
  { code: 'LYD', flag: '🇱🇾', name: 'Libyan Dinar' },
  { code: 'MDL', flag: '🇲🇩', name: 'Moldovan Leu' },
  { code: 'MGA', flag: '🇲🇬', name: 'Malagasy Ariary' },
  { code: 'MKD', flag: '🇲🇰', name: 'Macedonian Denar' },
  { code: 'MMK', flag: '🇲🇲', name: 'Myanmar Kyat' },
  { code: 'MNT', flag: '🇲🇳', name: 'Mongolian Tugrik' },
  { code: 'MOP', flag: '🇲🇴', name: 'Macanese Pataca' },
  { code: 'MRU', flag: '🇲🇷', name: 'Mauritanian Ouguiya' },
  { code: 'MUR', flag: '🇲🇺', name: 'Mauritian Rupee' },
  { code: 'MVR', flag: '🇲🇻', name: 'Maldivian Rufiyaa' },
  { code: 'MWK', flag: '🇲🇼', name: 'Malawian Kwacha' },
  { code: 'MZN', flag: '🇲🇿', name: 'Mozambican Metical' },
  { code: 'NAD', flag: '🇳🇦', name: 'Namibian Dollar' },
  { code: 'NIO', flag: '🇳🇮', name: 'Nicaraguan Córdoba' },
  { code: 'NPR', flag: '🇳🇵', name: 'Nepalese Rupee' },
  { code: 'PAB', flag: '🇵🇦', name: 'Panamanian Balboa' },
  { code: 'PGK', flag: '🇵🇬', name: 'Papua New Guinean Kina' },
  { code: 'PYG', flag: '🇵🇾', name: 'Paraguayan Guarani' },
  { code: 'RWF', flag: '🇷🇼', name: 'Rwandan Franc' },
  { code: 'SBD', flag: '🇸🇧', name: 'Solomon Islands Dollar' },
  { code: 'SCR', flag: '🇸🇨', name: 'Seychellois Rupee' },
  { code: 'SDG', flag: '🇸🇩', name: 'Sudanese Pound' },
  { code: 'SHP', flag: '🇸🇭', name: 'Saint Helena Pound' },
  { code: 'SLL', flag: '🇸🇱', name: 'Sierra Leonean Leone' },
  { code: 'SOS', flag: '🇸🇴', name: 'Somali Shilling' },
  { code: 'SRD', flag: '🇸🇷', name: 'Surinamese Dollar' },
  { code: 'SSP', flag: '🇸🇸', name: 'South Sudanese Pound' },
  { code: 'STN', flag: '🇸🇹', name: 'São Tomé & Príncipe Dobra' },
  { code: 'SYP', flag: '🇸🇾', name: 'Syrian Pound' },
  { code: 'SZL', flag: '🇸🇿', name: 'Swazi Lilangeni' },
  { code: 'TJS', flag: '🇹🇯', name: 'Tajikistani Somoni' },
  { code: 'TMT', flag: '🇹🇲', name: 'Turkmenistani Manat' },
  { code: 'TND', flag: '🇹🇳', name: 'Tunisian Dinar' },
  { code: 'TOP', flag: '🇹🇴', name: 'Tongan Paʻanga' },
  { code: 'TTD', flag: '🇹🇹', name: 'Trinidad & Tobago Dollar' },
  { code: 'TZS', flag: '🇹🇿', name: 'Tanzanian Shilling' },
  { code: 'UGX', flag: '🇺🇬', name: 'Ugandan Shilling' },
  { code: 'UYU', flag: '🇺🇾', name: 'Uruguayan Peso' },
  { code: 'UZS', flag: '🇺🇿', name: 'Uzbekistani Som' },
  { code: 'VES', flag: '🇻🇪', name: 'Venezuelan Bolívar' },
  { code: 'VUV', flag: '🇻🇺', name: 'Vanuatu Vatu' },
  { code: 'WST', flag: '🇼🇸', name: 'Samoan Tala' },
  { code: 'XAF', flag: '🇨🇲', name: 'Central African CFA Franc' },
  { code: 'XCD', flag: '🇦🇬', name: 'East Caribbean Dollar' },
  { code: 'XOF', flag: '🇸🇳', name: 'West African CFA Franc' },
  { code: 'XPF', flag: '🇵🇫', name: 'CFP Franc' },
  { code: 'YER', flag: '🇾🇪', name: 'Yemeni Rial' },
  { code: 'ZMW', flag: '🇿🇲', name: 'Zambian Kwacha' },
  { code: 'ZWL', flag: '🇿🇼', name: 'Zimbabwean Dollar' },
];

const COUNTRIES = [
  { name: 'United States', flag: '🇺🇸' },
  { name: 'India', flag: '🇮🇳' },
  { name: 'United Kingdom', flag: '🇬🇧' },
  { name: 'Germany', flag: '🇩🇪' },
  { name: 'France', flag: '🇫🇷' },
  { name: 'Netherlands', flag: '🇳🇱' },
  { name: 'Italy', flag: '🇮🇹' },
  { name: 'Spain', flag: '🇪🇸' },
  { name: 'Switzerland', flag: '🇨🇭' },
  { name: 'Sweden', flag: '🇸🇪' },
  { name: 'Norway', flag: '🇳🇴' },
  { name: 'Denmark', flag: '🇩🇰' },
  { name: 'Finland', flag: '🇫🇮' },
  { name: 'Japan', flag: '🇯🇵' },
  { name: 'China', flag: '🇨🇳' },
  { name: 'Hong Kong', flag: '🇭🇰' },
  { name: 'South Korea', flag: '🇰🇷' },
  { name: 'Taiwan', flag: '🇹🇼' },
  { name: 'Singapore', flag: '🇸🇬' },
  { name: 'Australia', flag: '🇦🇺' },
  { name: 'New Zealand', flag: '🇳🇿' },
  { name: 'Canada', flag: '🇨🇦' },
  { name: 'Brazil', flag: '🇧🇷' },
  { name: 'Mexico', flag: '🇲🇽' },
  { name: 'South Africa', flag: '🇿🇦' },
  { name: 'Israel', flag: '🇮🇱' },
  { name: 'Saudi Arabia', flag: '🇸🇦' },
  { name: 'United Arab Emirates', flag: '🇦🇪' },
  { name: 'Turkey', flag: '🇹🇷' },
  { name: 'Thailand', flag: '🇹🇭' },
  { name: 'Indonesia', flag: '🇮🇩' },
  { name: 'Malaysia', flag: '🇲🇾' },
  { name: 'Philippines', flag: '🇵🇭' },
  { name: 'Russia', flag: '🇷🇺' },
  { name: 'Poland', flag: '🇵🇱' },
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

function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

function useClickOutside(ref, onOutside) {
  useEffect(() => {
    const onDoc = (e) => {
      if (ref.current && !ref.current.contains(e.target)) onOutside();
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, [ref, onOutside]);
}

function TickerSearch({ onSelect, disabled }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const debounced = useDebounce(query, 250);
  const wrapRef = useRef(null);
  useClickOutside(wrapRef, () => setOpen(false));

  useEffect(() => {
    let cancelled = false;
    if (!debounced.trim()) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
    setResults([]);
      return;
    }
    setLoading(true);
    fetch(`${API_BASE}/search?q=${encodeURIComponent(debounced.trim())}&limit=10`)
      .then(r => r.json())
      .then(data => {
        if (!cancelled) {
          setResults(data.results || []);
          setHighlight(0);
          setOpen(true);
        }
      })
      .catch(() => { if (!cancelled) setResults([]); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [debounced]);

  const handleSelect = (item) => {
    setQuery('');
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setResults([]);
    setOpen(false);
    onSelect(item);
  };

  const handleKey = (e) => {
    if (!open || results.length === 0) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (query.trim()) onSelect({ ticker: query.trim().toUpperCase() });
      }
      return;
    }
    if (e.key === 'ArrowDown') { e.preventDefault(); setHighlight(h => Math.min(h + 1, results.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setHighlight(h => Math.max(h - 1, 0)); }
    else if (e.key === 'Enter') { e.preventDefault(); handleSelect(results[highlight]); }
    else if (e.key === 'Escape') { setOpen(false); }
  };

  return (
    <div ref={wrapRef} className="combobox" style={{ flex: 1, maxWidth: 520 }}>
      <input
        type="text"
        className="glass combobox-input"
        placeholder="Search by name or symbol (HDFC, Apple, Tesla, BTC…)"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
        onKeyDown={handleKey}
        disabled={disabled}
        autoComplete="off"
      />
      {open && (
        <div className="combobox-menu glass">
          {loading && <div className="combobox-empty">Searching…</div>}
          {!loading && results.length === 0 && debounced.trim() && (
            <div className="combobox-empty">No matches for “{debounced}”</div>
          )}
          {!loading && results.map((r, idx) => (
            <button
              key={r.ticker}
              type="button"
              className={`combobox-item ${idx === highlight ? 'active' : ''}`}
              onMouseEnter={() => setHighlight(idx)}
              onClick={() => handleSelect(r)}
            >
              <span className="combobox-flag">{r.country_flag}</span>
              <div className="combobox-main">
                <div className="combobox-ticker">{r.ticker}</div>
                <div className="combobox-name">{r.name}</div>
              </div>
              <div className="combobox-meta">
                <span>{r.exchange}</span>
                <span className="combobox-currency">{r.currency_symbol} {r.currency}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function CountrySearch({ value, onChange, onSubmit, disabled }) {
  const [query, setQuery] = useState(value || '');
  const [open, setOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const wrapRef = useRef(null);
  useClickOutside(wrapRef, () => setOpen(false));

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setQuery(value || '');
  }, [value]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return COUNTRIES;
    return COUNTRIES.filter(c => c.name.toLowerCase().includes(q));
  }, [query]);

  const handleSelect = (c) => {
    setQuery(c.name);
    onChange(c.name);
    setOpen(false);
  };

  const handleKey = (e) => {
    if (!open) {
      if (e.key === 'Enter') { e.preventDefault(); onSubmit(); }
      return;
    }
    if (e.key === 'ArrowDown') { e.preventDefault(); setHighlight(h => Math.min(h + 1, filtered.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setHighlight(h => Math.max(h - 1, 0)); }
    else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[highlight]) handleSelect(filtered[highlight]);
      else onSubmit();
    }
    else if (e.key === 'Escape') { setOpen(false); }
  };

  return (
    <div ref={wrapRef} className="combobox" style={{ flex: 1, minWidth: 280, maxWidth: 460 }}>
      <input
        type="text"
        className="glass combobox-input"
        placeholder="Choose a country (India, Germany, Brazil…)"
        value={query}
        onChange={(e) => { setQuery(e.target.value); onChange(e.target.value); setOpen(true); setHighlight(0); }}
        onFocus={() => setOpen(true)}
        onKeyDown={handleKey}
        disabled={disabled}
        autoComplete="off"
      />
      {open && filtered.length > 0 && (
        <div className="combobox-menu glass">
          {filtered.map((c, idx) => (
            <button
              key={c.name}
              type="button"
              className={`combobox-item ${idx === highlight ? 'active' : ''}`}
              onMouseEnter={() => setHighlight(idx)}
              onClick={() => handleSelect(c)}
            >
              <span className="combobox-flag">{c.flag}</span>
              <div className="combobox-main">
                <div className="combobox-ticker">{c.name}</div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function CurrencySearch({ value, onChange, placeholder = 'Select…', disabled }) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const wrapRef = useRef(null);
  useClickOutside(wrapRef, () => setOpen(false));

  const selected = useMemo(() => CURRENCIES.find(c => c.code === value), [value]);
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setQuery(selected ? `${selected.flag} ${selected.code}` : '');
  }, [selected]);

  const filtered = useMemo(() => {
    const q = query.toLowerCase().replace(/[^\w]/g, '');
    if (!q || (selected && query === `${selected.flag} ${selected.code}`)) return CURRENCIES;
    return CURRENCIES.filter(c => 
      c.code.toLowerCase().includes(q) || 
      c.name.toLowerCase().includes(q)
    );
  }, [query, selected]);

  const handleSelect = (c) => {
    setQuery(`${c.flag} ${c.code}`);
    onChange(c.code);
    setOpen(false);
  };

  return (
    <div ref={wrapRef} className="combobox" style={{ minWidth: 160, flex: 1 }}>
      <input
        type="text"
        className="glass combobox-input"
        placeholder={placeholder}
        value={query}
        onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
        onFocus={() => { setQuery(''); setOpen(true); }}
        onKeyDown={(e) => {
          if (e.key === 'ArrowDown') { e.preventDefault(); setHighlight(h => Math.min(h + 1, filtered.length - 1)); }
          else if (e.key === 'ArrowUp') { e.preventDefault(); setHighlight(h => Math.max(h - 1, 0)); }
          else if (e.key === 'Enter' && filtered[highlight]) { e.preventDefault(); handleSelect(filtered[highlight]); }
          else if (e.key === 'Escape') setOpen(false);
        }}
        disabled={disabled}
        autoComplete="off"
      />
      {open && (
        <div className="combobox-menu glass" style={{ width: 280 }}>
          {filtered.slice(0, 50).map((c, idx) => (
            <button
              key={c.code}
              type="button"
              className={`combobox-item ${idx === highlight ? 'active' : ''}`}
              onClick={() => handleSelect(c)}
              onMouseEnter={() => setHighlight(idx)}
            >
              <span className="combobox-flag">{c.flag}</span>
              <div className="combobox-main">
                <div className="combobox-ticker">{c.code}</div>
                <div className="combobox-name">{c.name}</div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function PriceChart({ data, currency, symbol, height = 240 }) {
  if (!data || data.length === 0) return <div className="chart-empty">No data available</div>;
  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }}
            tickFormatter={(d) => d.slice(5)} minTickGap={24} />
          <YAxis domain={['auto', 'auto']} tick={{ fill: '#94a3b8', fontSize: 11 }} width={70}
            tickFormatter={(v) => formatPrice(v, currency, symbol)} />
          <Tooltip
            contentStyle={{ background: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 8, color: '#f8fafc' }}
            labelStyle={{ color: '#cbd5e1' }}
            formatter={(value) => [formatPrice(value, currency, symbol), 'Close']} />
          <Line type="monotone" dataKey="close" stroke="#6366f1" strokeWidth={2}
            dot={false} activeDot={{ r: 4, fill: '#ec4899' }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function ValuationPanel({ ticker, currency, symbol }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    let cancelled = false;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true); setErr(null);
    fetch(`${API_BASE}/asset?ticker=${encodeURIComponent(ticker)}`)
      .then(async r => {
        const j = await r.json();
        if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
        if (j.error) throw new Error(j.error);
        return j;
      })
      .then(d => { if (!cancelled) setData(d); })
      .catch(e => { if (!cancelled) setErr(String(e.message || e)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [ticker]);

  if (loading) return <div className="valuation-panel"><div className="loader" style={{ width: 24, height: 24, margin: '0 auto' }} /></div>;
  if (err) {
    console.warn(`[UI] Valuation error for ${ticker}:`, err);
    return <div className="valuation-panel"><div className="chart-empty">No detailed valuation available for this asset type.</div></div>;
  }
  if (!data || data.error) return <div className="valuation-panel"><div className="chart-empty">Valuation snapshot unavailable.</div></div>;

  const verdictClass = (v) => {
    if (!v) return 'hold';
    const k = v.toLowerCase();
    if (k.includes('under')) return 'buy';
    if (k.includes('over')) return 'sell';
    if (k.includes('fair')) return 'hold';
    return 'hold';
  };

  const fmt = (v, digits = 2) => v == null || isNaN(v) ? '—' : Number(v).toFixed(digits);
  const fmtPct = (v) => v == null || isNaN(v) ? '—' : `${v >= 0 ? '+' : ''}${Number(v).toFixed(2)}%`;
  const fmtCap = (v) => {
    if (v == null) return '—';
    if (v >= 1e12) return (v / 1e12).toFixed(2) + 'T';
    if (v >= 1e9) return (v / 1e9).toFixed(2) + 'B';
    if (v >= 1e6) return (v / 1e6).toFixed(2) + 'M';
    return Number(v).toFixed(0);
  };
  const recKey = data.analyst_recommendation_key
    ? data.analyst_recommendation_key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
    : null;

  return (
    <div className="valuation-panel">
      <div className="valuation-header">
        <h4>Intrinsic Value & Valuation</h4>
        <span className={`tag ${verdictClass(data.valuation_verdict)}`}>
          {data.valuation_verdict || 'Unknown'}
          {data.valuation_upside_pct != null && ` · ${fmtPct(data.valuation_upside_pct)} upside`}
        </span>
      </div>

      <div className="valuation-grid">
        <div className="val-cell">
          <span className="val-label">Analyst target (mean)</span>
          <span className="val-value">{data.target_mean_price != null ? formatPrice(data.target_mean_price, currency, symbol) : '—'}</span>
          {data.target_low_price != null && data.target_high_price != null && (
            <span className="val-sub">Range: {formatPrice(data.target_low_price, currency, symbol)} → {formatPrice(data.target_high_price, currency, symbol)}</span>
          )}
        </div>
        <div className="val-cell">
          <span className="val-label">Analyst rating</span>
          <span className="val-value">{recKey || '—'}</span>
          {data.analyst_recommendation_mean != null && (
            <span className="val-sub">Score {fmt(data.analyst_recommendation_mean)} (1=Strong Buy · 5=Strong Sell)
              {data.number_of_analyst_opinions != null && ` · ${Math.round(data.number_of_analyst_opinions)} analysts`}</span>
          )}
        </div>
        <div className="val-cell">
          <span className="val-label">Trailing P/E</span>
          <span className="val-value">{fmt(data.pe_ratio)}</span>
        </div>
        <div className="val-cell">
          <span className="val-label">Forward P/E</span>
          <span className="val-value">{fmt(data.forward_pe)}</span>
        </div>
        <div className="val-cell">
          <span className="val-label">PEG</span>
          <span className="val-value">{fmt(data.peg_ratio)}</span>
        </div>
        <div className="val-cell">
          <span className="val-label">P/B</span>
          <span className="val-value">{fmt(data.price_to_book)}</span>
        </div>
        <div className="val-cell">
          <span className="val-label">P/S</span>
          <span className="val-value">{fmt(data.price_to_sales)}</span>
        </div>
        <div className="val-cell">
          <span className="val-label">Dividend yield</span>
          <span className="val-value">{data.dividend_yield ? (data.dividend_yield * (data.dividend_yield < 1 ? 100 : 1)).toFixed(2) + '%' : '—'}</span>
        </div>
        <div className="val-cell">
          <span className="val-label">Beta</span>
          <span className="val-value">{fmt(data.beta)}</span>
        </div>
        <div className="val-cell">
          <span className="val-label">Market cap</span>
          <span className="val-value">{symbol}{fmtCap(data.market_cap)}</span>
        </div>
        <div className="val-cell">
          <span className="val-label">52-week high</span>
          <span className="val-value">{data.fifty_two_week_high != null ? formatPrice(data.fifty_two_week_high, currency, symbol) : '—'}</span>
        </div>
        <div className="val-cell">
          <span className="val-label">52-week low</span>
          <span className="val-value">{data.fifty_two_week_low != null ? formatPrice(data.fifty_two_week_low, currency, symbol) : '—'}</span>
        </div>
      </div>

      {(data.sector || data.industry) && (
        <div className="val-meta">
          {data.long_name && <strong>{data.long_name}</strong>}
          {data.sector && <span> · {data.sector}</span>}
          {data.industry && <span> · {data.industry}</span>}
        </div>
      )}
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
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true); setErr(null);
    fetch(`${API_BASE}/history/${encodeURIComponent(ticker)}?period=${period}`)
      .then(async r => {
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || data.error || `HTTP ${r.status}`);
        return data;
      })
      .then(data => { if (!cancelled) setHistory(data.history || []); })
      .catch(e => { if (!cancelled) { setErr(String(e.message || e)); setHistory([]); } })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [ticker, period]);

  return (
    <div className="history-panel">
      <div className="period-row">
        {PERIODS.map(p => (
          <button key={p.value} type="button"
            className={`period-btn ${period === p.value ? 'active' : ''}`}
            onClick={() => setPeriod(p.value)}>
            {p.label}
          </button>
        ))}
      </div>
      {loading ? <div className="chart-loading"><div className="loader" style={{ width: 32, height: 32 }} /></div>
        : err ? <div className="chart-empty">Could not load history: {err}</div>
          : <PriceChart data={history} currency={currency} symbol={symbol} />}
    </div>
  );
}

function FxConverter() {
  const [base, setBase] = useState('USD');
  const [quote, setQuote] = useState('INR');
  const [amount, setAmount] = useState('100');
  const [period, setPeriod] = useState('1mo');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  const fetchRate = useCallback(async (b = base, q = quote, p = period) => {
    setLoading(true); setErr(null);
    try {
      const res = await fetch(`${API_BASE}/forex/${b}/${q}?period=${p}`);
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || json.error || `HTTP ${res.status}`);
      setData(json);
    } catch (e) { setErr(String(e.message || e)); setData(null); }
    finally { setLoading(false); }
  }, [base, quote, period]);

  useEffect(() => { fetchRate('USD', 'INR', '1mo'); /* eslint-disable-next-line */ }, []);

  const handleSwap = () => {
    const nb = quote, nq = base;
    setBase(nb); setQuote(nq); fetchRate(nb, nq, period);
  };

  const converted = useMemo(() => {
    if (!data?.rate) return null;
    const n = parseFloat(amount);
    return isNaN(n) ? null : n * data.rate;
  }, [amount, data]);

  return (
    <div className="glass" style={{ padding: '2rem', marginTop: '1rem' }}>
      <h2 style={{ marginBottom: '0.5rem' }}>FX Converter</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Live currency rates from Yahoo Finance, with historical rate charts.
      </p>

      <form onSubmit={(e) => { e.preventDefault(); fetchRate(); }} className="fx-form" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <input type="number" className="glass fx-input" style={{ width: 120, flex: 'none' }} value={amount} onChange={(e) => setAmount(e.target.value)} step="any" min="0" placeholder="Amount" />
        <CurrencySearch value={base} onChange={setBase} disabled={loading} />
        <button type="button" className="refresh-btn glass fx-swap" style={{ padding: '0.75rem' }} onClick={handleSwap} title="Swap">⇄</button>
        <CurrencySearch value={quote} onChange={setQuote} disabled={loading} />
        <button type="submit" className="refresh-btn glass" style={{ background: 'var(--primary)' }} disabled={loading}>
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
            <div className="period-row" style={{ marginBottom: '1rem' }}>
              {PERIODS.map(p => (
                <button key={p.value} type="button"
                  className={`period-btn ${period === p.value ? 'active' : ''}`}
                  onClick={() => { setPeriod(p.value); fetchRate(base, quote, p.value); }}>
                  {p.label}
                </button>
              ))}
            </div>
            <h4 style={{ marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>Rate history ({base}/{quote})</h4>
            <PriceChart data={data.history || []} currency={quote} symbol={quote} height={260} />
          </div>
        </>
      )}
    </div>
  );
}

function Toast({ kind = 'info', text, onClose }) {
  useEffect(() => {
    if (!text) return;
    const t = setTimeout(onClose, 5000);
    return () => clearTimeout(t);
  }, [text, onClose]);
  if (!text) return null;
  return (
    <div className={`toast toast-${kind} glass`}>
      <span>{text}</span>
      <button className="toast-close" onClick={onClose}>×</button>
    </div>
  );
}

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedRec, setSelectedRec] = useState(null);

  const [activeTab, setActiveTab] = useState('dashboard');
  const [analyzing, setAnalyzing] = useState(false);
  const [toast, setToast] = useState(null);

  const [basketCountry, setBasketCountry] = useState('');
  const [basket, setBasket] = useState([]);
  const [basketLoading, setBasketLoading] = useState(false);
  const [riskTolerance, setRiskTolerance] = useState('Medium');
  const [basketName, setBasketName] = useState('');
  const [savedBaskets, setSavedBaskets] = useState([]);

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

  const fetchBaskets = async () => {
    try {
      const res = await fetch(`${API_BASE}/baskets`);
      if (res.ok) {
        const data = await res.json();
        setSavedBaskets(data);
      }
    } catch (err) { console.error("Failed to fetch baskets", err); }
  };

  useEffect(() => {
    fetchRecommendations();
    fetchBaskets();
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
      } catch (e) { console.error("WS parse error", e); }
    };
    ws.onclose = () => console.log("WebSocket Disconnected");
    return () => ws.close();
  }, []);

  const handleAnalyze = async (item) => {
    const ticker = (item.ticker || '').toUpperCase();
    if (!ticker) return;
    setAnalyzing(true);
    try {
      const res = await fetch(`${API_BASE}/analyze?ticker=${encodeURIComponent(ticker)}`, { method: 'POST' });
      const data = await res.json().catch(() => ({}));
      if (res.status === 404) {
        setToast({ kind: 'error', text: data.detail || `No asset found for ${ticker}` });
      } else if (!res.ok) {
        setToast({ kind: 'error', text: data.detail || `Failed to analyze ${ticker}` });
      } else {
        setToast({ kind: 'info', text: `Analyzing ${ticker}…` });
      }
    } catch (err) {
      setToast({ kind: 'error', text: `Network error: ${err.message || err}` });
    } finally {
      setAnalyzing(false);
    }
  };

  const handleOpenModal = (item) => {
    const ticker = (item.ticker || '').toUpperCase();
    const existing = recommendations.find(r => r.ticker === ticker);
    if (existing) {
      setSelectedRec(existing);
    } else {
      // Mock a recommendation object to open the modal immediately
      // The internal panels (Valuation/History) will fetch data using the ticker.
      setSelectedRec({
        ticker,
        market_name: item.name || 'Stock/MF',
        country_flag: '🌐',
        currency: item.currency || 'INR',
        currency_symbol: '₹',
        current_price: 0,
        action: 'Analyzing...',
        confidence: 0,
        reasoning: item.reasoning || 'Requesting full analysis...',
        model_name: 'AI Agent',
        timestamp: new Date().toISOString()
      });
      // Also trigger a real analysis to populate the live dashboard
      handleAnalyze(item);
    }
  };

  const handleRefresh = async () => { setRefreshing(true); await fetchRecommendations(); };

  const handleAnalyzeAll = async () => {
    if (recommendations.length === 0) return;
    setRefreshing(true);
    setToast({ kind: 'info', text: `Batch analysis started for ${recommendations.length} assets...` });
    
    // Fire all analysis requests in parallel
    const promises = recommendations.map(rec => 
      fetch(`${API_BASE}/analyze?ticker=${encodeURIComponent(rec.ticker)}`, { method: 'POST' })
    );
    
    try {
      await Promise.all(promises);
    } catch (err) {
      console.error("Batch analysis error:", err);
      setToast({ kind: 'error', text: `Batch analysis failed: ${err.message || err}` });
    } finally {
      setRefreshing(false);
    }
  };

  const handleGenerateBasket = async (e, marketOverride = null) => {
    if (e) e.preventDefault();
    const market = marketOverride || basketCountry.trim();
    if (!market) return;
    setBasketLoading(true); setBasket([]); setBasketName('');
    try {
      const res = await fetch(`${API_BASE}/basket/${encodeURIComponent(market)}?risk=${riskTolerance}`);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || data.error || `HTTP ${res.status}`);
      
      let basketArr = data.basket || [];
      console.log(`[UI] Basket received for ${market}:`, basketArr);
      // Ensure percentage weights exist, fallback to even split
      const total = basketArr.reduce((sum, item) => sum + (item.percentage_weight || 0), 0);
      if (total === 0 || total < 90 || total > 110) {
        console.warn("[UI] Invalid or missing percentage weights. Normalizing...");
        const split = Math.floor(100 / basketArr.length);
        basketArr = basketArr.map((item, idx) => ({
          ...item,
          percentage_weight: idx === basketArr.length - 1 ? 100 - split * (basketArr.length - 1) : split
        }));
      }
      setBasket(basketArr);
      if (basketArr.length === 0) {
        setToast({ kind: 'error', text: `No basket suggestions returned for ${market}` });
      }
    } catch (err) {
      setToast({ kind: 'error', text: `Basket failed: ${err.message || err}` });
    } finally {
      setBasketLoading(false);
    }
  };

  const handleSaveBasket = async (e) => {
    if (e) e.preventDefault();
    if (!basketName.trim() || basket.length === 0) {
      setToast({ kind: 'error', text: 'Please enter a name and generate a basket first.' });
      return;
    }
    const payload = { name: basketName, items: basket };
    console.log("[UI] Saving basket with payload:", payload);
    try {
      const res = await fetch(`${API_BASE}/baskets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setToast({ kind: 'success', text: `Basket "${basketName}" saved!` });
        setBasketName(''); setBasket([]); fetchBaskets(); setActiveTab('dashboard');
      } else {
        console.error("[UI] Save failed:", data);
        if (res.status === 400 && data.detail?.includes("exist")) {
          setToast({ kind: 'error', text: `A basket named "${basketName}" already exists. Please choose a different name.` });
        } else {
          setToast({ kind: 'error', text: data.detail || `Error: ${res.status} - Could not save basket.` });
        }
      }
    } catch (err) {
      console.error("[UI] Network error during save:", err);
      setToast({ kind: 'error', text: `Network error: ${err.message || err}` });
    }
  };

  const handleDeleteBasket = async (name, e) => {
    if (e) e.stopPropagation();
    try {
      const res = await fetch(`${API_BASE}/baskets/${encodeURIComponent(name)}`, { method: 'DELETE' });
      if (res.ok) {
        setSavedBaskets(prev => prev.filter(b => b.name !== name));
        setToast({ kind: 'success', text: `Deleted basket "${name}"` });
      }
    } catch (err) { setToast({ kind: 'error', text: `Delete failed: ${err.message || err}` }); }
  };

  const handleDelete = async (ticker, e) => {
    if (e) e.stopPropagation();
    try {
      const res = await fetch(`${API_BASE}/recommendations/${encodeURIComponent(ticker)}`, { method: 'DELETE' });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setRecommendations(prev => prev.filter(r => r.ticker !== ticker));
        setToast({ kind: 'success', text: `Deleted ${ticker}` });
        if (selectedRec?.ticker === ticker) setSelectedRec(null);
      } else {
        setToast({ kind: 'error', text: data.detail || `Failed to delete ${ticker}` });
      }
    } catch (err) {
      setToast({ kind: 'error', text: `Delete failed: ${err.message || err}` });
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
      <Toast {...(toast || {})} onClose={() => setToast(null)} />

      <div className="header-actions" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '1rem', marginBottom: '1rem' }}>
        <div>
          <h1 className="title" style={{ background: 'linear-gradient(135deg, #fff 0%, #cbd5e1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>StockMind AI</h1>
          <p className="subtitle" style={{ margin: 0, marginTop: '0.5rem' }}>Long-term AI Recommendation Engine — Global Markets</p>
        </div>
        <div className="tabs" style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
          <button className={`tag glass ${activeTab === 'dashboard' ? 'buy' : ''}`} style={{cursor: 'pointer'}} onClick={() => setActiveTab('dashboard')}>Real-Time Dashboard</button>
          <button className={`tag glass ${activeTab === 'baskets' ? 'buy' : ''}`} style={{cursor: 'pointer'}} onClick={() => setActiveTab('baskets')}>Curated Baskets</button>
          <button className={`tag glass ${activeTab === 'indian-mfs' ? 'buy' : ''}`} style={{cursor: 'pointer'}} onClick={() => setActiveTab('indian-mfs')}>Indian Mutual Funds</button>
          <button className={`tag glass ${activeTab === 'fx' ? 'buy' : ''}`} style={{cursor: 'pointer'}} onClick={() => setActiveTab('fx')}>FX Converter</button>
        </div>
      </div>

      {activeTab === 'dashboard' && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
            <TickerSearch onSelect={handleAnalyze} disabled={analyzing} />
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button className="refresh-btn glass" onClick={handleAnalyzeAll} disabled={refreshing || analyzing}>
                {refreshing ? <span className="loader" style={{ width: 15, height: 15, borderWidth: '2px' }} /> : "🤖 Analyze All"}
              </button>
              <button className="refresh-btn glass" onClick={handleRefresh} disabled={refreshing}>
                {refreshing ? <span className="loader" style={{ width: 15, height: 15, borderWidth: '2px' }} /> : "🔄 Refresh List"}
              </button>
            </div>
          </div>

          {savedBaskets.length > 0 && (
            <div style={{ marginBottom: '3rem' }}>
              <h3 style={{ color: 'white', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ color: 'var(--primary)' }}>★</span> Saved Baskets
              </h3>
              <div className="dashboard-grid">
                {savedBaskets.map((b) => (
                  <div key={b.id} className="card glass saved-basket-card">
                    <div className="card-header" style={{ marginBottom: '1rem' }}>
                      <div className="ticker" style={{ fontSize: '1.25rem' }}>{b.name}</div>
                      <button className="delete-btn glass" onClick={(e) => handleDeleteBasket(b.name, e)}>×</button>
                    </div>
                    <div className="basket-items-list">
                      {b.items.map((item, idx) => (
                        <div key={idx} className="basket-item-mini-wrap" 
                             onClick={() => handleOpenModal(item)}
                             style={{ cursor: 'pointer' }}>
                          <div className="basket-item-mini">
                            <span className="ticker-mini" style={{ width: 85 }}>{item.ticker}</span>
                            <span className="weight-mini">{item.percentage_weight}%</span>
                            <span className="name-mini">{item.name}</span>
                          </div>
                          <div className="confidence-bar" style={{ height: 4, marginTop: 4, opacity: 0.6 }}>
                            <div className="confidence-fill" style={{ width: `${item.percentage_weight}%` }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Created: {new Date(b.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <h3 style={{ color: 'white', marginBottom: '1.5rem' }}>Live Recommendations</h3>
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
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                      <div className={`tag ${getTagClass(rec.action)}`}>{rec.action}</div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button className="refresh-btn glass" 
                                style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} 
                                onClick={(e) => { e.stopPropagation(); handleAnalyze(rec); }}
                                title="Analyze Again">
                          🔄
                        </button>
                        <button className="delete-btn glass" onClick={(e) => handleDelete(rec.ticker, e)} title="Delete recommendation">×</button>
                      </div>
                    </div>
                  </div>
                  <div className="confidence">
                    <span style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>Confidence: {Math.round(rec.confidence * 100)}%</span>
                    <div className="confidence-bar">
                      <div className="confidence-fill" style={{ width: `${rec.confidence * 100}%` }}></div>
                    </div>
                  </div>
                  <div className="reasoning">{rec.reasoning}</div>
                  <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>{new Date(rec.timestamp).toLocaleString()}</span>
                    <span>Model: {rec.model_name || 'AI Analyst'}</span>
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
          <h2 style={{ marginBottom: '1rem' }}>Curated AI Baskets</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            AI researches 3–5 high-quality assets (Stocks, ETFs, or MFs) based on your market and risk preference.
          </p>

          <form onSubmit={handleGenerateBasket} style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div style={{ flex: 1, minWidth: 280 }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Market / Country</label>
              <CountrySearch
                value={basketCountry}
                onChange={setBasketCountry}
                onSubmit={handleGenerateBasket}
                disabled={basketLoading}
              />
            </div>
            <div style={{ width: 160 }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Risk Tolerance</label>
              <select className="glass fx-select" style={{ width: '100%', height: 48 }} value={riskTolerance} onChange={(e) => setRiskTolerance(e.target.value)}>
                <option value="Low">Low Risk</option>
                <option value="Medium">Medium Risk</option>
                <option value="High">High Risk</option>
              </select>
            </div>
            <button type="submit" className="refresh-btn glass" style={{ height: 48, padding: '0 2rem', background: 'rgba(99, 102, 241, 0.5)' }} disabled={basketLoading || !basketCountry.trim()}>
              {basketLoading ? <span className="loader" /> : "Generate"}
            </button>
          </form>

          {basketLoading && (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'white' }}>
              <div className="loader" style={{ width: 50, height: 50 }} />
              <p style={{ marginTop: '1rem' }}>Our AI is researching appropriate assets for {basketCountry}…</p>
            </div>
          )}

          {basket.length > 0 && !basketLoading && (
            <>
              <div className="dashboard-grid">
                {basket.map((item, idx) => (
                  <div key={idx} className="card glass" onClick={() => handleOpenModal(item)}>
                    <div className="card-header" style={{ alignItems: 'flex-start', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>
                      <div style={{ flex: 1 }}>
                        <div className="ticker">{item.ticker}</div>
                        <div style={{ fontSize: '0.9rem', color: '#e2e8f0', marginTop: '0.2rem' }}>{item.name}</div>
                        {item.currency && (
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>Listed in {item.currency}</div>
                        )}
                      </div>
                      {item.percentage_weight && (
                        <div className="tag buy" style={{ fontSize: '1.1rem', padding: '0.4rem 0.8rem' }}>{item.percentage_weight}%</div>
                      )}
                    </div>
                    <div className="reasoning" style={{ WebkitLineClamp: 'unset', maxHeight: 'none' }}>{item.reasoning}</div>
                  </div>
                ))}
              </div>

              <div className="glass" style={{ marginTop: '2rem', padding: '1.5rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <div style={{ flex: 1 }}>
                  <h4 style={{ marginBottom: '0.5rem' }}>Save this basket?</h4>
                  <input
                    type="text"
                    className="glass combobox-input"
                    placeholder="Enter basket name (e.g. My India Growth Portfolio)"
                    value={basketName}
                    onChange={(e) => setBasketName(e.target.value)}
                  />
                </div>
                <button
                  className="refresh-btn glass"
                  style={{ height: 48, marginTop: '1.5rem', background: 'var(--primary)' }}
                  onClick={handleSaveBasket}
                  disabled={!basketName.trim()}
                >
                  Save to Dashboard
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'indian-mfs' && (
        <div className="glass" style={{ padding: '2rem', marginTop: '1rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>Indian Mutual Funds & ETFs</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            Curated high-quality Indian Mutual Funds and ETFs tailored to your risk profile.
          </p>

          <form onSubmit={(e) => handleGenerateBasket(e, 'Indian Mutual Funds')} style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div style={{ width: 200 }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Risk Tolerance</label>
              <select className="glass fx-select" style={{ width: '100%', height: 48 }} value={riskTolerance} onChange={(e) => setRiskTolerance(e.target.value)}>
                <option value="Low">Low Risk</option>
                <option value="Medium">Medium Risk</option>
                <option value="High">High Risk</option>
              </select>
            </div>
            <button type="submit" className="refresh-btn glass" style={{ height: 48, padding: '0 2.5rem', background: 'rgba(99, 102, 241, 0.5)' }} disabled={basketLoading}>
              {basketLoading ? <span className="loader" /> : "Generate Portfolio"}
            </button>
          </form>

          {basketLoading && (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'white' }}>
              <div className="loader" style={{ width: 50, height: 50 }} />
              <p style={{ marginTop: '1rem' }}>Analyzing Indian market data and historical MF performance…</p>
            </div>
          )}

          {basket.length > 0 && !basketLoading && (
            <>
              <div className="dashboard-grid">
                {basket.map((item, idx) => (
                  <div key={idx} className="card glass" onClick={() => handleOpenModal(item)}>
                    <div className="card-header" style={{ alignItems: 'flex-start', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>
                      <div style={{ flex: 1 }}>
                        <div className="ticker">{item.ticker}</div>
                        <div style={{ fontSize: '0.9rem', color: '#e2e8f0', marginTop: '0.2rem' }}>{item.name}</div>
                      </div>
                      <div className="tag buy" style={{ fontSize: '1.1rem', padding: '0.4rem 0.8rem' }}>{item.percentage_weight}%</div>
                    </div>
                    <div className="reasoning" style={{ WebkitLineClamp: 'unset', maxHeight: 'none' }}>{item.reasoning}</div>
                  </div>
                ))}
              </div>

              <div className="glass" style={{ marginTop: '2rem', padding: '1.5rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <div style={{ flex: 1 }}>
                  <h4 style={{ marginBottom: '0.5rem' }}>Save this MF Portfolio?</h4>
                  <input
                    type="text"
                    className="glass combobox-input"
                    placeholder="e.g. My Retirement MF Basket"
                    value={basketName}
                    onChange={(e) => setBasketName(e.target.value)}
                  />
                </div>
                <button
                  className="refresh-btn glass"
                  style={{ height: 48, marginTop: '1.5rem', background: 'var(--primary)' }}
                  onClick={handleSaveBasket}
                  disabled={!basketName.trim()}
                >
                  Save to Dashboard
                </button>
              </div>
            </>
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
              <span className={`tag ${getTagClass(selectedRec.action)}`} style={{ fontSize: '1rem', padding: '0.5rem 1rem' }}>{selectedRec.action}</span>
              <span style={{color: 'var(--text-secondary)'}}>Conf: {Math.round(selectedRec.confidence * 100)}%</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '1.5rem' }}>
              <ValuationPanel ticker={selectedRec.ticker} currency={selectedRec.currency || 'USD'} symbol={selectedRec.currency_symbol || '$'} />
              <HistoryPanel ticker={selectedRec.ticker} currency={selectedRec.currency || 'USD'} symbol={selectedRec.currency_symbol || '$'} />
            </div>

            <div style={{ lineHeight: 1.8, color: '#e2e8f0', background: 'rgba(0,0,0,0.2)', padding: '1.5rem', borderRadius: '12px', marginTop: '1.5rem' }}>
              <h4 style={{ marginBottom: '1rem', color: 'var(--primary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>AI Analyst Reasoning</span>
                <span style={{ fontSize: '0.7rem', opacity: 0.6 }}>Model: {selectedRec.model_name || 'AI Analyst'}</span>
              </h4>
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

import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, BarChart2, Globe, Shield, Zap, TrendingUp, AlertTriangle, 
  CheckCircle, XCircle, Database, Activity, FileText, Download, 
  Layers, Crosshair
} from 'lucide-react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from 'chart.js';
import { Radar, Bar } from 'react-chartjs-2';
import ReactMarkdown from 'react-markdown';
import jsPDF from 'jspdf';

import html2canvas from 'html2canvas';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

const API_BASE = '/api/v1';

const App = () => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [comparison, setComparison] = useState(null);
  const [baseline, setBaseline] = useState(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const reportRef = useRef(null);

  useEffect(() => {
    fetch(`${API_BASE}/baseline`)
      .then(res => res.ok ? res.json() : null)
      .then(data => { if (data) setBaseline(data); })
      .catch(() => {});
  }, []);

  const handleCompare = async (e) => {
    e.preventDefault();
    if (!url) return;
    
    setIsLoading(true);
    setError('');
    setStatus('Running deep crawl & 100-parameter analysis...');
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 min frontend timeout

      const res = await fetch(`${API_BASE}/compare?competitor_url=${encodeURIComponent(url)}`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      const contentType = res.headers.get("content-type");
      if (!res.ok) {
        if (contentType && contentType.includes("application/json")) {
          const err = await res.json();
          throw new Error(err.detail || 'API Error');
        } else {
          // Handle HTML error pages (like 504 Gateway Time-out)
          if (res.status === 504) throw new Error('Crawl Timeout: The site is too large or slow for an instant audit. Try another domain.');
          throw new Error(`Server Error (${res.status}): Please check backend logs.`);
        }
      }
      
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error('Invalid Data: Received an unexpected response format from server.');
      }

      const data = await res.json();
      setComparison(data);
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request Timed Out: The audit took longer than 10 minutes.');
      } else {
        setError(err.message);
      }
    } finally {

      setIsLoading(false);
      setStatus('');
    }
  };

  const exportPDF = async () => {
    const element = reportRef.current;
    const canvas = await html2canvas(element, { scale: 2 });
    const data = canvas.toDataURL('image/png');
    const pdf = new jsPDF('p', 'mm', 'a4');
    const imgProps = pdf.getImageProperties(data);
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
    pdf.addImage(data, 'PNG', 0, 0, pdfWidth, pdfHeight);
    pdf.save(`SEO-Comparison-${url.replace(/https?:\/\//, '')}.pdf`);
  };

  const radarData = comparison ? {
    labels: Object.keys(comparison.categories),
    datasets: [
      {
        label: 'Bajaj Life (Baseline)',
        data: Object.values(comparison.categories),
        backgroundColor: 'rgba(19, 200, 236, 0.2)',
        borderColor: 'rgba(19, 200, 236, 1)',
        borderWidth: 2,
      },
      {
        label: 'Competitor',
        data: Object.values(comparison.comp_categories),
        backgroundColor: 'rgba(245, 158, 11, 0.2)',
        borderColor: 'rgba(245, 158, 11, 1)',
        borderWidth: 2,
      },
    ],
  } : null;

  return (
    <div className="app">
      <nav className="glass" style={styles.nav}>
        <div className="container flex justify-between">
          <div className="flex" style={{ gap: '0.75rem' }}>
            <div style={styles.logoBg}>
              <BarChart2 color="white" size={24} />
            </div>
            <span style={styles.logoText}>
              SEO<span style={{ color: 'var(--accent-color)' }}>INTEL</span>
            </span>
          </div>
          <div className="flex" style={{ gap: '2rem' }}>
            {baseline && (
              <div className="flex" style={{ gap: '0.5rem', color: '#10b981', fontSize: '0.85rem', fontWeight: 600 }}>
                <CheckCircle size={16} /> Baseline Active
              </div>
            )}
            <a href="#results" style={styles.navLink}>Enterprise Audit</a>
          </div>
        </div>
      </nav>

      <header style={styles.hero}>
        <div className="container text-center fade-in">
          <div style={styles.badge}>
            <Activity size={14} /> 100-Parameter Strict Comparison
          </div>
          <h1 style={styles.heroTitle}>
            Insurance <span style={{ color: 'var(--accent-color)' }}>SEO Audit</span> Pro
          </h1>
          <p style={styles.heroSubtitle}>
            Uncover exactly why Bajaj is leading or lagging. Deep technical debt & YMYL analysis.
          </p>

          <form onSubmit={handleCompare} className="glass" style={styles.searchBar}>
            <div style={styles.searchInputWrap}>
              <Globe size={20} color="var(--accent-color)" style={{ marginRight: '0.75rem' }} />
              <input 
                type="url" 
                placeholder="Paste competitor URL here..." 
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                style={styles.searchInput}
                required
              />
            </div>
            <button type="submit" className="btn-primary" disabled={isLoading} style={styles.runBtn}>
              {isLoading ? <span className="spinner"></span> : <Crosshair size={18} style={{ marginRight: '0.5rem' }} />}
              {isLoading ? 'Analyzing...' : 'Strict Audit'}
            </button>
          </form>
          
          {isLoading && <div style={styles.statusMsg}>{status}</div>}
          {error && <div style={styles.errorMsg}>{error}</div>}
        </div>
      </header>

      {comparison && (
        <section id="results" className="container fade-in" style={{ paddingBottom: '6rem' }}>
          <div className="flex justify-between items-end" style={{ marginBottom: '2rem' }}>
            <div>
              <h2 style={{ fontSize: '2rem', fontWeight: 800 }}>Comparative Report</h2>
              <p style={{ color: 'var(--text-secondary)' }}>Bajaj Life vs {comparison.competitor_url}</p>
            </div>
            <button onClick={exportPDF} className="btn-secondary flex items-center" style={{ gap: '0.5rem' }}>
              <Download size={18} /> Export PDF
            </button>
          </div>

          <div ref={reportRef} style={{ background: '#f8fafc', padding: '1rem', borderRadius: '1rem' }}>
            {/* Score Cards */}
            <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
              <ScoreCard 
                title="Bajaj SEO Health" 
                value={comparison.overall_score} 
                icon={<Shield size={24} color="var(--accent-color)" />}
                label="Baseline Score"
              />
              <ScoreCard 
                title="Competitor Score" 
                value={comparison.competitor_score} 
                icon={<Globe size={24} color="#f59e0b" />}
                label="Overall grade"
              />
              <ScoreCard 
                title="Technical Debt" 
                value={comparison.techDebt} 
                icon={<AlertTriangle size={24} color={comparison.techDebt === 'High' ? '#ef4444' : '#10b981'} />}
                label="Risk Indicator"
              />
            </div>

            {/* Charts Row */}
            <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', marginTop: '2rem', gap: '1.5rem' }}>
              <div className="card">
                <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Layers size={20} color="var(--accent-color)" /> Category Comparison
                </h3>
                <div style={{ height: '350px' }}>
                  <Radar data={radarData} options={{ maintainAspectRatio: false }} />
                </div>
              </div>
            </div>

            {/* AI Insights - Full Width for Readability */}
             <div className="card" style={{ marginTop: '2rem' }}>
                <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Zap size={20} color="#f59e0b" /> AI Strategic Insights
                </h3>
                <div style={{ background: '#f8fafc', padding: '2rem', borderRadius: '0.75rem', border: '1px solid #e2e8f0' }}>
                  <ReactMarkdown 
                    components={{
                      h3: ({node, ...props}) => <h3 style={{ fontSize: '1.25rem', fontWeight: 800, marginTop: '1.5rem', marginBottom: '0.75rem', color: '#0f172a' }} {...props} />,
                      p: ({node, ...props}) => <p style={{ marginBottom: '1rem', lineHeight: 1.7, color: '#334155' }} {...props} />,
                      ul: ({node, ...props}) => <ul style={{ paddingLeft: '1.5rem', marginBottom: '1rem' }} {...props} />,
                      li: ({node, ...props}) => <li style={{ marginBottom: '0.5rem', color: '#475569' }} {...props} />,
                      strong: ({node, ...props}) => <strong style={{ color: '#0f172a', fontWeight: 600 }} {...props} />
                    }}
                  >
                    {comparison.ai_analysis}
                  </ReactMarkdown>
                </div>
              </div>

            <div className="grid">
              {/* Spacer div was here, removed to keep structure clean */}
            </div>


            {/* Audit Table */}
            <div className="card" style={{ marginTop: '2rem' }}>
              <h3 style={{ marginBottom: '1.5rem' }}>Strict Parameter Audit</h3>
              <table style={styles.table}>
                <thead>
                  <tr style={styles.tableHead}>
                    <th style={styles.th}>SEO Parameter</th>
                    <th style={styles.th}>Bajaj Life</th>
                    <th style={styles.th}>Competitor</th>
                    <th style={styles.th}>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.details.map((item, i) => (
                    <tr key={i} style={styles.tableRow}>
                      <td style={styles.td}><strong>{item.label}</strong></td>
                      <td style={styles.td}>{item.baseline}</td>
                      <td style={styles.td}>{item.competitor}</td>
                      <td style={styles.td}>
                        <span style={{
                          ...styles.statusBadge,
                          background: item.status === 'Optimized' ? '#d1fae5' : '#fee2e2',
                          color: item.status === 'Optimized' ? '#065f46' : '#991b1b'
                        }}>
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

const ScoreCard = ({ title, value, icon, label }) => (
  <div className="card flex items-center" style={{ gap: '1.5rem', padding: '1.5rem' }}>
    <div style={{ background: '#f1f5f9', padding: '1rem', borderRadius: '1rem' }}>{icon}</div>
    <div>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{title}</p>
      <div style={{ fontSize: '2rem', fontWeight: 800 }}>{value}</div>
      <p style={{ fontSize: '0.75rem', opacity: 0.7 }}>{label}</p>
    </div>
  </div>
);

const styles = {
  nav: { padding: '1rem 0', position: 'sticky', top: 0, zIndex: 100, borderBottom: '1px solid rgba(0,0,0,0.05)' },
  logoBg: { background: 'var(--accent-color)', padding: '0.5rem', borderRadius: '0.5rem' },
  logoText: { fontWeight: 900, fontSize: '1.4rem', letterSpacing: '-0.02em' },
  navLink: { textDecoration: 'none', color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.9rem' },
  hero: { padding: '4rem 0' },
  badge: { display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: '#e0f2fe', color: '#0369a1', padding: '0.5rem 1rem', borderRadius: '100px', fontSize: '0.8rem', fontWeight: 700, marginBottom: '2rem' },
  heroTitle: { fontSize: '4rem', fontWeight: 900, marginBottom: '1.5rem', letterSpacing: '-0.04em' },
  heroSubtitle: { color: 'var(--text-secondary)', fontSize: '1.25rem', maxWidth: '600px', margin: '0 auto 3rem auto' },
  searchBar: { padding: '0.5rem', borderRadius: '100px', maxWidth: '700px', margin: '0 auto', display: 'flex', border: '2px solid #e2e8f0', background: 'white' },
  searchInputWrap: { padding: '0 1.5rem', display: 'flex', alignItems: 'center', flex: 1 },
  searchInput: { border: 'none', outline: 'none', background: 'transparent', width: '100%', fontSize: '1rem', color: '#1e293b' }, // Fixed color: was white on white
  runBtn: { padding: '0.75rem 2rem', borderRadius: '100px', display: 'flex', alignItems: 'center', fontWeight: 700 },
  statusMsg: { marginTop: '2rem', color: 'var(--accent-color)', fontWeight: 600 },
  errorMsg: { marginTop: '1rem', color: '#ef4444' },
  table: { width: '100%', borderCollapse: 'collapse' },
  tableHead: { borderBottom: '2px solid #f1f5f9', textAlign: 'left' },
  th: { padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.8rem', textTransform: 'uppercase' },
  tableRow: { borderBottom: '1px solid #f1f5f9' },
  td: { padding: '1.25rem 1rem', fontSize: '0.95rem' },
  statusBadge: { padding: '0.35rem 0.75rem', borderRadius: '100px', fontSize: '0.75rem', fontWeight: 800 },
};

export default App;

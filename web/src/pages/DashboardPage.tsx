import { useEffect, useState } from 'react';
import { getTrends, getSummary } from '../api/client';
import TrendChart from '../components/TrendChart';

export default function DashboardPage() {
  const [patientId, setPatientId] = useState('margaret');
  const [trends, setTrends] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);

  const load = (pid: string) => {
    getTrends(pid).then((d) => setTrends(Array.isArray(d) ? d : d.trends || [])).catch(() => setTrends([]));
    getSummary(pid).then((d) => setSummary(d)).catch(() => setSummary(null));
  };

  useEffect(() => {
    // try to get patient id from last session
    const s = JSON.parse(sessionStorage.getItem('session') || 'null');
    const pid = s?.patient_id || 'margaret';
    setPatientId(pid);
    load(pid);
  }, []);

  return (
    <div className="page dashboard-page">
      <h2 className="dash-title">📊 Caregiver Dashboard</h2>
      <p className="dash-patient">Patient: <strong>{patientId}</strong></p>

      <section className="card">
        <h3>Cognitive Trends</h3>
        <TrendChart data={trends} />
      </section>

      {summary && (
        <section className="card">
          <h3>Session Summary</h3>
          {summary.summary ? (
            <p>{summary.summary}</p>
          ) : summary.sessions ? (
            summary.sessions.map((s: any, i: number) => (
              <div key={i} className="summary-item">
                <strong>{s.date || `Session ${i + 1}`}</strong>
                <p>{s.summary || s.notes || JSON.stringify(s)}</p>
              </div>
            ))
          ) : (
            <p>{JSON.stringify(summary)}</p>
          )}
        </section>
      )}

      {summary?.alerts && summary.alerts.length > 0 && (
        <section className="card">
          <h3>⚠️ Alerts</h3>
          {summary.alerts.map((a: any, i: number) => (
            <div key={i} className="alert-item">{typeof a === 'string' ? a : a.message || JSON.stringify(a)}</div>
          ))}
        </section>
      )}

      <button className="btn-secondary" onClick={() => alert('Export coming soon!')}>
        📥 Export Report
      </button>
    </div>
  );
}

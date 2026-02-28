import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPatients, startSession } from '../api/client';

interface Patient {
  id: string;
  name: string;
  [k: string]: unknown;
}

export default function HomePage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selected, setSelected] = useState('');
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  useEffect(() => {
    getPatients().then((d) => {
      const list = Array.isArray(d) ? d : d.patients || [];
      setPatients(list);
      if (list.length) setSelected(list[0].id);
    });
  }, []);

  const start = async () => {
    if (!selected) return;
    setLoading(true);
    try {
      const s = await startSession(selected);
      sessionStorage.setItem('session', JSON.stringify(s));
      nav('/chat');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page home-page">
      <div className="home-card">
        <h1 className="logo">🧠 Memowell</h1>
        <p className="subtitle">Alzheimer's Companion Therapy</p>

        <label className="field-label">Select Patient</label>
        <select className="select" value={selected} onChange={(e) => setSelected(e.target.value)}>
          {patients.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>

        <button className="btn-primary" onClick={start} disabled={loading || !selected}>
          {loading ? 'Starting…' : 'Start Session'}
        </button>

        <button className="btn-secondary" onClick={() => nav('/dashboard')}>
          View Dashboard
        </button>
      </div>
    </div>
  );
}

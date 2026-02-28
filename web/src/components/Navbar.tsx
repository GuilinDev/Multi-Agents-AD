import { useLocation, useNavigate } from 'react-router-dom';

const tabs = [
  { path: '/', label: '🏠', title: 'Home' },
  { path: '/chat', label: '💬', title: 'Chat' },
  { path: '/dashboard', label: '📊', title: 'Dashboard' },
];

export default function Navbar() {
  const loc = useLocation();
  const nav = useNavigate();
  return (
    <nav className="navbar">
      {tabs.map((t) => (
        <button
          key={t.path}
          className={`navbar-tab ${loc.pathname === t.path ? 'active' : ''}`}
          onClick={() => nav(t.path)}
        >
          <span className="navbar-icon">{t.label}</span>
          <span className="navbar-title">{t.title}</span>
        </button>
      ))}
    </nav>
  );
}

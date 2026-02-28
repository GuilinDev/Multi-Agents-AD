import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import DashboardPage from './pages/DashboardPage';
import Navbar from './components/Navbar';

export default function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
      <Navbar />
    </div>
  );
}

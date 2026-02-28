import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendChat, endSession } from '../api/client';
import MessageBubble from '../components/MessageBubble';
import VoiceButton from '../components/VoiceButton';

interface Msg {
  text: string;
  isUser: boolean;
  timestamp: string;
  emotion?: string;
  imageUrl?: string;
}

export default function ChatPage() {
  const nav = useNavigate();
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const bottom = useRef<HTMLDivElement>(null);
  const startTime = useRef(Date.now());

  const session = JSON.parse(sessionStorage.getItem('session') || 'null');

  useEffect(() => {
    if (!session) {
      nav('/');
      return;
    }
    const iv = setInterval(() => setElapsed(Math.floor((Date.now() - startTime.current) / 1000)), 1000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth' });
  }, [msgs]);

  const now = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const send = async (message?: string, audio?: Blob) => {
    if (!session) return;
    const userText = message || '🎤 Voice message';
    setMsgs((m) => [...m, { text: userText, isUser: true, timestamp: now() }]);
    setInput('');
    setSending(true);
    try {
      const res = await sendChat(session.session_id, message, audio);
      if (res.audio_url) {
        try { new Audio(res.audio_url).play(); } catch {}
      }
      setMsgs((m) => [
        ...m,
        {
          text: res.response,
          isUser: false,
          timestamp: now(),
          emotion: res.monitor?.emotion,
          imageUrl: res.image_url,
        },
      ]);
    } catch {
      setMsgs((m) => [...m, { text: '⚠️ Failed to send.', isUser: false, timestamp: now() }]);
    } finally {
      setSending(false);
    }
  };

  const handleEnd = async () => {
    if (session) await endSession(session.session_id).catch(() => {});
    sessionStorage.removeItem('session');
    nav('/');
  };

  const fmt = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;

  if (!session) return null;

  return (
    <div className="page chat-page">
      <header className="chat-header">
        <div>
          <strong>{session.patient_name}</strong>
          <span className="timer">{fmt(elapsed)}</span>
        </div>
        <button className="btn-end" onClick={handleEnd}>End</button>
      </header>

      <div className="chat-messages">
        {msgs.map((m, i) => (
          <MessageBubble key={i} {...m} />
        ))}
        {sending && (
          <div className="msg-row msg-left">
            <div className="msg-bubble msg-bot typing">
              <span className="dot" /><span className="dot" /><span className="dot" />
            </div>
          </div>
        )}
        <div ref={bottom} />
      </div>

      <div className="chat-input-bar">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && input.trim() && send(input.trim())}
          placeholder="Type a message…"
        />
        <VoiceButton onRecorded={(b) => send(undefined, b)} />
        <button
          className="send-btn"
          onClick={() => input.trim() && send(input.trim())}
          disabled={!input.trim() || sending}
        >
          ➤
        </button>
      </div>
    </div>
  );
}

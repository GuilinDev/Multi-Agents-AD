import { useRef, useState } from 'react';

interface Props {
  onRecorded: (blob: Blob) => void;
}

export default function VoiceButton({ onRecorded }: Props) {
  const [recording, setRecording] = useState(false);
  const mr = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const rec = new MediaRecorder(stream);
    chunks.current = [];
    rec.ondataavailable = (e) => chunks.current.push(e.data);
    rec.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(chunks.current, { type: 'audio/webm' });
      onRecorded(blob);
    };
    rec.start();
    mr.current = rec;
    setRecording(true);
  };

  const stop = () => {
    mr.current?.stop();
    setRecording(false);
  };

  return (
    <button
      className={`voice-btn ${recording ? 'recording' : ''}`}
      onPointerDown={start}
      onPointerUp={stop}
      onPointerLeave={stop}
      type="button"
    >
      {recording ? <span className="pulse-dot" /> : '🎤'}
    </button>
  );
}

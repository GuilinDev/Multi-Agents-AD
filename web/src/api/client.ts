const BASE = '';

export async function getPatients() {
  const r = await fetch(`${BASE}/api/patients`);
  return r.json();
}

export async function startSession(patientId: string) {
  const r = await fetch(`${BASE}/api/session/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ patient_id: patientId }),
  });
  return r.json();
}

export async function sendChat(sessionId: string, message?: string, audio?: Blob) {
  const fd = new FormData();
  fd.append('session_id', sessionId);
  if (message) fd.append('message', message);
  if (audio) fd.append('audio', audio, 'recording.webm');
  const r = await fetch(`${BASE}/api/chat`, { method: 'POST', body: fd });
  return r.json();
}

export async function getTrends(patientId: string) {
  const r = await fetch(`${BASE}/api/trends/${patientId}`);
  return r.json();
}

export async function getSummary(patientId: string) {
  const r = await fetch(`${BASE}/api/summary/${patientId}`);
  return r.json();
}

export async function endSession(sessionId: string) {
  const fd = new FormData();
  fd.append('session_id', sessionId);
  const r = await fetch(`${BASE}/api/session/end`, { method: 'POST', body: fd });
  return r.json();
}

import { Platform } from 'react-native';
import type {
  Patient,
  ChatResponse,
  SessionInfo,
  TrendsData,
  SummaryData,
} from '../types';

function getDefaultBaseUrl(): string {
  // Next.js (web): same origin, use relative paths
  if (Platform.OS === 'web') return '';
  // Android emulator
  if (Platform.OS === 'android') return 'http://10.0.2.2:8000';
  // iOS simulator
  return 'http://localhost:8000';
}

let baseUrl: string = getDefaultBaseUrl();

export function getBaseUrl(): string {
  return baseUrl;
}

export function setBaseUrl(url: string): void {
  baseUrl = url;
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${baseUrl}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getPatients(): Promise<Patient[]> {
  return apiGet('/api/patients');
}

export async function startSession(patientId: string): Promise<SessionInfo> {
  const res = await fetch(`${baseUrl}/api/session/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ patient_id: patientId }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function sendMessage(
  sessionId: string,
  message: string
): Promise<ChatResponse> {
  const form = new FormData();
  form.append('session_id', sessionId);
  form.append('message', message);
  const res = await fetch(`${baseUrl}/api/chat`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function sendAudio(
  sessionId: string,
  audioUri: string
): Promise<ChatResponse> {
  const form = new FormData();
  form.append('session_id', sessionId);
  form.append('message', '');
  form.append('audio', {
    uri: audioUri,
    name: 'recording.wav',
    type: 'audio/wav',
  } as any);
  const res = await fetch(`${baseUrl}/api/chat`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function endSession(
  sessionId: string
): Promise<{ session_id: string; summary: string; turns: number }> {
  const form = new FormData();
  form.append('session_id', sessionId);
  const res = await fetch(`${baseUrl}/api/session/end`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getTrends(patientId: string): Promise<TrendsData> {
  return apiGet(`/api/trends/${patientId}`);
}

export async function getSummary(patientId: string): Promise<SummaryData> {
  return apiGet(`/api/summary/${patientId}`);
}

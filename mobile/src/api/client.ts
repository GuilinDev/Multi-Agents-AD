import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  Patient,
  ChatResponse,
  SessionInfo,
  TrendsData,
  SummaryData,
} from '../types';

const DEFAULT_BASE_URL = 'http://localhost:8000';
const API_URL_KEY = '@memowell_api_url';

let cachedBaseUrl: string | null = null;

export async function getBaseUrl(): Promise<string> {
  if (cachedBaseUrl) return cachedBaseUrl;
  try {
    const stored = await AsyncStorage.getItem(API_URL_KEY);
    cachedBaseUrl = stored || DEFAULT_BASE_URL;
  } catch {
    cachedBaseUrl = DEFAULT_BASE_URL;
  }
  return cachedBaseUrl;
}

export async function setBaseUrl(url: string): Promise<void> {
  cachedBaseUrl = url;
  await AsyncStorage.setItem(API_URL_KEY, url);
}

async function apiGet<T>(path: string): Promise<T> {
  const base = await getBaseUrl();
  const res = await fetch(`${base}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getPatients(): Promise<Patient[]> {
  return apiGet('/api/patients');
}

export async function startSession(patientId: string): Promise<SessionInfo> {
  const base = await getBaseUrl();
  const res = await fetch(`${base}/api/session/start`, {
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
  const base = await getBaseUrl();
  const form = new FormData();
  form.append('session_id', sessionId);
  form.append('message', message);
  const res = await fetch(`${base}/api/chat`, {
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
  const base = await getBaseUrl();
  const form = new FormData();
  form.append('session_id', sessionId);
  form.append('message', '');
  form.append('audio', {
    uri: audioUri,
    name: 'recording.wav',
    type: 'audio/wav',
  } as any);
  const res = await fetch(`${base}/api/chat`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function endSession(
  sessionId: string
): Promise<{ session_id: string; summary: string; turns: number }> {
  const base = await getBaseUrl();
  const form = new FormData();
  form.append('session_id', sessionId);
  const res = await fetch(`${base}/api/session/end`, {
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

export function audioUrl(path: string | null, baseUrl: string): string | null {
  if (!path) return null;
  return `${baseUrl}${path}`;
}

export function imageUrl(path: string | null, baseUrl: string): string | null {
  if (!path) return null;
  return `${baseUrl}${path}`;
}

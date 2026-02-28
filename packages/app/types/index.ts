export interface Patient {
  id: string;
  name: string;
  age: number;
  diagnosis: string;
  cognitive_level: string;
}

export interface MonitorReport {
  emotion: string;
  engagement: string;
  memory_quality: string;
  cognitive_signs: string;
  risk_flags: string;
  recommendation: string;
  turn: number;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  audioUrl?: string;
  imageUrl?: string;
  monitor?: MonitorReport;
  timestamp: Date;
}

export interface ChatResponse {
  response: string;
  monitor: MonitorReport;
  audio_url: string | null;
  image_url: string | null;
  turn: number;
}

export interface SessionInfo {
  session_id: string;
  patient_name: string;
  patient_id: string;
}

export interface TrendEntry {
  session_date: string;
  turn: number;
  emotion: string;
  memory_quality: string;
  engagement: string;
  scores: {
    emotion: number;
    memory_quality: number;
    engagement: number;
  };
  risk_flags: string;
}

export interface AlertEntry {
  date: string;
  turn: number;
  flag: string;
  emotion: string;
}

export interface TrendsData {
  trends: TrendEntry[];
  alerts: AlertEntry[];
}

export interface SummaryData {
  patient_id: string;
  patient_name: string;
  summary: string;
  session_count: number;
}

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { getSimulationDashboard } from '../../api/client';

// ArkSim-inspired color palette — muted, professional
const C = {
  bg: '#f5f7fa',
  card: '#ffffff',
  border: '#e8ecef',
  text: '#1a1a1a',
  textSec: '#64748b',
  textDim: '#94a3b8',
  blue: '#3b82f6',
  green: '#10b981',
  indigo: '#6366f1',
  amber: '#f59e0b',
  pink: '#ec4899',
  red: '#ef4444',
  purple: '#8b5cf6',
  teal: '#14b8a6',
};

const METRIC_COLORS: Record<string, string> = {
  Agitation: C.amber,
  Confusion: C.blue,
  Refusal: C.indigo,
  Wandering: C.teal,
  Fall: C.red,
  Aggression: C.pink,
  Sundowning: C.amber,
  Sleep_Disturbance: C.purple,
  Other: C.textDim,
  AGITATION: C.amber,
  CONFUSION: C.blue,
  REFUSAL: C.indigo,
  WANDERING: C.teal,
  FALL: C.red,
  AGGRESSION: C.pink,
  SUNDOWNING: C.amber,
  SLEEP_DISTURBANCE: C.purple,
  OTHER: C.textDim,
};

interface DashboardData {
  total_events: number;
  total_patients: number;
  patients_with_events: number;
  event_types: Record<string, number>;
  severities: Record<string, number>;
  shifts: Record<string, number>;
  protocol_coverage_pct: number;
  intervention_rate_pct: number;
  resolution_rate_pct: number;
  top_patients: { name: string; events: number }[];
}

/* ─── Metric Card (ArkSim style: left color border, large number) ─── */
function MetricCard({ label, value, suffix, color, icon }: {
  label: string; value: number | string; suffix?: string; color: string; icon: string;
}) {
  return (
    <View style={[s.metricCard, { borderLeftColor: color, borderLeftWidth: 4 }]}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <View style={{ flex: 1 }}>
          <Text style={s.metricLabel}>{label}</Text>
          <Text style={s.metricValue}>{value}{suffix}</Text>
        </View>
        <Text style={[s.metricIcon, { color }]}>{icon}</Text>
      </View>
    </View>
  );
}

/* ─── Progress Bar (ArkSim style: thin gradient bar with score badge) ─── */
function ProgressMetric({ label, value, color, badge }: {
  label: string; value: number; color: string; badge: string;
}) {
  const badgeColor = value >= 80 ? '#dcfce7' : value >= 60 ? '#dbeafe' : value >= 40 ? '#fef3c7' : '#fecaca';
  const badgeText = value >= 80 ? '#15803d' : value >= 60 ? '#1d4ed8' : value >= 40 ? '#92400e' : '#dc2626';

  return (
    <View style={[s.perfItem, { borderLeftColor: color }]}>
      <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
        <Text style={s.perfLabel}>{label}</Text>
        <View style={[s.badge, { backgroundColor: badgeColor }]}>
          <Text style={[s.badgeText, { color: badgeText }]}>{badge}</Text>
        </View>
      </View>
      <Text style={s.perfValue}>{value}%</Text>
      <View style={s.barContainer}>
        <View style={[s.bar, { width: `${value}%`, backgroundColor: color }]} />
      </View>
    </View>
  );
}

/* ─── Bar Chart Row ─── */
function BarRow({ label, value, maxValue, color }: {
  label: string; value: number; maxValue: number; color: string;
}) {
  const pct = maxValue > 0 ? (value / maxValue) * 100 : 0;
  return (
    <View style={s.barRow}>
      <Text style={s.barLabel}>{label.replace('_', ' ')}</Text>
      <View style={s.barTrack}>
        <View style={[s.barFill, { width: `${Math.max(pct, 2)}%`, backgroundColor: color }]} />
      </View>
      <Text style={s.barCount}>{value}</Text>
    </View>
  );
}

/* ─── Main Dashboard ─── */
export function SimulationDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refresh = async () => {
    setLoading(true);
    setError('');
    try {
      const d = await getSimulationDashboard();
      setData(d);
    } catch (e: any) {
      setError(e.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, []);

  if (loading) {
    return (
      <View style={[s.screen, s.center]}>
        <ActivityIndicator size="large" color={C.blue} />
        <Text style={{ color: C.textSec, marginTop: 12, fontSize: 14 }}>Loading simulation data...</Text>
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={[s.screen, s.center]}>
        <Text style={{ color: C.red, fontSize: 16, marginBottom: 16 }}>⚠ {error || 'No data'}</Text>
        <TouchableOpacity style={s.retryBtn} onPress={refresh}>
          <Text style={{ color: '#fff', fontWeight: '600' }}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const maxEventType = Math.max(...Object.values(data.event_types), 1);
  const maxSeverity = Math.max(...Object.values(data.severities), 1);
  const maxPatient = data.top_patients.length > 0 ? data.top_patients[0].events : 1;

  const protocolBadge = data.protocol_coverage_pct >= 90 ? 'Excellent' : data.protocol_coverage_pct >= 70 ? 'Good' : 'Needs Work';
  const interventionBadge = data.intervention_rate_pct >= 80 ? 'Excellent' : data.intervention_rate_pct >= 60 ? 'Good' : 'Needs Work';
  const resolutionBadge = data.resolution_rate_pct >= 50 ? 'Good' : data.resolution_rate_pct >= 20 ? 'Fair' : 'Needs Work';

  return (
    <ScrollView style={s.screen} contentContainerStyle={s.content}>
      {/* ── Header ── */}
      <View style={s.header}>
        <Text style={s.title}>CareLoop AI — Simulation Report</Text>
        <Text style={s.subtitle}>Multi-Agent Nursing Home Simulation · 4 Models · 27B–32B Parameters</Text>
      </View>

      {/* ── Key Metrics (ArkSim grid style) ── */}
      <View style={s.metricsGrid}>
        <MetricCard label="Total Events" value={data.total_events} color={C.blue} icon="📊" />
        <MetricCard label="Patients Simulated" value={data.patients_with_events} color={C.green} icon="🏥" />
        <MetricCard label="Event Types" value={Object.keys(data.event_types).length} color={C.indigo} icon="🏷️" />
        <MetricCard label="AI Models Tested" value={4} color={C.amber} icon="🤖" />
      </View>

      {/* ── Performance Scores (ArkSim progress bar style) ── */}
      <Text style={s.sectionTitle}>📈 Performance Metrics</Text>
      <View style={s.perfSection}>
        <View style={s.perfGrid}>
          <ProgressMetric label="Protocol Coverage" value={data.protocol_coverage_pct} color={C.green} badge={protocolBadge} />
          <ProgressMetric label="Intervention Rate" value={data.intervention_rate_pct} color={C.blue} badge={interventionBadge} />
          <ProgressMetric label="Resolution Rate" value={data.resolution_rate_pct} color={C.purple} badge={resolutionBadge} />
        </View>
        <View style={s.methodNote}>
          <Text style={s.methodText}>
            Protocol coverage measures events matched to evidence-based guidelines (CMS, APA, NICE). 
            Intervention rate tracks caregiver response. Resolution rate measures completed outcome loops.
          </Text>
        </View>
      </View>

      {/* ── Event Distribution ── */}
      <Text style={s.sectionTitle}>🏷️ Event Type Distribution</Text>
      <View style={s.chartCard}>
        {Object.entries(data.event_types)
          .sort((a, b) => b[1] - a[1])
          .map(([type, count]) => (
            <BarRow key={type} label={type} value={count} maxValue={maxEventType}
              color={METRIC_COLORS[type] || C.textDim} />
          ))}
      </View>

      {/* ── Severity ── */}
      <Text style={s.sectionTitle}>⚠️ Severity Distribution</Text>
      <View style={s.chartCard}>
        {Object.entries(data.severities)
          .sort((a, b) => {
            const order = ['Critical', 'High', 'Medium', 'Low', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
            return order.indexOf(a[0]) - order.indexOf(b[0]);
          })
          .map(([sev, count]) => {
            const u = sev.toUpperCase();
            const color = u.includes('CRITICAL') ? C.red : u.includes('HIGH') ? C.pink : u.includes('MEDIUM') ? C.amber : C.green;
            return <BarRow key={sev} label={sev} value={count} maxValue={maxSeverity} color={color} />;
          })}
      </View>

      {/* ── Top Patients ── */}
      <Text style={s.sectionTitle}>👥 Top Patients by Event Count</Text>
      <View style={s.chartCard}>
        {data.top_patients.map((p, i) => (
          <BarRow key={p.name} label={`${i + 1}. ${p.name}`} value={p.events} maxValue={maxPatient} color={C.blue} />
        ))}
      </View>

      {/* ── Footer ── */}
      <View style={s.footer}>
        <Text style={s.footerText}>CareLoop AI — Evidence-based nursing home simulation</Text>
        <Text style={s.footerText}>Powered by Nemotron 30B · Qwen 3.5 27B · DeepSeek-R1 32B · Mistral Small 24B</Text>
        <Text style={s.footerText}>Running on NVIDIA DGX Spark · 128GB Unified Memory</Text>
      </View>
    </ScrollView>
  );
}

/* ─── Styles (ArkSim-inspired) ─── */
const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: C.bg },
  center: { justifyContent: 'center', alignItems: 'center' },
  content: { padding: 24, paddingBottom: 60, maxWidth: 1400, alignSelf: 'center', width: '100%' },
  retryBtn: { backgroundColor: C.blue, paddingHorizontal: 24, paddingVertical: 10, borderRadius: 8 },

  // Header
  header: { marginBottom: 32 },
  title: { fontSize: 28, fontWeight: '600', color: C.text, marginBottom: 8 },
  subtitle: { fontSize: 14, color: C.textSec, lineHeight: 20 },

  // Section
  sectionTitle: { fontSize: 18, fontWeight: '600', color: C.text, marginTop: 32, marginBottom: 16 },

  // Metric Cards (grid)
  metricsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 16, marginBottom: 8 },
  metricCard: {
    flex: 1, minWidth: 220, backgroundColor: C.card, borderRadius: 12, padding: 24,
    borderWidth: 1, borderColor: C.border,
    shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 3, shadowOffset: { width: 0, height: 1 },
  },
  metricLabel: { fontSize: 14, color: C.textSec, fontWeight: '500', marginBottom: 8 },
  metricValue: { fontSize: 36, fontWeight: '700', color: C.text },
  metricIcon: { fontSize: 40, opacity: 0.25 },

  // Performance section
  perfSection: {
    backgroundColor: '#f8fafc', borderRadius: 12, padding: 24,
    borderWidth: 1, borderColor: C.border,
  },
  perfGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 16 },
  perfItem: {
    flex: 1, minWidth: 200, backgroundColor: C.card, borderRadius: 8, padding: 20,
    borderLeftWidth: 4, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 3, shadowOffset: { width: 0, height: 1 },
  },
  perfLabel: { fontSize: 14, color: C.textSec, fontWeight: '500' },
  perfValue: { fontSize: 28, fontWeight: '700', color: C.text, marginBottom: 4 },
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4, marginLeft: 8 },
  badgeText: { fontSize: 12, fontWeight: '600' },
  barContainer: { width: '100%', height: 8, backgroundColor: '#e5e7eb', borderRadius: 4, overflow: 'hidden', marginTop: 8 },
  bar: { height: '100%', borderRadius: 4 },
  methodNote: { marginTop: 16, padding: 12, backgroundColor: '#f1f5f9', borderRadius: 8 },
  methodText: { fontSize: 13, color: C.textSec, lineHeight: 20 },

  // Chart cards
  chartCard: {
    backgroundColor: C.card, borderRadius: 12, padding: 20,
    borderWidth: 1, borderColor: C.border,
    shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 3, shadowOffset: { width: 0, height: 1 },
  },
  barRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  barLabel: { width: 130, fontSize: 14, color: C.textSec, fontWeight: '500' },
  barTrack: { flex: 1, height: 24, backgroundColor: '#f1f5f9', borderRadius: 6, overflow: 'hidden', marginHorizontal: 12 },
  barFill: { height: '100%', borderRadius: 6 },
  barCount: { width: 40, fontSize: 14, color: C.text, textAlign: 'right', fontWeight: '600' },

  // Footer
  footer: { marginTop: 40, paddingTop: 20, borderTopWidth: 1, borderTopColor: C.border, alignItems: 'center' },
  footerText: { color: C.textDim, fontSize: 13, marginBottom: 4 },
});

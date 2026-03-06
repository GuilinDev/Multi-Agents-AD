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

const COLORS = {
  bg: '#f8f9fa',
  surface: '#ffffff',
  border: '#e9ecef',
  text: '#212529',
  textDim: '#6c757d',
  blue: '#4a90d9',
  green: '#52b788',
  cyan: '#5ba4cf',
  purple: '#8b7ec8',
  yellow: '#e0a458',
  red: '#d9534f',
  orange: '#e8845f',
};

const EVENT_COLORS: Record<string, string> = {
  Agitation: COLORS.yellow,
  Confusion: COLORS.blue,
  Refusal: COLORS.purple,
  Wandering: COLORS.cyan,
  Fall: COLORS.red,
  Aggression: COLORS.orange,
  Sundowning: COLORS.yellow,
  Sleep_Disturbance: COLORS.cyan,
  Other: COLORS.textDim,
  // Also handle uppercase keys from older data
  AGITATION: COLORS.yellow,
  CONFUSION: COLORS.blue,
  REFUSAL: COLORS.purple,
  WANDERING: COLORS.cyan,
  FALL: COLORS.red,
  AGGRESSION: COLORS.orange,
  SUNDOWNING: COLORS.yellow,
  SLEEP_DISTURBANCE: COLORS.cyan,
  OTHER: COLORS.textDim,
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

function StatCard({ label, value, suffix, color }: { label: string; value: number | string; suffix?: string; color: string }) {
  return (
    <View style={[styles.statCard, { borderLeftColor: color, borderLeftWidth: 3 }]}>
      <Text style={[styles.statValue, { color: COLORS.text }]}>{value}{suffix}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function BarRow({ label, value, maxValue, color }: { label: string; value: number; maxValue: number; color: string }) {
  const pct = maxValue > 0 ? (value / maxValue) * 100 : 0;
  return (
    <View style={styles.barRow}>
      <Text style={styles.barLabel}>{label}</Text>
      <View style={styles.barTrack}>
        <View style={[styles.barFill, { width: `${pct}%`, backgroundColor: color, opacity: 0.75 }]} />
      </View>
      <Text style={styles.barValue}>{value}</Text>
    </View>
  );
}

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
      <View style={[styles.screen, styles.center]}>
        <ActivityIndicator size="large" color={COLORS.blue} />
        <Text style={[styles.text, { marginTop: 12 }]}>Loading simulation data...</Text>
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={[styles.screen, styles.center]}>
        <Text style={styles.errorText}>⚠️ {error || 'No data'}</Text>
        <TouchableOpacity style={styles.retryBtn} onPress={refresh}>
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const maxEventType = Math.max(...Object.values(data.event_types), 1);
  const maxPatientEvents = data.top_patients.length > 0 ? data.top_patients[0].events : 1;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      {/* Header */}
      <Text style={styles.title}>🔬 CareLoop AI</Text>
      <Text style={styles.subtitle}>Multi-Agent Simulation Dashboard</Text>

      {/* Key Metrics */}
      <View style={styles.statsRow}>
        <StatCard label="Total Events" value={data.total_events} color={COLORS.blue} />
        <StatCard label="Patients" value={data.patients_with_events} color={COLORS.green} />
        <StatCard label="Protocol Coverage" value={data.protocol_coverage_pct} suffix="%" color={COLORS.cyan} />
      </View>
      <View style={styles.statsRow}>
        <StatCard label="Intervention Rate" value={data.intervention_rate_pct} suffix="%" color={COLORS.purple} />
        <StatCard label="Resolution Rate" value={data.resolution_rate_pct} suffix="%" color={COLORS.green} />
        <StatCard label="Models Tested" value={4} color={COLORS.yellow} />
      </View>

      {/* Event Type Distribution */}
      <Text style={styles.sectionTitle}>Event Type Distribution</Text>
      <View style={styles.card}>
        {Object.entries(data.event_types)
          .sort((a, b) => b[1] - a[1])
          .map(([type, count]) => (
            <BarRow
              key={type}
              label={type.replace('_', ' ')}
              value={count}
              maxValue={maxEventType}
              color={EVENT_COLORS[type] || COLORS.textDim}
            />
          ))}
      </View>

      {/* Severity Distribution */}
      <Text style={styles.sectionTitle}>Severity Distribution</Text>
      <View style={styles.card}>
        {Object.entries(data.severities)
          .sort((a, b) => {
            const order = ['Critical', 'High', 'Medium', 'Low', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
            return order.indexOf(a[0]) - order.indexOf(b[0]);
          })
          .map(([sev, count]) => {
            const s = sev.toUpperCase();
            return (
              <BarRow
                key={sev}
                label={sev}
                value={count}
                maxValue={Math.max(...Object.values(data.severities), 1)}
                color={s.includes('CRITICAL') ? COLORS.red : s.includes('HIGH') ? COLORS.orange : s.includes('MEDIUM') ? COLORS.yellow : COLORS.green}
              />
            );
          })}
      </View>

      {/* Shift Distribution */}
      <Text style={styles.sectionTitle}>Shift Distribution</Text>
      <View style={styles.card}>
        {Object.entries(data.shifts).map(([shift, count]) => {
          const s = shift.toUpperCase();
          return (
            <BarRow
              key={shift}
              label={shift}
              value={count}
              maxValue={Math.max(...Object.values(data.shifts), 1)}
              color={s.includes('DAY') ? COLORS.yellow : s.includes('EVENING') ? COLORS.purple : COLORS.blue}
            />
          );
        })}
      </View>

      {/* Top Patients */}
      <Text style={styles.sectionTitle}>Top Patients by Event Count</Text>
      <View style={styles.card}>
        {data.top_patients.map((p, i) => (
          <BarRow
            key={p.name}
            label={`${i + 1}. ${p.name}`}
            value={p.events}
            maxValue={maxPatientEvents}
            color={COLORS.blue}
          />
        ))}
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          CareLoop AI — Evidence-based nursing home simulation
        </Text>
        <Text style={styles.footerText}>
          4 models × 3 shifts | 27B–32B parameter range | NVIDIA DGX Spark
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: COLORS.bg },
  center: { justifyContent: 'center', alignItems: 'center' },
  content: { padding: 20, paddingBottom: 60 },
  text: { color: COLORS.text, fontSize: 14 },
  title: { fontSize: 26, fontWeight: '600', color: COLORS.text, textAlign: 'center' },
  subtitle: { fontSize: 13, color: COLORS.textDim, textAlign: 'center', marginBottom: 24, letterSpacing: 0.5 },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: COLORS.text, marginTop: 28, marginBottom: 12 },
  statsRow: { flexDirection: 'row', gap: 12, marginBottom: 12 },
  statCard: {
    flex: 1, backgroundColor: COLORS.surface, borderRadius: 10, padding: 16,
    borderWidth: 1, borderColor: COLORS.border,
    shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 8, shadowOffset: { width: 0, height: 2 },
  },
  statValue: { fontSize: 26, fontWeight: '600' },
  statLabel: { fontSize: 11, color: COLORS.textDim, marginTop: 4, textTransform: 'uppercase', letterSpacing: 0.5 },
  card: {
    backgroundColor: COLORS.surface, borderRadius: 10, padding: 16,
    borderWidth: 1, borderColor: COLORS.border,
    shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 8, shadowOffset: { width: 0, height: 2 },
  },
  barRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  barLabel: { width: 120, fontSize: 13, color: COLORS.textDim },
  barTrack: { flex: 1, height: 22, backgroundColor: '#f1f3f5', borderRadius: 6, overflow: 'hidden', marginHorizontal: 10 },
  barFill: { height: '100%', borderRadius: 6 },
  barValue: { width: 40, fontSize: 13, color: COLORS.text, textAlign: 'right', fontWeight: '600' },
  errorText: { color: COLORS.red, fontSize: 16, marginBottom: 16 },
  retryBtn: { backgroundColor: COLORS.blue, paddingHorizontal: 24, paddingVertical: 10, borderRadius: 8 },
  retryText: { color: '#fff', fontWeight: '600' },
  footer: { marginTop: 32, alignItems: 'center' },
  footerText: { color: COLORS.textDim, fontSize: 12, marginBottom: 4 },
});

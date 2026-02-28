import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { colors } from '../../theme/colors';
import type { TrendEntry, AlertEntry, SummaryData } from '../../types';
import { getTrends, getSummary } from '../../api/client';
import { TrendChart } from '../../components/trend-chart';

export function DashboardScreen() {
  const [trends, setTrends] = useState<TrendEntry[]>([]);
  const [alerts, setAlerts] = useState<AlertEntry[]>([]);
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const patientId = 'margaret';

  const refresh = async () => {
    setLoading(true);
    setError('');
    try {
      const [trendData, summaryData] = await Promise.all([
        getTrends(patientId),
        getSummary(patientId),
      ]);
      setTrends(trendData.trends);
      setAlerts(trendData.alerts);
      setSummary(summaryData);
    } catch {
      setError('Could not load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.header}>👨‍⚕️ Caregiver Dashboard</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <TouchableOpacity style={styles.refreshButton} onPress={refresh} disabled={loading}>
        {loading ? (
          <ActivityIndicator color="#FFF" size="small" />
        ) : (
          <Text style={styles.refreshText}>🔄 Refresh</Text>
        )}
      </TouchableOpacity>

      {summary && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{summary.patient_name}</Text>
          <Text style={styles.cardSubtitle}>{summary.session_count} sessions recorded</Text>
          <Text style={styles.summaryText}>{summary.summary}</Text>
        </View>
      )}

      <TrendChart trends={trends} />

      <Text style={styles.sectionTitle}>⚠️ Alerts</Text>
      {alerts.length === 0 ? (
        <Text style={styles.emptyText}>No alerts recorded.</Text>
      ) : (
        alerts.slice(-10).reverse().map((a, i) => (
          <View key={i} style={styles.alertCard}>
            <View style={styles.alertHeader}>
              <Text style={styles.alertDate}>{a.date}</Text>
              <Text style={styles.alertEmotion}>{a.emotion}</Text>
            </View>
            <Text style={styles.alertFlag}>⚠️ {a.flag}</Text>
          </View>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20, paddingTop: 16, paddingBottom: 40 },
  header: { fontSize: 28, fontWeight: '700', color: colors.text, marginBottom: 16 },
  error: { color: colors.error, fontSize: 15, marginBottom: 12 },
  refreshButton: {
    backgroundColor: colors.primary, paddingVertical: 12, paddingHorizontal: 24,
    borderRadius: 12, alignSelf: 'flex-start', marginBottom: 20,
  },
  refreshText: { color: '#FFF', fontSize: 16, fontWeight: '600' },
  card: {
    backgroundColor: colors.surface, padding: 20, borderRadius: 16,
    marginBottom: 20, borderWidth: 1, borderColor: colors.border,
  },
  cardTitle: { fontSize: 22, fontWeight: '700', color: colors.primary },
  cardSubtitle: { fontSize: 14, color: colors.textSecondary, marginTop: 4, marginBottom: 12 },
  summaryText: { fontSize: 16, lineHeight: 24, color: colors.text },
  sectionTitle: { fontSize: 20, fontWeight: '700', color: colors.text, marginTop: 20, marginBottom: 12 },
  emptyText: { fontSize: 16, color: colors.textLight, fontStyle: 'italic' },
  alertCard: {
    backgroundColor: '#FFF3E0', padding: 14, borderRadius: 12, marginBottom: 10,
    borderLeftWidth: 4, borderLeftColor: colors.warning,
  },
  alertHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  alertDate: { fontSize: 13, color: colors.textSecondary, fontWeight: '600' },
  alertEmotion: { fontSize: 13, color: colors.warning, fontWeight: '600', textTransform: 'capitalize' },
  alertFlag: { fontSize: 15, color: colors.text },
});

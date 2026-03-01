import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { colors } from '../../theme/colors';
import { SignaturePad } from '../../components/signature-pad';
import { listEvents, generateHandoff, acknowledgeHandoff } from '../../api/client';
import type { EventOut } from '../../types';

export function HandoffScreen() {
  const [events, setEvents] = useState<EventOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [signed, setSigned] = useState(false);
  const [signatureData, setSignatureData] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadEvents();
  }, []);

  async function loadEvents() {
    try {
      setLoading(true);
      setError(null);
      const data = await listEvents();
      setEvents(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load events');
    } finally {
      setLoading(false);
    }
  }

  const alerts = events.filter((e) => e.severity === 'high' || e.severity === 'critical');
  const regularEvents = events;

  const handleConfirmSignature = (data: string) => {
    setSignatureData(data);
    Alert.alert('Signature Confirmed', 'You can now submit the handoff.');
  };

  const handleSubmitHandoff = async () => {
    if (!signatureData) return;
    try {
      setSubmitting(true);
      // Generate handoff for current shift
      const patientIds = [...new Set(events.map((e) => e.patient_id))];
      const handoff = await generateHandoff('day', 1, patientIds);
      // Acknowledge the handoff
      if (handoff?.id) {
        await acknowledgeHandoff(handoff.id);
      }
      setSigned(true);
      Alert.alert('Handoff Complete', 'Shift handoff has been recorded successfully.');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to submit handoff');
    } finally {
      setSubmitting(false);
    }
  };

  function formatTime(dateStr?: string): string {
    if (!dateStr) return '--:--';
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={{ marginTop: 12, color: colors.textSecondary }}>Loading events...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center', padding: 24 }]}>
        <Text style={{ color: colors.error, fontSize: 16, textAlign: 'center', marginBottom: 16 }}>{error}</Text>
        <TouchableOpacity onPress={loadEvents} style={styles.submitButton}>
          <Text style={styles.submitText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Shift Handoff</Text>

      {/* Summary */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Shift Summary</Text>
        <View style={styles.summaryRow}>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryNumber}>{events.length}</Text>
            <Text style={styles.summaryLabel}>Events</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={[styles.summaryNumber, { color: colors.warning }]}>{alerts.length}</Text>
            <Text style={styles.summaryLabel}>Alerts</Text>
          </View>
        </View>
      </View>

      {/* Alerts */}
      {alerts.map((alert) => (
        <View key={alert.id} style={styles.alertCard}>
          <Text style={styles.alertText}>⚠️ {alert.description}</Text>
        </View>
      ))}

      {/* Events */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Events</Text>
        {regularEvents.length === 0 ? (
          <Text style={{ color: colors.textSecondary, fontStyle: 'italic' }}>No events recorded this shift.</Text>
        ) : (
          regularEvents.map((event) => (
            <View key={event.id} style={styles.eventRow}>
              <Text style={styles.eventTime}>{formatTime(event.event_at || event.created_at)}</Text>
              <Text style={styles.eventText}>{event.description}</Text>
            </View>
          ))
        )}
      </View>

      {/* Signature */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Outgoing Caregiver Signature</Text>
        {signed ? (
          <View style={styles.signedBadge}>
            <Text style={styles.signedText}>✓ Signed</Text>
          </View>
        ) : (
          <>
            <SignaturePad onConfirm={handleConfirmSignature} />
            <TouchableOpacity
              style={[styles.submitButton, (!signatureData || submitting) && styles.submitDisabled]}
              onPress={handleSubmitHandoff}
              disabled={!signatureData || submitting}
            >
              <Text style={styles.submitText}>{submitting ? 'Submitting...' : 'Submit Handoff'}</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 16, paddingBottom: 40 },
  title: { fontSize: 24, fontWeight: '700', color: colors.text, marginBottom: 16 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardTitle: { fontSize: 16, fontWeight: '600', color: colors.text, marginBottom: 12 },
  summaryRow: { flexDirection: 'row', gap: 24 },
  summaryItem: { alignItems: 'center' },
  summaryNumber: { fontSize: 28, fontWeight: '700', color: colors.primary },
  summaryLabel: { fontSize: 13, color: colors.textSecondary, marginTop: 2 },
  alertCard: {
    backgroundColor: '#FFF3E0',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: colors.warning,
  },
  alertText: { fontSize: 14, color: colors.text },
  eventRow: {
    flexDirection: 'row',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  eventTime: { width: 52, fontSize: 13, fontWeight: '600', color: colors.primary },
  eventText: { flex: 1, fontSize: 14, color: colors.text },
  signedBadge: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  signedText: { fontSize: 18, fontWeight: '600', color: colors.success },
  submitButton: {
    marginTop: 16,
    paddingVertical: 14,
    borderRadius: 8,
    backgroundColor: colors.primary,
    alignItems: 'center',
  },
  submitDisabled: { opacity: 0.4 },
  submitText: { color: '#FFF', fontSize: 16, fontWeight: '600' },
});

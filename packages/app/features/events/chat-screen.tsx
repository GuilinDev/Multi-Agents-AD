import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Modal,
  Switch,
} from 'react-native';
import { useRouter } from 'solito/router';
import { colors } from '../../theme/colors';
import type { EventReportResponse, EventOut } from '../../types';
import {
  reportEvent,
  recordIntervention,
  recordOutcome,
  listEvents,
} from '../../api/client';
import { VoiceButton } from '../../components/voice-button';

const REPORTER_ID = 1; // hardcoded demo user

function ProtocolCard({ protocol }: { protocol: any }) {
  const [expanded, setExpanded] = useState(false);
  const hasSteps = protocol.steps && protocol.steps.length > 0;
  const sourceLabel = protocol.source || 'Unknown';
  
  return (
    <View style={styles.protocolCard}>
      <View style={styles.protocolHeader}>
        <View style={styles.sourceTag}>
          <Text style={styles.sourceTagText}>{sourceLabel}</Text>
        </View>
        {protocol.page > 0 && (
          <Text style={styles.protocolPage}>p.{protocol.page}</Text>
        )}
      </View>
      {hasSteps ? (
        <View style={styles.stepsContainer}>
          {protocol.steps.map((step: string, idx: number) => (
            <Text key={idx} style={styles.stepText}>✅ {step}</Text>
          ))}
        </View>
      ) : (
        <Text style={styles.protocolText} numberOfLines={expanded ? undefined : 4}>
          {(protocol.text_preview || protocol.text || '').substring(0, 200)}
        </Text>
      )}
      {protocol.text && protocol.text.length > 200 && (
        <TouchableOpacity onPress={() => setExpanded(!expanded)}>
          <Text style={styles.expandToggle}>
            {expanded ? 'Show less ▲' : 'Show more ▼'}
          </Text>
        </TouchableOpacity>
      )}
      {expanded && protocol.text && (
        <Text style={styles.fullText}>{protocol.text}</Text>
      )}
    </View>
  );
}

interface Props {
  patientId: string;
  patientName: string;
}

export function ChatScreen({ patientId, patientName }: Props) {
  const router = useRouter();
  const [text, setText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<EventReportResponse | null>(null);
  const [error, setError] = useState('');

  // Intervention modal
  const [showIntervention, setShowIntervention] = useState(false);
  const [interventionText, setInterventionText] = useState('');
  const [interventionSaving, setInterventionSaving] = useState(false);

  // Outcome modal
  const [showOutcome, setShowOutcome] = useState(false);
  const [outcomeText, setOutcomeText] = useState('');
  const [outcomeResolved, setOutcomeResolved] = useState(false);
  const [outcomeSaving, setOutcomeSaving] = useState(false);

  // History
  const [history, setHistory] = useState<EventOut[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const numericPatientId = parseInt(patientId, 10);

  const loadHistory = async () => {
    try {
      const events = await listEvents(numericPatientId);
      setHistory(events);
    } catch {}
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleReport = async () => {
    if (!text.trim()) return;
    setSubmitting(true);
    setError('');
    setResult(null);
    try {
      const res = await reportEvent(numericPatientId, REPORTER_ID, text.trim());
      setResult(res);
      setText('');
      loadHistory();
    } catch (e: any) {
      setError(e.message || 'Failed to report event');
    } finally {
      setSubmitting(false);
    }
  };

  const handleIntervention = async () => {
    if (!interventionText.trim() || !result) return;
    setInterventionSaving(true);
    try {
      await recordIntervention(result.event_id, interventionText.trim());
      setShowIntervention(false);
      setInterventionText('');
      loadHistory();
    } catch (e: any) {
      setError(e.message || 'Failed to record intervention');
    } finally {
      setInterventionSaving(false);
    }
  };

  const handleOutcome = async () => {
    if (!outcomeText.trim() || !result) return;
    setOutcomeSaving(true);
    try {
      await recordOutcome(result.event_id, outcomeText.trim(), outcomeResolved);
      setShowOutcome(false);
      setOutcomeText('');
      setOutcomeResolved(false);
      loadHistory();
    } catch (e: any) {
      setError(e.message || 'Failed to record outcome');
    } finally {
      setOutcomeSaving(false);
    }
  };

  const severityColor = (s: string) => {
    switch (s.toLowerCase()) {
      case 'high': return colors.error;
      case 'medium': return '#F5A623';
      default: return colors.primary;
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={styles.backButton}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{patientName}</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView style={styles.body} contentContainerStyle={styles.bodyContent}>
        {/* Event Report Form */}
        <Text style={styles.sectionTitle}>Report Behavioral Event</Text>
        <View style={styles.inputWrapper}>
          <TextInput
            style={styles.textInput}
            value={text}
            onChangeText={setText}
            placeholder="Describe the behavioral event..."
            placeholderTextColor={colors.textLight}
            multiline
            editable={!submitting}
          />
          <View style={styles.voiceButtonContainer}>
            <VoiceButton onRecordingComplete={() => {}} disabled={submitting} />
          </View>
        </View>
        <TouchableOpacity
          style={[styles.reportButton, (!text.trim() || submitting) && styles.reportButtonDisabled]}
          onPress={handleReport}
          disabled={!text.trim() || submitting}
          activeOpacity={0.7}
        >
          {submitting ? (
            <ActivityIndicator color="#FFF" />
          ) : (
            <Text style={styles.reportButtonText}>Report Event</Text>
          )}
        </TouchableOpacity>

        {error ? <Text style={styles.error}>{error}</Text> : null}

        {/* Result */}
        {result && (
          <View style={styles.resultCard}>
            <Text style={styles.resultTitle}>Event Reported</Text>

            <View style={styles.parsedRow}>
              <Text style={styles.parsedLabel}>Type:</Text>
              <Text style={styles.parsedValue}>{result.parsed.event_type}</Text>
            </View>
            <View style={styles.parsedRow}>
              <Text style={styles.parsedLabel}>Severity:</Text>
              <Text style={[styles.parsedValue, { color: severityColor(result.parsed.severity) }]}>
                {result.parsed.severity}
              </Text>
            </View>
            <View style={styles.parsedRow}>
              <Text style={styles.parsedLabel}>Trigger:</Text>
              <Text style={styles.parsedValue}>{result.parsed.trigger}</Text>
            </View>
            <View style={styles.parsedRow}>
              <Text style={styles.parsedLabel}>Location:</Text>
              <Text style={styles.parsedValue}>{result.parsed.location}</Text>
            </View>
            <View style={styles.parsedRow}>
              <Text style={styles.parsedLabel}>Summary:</Text>
              <Text style={styles.parsedValue}>{result.parsed.summary}</Text>
            </View>

            {result.protocols.length > 0 ? (
              <>
                <Text style={styles.protocolTitle}>Protocol Suggestions</Text>
                {result.protocols.map((p, i) => (
                  <ProtocolCard key={i} protocol={p} />
                ))}
              </>
            ) : (
              <View style={styles.noProtocolBanner}>
                <Text style={styles.noProtocolText}>
                  ✅ No behavioral issues detected. Continue routine monitoring.
                </Text>
              </View>
            )}

            {/* Action buttons */}
            <View style={styles.actionRow}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => setShowIntervention(true)}
              >
                <Text style={styles.actionButtonText}>Record Intervention</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.actionButton, styles.actionButtonSecondary]}
                onPress={() => setShowOutcome(true)}
              >
                <Text style={[styles.actionButtonText, styles.actionButtonTextSecondary]}>
                  Record Outcome
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* History */}
        <TouchableOpacity
          style={styles.historyToggle}
          onPress={() => setShowHistory(!showHistory)}
        >
          <Text style={styles.historyToggleText}>
            {showHistory ? '▼' : '▶'} Event History ({history.length})
          </Text>
        </TouchableOpacity>

        {showHistory && history.map((evt) => (
          <View key={evt.id} style={styles.historyCard}>
            <View style={styles.historyHeader}>
              <Text style={styles.historyType}>{evt.event_type}</Text>
              <Text style={[styles.historySeverity, { color: severityColor(evt.severity) }]}>
                {evt.severity}
              </Text>
            </View>
            <Text style={styles.historyDesc} numberOfLines={2}>{evt.description}</Text>
            {evt.intervention_description && (
              <Text style={styles.historyMeta}>
                ✅ Intervention: {evt.intervention_description}
              </Text>
            )}
            {evt.resolved && <Text style={styles.historyResolved}>Resolved</Text>}
            {evt.created_at && (
              <Text style={styles.historyDate}>
                {new Date(evt.created_at).toLocaleDateString()}
              </Text>
            )}
          </View>
        ))}
      </ScrollView>

      {/* Intervention Modal */}
      <Modal visible={showIntervention} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Record Intervention</Text>
            <TextInput
              style={styles.modalInput}
              value={interventionText}
              onChangeText={setInterventionText}
              placeholder="Describe the intervention taken..."
              placeholderTextColor={colors.textLight}
              multiline
            />
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.modalCancel}
                onPress={() => setShowIntervention(false)}
              >
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalSave, interventionSaving && styles.reportButtonDisabled]}
                onPress={handleIntervention}
                disabled={interventionSaving}
              >
                {interventionSaving ? (
                  <ActivityIndicator color="#FFF" size="small" />
                ) : (
                  <Text style={styles.modalSaveText}>Save</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Outcome Modal */}
      <Modal visible={showOutcome} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Record Outcome</Text>
            <TextInput
              style={styles.modalInput}
              value={outcomeText}
              onChangeText={setOutcomeText}
              placeholder="Describe the outcome..."
              placeholderTextColor={colors.textLight}
              multiline
            />
            <View style={styles.resolvedRow}>
              <Text style={styles.resolvedLabel}>Resolved?</Text>
              <Switch
                value={outcomeResolved}
                onValueChange={setOutcomeResolved}
                trackColor={{ true: colors.primary, false: colors.border }}
              />
            </View>
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.modalCancel}
                onPress={() => setShowOutcome(false)}
              >
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalSave, outcomeSaving && styles.reportButtonDisabled]}
                onPress={handleOutcome}
                disabled={outcomeSaving}
              >
                {outcomeSaving ? (
                  <ActivityIndicator color="#FFF" size="small" />
                ) : (
                  <Text style={styles.modalSaveText}>Save</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 16, paddingVertical: 12, backgroundColor: colors.surface,
    borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  headerTitle: { fontSize: 18, fontWeight: '600', color: colors.text },
  backButton: { color: colors.primary, fontSize: 16, fontWeight: '600' },
  body: { flex: 1 },
  bodyContent: { padding: 16, paddingBottom: 40 },
  sectionTitle: {
    fontSize: 20, fontWeight: '600', color: colors.text, marginBottom: 12,
  },
  inputWrapper: {
    flexDirection: 'row', alignItems: 'flex-start',
    backgroundColor: colors.card, borderRadius: 16, borderWidth: 1,
    borderColor: colors.border, paddingRight: 6,
  },
  textInput: {
    flex: 1, minHeight: 100, maxHeight: 200,
    paddingHorizontal: 16, paddingVertical: 12, fontSize: 16, color: colors.text,
    textAlignVertical: 'top',
  },
  voiceButtonContainer: {
    paddingTop: 12,
  },
  reportButton: {
    backgroundColor: colors.primary, paddingVertical: 16,
    borderRadius: 16, alignItems: 'center', marginTop: 12, elevation: 3,
    shadowColor: colors.primaryDark, shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3, shadowRadius: 6,
  },
  reportButtonDisabled: { opacity: 0.4 },
  reportButtonText: { color: '#FFF', fontSize: 18, fontWeight: '700' },
  error: { color: colors.error, fontSize: 14, marginTop: 8 },

  // Result card
  resultCard: {
    backgroundColor: colors.surface, borderRadius: 16, padding: 16, marginTop: 20,
    borderWidth: 1, borderColor: colors.border,
  },
  resultTitle: { fontSize: 18, fontWeight: '700', color: colors.primary, marginBottom: 12 },
  parsedRow: { flexDirection: 'row', marginBottom: 6 },
  parsedLabel: { fontSize: 14, fontWeight: '600', color: colors.textSecondary, width: 80 },
  parsedValue: { fontSize: 14, color: colors.text, flex: 1 },

  protocolTitle: {
    fontSize: 16, fontWeight: '600', color: colors.text, marginTop: 16, marginBottom: 8,
  },
  protocolCard: {
    backgroundColor: colors.card, borderRadius: 12, padding: 12, marginBottom: 8,
    borderLeftWidth: 3, borderLeftColor: colors.primary,
  },
  protocolHeader: {
    flexDirection: 'row', alignItems: 'center', marginBottom: 8, gap: 8,
  },
  sourceTag: {
    backgroundColor: colors.primary, borderRadius: 6, paddingHorizontal: 8, paddingVertical: 2,
  },
  sourceTagText: { color: '#FFF', fontSize: 11, fontWeight: '700' },
  protocolPage: { fontSize: 12, color: colors.textSecondary },
  stepsContainer: { gap: 6 },
  stepText: { fontSize: 14, color: colors.text, lineHeight: 20 },
  protocolText: { fontSize: 14, color: colors.text, lineHeight: 20 },
  expandToggle: { fontSize: 13, color: colors.primary, marginTop: 6, fontWeight: '600' },
  fullText: { fontSize: 13, color: colors.textSecondary, marginTop: 8, lineHeight: 18 },
  noProtocolBanner: {
    backgroundColor: '#E8F5E9', borderRadius: 12, padding: 16, marginTop: 16,
  },
  noProtocolText: { fontSize: 15, color: '#2E7D32', textAlign: 'center', fontWeight: '600' },
  protocolSource: { fontSize: 12, color: colors.textSecondary, marginTop: 4 },

  actionRow: { flexDirection: 'row', gap: 10, marginTop: 16 },
  actionButton: {
    flex: 1, backgroundColor: colors.primary, paddingVertical: 12,
    borderRadius: 12, alignItems: 'center',
  },
  actionButtonSecondary: {
    backgroundColor: 'transparent', borderWidth: 2, borderColor: colors.primary,
  },
  actionButtonText: { color: '#FFF', fontSize: 14, fontWeight: '600' },
  actionButtonTextSecondary: { color: colors.primary },

  // History
  historyToggle: { marginTop: 24, paddingVertical: 8 },
  historyToggleText: { fontSize: 16, fontWeight: '600', color: colors.primary },
  historyCard: {
    backgroundColor: colors.surface, borderRadius: 12, padding: 12, marginTop: 8,
    borderWidth: 1, borderColor: colors.border,
  },
  historyHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  historyType: { fontSize: 14, fontWeight: '600', color: colors.text },
  historySeverity: { fontSize: 13, fontWeight: '600' },
  historyDesc: { fontSize: 13, color: colors.textSecondary, marginBottom: 4 },
  historyMeta: { fontSize: 12, color: colors.primary },
  historyResolved: { fontSize: 12, color: colors.primary, fontWeight: '600', marginTop: 2 },
  historyDate: { fontSize: 11, color: colors.textLight, marginTop: 4 },

  // Modals
  modalOverlay: {
    flex: 1, backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center', padding: 24,
  },
  modalContent: {
    backgroundColor: colors.surface, borderRadius: 20, padding: 24,
  },
  modalTitle: { fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 16 },
  modalInput: {
    backgroundColor: colors.card, borderRadius: 12, padding: 12,
    fontSize: 15, color: colors.text, minHeight: 80, textAlignVertical: 'top',
    borderWidth: 1, borderColor: colors.border,
  },
  resolvedRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    marginTop: 12,
  },
  resolvedLabel: { fontSize: 15, color: colors.text },
  modalActions: { flexDirection: 'row', gap: 10, marginTop: 16 },
  modalCancel: {
    flex: 1, paddingVertical: 12, borderRadius: 12,
    alignItems: 'center', backgroundColor: colors.card,
  },
  modalCancelText: { fontSize: 15, color: colors.textSecondary, fontWeight: '600' },
  modalSave: {
    flex: 1, paddingVertical: 12, borderRadius: 12,
    alignItems: 'center', backgroundColor: colors.primary,
  },
  modalSaveText: { color: '#FFF', fontSize: 15, fontWeight: '600' },
});

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { useRouter } from 'solito/router';
import { colors } from '../../theme/colors';
import type { Patient } from '../../types';
import { getPatients } from '../../api/client';

export function HomeScreen() {
  const router = useRouter();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selected, setSelected] = useState<string>('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      const list = await getPatients();
      setPatients(list);
      if (list.length > 0) setSelected(list[0].id);
    } catch {
      setError('Could not connect to server. Check Settings.');
    }
  };

  const handleStart = () => {
    if (!selected) return;
    const patient = patients.find((p) => p.id === selected);
    if (!patient) return;
    router.push({
      pathname: '/chat',
      query: {
        patientId: patient.id,
        patientName: patient.name,
      },
    });
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.emoji}>🧠</Text>
      <Text style={styles.title}>Memowell</Text>
      <Text style={styles.subtitle}>Behavioral Event Reporter</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <Text style={styles.sectionTitle}>Select Patient</Text>

      {patients.map((p) => (
        <TouchableOpacity
          key={p.id}
          style={[styles.patientCard, selected === p.id && styles.patientCardSelected]}
          onPress={() => setSelected(p.id)}
          activeOpacity={0.7}
        >
          <Text style={styles.patientName}>{p.name}</Text>
          <Text style={styles.patientInfo}>
            Age {p.age} · {p.cognitive_level}
          </Text>
        </TouchableOpacity>
      ))}

      <TouchableOpacity
        style={[styles.startButton, !selected && styles.startButtonDisabled]}
        onPress={handleStart}
        disabled={!selected}
        activeOpacity={0.7}
      >
        <Text style={styles.startButtonText}>Report Event</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, paddingTop: 60, alignItems: 'center' },
  emoji: { fontSize: 64, marginBottom: 8 },
  title: { fontSize: 36, fontWeight: '700', color: colors.primary, marginBottom: 4 },
  subtitle: { fontSize: 18, color: colors.textSecondary, marginBottom: 40 },
  sectionTitle: {
    fontSize: 20, fontWeight: '600', color: colors.text,
    alignSelf: 'flex-start', marginBottom: 12,
  },
  patientCard: {
    width: '100%', backgroundColor: colors.surface, padding: 20,
    borderRadius: 16, marginBottom: 12, borderWidth: 2, borderColor: colors.border,
  },
  patientCardSelected: { borderColor: colors.primary, backgroundColor: colors.card },
  patientName: { fontSize: 20, fontWeight: '600', color: colors.text },
  patientInfo: { fontSize: 15, color: colors.textSecondary, marginTop: 4 },
  startButton: {
    width: '100%', backgroundColor: colors.primary, paddingVertical: 18,
    borderRadius: 16, alignItems: 'center', marginTop: 24, elevation: 3,
    shadowColor: colors.primaryDark, shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3, shadowRadius: 6,
  },
  startButtonDisabled: { opacity: 0.5 },
  startButtonText: { color: '#FFF', fontSize: 20, fontWeight: '700' },
  error: { color: colors.error, fontSize: 15, marginBottom: 16, textAlign: 'center' },
});

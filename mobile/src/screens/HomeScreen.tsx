import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { colors } from '../theme/colors';
import { Patient } from '../types';
import { getPatients, startSession } from '../api/client';

interface Props {
  navigation: any;
}

export default function HomeScreen({ navigation }: Props) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selected, setSelected] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      const list = await getPatients();
      setPatients(list);
      if (list.length > 0) setSelected(list[0].id);
    } catch (e: any) {
      setError('Could not connect to server. Check Settings.');
    }
  };

  const handleStart = async () => {
    if (!selected) return;
    setLoading(true);
    setError('');
    try {
      const session = await startSession(selected);
      navigation.navigate('Chat', { session });
    } catch (e: any) {
      setError(e.message || 'Failed to start session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.emoji}>🧠</Text>
      <Text style={styles.title}>Memowell</Text>
      <Text style={styles.subtitle}>Reminiscence Therapy Companion</Text>

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
        style={[styles.startButton, (!selected || loading) && styles.startButtonDisabled]}
        onPress={handleStart}
        disabled={!selected || loading}
        activeOpacity={0.7}
      >
        {loading ? (
          <ActivityIndicator color="#FFF" />
        ) : (
          <Text style={styles.startButtonText}>Start Session</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: 24,
    paddingTop: 60,
    alignItems: 'center',
  },
  emoji: {
    fontSize: 64,
    marginBottom: 8,
  },
  title: {
    fontSize: 36,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 18,
    color: colors.textSecondary,
    marginBottom: 40,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.text,
    alignSelf: 'flex-start',
    marginBottom: 12,
  },
  patientCard: {
    width: '100%',
    backgroundColor: colors.surface,
    padding: 20,
    borderRadius: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: colors.border,
  },
  patientCardSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.card,
  },
  patientName: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.text,
  },
  patientInfo: {
    fontSize: 15,
    color: colors.textSecondary,
    marginTop: 4,
  },
  startButton: {
    width: '100%',
    backgroundColor: colors.primary,
    paddingVertical: 18,
    borderRadius: 16,
    alignItems: 'center',
    marginTop: 24,
    elevation: 3,
    shadowColor: colors.primaryDark,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  startButtonDisabled: {
    opacity: 0.5,
  },
  startButtonText: {
    color: '#FFF',
    fontSize: 20,
    fontWeight: '700',
  },
  error: {
    color: colors.error,
    fontSize: 15,
    marginBottom: 16,
    textAlign: 'center',
  },
});

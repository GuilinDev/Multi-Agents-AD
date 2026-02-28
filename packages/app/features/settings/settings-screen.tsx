import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { colors } from '../../theme/colors';
import { getBaseUrl, setBaseUrl } from '../../api/client';

export function SettingsScreen() {
  const [url, setUrl] = useState(getBaseUrl());
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    let cleanUrl = url.trim();
    if (cleanUrl.endsWith('/')) cleanUrl = cleanUrl.slice(0, -1);
    setBaseUrl(cleanUrl);
    setUrl(cleanUrl);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.header}>⚙️ Settings</Text>

      <Text style={styles.label}>API Server URL</Text>
      <TextInput
        style={styles.input}
        value={url}
        onChangeText={setUrl}
        placeholder="http://localhost:8000"
        placeholderTextColor={colors.textLight}
        autoCapitalize="none"
        autoCorrect={false}
      />
      <Text style={styles.hint}>
        Enter the URL where the Memowell API is running.
      </Text>

      <TouchableOpacity style={styles.saveButton} onPress={handleSave} activeOpacity={0.7}>
        <Text style={styles.saveText}>{saved ? '✓ Saved!' : 'Save'}</Text>
      </TouchableOpacity>

      <View style={styles.aboutSection}>
        <Text style={styles.aboutTitle}>About Memowell</Text>
        <Text style={styles.aboutText}>
          Multi-Agent Alzheimer's Companion{'\n'}
          Reminiscence therapy powered by dual AI agents{'\n\n'}
          TherapyAgent — compassionate conversation{'\n'}
          MonitorAgent — real-time cognitive monitoring
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, paddingTop: 16 },
  header: { fontSize: 28, fontWeight: '700', color: colors.text, marginBottom: 32 },
  label: { fontSize: 17, fontWeight: '600', color: colors.text, marginBottom: 8 },
  input: {
    backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
    borderRadius: 12, paddingHorizontal: 16, paddingVertical: 14, fontSize: 17, color: colors.text,
  },
  hint: { fontSize: 13, color: colors.textLight, marginTop: 8, lineHeight: 20 },
  saveButton: {
    backgroundColor: colors.primary, paddingVertical: 16, borderRadius: 12,
    alignItems: 'center', marginTop: 24,
  },
  saveText: { color: '#FFF', fontSize: 18, fontWeight: '700' },
  aboutSection: { marginTop: 48, padding: 20, backgroundColor: colors.card, borderRadius: 16 },
  aboutTitle: { fontSize: 18, fontWeight: '700', color: colors.primary, marginBottom: 8 },
  aboutText: { fontSize: 15, lineHeight: 24, color: colors.textSecondary },
});

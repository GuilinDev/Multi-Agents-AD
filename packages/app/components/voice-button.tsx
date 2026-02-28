import React from 'react';
import { TouchableOpacity, Text, StyleSheet, Platform } from 'react-native';
import { colors } from '../theme/colors';

interface Props {
  onRecordingComplete: (uri: string) => void;
  disabled?: boolean;
}

/**
 * VoiceButton — placeholder for cross-platform voice recording.
 * On native, integrate expo-av Recording.
 * On web, integrate MediaRecorder API.
 * This stub renders the UI; platform-specific logic injected via props or context.
 */
export function VoiceButton({ onRecordingComplete, disabled }: Props) {
  const handlePress = () => {
    if (Platform.OS === 'web') {
      // Web: use MediaRecorder API (implement in apps/next)
      console.warn('Voice recording not yet implemented for web');
    }
    // Native recording handled at the app level (apps/expo)
  };

  return (
    <TouchableOpacity
      style={styles.button}
      onPress={handlePress}
      disabled={disabled}
      activeOpacity={0.7}
    >
      <Text style={styles.icon}>🎤</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
  },
  icon: { fontSize: 24 },
});

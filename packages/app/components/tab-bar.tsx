import React from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { useRouter } from 'solito/router';
import { colors } from '../theme/colors';

const TABS = [
  { key: 'home', label: 'Home', icon: '🏠', path: '/' },
  { key: 'simulation', label: 'Simulation', icon: '🔬', path: '/simulation' },
  { key: 'dashboard', label: 'Dashboard', icon: '📊', path: '/dashboard' },
  { key: 'handoff', label: 'Handoff', icon: '📋', path: '/handoff' },
  { key: 'settings', label: 'Settings', icon: '⚙️', path: '/settings' },
];

interface Props {
  currentPath?: string;
}

export function TabBar({ currentPath = '/' }: Props) {
  const router = useRouter();
  return (
    <View style={styles.container}>
      {TABS.map((tab) => {
        const isActive = currentPath === tab.path;
        return (
          <TouchableOpacity
            key={tab.key}
            style={styles.tab}
            onPress={() => router.push(tab.path)}
            activeOpacity={0.7}
          >
            <Text style={styles.icon}>{tab.icon}</Text>
            <Text style={[styles.label, isActive && styles.labelActive]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    height: 60,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    alignItems: 'center',
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 6,
  },
  icon: {
    fontSize: 20,
  },
  label: {
    fontSize: 11,
    color: colors.textSecondary,
    marginTop: 2,
  },
  labelActive: {
    color: colors.primary,
    fontWeight: '600',
  },
});

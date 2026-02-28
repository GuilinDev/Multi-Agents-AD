import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import type { TrendEntry } from '../types';

interface Props {
  trends: TrendEntry[];
}

/**
 * TrendChart — cross-platform trend visualization.
 * Uses a simple bar-based display that works on both web and native.
 * For richer charts, apps can override with platform-specific libraries.
 */
export function TrendChart({ trends }: Props) {
  if (trends.length < 2) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>Not enough data for trends yet.</Text>
      </View>
    );
  }

  const recent = trends.slice(-10);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Cognitive Trends</Text>
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: colors.happy }]} />
          <Text style={styles.legendLabel}>Emotion</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: colors.calm }]} />
          <Text style={styles.legendLabel}>Memory</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: colors.nostalgic }]} />
          <Text style={styles.legendLabel}>Engagement</Text>
        </View>
      </View>
      {recent.map((entry, i) => (
        <View key={i} style={styles.row}>
          <Text style={styles.rowLabel}>{i + 1}</Text>
          <View style={styles.bars}>
            <View style={[styles.bar, { width: `${entry.scores.emotion * 10}%`, backgroundColor: colors.happy }]} />
            <View style={[styles.bar, { width: `${entry.scores.memory_quality * 10}%`, backgroundColor: colors.calm }]} />
            <View style={[styles.bar, { width: `${entry.scores.engagement * 10}%`, backgroundColor: colors.nostalgic }]} />
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginVertical: 12 },
  title: { fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 8 },
  legend: { flexDirection: 'row', marginBottom: 12, gap: 16 },
  legendItem: { flexDirection: 'row', alignItems: 'center' },
  legendDot: { width: 10, height: 10, borderRadius: 5, marginRight: 4 },
  legendLabel: { fontSize: 13, color: colors.textSecondary },
  row: { flexDirection: 'row', alignItems: 'center', marginBottom: 6 },
  rowLabel: { width: 24, fontSize: 12, color: colors.textLight, textAlign: 'center' },
  bars: { flex: 1, gap: 2 },
  bar: { height: 6, borderRadius: 3 },
  empty: { padding: 40, alignItems: 'center' },
  emptyText: { fontSize: 16, color: colors.textLight },
});

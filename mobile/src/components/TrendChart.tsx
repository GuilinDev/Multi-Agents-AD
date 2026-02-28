import React from 'react';
import { View, Text, Dimensions, StyleSheet } from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { colors } from '../theme/colors';
import { TrendEntry } from '../types';

interface Props {
  trends: TrendEntry[];
}

export default function TrendChart({ trends }: Props) {
  if (trends.length < 2) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>Not enough data for trends yet.</Text>
      </View>
    );
  }

  const recent = trends.slice(-30);
  const labels = recent.map((_, i) => (i % 5 === 0 ? `${i}` : ''));
  const emotionData = recent.map((t) => t.scores.emotion);
  const memoryData = recent.map((t) => t.scores.memory_quality);
  const engagementData = recent.map((t) => t.scores.engagement);

  const screenWidth = Dimensions.get('window').width - 40;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Cognitive Trends</Text>
      <LineChart
        data={{
          labels,
          datasets: [
            { data: emotionData, color: () => colors.happy, strokeWidth: 2 },
            { data: memoryData, color: () => colors.calm, strokeWidth: 2 },
            { data: engagementData, color: () => colors.nostalgic, strokeWidth: 2 },
          ],
          legend: ['Emotion', 'Memory', 'Engagement'],
        }}
        width={screenWidth}
        height={220}
        chartConfig={{
          backgroundColor: colors.surface,
          backgroundGradientFrom: colors.surface,
          backgroundGradientTo: colors.card,
          decimalCount: 0,
          color: (opacity = 1) => `rgba(107, 127, 215, ${opacity})`,
          labelColor: () => colors.textSecondary,
          propsForDots: { r: '3', strokeWidth: '1', stroke: colors.primary },
        }}
        bezier
        style={styles.chart}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 12,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 8,
  },
  chart: {
    borderRadius: 12,
  },
  empty: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: colors.textLight,
  },
});

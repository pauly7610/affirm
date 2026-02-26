import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface ConfidenceMeterProps {
  level: 'high' | 'med' | 'low';
  compact?: boolean;
}

const LEVELS = {
  high: { label: 'High', color: '#34C77B', bg: '#E6F9EF', bars: 3 },
  med: { label: 'Medium', color: '#E5A83B', bg: '#FFF6E5', bars: 2 },
  low: { label: 'Low', color: '#D97706', bg: '#FFF6E5', bars: 1 },
};

export function ConfidenceMeter({ level, compact }: ConfidenceMeterProps) {
  const config = LEVELS[level];

  return (
    <View style={styles.container}>
      <View style={styles.bars}>
        {[1, 2, 3].map(i => (
          <View
            key={i}
            style={[
              styles.bar,
              {
                backgroundColor: i <= config.bars ? config.color : '#E5E7EB',
                height: 8 + i * 3,
              },
            ]}
          />
        ))}
      </View>
      {!compact && (
        <Text style={[styles.label, { color: config.color }]}>{config.label}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 6,
  },
  bars: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 2,
  },
  bar: {
    width: 4,
    borderRadius: 2,
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
  },
});

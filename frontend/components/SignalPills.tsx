import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

interface Signal {
  icon: string;
  text: string;
  color: 'mint' | 'blue' | 'amber';
}

const COLOR_MAP = {
  mint: { bg: '#E6F9EF', text: '#1B8A4A', glow: '#34C77B' },
  blue: { bg: '#E8EEFF', text: '#2B4FC7', glow: '#3B6BF5' },
  amber: { bg: '#FFF6E5', text: '#A16B07', glow: '#E5A83B' },
};

interface SignalPillsProps {
  signals: Signal[];
}

export function SignalPills({ signals }: SignalPillsProps) {
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}
    >
      {signals.map((signal, i) => {
        const colors = COLOR_MAP[signal.color];
        return (
          <View key={i} style={[styles.pill, { backgroundColor: colors.bg }]}>
            <Text style={styles.icon}>{signal.icon}</Text>
            <Text style={[styles.text, { color: colors.text }]}>{signal.text}</Text>
          </View>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingBottom: 12,
    gap: 8,
  },
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 6,
  },
  icon: {
    fontSize: 14,
  },
  text: {
    fontSize: 13,
    fontWeight: '500',
  },
});

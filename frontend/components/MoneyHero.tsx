import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Surface } from './Surface';

interface MoneyHeroProps {
  greeting: string;
  amount: number;
  label: string;
  microcopy: string;
}

export function MoneyHero({ greeting, amount, label, microcopy }: MoneyHeroProps) {
  return (
    <Surface>
      <Text style={styles.greeting}>{greeting}</Text>
      <Text style={styles.amount}>
        ${amount.toLocaleString('en-US', { minimumFractionDigits: 0 })}
      </Text>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.microcopy}>{microcopy}</Text>
    </Surface>
  );
}

const styles = StyleSheet.create({
  greeting: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 4,
  },
  amount: {
    fontSize: 48,
    fontWeight: '700',
    color: '#1A1D23',
    letterSpacing: -1,
    fontVariant: ['tabular-nums'],
  },
  label: {
    fontSize: 15,
    color: '#6B7280',
    marginTop: 2,
  },
  microcopy: {
    fontSize: 13,
    color: '#9CA3AF',
    marginTop: 8,
  },
});

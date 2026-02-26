import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { DecisionItem } from '../types';
import { ConfidenceMeter } from './ConfidenceMeter';

interface DecisionCardProps {
  item: DecisionItem;
  isRecommended?: boolean;
  onPress?: () => void;
  onReview?: () => void;
}

export function DecisionCard({ item, isRecommended, onPress, onReview }: DecisionCardProps) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        styles.card,
        isRecommended && styles.recommended,
        pressed && styles.pressed,
      ]}
    >
      {isRecommended && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>Recommended</Text>
        </View>
      )}

      <View style={styles.header}>
        <View style={styles.merchantIcon}>
          <Text style={styles.merchantInitial}>
            {item.merchantName.charAt(0)}
          </Text>
        </View>
        <View style={styles.headerText}>
          <Text style={styles.merchantName}>{item.merchantName}</Text>
          <Text style={styles.productName} numberOfLines={1}>{item.productName}</Text>
        </View>
      </View>

      <View style={styles.priceRow}>
        <View>
          <Text style={styles.monthlyPayment}>
            ${item.monthlyPayment.toFixed(0)}
          </Text>
          <Text style={styles.monthlyLabel}>/mo</Text>
        </View>
        <View style={styles.priceDetails}>
          <Text style={styles.detailText}>
            {item.apr === 0 ? '0% APR' : `${item.apr}% APR`}
          </Text>
          <Text style={styles.detailText}>
            ${item.totalPrice.toLocaleString()} total
          </Text>
          <Text style={styles.detailText}>
            {item.termMonths} months
          </Text>
        </View>
      </View>

      <View style={styles.footer}>
        <View style={styles.confidenceRow}>
          <ConfidenceMeter level={item.eligibilityConfidence} />
          <Text style={styles.reason} numberOfLines={2}>{item.reason}</Text>
        </View>
      </View>

      <Pressable style={styles.cta} onPress={onReview}>
        <Text style={styles.ctaText}>Review plan</Text>
      </Pressable>

      <Text style={styles.disclosure}>{item.disclosure}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 20,
    marginHorizontal: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 3,
  },
  recommended: {
    borderWidth: 1.5,
    borderColor: '#3B6BF5',
    shadowOpacity: 0.1,
    shadowRadius: 16,
  },
  pressed: {
    transform: [{ scale: 0.98 }],
    shadowOpacity: 0.1,
  },
  badge: {
    alignSelf: 'flex-start',
    backgroundColor: '#E8EEFF',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 12,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#3B6BF5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 16,
  },
  merchantIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  merchantInitial: {
    fontSize: 18,
    fontWeight: '700',
    color: '#6B7280',
  },
  headerText: {
    flex: 1,
  },
  merchantName: {
    fontSize: 13,
    color: '#6B7280',
    fontWeight: '500',
  },
  productName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1D23',
    marginTop: 1,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: 14,
  },
  monthlyPayment: {
    fontSize: 36,
    fontWeight: '700',
    color: '#1A1D23',
    fontVariant: ['tabular-nums'],
    lineHeight: 40,
  },
  monthlyLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: -2,
  },
  priceDetails: {
    alignItems: 'flex-end',
    gap: 2,
  },
  detailText: {
    fontSize: 13,
    color: '#6B7280',
    fontVariant: ['tabular-nums'],
  },
  footer: {
    marginBottom: 14,
  },
  confidenceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  reason: {
    flex: 1,
    fontSize: 12,
    color: '#9CA3AF',
    lineHeight: 16,
  },
  cta: {
    backgroundColor: '#3B6BF5',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 8,
  },
  ctaText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  disclosure: {
    fontSize: 11,
    color: '#9CA3AF',
    textAlign: 'center',
  },
});

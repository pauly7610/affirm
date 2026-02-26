import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { DecisionItem } from '../types';
import { ConfidenceMeter } from './ConfidenceMeter';
import { colors, radii, shadows } from '../lib/theme';

interface DecisionCardProps {
  item: DecisionItem;
  isRecommended?: boolean;
  whyRecommended?: string;
  onPress?: () => void;
  onReview?: () => void;
}

export function DecisionCard({ item, isRecommended, whyRecommended, onPress, onReview }: DecisionCardProps) {
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
          <View style={styles.badgeDot} />
          <Text style={styles.badgeText}>Recommended</Text>
        </View>
      )}

      <View style={styles.header}>
        <View style={[styles.merchantIcon, isRecommended && styles.merchantIconTinted]}>
          <Text style={[styles.merchantInitial, isRecommended && styles.merchantInitialTinted]}>
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

      {item.safetySignals && item.safetySignals.length > 0 && (
        <View style={styles.safetyBlock}>
          {item.safetySignals.slice(0, 2).map((signal, i) => {
            const isDeterministic = signal.startsWith('0% APR');
            return (
              <View key={i} style={styles.safetyRow}>
                <Text style={isDeterministic ? styles.safetyCheckGreen : styles.safetyDot}>
                  {isDeterministic ? '\u2713' : '\u00B7'}
                </Text>
                <Text style={styles.safetyText}>{signal}</Text>
              </View>
            );
          })}
        </View>
      )}

      {isRecommended && whyRecommended ? (
        <Text style={styles.whyRecommended} numberOfLines={1}>{whyRecommended}</Text>
      ) : null}

      <Pressable
        style={[styles.cta, !isRecommended && styles.ctaOutline]}
        onPress={onReview}
      >
        <Text style={[styles.ctaText, !isRecommended && styles.ctaTextOutline]}>Review plan</Text>
      </Pressable>

      <Text style={styles.disclosure}>{item.disclosure}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radii.card,
    padding: 20,
    marginHorizontal: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.soft,
  },
  recommended: {
    borderWidth: 1,
    borderColor: colors.primary,
    ...shadows.soft,
  },
  pressed: {
    transform: [{ scale: 0.98 }],
  },
  badge: {
    alignSelf: 'flex-start',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.bgMuted,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radii.badge,
    marginBottom: 12,
    gap: 6,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  badgeDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.primary,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '500',
    color: colors.textSecondary,
    letterSpacing: 0.2,
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
    borderRadius: radii.merchantIcon,
    backgroundColor: colors.merchantBg,
    justifyContent: 'center',
    alignItems: 'center',
  },
  merchantIconTinted: {
    backgroundColor: colors.primaryLight,
  },
  merchantInitial: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.textSecondary,
  },
  merchantInitialTinted: {
    color: colors.primary,
  },
  headerText: {
    flex: 1,
  },
  merchantName: {
    fontSize: 13,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  productName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
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
    color: colors.textPrimary,
    fontVariant: ['tabular-nums'],
    lineHeight: 40,
  },
  monthlyLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: -2,
  },
  priceDetails: {
    alignItems: 'flex-end',
    gap: 2,
  },
  detailText: {
    fontSize: 13,
    color: colors.textMeta,
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
    color: colors.textSecondary,
    lineHeight: 16,
  },
  whyRecommended: {
    fontSize: 12,
    color: colors.textSecondary,
    lineHeight: 17,
    marginBottom: 12,
    fontStyle: 'italic',
  },
  cta: {
    backgroundColor: colors.primary,
    borderRadius: radii.cta,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 8,
  },
  ctaOutline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.borderOutline,
  },
  ctaText: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.surface,
  },
  ctaTextOutline: {
    color: colors.textSecondary,
  },
  safetyBlock: {
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: 10,
    marginBottom: 14,
    gap: 5,
  },
  safetyRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  safetyCheckGreen: {
    fontSize: 13,
    color: colors.safeGreen,
    fontWeight: '700',
    width: 14,
    textAlign: 'center',
  },
  safetyDot: {
    fontSize: 18,
    color: colors.textTertiary,
    fontWeight: '400',
    width: 14,
    textAlign: 'center',
    lineHeight: 18,
  },
  safetyText: {
    fontSize: 12,
    color: colors.textMeta,
    lineHeight: 16,
  },
  disclosure: {
    fontSize: 11,
    color: colors.textTertiary,
    textAlign: 'center',
  },
});

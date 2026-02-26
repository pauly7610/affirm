import React from 'react';
import { View, Text, StyleSheet, Pressable, Modal, ScrollView } from 'react-native';
import { DecisionItem } from '../types';
import { ConfidenceMeter } from './ConfidenceMeter';

interface PlanModalProps {
  item: DecisionItem | null;
  visible: boolean;
  onClose: () => void;
}

export function PlanModal({ item, visible, onClose }: PlanModalProps) {
  if (!item) return null;

  return (
    <Modal visible={visible} animationType="slide" transparent presentationStyle="overFullScreen">
      <View style={styles.overlay}>
        <View style={styles.sheet}>
          <View style={styles.handle} />
          <ScrollView showsVerticalScrollIndicator={false}>
            <View style={styles.merchantRow}>
              <View style={styles.merchantIcon}>
                <Text style={styles.merchantInitial}>{item.merchantName.charAt(0)}</Text>
              </View>
              <View>
                <Text style={styles.merchantName}>{item.merchantName}</Text>
                <Text style={styles.productName}>{item.productName}</Text>
              </View>
            </View>

            <View style={styles.heroRow}>
              <View>
                <Text style={styles.monthlyAmount}>${item.monthlyPayment.toFixed(0)}</Text>
                <Text style={styles.monthlyLabel}>per month</Text>
              </View>
              <ConfidenceMeter level={item.eligibilityConfidence} />
            </View>

            <View style={styles.detailsGrid}>
              <DetailBox label="Total price" value={`$${item.totalPrice.toLocaleString()}`} />
              <DetailBox label="APR" value={item.apr === 0 ? '0%' : `${item.apr}%`} />
              <DetailBox label="Term" value={`${item.termMonths} mo`} />
              <DetailBox label="Category" value={item.category} />
            </View>

            <View style={styles.reasonBox}>
              <Text style={styles.reasonLabel}>Why you're seeing this</Text>
              <Text style={styles.reasonText}>{item.reason}</Text>
            </View>

            <Pressable style={styles.ctaPrimary} onPress={onClose}>
              <Text style={styles.ctaPrimaryText}>Continue</Text>
            </Pressable>

            <Text style={styles.disclaimer}>
              {item.disclosure} Rates and terms are estimates. Actual terms will be presented at checkout based on your full application.
            </Text>

            <Pressable style={styles.ctaSecondary} onPress={onClose}>
              <Text style={styles.ctaSecondaryText}>Close</Text>
            </Pressable>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

function DetailBox({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.detailBox}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={styles.detailValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 40,
    maxHeight: '85%',
  },
  handle: {
    width: 36,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#D1D5DB',
    alignSelf: 'center',
    marginBottom: 20,
  },
  merchantRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    marginBottom: 24,
  },
  merchantIcon: {
    width: 48,
    height: 48,
    borderRadius: 14,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  merchantInitial: {
    fontSize: 20,
    fontWeight: '700',
    color: '#6B7280',
  },
  merchantName: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  productName: {
    fontSize: 17,
    fontWeight: '600',
    color: '#1A1D23',
    marginTop: 2,
  },
  heroRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: 24,
  },
  monthlyAmount: {
    fontSize: 48,
    fontWeight: '700',
    color: '#1A1D23',
    fontVariant: ['tabular-nums'],
    lineHeight: 52,
  },
  monthlyLabel: {
    fontSize: 15,
    color: '#6B7280',
  },
  detailsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 20,
  },
  detailBox: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#F8FAFB',
    borderRadius: 12,
    padding: 14,
  },
  detailLabel: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1D23',
    fontVariant: ['tabular-nums'],
  },
  reasonBox: {
    backgroundColor: '#F8FAFB',
    borderRadius: 12,
    padding: 14,
    marginBottom: 24,
  },
  reasonLabel: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 4,
  },
  reasonText: {
    fontSize: 14,
    color: '#1A1D23',
    lineHeight: 20,
  },
  ctaPrimary: {
    backgroundColor: '#3B6BF5',
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  ctaPrimaryText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  disclaimer: {
    fontSize: 11,
    color: '#9CA3AF',
    textAlign: 'center',
    lineHeight: 16,
    marginBottom: 12,
  },
  ctaSecondary: {
    paddingVertical: 12,
    alignItems: 'center',
  },
  ctaSecondaryText: {
    fontSize: 15,
    fontWeight: '500',
    color: '#6B7280',
  },
});

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable, Switch } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Surface } from '../../components/Surface';
import { Sparkline } from '../../components/Sparkline';
import { ConfidenceMeter } from '../../components/ConfidenceMeter';
import { PlanModal } from '../../components/PlanModal';
import { Skeleton } from '../../components/Skeleton';
import { getProfileSummary } from '../../lib/api';
import { ProfileSummary, ActivePlan, DecisionItem } from '../../types';

export default function ProfileScreen() {
  const [profile, setProfile] = useState<ProfileSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedAccordion, setExpandedAccordion] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<ActivePlan | null>(null);
  const [toggles, setToggles] = useState({
    personalizedOffers: true,
    dataSharing: false,
    notifications: true,
  });

  useEffect(() => {
    getProfileSummary()
      .then(setProfile)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const planToDecisionItem = (plan: ActivePlan): DecisionItem => ({
    id: plan.id,
    merchantName: plan.merchantName,
    productName: plan.productName,
    category: '',
    imageUrl: null,
    totalPrice: plan.totalAmount,
    termMonths: plan.termMonths,
    apr: plan.apr,
    monthlyPayment: plan.monthlyPayment,
    eligibilityConfidence: 'high',
    reason: `${((plan.totalPaid / plan.totalAmount) * 100).toFixed(0)}% paid. On track.`,
    disclosure: 'Plan details reflect current balance.',
  });

  if (loading) {
    return (
      <LinearGradient colors={['#F0F4F8', '#F8FAFB', '#FFFFFF']} style={styles.gradient}>
        <SafeAreaView style={styles.safe} edges={['top']}>
          <View style={{ padding: 20, gap: 16 }}>
            <Skeleton height={120} borderRadius={20} />
            <Skeleton height={80} borderRadius={20} />
            <Skeleton height={160} borderRadius={20} />
          </View>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  if (!profile) return null;
  const { user, eligibility, plans, insights } = profile;

  return (
    <LinearGradient colors={['#F0F4F8', '#F8FAFB', '#FFFFFF']} style={styles.gradient}>
      <SafeAreaView style={styles.safe} edges={['top']}>
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>
          {/* Profile Header */}
          <Surface>
            <View style={styles.profileHeader}>
              <View style={styles.avatar}>
                <Text style={styles.avatarText}>PC</Text>
              </View>
              <View style={styles.profileInfo}>
                <Text style={styles.profileName}>{user.name}</Text>
                <View style={styles.healthRow}>
                  <Text style={styles.healthLabel}>Account health:</Text>
                  <Text style={styles.healthValue}>
                    {user.accountHealth === 'strong' ? 'Strong' : user.accountHealth}
                  </Text>
                  <ConfidenceMeter level="high" compact />
                </View>
              </View>
            </View>
            <View style={styles.statsRow}>
              <StatBox label="Spending power" value={`$${user.spendingPower.toLocaleString()}`} />
              <StatBox label="Active plans" value={String(user.activePlansCount)} />
              <StatBox label="On-time payments" value={user.paymentStatus === 'excellent' ? 'Excellent' : user.paymentStatus} />
            </View>
          </Surface>

          {/* Spending Power */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Spending Power</Text>
          </View>
          <Surface>
            <Text style={styles.eligibilityAmount}>
              ${eligibility.spendingPower.toLocaleString()}
            </Text>
            <Text style={styles.eligibilityLabel}>Estimated eligibility</Text>
            <Text style={styles.eligibilityExplain}>{eligibility.explanation}</Text>
          </Surface>

          {/* Active Plans */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Active Plans</Text>
          </View>
          {plans.map((plan) => (
            <Surface key={plan.id}>
              <View style={styles.planHeader}>
                <View style={styles.planIcon}>
                  <Text style={styles.planInitial}>{plan.merchantName.charAt(0)}</Text>
                </View>
                <View style={styles.planInfo}>
                  <Text style={styles.planMerchant}>{plan.merchantName}</Text>
                  <Text style={styles.planProduct}>{plan.productName}</Text>
                </View>
              </View>
              <View style={styles.planDetails}>
                <View style={styles.planDetailItem}>
                  <Text style={styles.planDetailLabel}>Remaining</Text>
                  <Text style={styles.planDetailValue}>${plan.remainingBalance.toFixed(0)}</Text>
                </View>
                <View style={styles.planDetailItem}>
                  <Text style={styles.planDetailLabel}>Next payment</Text>
                  <Text style={styles.planDetailValue}>{plan.nextPaymentDate}</Text>
                </View>
                <View style={styles.planDetailItem}>
                  <Text style={styles.planDetailLabel}>Monthly</Text>
                  <Text style={styles.planDetailValue}>${plan.monthlyPayment.toFixed(0)}</Text>
                </View>
              </View>
              {/* Progress bar */}
              <View style={styles.progressTrack}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${(plan.totalPaid / plan.totalAmount) * 100}%` },
                  ]}
                />
              </View>
              <Text style={styles.progressLabel}>
                {((plan.totalPaid / plan.totalAmount) * 100).toFixed(0)}% paid
              </Text>
              <Pressable
                style={styles.viewDetailsBtn}
                onPress={() => setSelectedPlan(plan)}
              >
                <Text style={styles.viewDetailsBtnText}>View details</Text>
              </Pressable>
            </Surface>
          ))}

          {/* Financial Insights */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Financial Insights</Text>
          </View>
          {insights.map((insight) => (
            <Surface key={insight.id}>
              <View style={styles.insightRow}>
                <View style={styles.insightContent}>
                  <Text style={styles.insightIcon}>
                    {insight.type === 'saving' ? '💡' : insight.type === 'behavior' ? '✅' : '📊'}
                  </Text>
                  <Text style={styles.insightText}>{insight.text}</Text>
                </View>
                {insight.sparklineData && (
                  <Sparkline
                    data={insight.sparklineData}
                    width={70}
                    height={24}
                    color={insight.type === 'saving' ? '#34C77B' : '#3B6BF5'}
                  />
                )}
              </View>
            </Surface>
          ))}

          {/* Privacy & Control */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Privacy & Control</Text>
          </View>
          <Surface>
            <Pressable
              style={styles.accordionHeader}
              onPress={() => setExpandedAccordion(!expandedAccordion)}
            >
              <Text style={styles.accordionTitle}>How recommendations work</Text>
              <Text style={styles.accordionArrow}>{expandedAccordion ? '▲' : '▼'}</Text>
            </Pressable>
            {expandedAccordion && (
              <View style={styles.accordionBody}>
                <Text style={styles.accordionText}>
                  {'\u2022'} We analyze your payment history and spending patterns{'\n'}
                  {'\u2022'} Offers are ranked by affordability, APR, and eligibility{'\n'}
                  {'\u2022'} We never share your data with merchants without consent{'\n'}
                  {'\u2022'} Checking eligibility does not affect your credit score
                </Text>
              </View>
            )}
          </Surface>
          <Surface>
            <ToggleRow
              label="Personalized offers"
              sublabel="See offers tailored to your profile"
              value={toggles.personalizedOffers}
              onToggle={(v) => setToggles((p) => ({ ...p, personalizedOffers: v }))}
            />
            <View style={styles.divider} />
            <ToggleRow
              label="Data sharing"
              sublabel="Share anonymized data to improve recommendations"
              value={toggles.dataSharing}
              onToggle={(v) => setToggles((p) => ({ ...p, dataSharing: v }))}
            />
            <View style={styles.divider} />
            <ToggleRow
              label="Notifications"
              sublabel="Payment reminders and eligibility updates"
              value={toggles.notifications}
              onToggle={(v) => setToggles((p) => ({ ...p, notifications: v }))}
            />
          </Surface>
          <Text style={styles.privacyNote}>
            Your data is encrypted and stored securely. You can request deletion at any time.
          </Text>

          <View style={{ height: 32 }} />
        </ScrollView>
      </SafeAreaView>

      {selectedPlan && (
        <PlanModal
          item={planToDecisionItem(selectedPlan)}
          visible={!!selectedPlan}
          onClose={() => setSelectedPlan(null)}
        />
      )}
    </LinearGradient>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.statBox}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function ToggleRow({
  label,
  sublabel,
  value,
  onToggle,
}: {
  label: string;
  sublabel: string;
  value: boolean;
  onToggle: (v: boolean) => void;
}) {
  return (
    <View style={styles.toggleRow}>
      <View style={styles.toggleInfo}>
        <Text style={styles.toggleLabel}>{label}</Text>
        <Text style={styles.toggleSublabel}>{sublabel}</Text>
      </View>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: '#D1D5DB', true: '#93B4FD' }}
        thumbColor={value ? '#3B6BF5' : '#F3F4F6'}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  safe: { flex: 1 },
  scroll: { paddingTop: 8, paddingBottom: 20 },
  section: { paddingHorizontal: 20, marginTop: 20, marginBottom: 10 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#1A1D23' },
  profileHeader: { flexDirection: 'row', alignItems: 'center', gap: 16, marginBottom: 20 },
  avatar: {
    width: 56, height: 56, borderRadius: 28, backgroundColor: '#E8EEFF',
    justifyContent: 'center', alignItems: 'center',
  },
  avatarText: { fontSize: 20, fontWeight: '700', color: '#3B6BF5' },
  profileInfo: { flex: 1 },
  profileName: { fontSize: 20, fontWeight: '700', color: '#1A1D23' },
  healthRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 4 },
  healthLabel: { fontSize: 13, color: '#6B7280' },
  healthValue: { fontSize: 13, fontWeight: '600', color: '#34C77B' },
  statsRow: { flexDirection: 'row', gap: 10 },
  statBox: { flex: 1, backgroundColor: '#F8FAFB', borderRadius: 12, padding: 12, alignItems: 'center' },
  statValue: { fontSize: 18, fontWeight: '700', color: '#1A1D23', fontVariant: ['tabular-nums'] },
  statLabel: { fontSize: 11, color: '#9CA3AF', marginTop: 2, textAlign: 'center' },
  eligibilityAmount: { fontSize: 36, fontWeight: '700', color: '#1A1D23', fontVariant: ['tabular-nums'] },
  eligibilityLabel: { fontSize: 14, color: '#6B7280', marginTop: 2 },
  eligibilityExplain: { fontSize: 13, color: '#9CA3AF', marginTop: 8, lineHeight: 18 },
  planHeader: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 14 },
  planIcon: { width: 40, height: 40, borderRadius: 10, backgroundColor: '#F3F4F6', justifyContent: 'center', alignItems: 'center' },
  planInitial: { fontSize: 16, fontWeight: '700', color: '#6B7280' },
  planInfo: { flex: 1 },
  planMerchant: { fontSize: 13, color: '#6B7280', fontWeight: '500' },
  planProduct: { fontSize: 15, fontWeight: '600', color: '#1A1D23' },
  planDetails: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  planDetailItem: { flex: 1, backgroundColor: '#F8FAFB', borderRadius: 8, padding: 10 },
  planDetailLabel: { fontSize: 11, color: '#9CA3AF' },
  planDetailValue: { fontSize: 14, fontWeight: '600', color: '#1A1D23', fontVariant: ['tabular-nums'], marginTop: 2 },
  progressTrack: { height: 6, backgroundColor: '#F3F4F6', borderRadius: 3, overflow: 'hidden', marginBottom: 6 },
  progressFill: { height: '100%', backgroundColor: '#34C77B', borderRadius: 3 },
  progressLabel: { fontSize: 12, color: '#6B7280', marginBottom: 10 },
  viewDetailsBtn: { alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, backgroundColor: '#E8EEFF', borderRadius: 8 },
  viewDetailsBtnText: { fontSize: 13, fontWeight: '600', color: '#3B6BF5' },
  insightRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  insightContent: { flex: 1, flexDirection: 'row', alignItems: 'flex-start', gap: 10, marginRight: 12 },
  insightIcon: { fontSize: 18 },
  insightText: { flex: 1, fontSize: 14, color: '#1A1D23', lineHeight: 20 },
  accordionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  accordionTitle: { fontSize: 15, fontWeight: '600', color: '#1A1D23' },
  accordionArrow: { fontSize: 12, color: '#9CA3AF' },
  accordionBody: { marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: '#F3F4F6' },
  accordionText: { fontSize: 13, color: '#6B7280', lineHeight: 22 },
  toggleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 10 },
  toggleInfo: { flex: 1, marginRight: 16 },
  toggleLabel: { fontSize: 15, fontWeight: '500', color: '#1A1D23' },
  toggleSublabel: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  divider: { height: 1, backgroundColor: '#F3F4F6' },
  privacyNote: { fontSize: 12, color: '#9CA3AF', textAlign: 'center', paddingHorizontal: 32, marginTop: 12 },
});

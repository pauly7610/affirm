import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable, RefreshControl } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { MoneyHero } from '../../components/MoneyHero';
import { SignalPills } from '../../components/SignalPills';
import { DecisionCard } from '../../components/DecisionCard';
import { PlanModal } from '../../components/PlanModal';
import { Surface } from '../../components/Surface';
import { DecisionCardSkeleton } from '../../components/Skeleton';
import { searchQuery } from '../../lib/api';
import { DecisionItem } from '../../types';
import { useSearch } from '../../context/SearchContext';

const SIGNALS = [
  { icon: '📉', text: 'Spending lower this month', color: 'mint' as const },
  { icon: '✨', text: 'Eligible for 0% APR offers', color: 'blue' as const },
  { icon: '🛡️', text: 'Credit impact: none', color: 'amber' as const },
];

const EXPLORE_CHIPS = [
  { label: '💻 Electronics', query: 'electronics' },
  { label: '✈️ Travel', query: 'travel vacation' },
  { label: '👟 Sneakers', query: 'sneakers shoes' },
  { label: '🏠 Home upgrades', query: 'home furniture' },
  { label: '💰 Stay under $50/mo', query: 'stay under $50/mo' },
];

export default function HomeScreen() {
  const router = useRouter();
  const { runSearch, setQuery } = useSearch();
  const [opportunities, setOpportunities] = useState<DecisionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<DecisionItem | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchOpportunities = useCallback(async () => {
    try {
      const res = await searchQuery({ query: 'for you' });
      setOpportunities(res.results.slice(0, 4));
    } catch {
      setOpportunities([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchOpportunities();
  }, [fetchOpportunities]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchOpportunities();
  };

  const handleExploreChip = (query: string) => {
    setQuery(query);
    runSearch(query);
    router.push('/(tabs)/search');
  };

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning, Paul';
    if (h < 17) return 'Good afternoon, Paul';
    return 'Good evening, Paul';
  };

  return (
    <LinearGradient colors={['#F0F4F8', '#F8FAFB', '#FFFFFF']} style={styles.gradient}>
      <SafeAreaView style={styles.safe} edges={['top']}>
        <ScrollView
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scroll}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#3B6BF5" />}
        >
          {/* Money Hero */}
          <MoneyHero
            greeting={greeting()}
            amount={1200}
            label="Available to spend"
            microcopy="Checking won't affect your credit score."
          />

          {/* Signal Pills */}
          <SignalPills signals={SIGNALS} />

          {/* Opportunities */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Opportunities</Text>
          </View>
          {loading ? (
            <>
              <DecisionCardSkeleton />
              <DecisionCardSkeleton />
              <DecisionCardSkeleton />
            </>
          ) : (
            opportunities.map((item, i) => (
              <DecisionCard
                key={item.id}
                item={item}
                isRecommended={i === 0}
                onPress={() => setSelectedItem(item)}
                onReview={() => setSelectedItem(item)}
              />
            ))
          )}

          {/* Explore Chips */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Explore</Text>
          </View>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.chipsRow}
          >
            {EXPLORE_CHIPS.map((chip) => (
              <Pressable
                key={chip.query}
                style={({ pressed }) => [styles.chip, pressed && styles.chipPressed]}
                onPress={() => handleExploreChip(chip.query)}
              >
                <Text style={styles.chipText}>{chip.label}</Text>
              </Pressable>
            ))}
          </ScrollView>

          {/* Heads Up */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Heads up</Text>
          </View>
          <Surface>
            <View style={styles.reminderRow}>
              <Text style={styles.reminderIcon}>📅</Text>
              <View style={styles.reminderContent}>
                <Text style={styles.reminderTitle}>Next payment: $38 due in 3 days</Text>
                <Text style={styles.reminderSub}>Paying on time keeps your eligibility strong.</Text>
              </View>
            </View>
          </Surface>
          <Surface>
            <View style={styles.reminderRow}>
              <Text style={styles.reminderIcon}>🔄</Text>
              <View style={styles.reminderContent}>
                <Text style={styles.reminderTitle}>Eligibility refresh available</Text>
                <Pressable style={styles.refreshBtn}>
                  <Text style={styles.refreshBtnText}>Refresh</Text>
                </Pressable>
              </View>
            </View>
          </Surface>

          <View style={{ height: 32 }} />
        </ScrollView>
      </SafeAreaView>

      {/* Plan Modal */}
      <PlanModal
        item={selectedItem}
        visible={!!selectedItem}
        onClose={() => setSelectedItem(null)}
      />
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  safe: { flex: 1 },
  scroll: { paddingTop: 8, paddingBottom: 20 },
  section: { paddingHorizontal: 20, marginTop: 20, marginBottom: 10 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#1A1D23' },
  chipsRow: { paddingHorizontal: 16, gap: 8, paddingBottom: 8 },
  chip: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 2,
  },
  chipPressed: { transform: [{ scale: 0.96 }], backgroundColor: '#F3F4F6' },
  chipText: { fontSize: 14, fontWeight: '500', color: '#1A1D23' },
  reminderRow: { flexDirection: 'row', gap: 14, alignItems: 'flex-start' },
  reminderIcon: { fontSize: 22, marginTop: 2 },
  reminderContent: { flex: 1 },
  reminderTitle: { fontSize: 15, fontWeight: '600', color: '#1A1D23', marginBottom: 4 },
  reminderSub: { fontSize: 13, color: '#6B7280', lineHeight: 18 },
  refreshBtn: {
    alignSelf: 'flex-start',
    backgroundColor: '#E8EEFF',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 10,
    marginTop: 8,
  },
  refreshBtnText: { fontSize: 13, fontWeight: '600', color: '#3B6BF5' },
});

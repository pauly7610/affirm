import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { DecisionCard } from '../../components/DecisionCard';
import { PlanModal } from '../../components/PlanModal';
import { Surface } from '../../components/Surface';
import { Sparkline } from '../../components/Sparkline';
import { DecisionCardSkeleton } from '../../components/Skeleton';
import { useSearch } from '../../context/SearchContext';
import { DecisionItem, MonthlyImpactBar } from '../../types';

const GOAL_CHIPS = [
  { label: 'Upgrade my laptop', query: 'laptop under $800' },
  { label: 'Plan a trip', query: 'travel vacation' },
  { label: 'Only 0% APR', query: '0% APR' },
  { label: 'Stay under $50/mo', query: 'stay under $50/mo' },
  { label: 'Cheaper options', query: 'cheaper options under $500' },
];

const REFINE_CHIPS = [
  { key: 'lowest_monthly', label: 'Lower monthly' },
  { key: 'only_zero_apr', label: 'Only 0% APR' },
  { key: 'lowest_total', label: 'Cheaper total' },
  { key: 'compare_brands', label: 'Compare brands' },
  { key: 'shortest_term', label: 'Shorter term' },
];

export default function SearchScreen() {
  const { query, results, loading, error, runSearch, setQuery, activeRefines } = useSearch();
  const [inputValue, setInputValue] = useState(query);
  const [selectedItem, setSelectedItem] = useState<DecisionItem | null>(null);
  const [localRefines, setLocalRefines] = useState<Record<string, boolean>>({});

  useEffect(() => {
    setInputValue(query);
  }, [query]);

  const handleSubmit = () => {
    if (inputValue.trim()) {
      setQuery(inputValue.trim());
      runSearch(inputValue.trim(), buildRefine(localRefines));
    }
  };

  const handleChipSearch = (q: string) => {
    setInputValue(q);
    setQuery(q);
    setLocalRefines({});
    runSearch(q);
  };

  const handleRefine = (key: string) => {
    const updated = { ...localRefines, [key]: !localRefines[key] };
    setLocalRefines(updated);
    if (query) {
      runSearch(query, buildRefine(updated));
    }
  };

  const buildRefine = (refines: Record<string, boolean>) => {
    const r: Record<string, unknown> = {};
    if (refines['only_zero_apr']) r.onlyZeroApr = true;
    if (refines['lowest_monthly']) r.sort = 'lowest_monthly';
    if (refines['lowest_total']) r.sort = 'lowest_total';
    if (refines['shortest_term']) r.sort = 'shortest_term';
    return r;
  };

  const hasResults = results && results.results.length > 0;

  return (
    <LinearGradient colors={['#F0F4F8', '#F8FAFB', '#FFFFFF']} style={styles.gradient}>
      <SafeAreaView style={styles.safe} edges={['top']}>
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>
          {/* Search Input */}
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              value={inputValue}
              onChangeText={setInputValue}
              onSubmitEditing={handleSubmit}
              placeholder="Try 'laptop under $800 with 0% APR'"
              placeholderTextColor="#9CA3AF"
              returnKeyType="search"
              autoCorrect={false}
            />
          </View>

          {/* Goal Chips (shown when no results) */}
          {!hasResults && !loading && (
            <View>
              <Text style={styles.chipSectionLabel}>Popular goals</Text>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.chipsRow}
              >
                {GOAL_CHIPS.map((chip) => (
                  <Pressable
                    key={chip.query}
                    style={({ pressed }) => [styles.goalChip, pressed && styles.chipPressed]}
                    onPress={() => handleChipSearch(chip.query)}
                  >
                    <Text style={styles.goalChipText}>{chip.label}</Text>
                  </Pressable>
                ))}
              </ScrollView>
            </View>
          )}

          {/* Loading Skeletons */}
          {loading && (
            <View style={styles.skeletonWrap}>
              <Surface style={{ marginHorizontal: 0 }}>
                <View style={styles.skeletonSummary}>
                  <View style={[styles.skeletonBar, { width: '90%' }]} />
                  <View style={[styles.skeletonBar, { width: '60%', marginTop: 8 }]} />
                </View>
              </Surface>
              <DecisionCardSkeleton />
              <DecisionCardSkeleton />
              <DecisionCardSkeleton />
            </View>
          )}

          {/* Error */}
          {error && (
            <Surface>
              <Text style={styles.errorText}>{error}</Text>
            </Surface>
          )}

          {/* Results */}
          {hasResults && !loading && (
            <View>
              {/* AI Summary */}
              <Surface>
                <Text style={styles.summaryText}>{results.aiSummary}</Text>
              </Surface>

              {/* Monthly Impact Bars */}
              {results.monthlyImpact && results.monthlyImpact.length > 0 && (
                <Surface>
                  <Text style={styles.impactTitle}>Monthly impact</Text>
                  <View style={styles.barsRow}>
                    {results.monthlyImpact.map((bar: MonthlyImpactBar, i: number) => {
                      const maxVal = Math.max(...results.monthlyImpact.map((b: MonthlyImpactBar) => b.value));
                      const pct = maxVal > 0 ? (bar.value / maxVal) * 100 : 0;
                      return (
                        <View key={i} style={styles.barItem}>
                          <View style={styles.barTrack}>
                            <View
                              style={[
                                styles.barFill,
                                { height: `${Math.max(pct, 8)}%`, backgroundColor: i === 0 ? '#3B6BF5' : '#D1D5DB' },
                              ]}
                            />
                          </View>
                          <Text style={styles.barValue}>${bar.value.toFixed(0)}</Text>
                          <Text style={styles.barLabel}>{bar.label}</Text>
                        </View>
                      );
                    })}
                  </View>
                </Surface>
              )}

              {/* Refine Chips */}
              <Text style={styles.refineLabel}>Refine my plan</Text>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.chipsRow}
              >
                {REFINE_CHIPS.map((chip) => {
                  const active = localRefines[chip.key];
                  return (
                    <Pressable
                      key={chip.key}
                      style={[styles.refineChip, active && styles.refineChipActive]}
                      onPress={() => handleRefine(chip.key)}
                    >
                      <Text style={[styles.refineChipText, active && styles.refineChipTextActive]}>
                        {chip.label}
                      </Text>
                    </Pressable>
                  );
                })}
              </ScrollView>

              {/* Decision Cards */}
              {results.results.map((item: DecisionItem, i: number) => (
                <DecisionCard
                  key={item.id}
                  item={item}
                  isRecommended={i === 0}
                  onPress={() => setSelectedItem(item)}
                  onReview={() => setSelectedItem(item)}
                />
              ))}

              {/* Disclaimers */}
              <View style={styles.disclaimers}>
                {results.disclaimers.map((d: string, i: number) => (
                  <Text key={i} style={styles.disclaimerText}>{d}</Text>
                ))}
              </View>
            </View>
          )}

          <View style={{ height: 32 }} />
        </ScrollView>
      </SafeAreaView>

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
  scroll: { paddingTop: 12, paddingBottom: 20 },
  inputContainer: { paddingHorizontal: 16, marginBottom: 16 },
  input: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    paddingHorizontal: 18,
    paddingVertical: 14,
    fontSize: 16,
    color: '#1A1D23',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 3,
  },
  chipSectionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  chipsRow: { paddingHorizontal: 16, gap: 8, paddingBottom: 8 },
  goalChip: {
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
  goalChipText: { fontSize: 14, fontWeight: '500', color: '#1A1D23' },
  skeletonWrap: { paddingHorizontal: 16, gap: 12 },
  skeletonSummary: { padding: 4 },
  skeletonBar: { height: 12, borderRadius: 6, backgroundColor: '#E5E7EB' },
  errorText: { fontSize: 14, color: '#D97706', textAlign: 'center' },
  summaryText: { fontSize: 14, color: '#6B7280', lineHeight: 20 },
  impactTitle: { fontSize: 13, fontWeight: '600', color: '#6B7280', marginBottom: 12 },
  barsRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'flex-end', height: 80 },
  barItem: { alignItems: 'center', flex: 1 },
  barTrack: { width: 20, height: 60, backgroundColor: '#F3F4F6', borderRadius: 4, justifyContent: 'flex-end', overflow: 'hidden' },
  barFill: { width: '100%', borderRadius: 4 },
  barValue: { fontSize: 11, fontWeight: '600', color: '#1A1D23', marginTop: 4, fontVariant: ['tabular-nums'] },
  barLabel: { fontSize: 10, color: '#9CA3AF', marginTop: 2 },
  refineLabel: { fontSize: 14, fontWeight: '600', color: '#6B7280', paddingHorizontal: 20, marginTop: 16, marginBottom: 10 },
  refineChip: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  refineChipActive: { backgroundColor: '#3B6BF5', borderColor: '#3B6BF5' },
  refineChipText: { fontSize: 13, fontWeight: '500', color: '#6B7280' },
  refineChipTextActive: { color: '#FFFFFF' },
  disclaimers: { paddingHorizontal: 20, marginTop: 16, gap: 4 },
  disclaimerText: { fontSize: 11, color: '#9CA3AF', textAlign: 'center' },
});

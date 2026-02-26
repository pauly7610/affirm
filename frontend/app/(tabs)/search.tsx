import React, { useState, useEffect, useCallback, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, Pressable, LayoutAnimation, Platform, UIManager, Animated } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { DecisionCard } from '../../components/DecisionCard';
import { PlanModal } from '../../components/PlanModal';
import { Surface } from '../../components/Surface';
import { Sparkline } from '../../components/Sparkline';
import { DecisionCardSkeleton } from '../../components/Skeleton';
import { useSearch } from '../../context/SearchContext';
import { DecisionItem, MonthlyImpactBar, TraceStep } from '../../types';
import { colors, radii } from '../../lib/theme';
import { trackEvent } from '../../lib/analytics';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

const PORTFOLIO_MODE = process.env.EXPO_PUBLIC_PORTFOLIO_MODE === 'true';

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

const CONSTRAINT_PRIORITY: string[] = ['budget', 'maxMonthly', 'zeroApr', 'category'];
const MAX_CONSTRAINT_CHIPS = 3;

const formatConstraintLabel = (key: string, value: string | boolean): string => {
  switch (key) {
    case 'budget': return `Under $${value}`;
    case 'maxMonthly': return `Under $${value}/mo`;
    case 'zeroApr': return '0% APR';
    case 'category': return String(value);
    default: return `${key}: ${String(value)}`;
  }
};

const prioritizeConstraints = (constraints: Record<string, string | boolean>) => {
  const entries = Object.entries(constraints);
  entries.sort((a, b) => {
    const ai = CONSTRAINT_PRIORITY.indexOf(a[0]);
    const bi = CONSTRAINT_PRIORITY.indexOf(b[0]);
    return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
  });
  return entries;
};

export default function SearchScreen() {
  const { query, results, loading, error, runSearch, setQuery, activeRefines } = useSearch();
  const [inputValue, setInputValue] = useState(query);
  const [selectedItem, setSelectedItem] = useState<DecisionItem | null>(null);
  const [localRefines, setLocalRefines] = useState<Record<string, boolean>>({});
  const [traceOpen, setTraceOpen] = useState(false);

  // Progressive reveal animations
  const summaryAnim = useRef(new Animated.Value(0)).current;
  const recommendedAnim = useRef(new Animated.Value(0)).current;
  const alternatesAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    setInputValue(query);
  }, [query]);

  // Progressive reveal when results arrive
  useEffect(() => {
    if (results && results.results.length > 0 && !loading) {
      summaryAnim.setValue(0);
      recommendedAnim.setValue(0);
      alternatesAnim.setValue(0);
      Animated.stagger(120, [
        Animated.timing(summaryAnim, { toValue: 1, duration: 300, useNativeDriver: true }),
        Animated.timing(recommendedAnim, { toValue: 1, duration: 300, useNativeDriver: true }),
        Animated.timing(alternatesAnim, { toValue: 1, duration: 300, useNativeDriver: true }),
      ]).start();
    }
  }, [results, loading]);

  const handleSubmit = () => {
    if (inputValue.trim()) {
      trackEvent('search_submitted', { query: inputValue.trim(), source: 'input' });
      setQuery(inputValue.trim());
      runSearch(inputValue.trim(), buildRefine(localRefines));
    }
  };

  const handleChipSearch = (q: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    trackEvent('search_submitted', { query: q, source: 'chip' });
    setInputValue(q);
    setQuery(q);
    setLocalRefines({});
    runSearch(q);
  };

  const handleRefine = (key: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    const updated = { ...localRefines, [key]: !localRefines[key] };
    trackEvent('refine_applied', { key, active: updated[key], query });
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
    <LinearGradient colors={[colors.bg, colors.surface]} style={styles.gradient}>
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
              placeholderTextColor={colors.textTertiary}
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
              <Animated.View style={{ opacity: summaryAnim, transform: [{ translateY: summaryAnim.interpolate({ inputRange: [0, 1], outputRange: [12, 0] }) }] }}>
                <Surface>
                  <Text style={styles.summaryText}>{results.aiSummary}</Text>
                </Surface>

                {/* Optimized for (agentic plan chips) */}
                {results.appliedConstraints && Object.keys(results.appliedConstraints).length > 0 && (() => {
                  const sorted = prioritizeConstraints(results.appliedConstraints);
                  const visible = sorted.slice(0, MAX_CONSTRAINT_CHIPS);
                  const overflow = sorted.length - MAX_CONSTRAINT_CHIPS;
                  return (
                    <Surface variant="muted">
                      <Text style={styles.optimizedLabel}>Optimized for</Text>
                      <View style={styles.optimizedChips}>
                        {visible.map(([k, v]) => (
                          <View key={k} style={styles.optimizedChip}>
                            <Text style={styles.optimizedChipText}>{formatConstraintLabel(k, v)}</Text>
                          </View>
                        ))}
                        {overflow > 0 && (
                          <View key="_overflow" style={styles.optimizedChip}>
                            <Text style={styles.optimizedChipText}>+{overflow} more</Text>
                          </View>
                        )}
                      </View>
                      <Text style={styles.trustMicrocopy}>Estimates shown. Final approval happens at checkout.</Text>
                    </Surface>
                  );
                })()}
              </Animated.View>

              {/* Recommended card */}
              <Animated.View style={{ opacity: recommendedAnim, transform: [{ translateY: recommendedAnim.interpolate({ inputRange: [0, 1], outputRange: [12, 0] }) }] }}>
                {results.results.length > 0 && (
                  <DecisionCard
                    key={results.results[0].id}
                    item={results.results[0]}
                    isRecommended
                    whyRecommended={results.whyThisRecommendation || undefined}
                    onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); trackEvent('offer_selected', { offerId: results.results[0].id, rank: 0, recommended: true }); setSelectedItem(results.results[0]); }}
                    onReview={() => { trackEvent('plan_modal_opened', { offerId: results.results[0].id, rank: 0 }); setSelectedItem(results.results[0]); }}
                  />
                )}
              </Animated.View>

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

              {/* Alternative cards */}
              <Animated.View style={{ opacity: alternatesAnim, transform: [{ translateY: alternatesAnim.interpolate({ inputRange: [0, 1], outputRange: [12, 0] }) }] }}>
                {results.results.slice(1).map((item: DecisionItem, idx: number) => (
                  <DecisionCard
                    key={item.id}
                    item={item}
                    onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); trackEvent('offer_selected', { offerId: item.id, rank: idx + 1 }); setSelectedItem(item); }}
                    onReview={() => { trackEvent('plan_modal_opened', { offerId: item.id, rank: idx + 1 }); setSelectedItem(item); }}
                  />
                ))}
              </Animated.View>

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
                                { height: `${Math.max(pct, 8)}%`, backgroundColor: i === 0 ? colors.primary : colors.barDefault },
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

              {/* Portfolio Mode: dev trace */}
              {PORTFOLIO_MODE && results.debugTrace && results.debugTrace.length > 0 && (
                <Surface variant="muted">
                  <Pressable
                    style={styles.devPanelHeader}
                    onPress={() => setTraceOpen(prev => !prev)}
                  >
                    <Text style={styles.devPanelTitle}>How we formed results</Text>
                    <Text style={styles.devPanelChevron}>{traceOpen ? '▲' : '▼'}</Text>
                  </Pressable>
                  {traceOpen && (
                    <View style={styles.devPanelBody}>
                      {results.debugTrace!.slice(0, 5).map((t: TraceStep, i: number) => (
                        <View key={i} style={styles.traceRow}>
                          <Text style={styles.traceStep}>{t.step}</Text>
                          <Text style={styles.traceMs}>{t.ms}ms</Text>
                        </View>
                      ))}
                      <Text style={styles.traceTotalMs}>
                        Total: {results.debugTrace!.reduce((sum: number, t: TraceStep) => sum + t.ms, 0).toFixed(1)}ms
                      </Text>
                    </View>
                  )}
                  <View style={styles.agentVersionRow}>
                    <Text style={styles.agentVersionText}>Agent v1</Text>
                    <Text style={styles.agentVersionText}>Ranking: retrieve → rerank → affordability score</Text>
                  </View>
                </Surface>
              )}

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
    backgroundColor: colors.surface,
    borderRadius: radii.surface,
    paddingHorizontal: 18,
    paddingVertical: 14,
    fontSize: 16,
    color: colors.textPrimary,
    borderWidth: 1,
    borderColor: colors.border,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 1,
  },
  chipSectionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textSecondary,
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  chipsRow: { paddingHorizontal: 16, gap: 8, paddingBottom: 8 },
  goalChip: {
    backgroundColor: colors.surface,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: radii.chip,
    borderWidth: 1,
    borderColor: colors.border,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.03,
    shadowRadius: 4,
    elevation: 1,
  },
  chipPressed: { transform: [{ scale: 0.96 }], backgroundColor: colors.merchantBg },
  goalChipText: { fontSize: 14, fontWeight: '500', color: colors.textPrimary },
  skeletonWrap: { paddingHorizontal: 16, gap: 12 },
  skeletonSummary: { padding: 4 },
  skeletonBar: { height: 12, borderRadius: 6, backgroundColor: colors.skeleton },
  errorText: { fontSize: 14, color: colors.error, textAlign: 'center' },
  summaryText: { fontSize: 14, color: colors.textSecondary, lineHeight: 20 },
  impactTitle: { fontSize: 13, fontWeight: '600', color: colors.textSecondary, marginBottom: 12 },
  barsRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'flex-end', height: 80 },
  barItem: { alignItems: 'center', flex: 1 },
  barTrack: { width: 20, height: 60, backgroundColor: colors.merchantBg, borderRadius: 4, justifyContent: 'flex-end', overflow: 'hidden' },
  barFill: { width: '100%', borderRadius: 4 },
  barValue: { fontSize: 11, fontWeight: '600', color: colors.textPrimary, marginTop: 4, fontVariant: ['tabular-nums'] },
  barLabel: { fontSize: 10, color: colors.textTertiary, marginTop: 2 },
  refineLabel: { fontSize: 14, fontWeight: '600', color: colors.textSecondary, paddingHorizontal: 20, marginTop: 16, marginBottom: 10 },
  refineChip: {
    backgroundColor: colors.surface,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
  },
  refineChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  refineChipText: { fontSize: 13, fontWeight: '500', color: colors.textSecondary },
  refineChipTextActive: { color: colors.surface },
  disclaimers: { paddingHorizontal: 20, marginTop: 16, gap: 4 },
  disclaimerText: { fontSize: 11, color: colors.textTertiary, textAlign: 'center' },
  optimizedLabel: { fontSize: 12, fontWeight: '600', color: colors.textSecondary, marginBottom: 8 },
  optimizedChips: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  optimizedChip: {
    backgroundColor: colors.surface,
    borderRadius: radii.surface,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: colors.border,
  },
  optimizedChipText: { fontSize: 12, fontWeight: '500', color: colors.primary },
  trustMicrocopy: { fontSize: 11, color: colors.textTertiary, marginTop: 10 },
  devPanelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingBottom: 8,
  },
  devPanelTitle: { fontSize: 12, fontWeight: '600', color: colors.textSecondary },
  devPanelChevron: { fontSize: 10, color: colors.textTertiary },
  devPanelBody: { gap: 6, marginTop: 4 },
  traceRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  traceStep: { fontSize: 12, fontWeight: '500', color: colors.textMeta, width: 80 },
  traceMs: { fontSize: 12, color: colors.primary, width: 55, textAlign: 'right', fontVariant: ['tabular-nums'] },
  traceTotalMs: { fontSize: 12, fontWeight: '600', color: colors.textPrimary, marginTop: 6 },
  agentVersionRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: colors.border },
  agentVersionText: { fontSize: 10, color: colors.textTertiary },
});

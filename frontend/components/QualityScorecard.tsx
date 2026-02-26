import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from 'react-native';
import { Surface } from './Surface';
import { getScorecard } from '../lib/api';
import { ScorecardResponse, ScorecardQueryResult } from '../types';
import { colors } from '../lib/theme';

export function QualityScorecard({ onClose }: { onClose: () => void }) {
  const [data, setData] = useState<ScorecardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getScorecard()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <View style={s.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={s.loadingText}>Running eval suite...</Text>
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={s.center}>
        <Text style={s.errorText}>Failed to load scorecard</Text>
        <Text style={s.errorDetail}>{error}</Text>
        <Pressable style={s.closeBtn} onPress={onClose}>
          <Text style={s.closeBtnText}>Close</Text>
        </Pressable>
      </View>
    );
  }

  const passRate = data.total_queries > 0
    ? Math.round((data.passed / data.total_queries) * 100)
    : 0;

  return (
    <ScrollView style={s.container} contentContainerStyle={s.scroll}>
      <View style={s.header}>
        <Text style={s.title}>Search Quality</Text>
        <Pressable onPress={onClose} hitSlop={12}>
          <Text style={s.closeX}>Done</Text>
        </Pressable>
      </View>

      {/* Hero metrics */}
      <View style={s.metricsRow}>
        <MetricCard label="Pass rate" value={`${passRate}%`} color={passRate >= 80 ? '#34C77B' : '#D97706'} />
        <MetricCard label="Constraint" value={`${data.constraint_adherence_pct}%`} color={data.constraint_adherence_pct >= 90 ? '#34C77B' : '#D97706'} />
        <MetricCard label="Avg latency" value={`${data.avg_latency_ms}ms`} color={data.avg_latency_ms < 100 ? '#34C77B' : '#D97706'} />
        <MetricCard label="p95" value={`${data.p95_latency_ms}ms`} color={data.p95_latency_ms < 200 ? '#34C77B' : '#D97706'} />
      </View>

      {/* Step latencies */}
      <Surface>
        <Text style={s.sectionTitle}>Pipeline step latency (avg ms)</Text>
        <View style={s.stepsGrid}>
          {Object.entries(data.step_latencies).map(([step, ms]) => (
            <View key={step} style={s.stepRow}>
              <Text style={s.stepName}>{step}</Text>
              <View style={s.stepBarTrack}>
                <View style={[s.stepBarFill, { width: `${Math.min((ms / 20) * 100, 100)}%` }]} />
              </View>
              <Text style={s.stepMs}>{ms}ms</Text>
            </View>
          ))}
        </View>
      </Surface>

      {/* Per-query results */}
      <Text style={[s.sectionTitle, { paddingHorizontal: 20, marginTop: 16 }]}>Per-query results</Text>
      {data.queries.map((q) => (
        <Surface key={q.id}>
          <View style={s.queryRow}>
            <Text style={[s.queryStatus, q.passed ? s.pass : s.fail]}>
              {q.passed ? 'PASS' : 'FAIL'}
            </Text>
            <View style={s.queryInfo}>
              <Text style={s.queryText} numberOfLines={1}>{q.query}</Text>
              <Text style={s.queryMeta}>
                {q.result_count} results | {q.latency_ms}ms | constraint: {q.constraint_ok ? 'OK' : 'FAIL'}
              </Text>
            </View>
          </View>
        </Surface>
      ))}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

function MetricCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <View style={s.metricCard}>
      <Text style={[s.metricValue, { color }]}>{value}</Text>
      <Text style={s.metricLabel}>{label}</Text>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  scroll: { paddingBottom: 40 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 40 },
  loadingText: { marginTop: 12, fontSize: 14, color: colors.textSecondary },
  errorText: { fontSize: 16, fontWeight: '600', color: '#D97706' },
  errorDetail: { fontSize: 13, color: colors.textTertiary, marginTop: 6 },
  closeBtn: { marginTop: 20, paddingHorizontal: 20, paddingVertical: 10, backgroundColor: colors.primary, borderRadius: 10 },
  closeBtnText: { color: '#FFF', fontWeight: '600' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingTop: 12 },
  title: { fontSize: 22, fontWeight: '700', color: colors.textPrimary },
  closeX: { fontSize: 15, fontWeight: '600', color: colors.textTertiary },
  metricsRow: { flexDirection: 'row', paddingHorizontal: 12, gap: 8, marginBottom: 16 },
  metricCard: {
    flex: 1, backgroundColor: '#FFFFFF', borderRadius: 14, padding: 14, alignItems: 'center',
    borderWidth: 1, borderColor: colors.border,
  },
  metricValue: { fontSize: 20, fontWeight: '700', fontVariant: ['tabular-nums'] },
  metricLabel: { fontSize: 11, color: colors.textTertiary, marginTop: 2, textAlign: 'center' },
  sectionTitle: { fontSize: 14, fontWeight: '600', color: colors.textPrimary, marginBottom: 10 },
  stepsGrid: { gap: 8 },
  stepRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  stepName: { width: 80, fontSize: 12, color: colors.textSecondary, fontWeight: '500' },
  stepBarTrack: { flex: 1, height: 6, backgroundColor: '#F3F4F6', borderRadius: 3, overflow: 'hidden' },
  stepBarFill: { height: '100%', backgroundColor: colors.primary, borderRadius: 3 },
  stepMs: { width: 48, fontSize: 12, color: colors.textTertiary, fontVariant: ['tabular-nums'], textAlign: 'right' },
  queryRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  queryStatus: { fontSize: 11, fontWeight: '700', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, overflow: 'hidden' },
  pass: { color: '#166534', backgroundColor: '#DCFCE7' },
  fail: { color: '#9A3412', backgroundColor: '#FEF3C7' },
  queryInfo: { flex: 1 },
  queryText: { fontSize: 14, color: colors.textPrimary, fontWeight: '500' },
  queryMeta: { fontSize: 12, color: colors.textTertiary, marginTop: 2, fontVariant: ['tabular-nums'] },
});

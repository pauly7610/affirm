import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable, Animated } from 'react-native';
import { colors } from '../lib/theme';

const DEMO_STEPS = [
  {
    step: 1,
    tab: 'Home',
    title: 'Start here',
    instruction: 'Tap "Upgrade my laptop" chip to begin a search.',
  },
  {
    step: 2,
    tab: 'Search',
    title: 'See agentic results',
    instruction: 'Review the AI summary, then tap "Only 0% APR" refine chip.',
  },
  {
    step: 3,
    tab: 'Search',
    title: 'Explore a plan',
    instruction: 'Tap "Review plan" on the recommended card to see monthly details.',
  },
  {
    step: 4,
    tab: 'Profile',
    title: 'Trust & transparency',
    instruction: 'Open "How Recommendations Work" and toggle Personalization off.',
  },
  {
    step: 5,
    tab: 'Profile',
    title: 'About this prototype',
    instruction: 'Scroll down and expand "About This Prototype" to see the pipeline.',
  },
];

export function DemoWalkthrough() {
  const [visible, setVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  if (!visible) {
    return (
      <Pressable style={s.fab} onPress={() => setVisible(true)}>
        <Text style={s.fabText}>Demo</Text>
      </Pressable>
    );
  }

  const step = DEMO_STEPS[currentStep];
  const isLast = currentStep === DEMO_STEPS.length - 1;
  const isFirst = currentStep === 0;

  return (
    <View style={s.overlay}>
      <View style={s.card}>
        <View style={s.header}>
          <Text style={s.stepBadge}>Step {step.step}/{DEMO_STEPS.length}</Text>
          <Text style={s.tab}>{step.tab}</Text>
          <Pressable onPress={() => setVisible(false)} hitSlop={12}>
            <Text style={s.close}>Done</Text>
          </Pressable>
        </View>
        <Text style={s.title}>{step.title}</Text>
        <Text style={s.instruction}>{step.instruction}</Text>
        <View style={s.nav}>
          {!isFirst && (
            <Pressable style={s.navBtn} onPress={() => setCurrentStep(currentStep - 1)}>
              <Text style={s.navBtnText}>Back</Text>
            </Pressable>
          )}
          <View style={{ flex: 1 }} />
          {!isLast ? (
            <Pressable style={[s.navBtn, s.navBtnPrimary]} onPress={() => setCurrentStep(currentStep + 1)}>
              <Text style={[s.navBtnText, s.navBtnTextPrimary]}>Next</Text>
            </Pressable>
          ) : (
            <Pressable style={[s.navBtn, s.navBtnPrimary]} onPress={() => { setVisible(false); setCurrentStep(0); }}>
              <Text style={[s.navBtnText, s.navBtnTextPrimary]}>Finish</Text>
            </Pressable>
          )}
        </View>
        {/* Progress dots */}
        <View style={s.dots}>
          {DEMO_STEPS.map((_, i) => (
            <View key={i} style={[s.dot, i === currentStep && s.dotActive]} />
          ))}
        </View>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  fab: {
    position: 'absolute',
    bottom: 100,
    right: 20,
    backgroundColor: colors.primary,
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 6,
    zIndex: 999,
  },
  fabText: { color: '#FFF', fontSize: 14, fontWeight: '700' },
  overlay: {
    position: 'absolute',
    bottom: 100,
    left: 16,
    right: 16,
    zIndex: 999,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 18,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 16,
    elevation: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  stepBadge: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.primary,
    backgroundColor: colors.primaryLight,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    overflow: 'hidden',
  },
  tab: { fontSize: 11, color: colors.textTertiary, marginLeft: 8, flex: 1 },
  close: { fontSize: 13, color: colors.textTertiary, fontWeight: '600' },
  title: { fontSize: 16, fontWeight: '700', color: colors.textPrimary, marginBottom: 4 },
  instruction: { fontSize: 14, color: colors.textSecondary, lineHeight: 20, marginBottom: 14 },
  nav: { flexDirection: 'row', alignItems: 'center' },
  navBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.borderOutline,
  },
  navBtnPrimary: { backgroundColor: colors.primary, borderColor: colors.primary },
  navBtnText: { fontSize: 13, fontWeight: '600', color: colors.textSecondary },
  navBtnTextPrimary: { color: '#FFFFFF' },
  dots: { flexDirection: 'row', justifyContent: 'center', marginTop: 12, gap: 6 },
  dot: { width: 6, height: 6, borderRadius: 3, backgroundColor: colors.borderSubtle },
  dotActive: { backgroundColor: colors.primary, width: 18 },
});

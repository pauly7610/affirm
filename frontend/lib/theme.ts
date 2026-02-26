export const colors = {
  primary: '#2F6FED',
  primaryLight: '#EEF2FF',

  bg: '#F6F7FB',
  bgMuted: '#F8FAFC',
  surface: '#FFFFFF',
  border: '#E8EDF3',
  borderSubtle: '#E5E7EB',
  borderOutline: '#D1D5DB',

  textPrimary: '#1A1D23',
  textSecondary: '#6B7280',
  textTertiary: '#9CA3AF',
  textMeta: '#475569',

  shadow: '#000000',
  error: '#D97706',
  barDefault: '#D1D5DB',
  skeleton: '#E5E7EB',
  merchantBg: '#F3F4F6',
} as const;

export const radii = {
  surface: 16,
  card: 16,
  chip: 20,
  cta: 12,
  badge: 20,
  merchantIcon: 12,
} as const;

export const shadows = {
  soft: {
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 1 } as const,
    shadowOpacity: 0.03,
    shadowRadius: 8,
    elevation: 1,
  },
  medium: {
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 1 } as const,
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 2,
  },
} as const;

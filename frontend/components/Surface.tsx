import React, { ReactNode } from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { colors, radii, shadows } from '../lib/theme';

interface SurfaceProps {
  children: ReactNode;
  style?: ViewStyle;
  variant?: 'default' | 'muted';
  inset?: boolean;
}

export function Surface({ children, style, variant = 'default', inset }: SurfaceProps) {
  return (
    <View
      style={[
        styles.surface,
        variant === 'muted' && styles.muted,
        inset && styles.inset,
        style,
      ]}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  surface: {
    backgroundColor: colors.surface,
    borderRadius: radii.surface,
    padding: 20,
    marginHorizontal: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.soft,
  },
  muted: {
    backgroundColor: colors.bgMuted,
  },
  inset: {
    marginHorizontal: 0,
  },
});

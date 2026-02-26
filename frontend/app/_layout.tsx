import React from 'react';
import { View } from 'react-native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SearchProvider } from '../context/SearchContext';
import { DemoWalkthrough } from '../components/DemoWalkthrough';

const PORTFOLIO_MODE = process.env.EXPO_PUBLIC_PORTFOLIO_MODE === 'true';

export default function RootLayout() {
  return (
    <SearchProvider>
      <StatusBar style="dark" />
      <View style={{ flex: 1 }}>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(tabs)" />
        </Stack>
        {PORTFOLIO_MODE && <DemoWalkthrough />}
      </View>
    </SearchProvider>
  );
}

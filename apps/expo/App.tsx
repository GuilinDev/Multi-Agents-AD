import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Text } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { HomeScreen, ChatScreen, DashboardScreen, SettingsScreen } from '@memowell/app';
import { colors } from '@memowell/app/theme/colors';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function ChatStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.surface },
        headerTintColor: colors.text,
        headerTitleStyle: { fontWeight: '600', fontSize: 18 },
      }}
    >
      <Stack.Screen name="Home" options={{ title: 'Memowell' }}>
        {() => <HomeScreen />}
      </Stack.Screen>
      <Stack.Screen name="Chat" options={{ title: 'Therapy Session' }}>
        {({ route }: any) => (
          <ChatScreen
            sessionId={route.params?.sessionId}
            patientName={route.params?.patientName}
          />
        )}
      </Stack.Screen>
    </Stack.Navigator>
  );
}

function TabIcon({ label, focused }: { label: string; focused: boolean }) {
  return <Text style={{ fontSize: 22, opacity: focused ? 1 : 0.5 }}>{label}</Text>;
}

export default function App() {
  return (
    <>
      <StatusBar style="dark" />
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={{
            headerShown: false,
            tabBarStyle: {
              backgroundColor: colors.surface,
              borderTopColor: colors.border,
              height: 88,
              paddingBottom: 28,
              paddingTop: 8,
            },
            tabBarLabelStyle: { fontSize: 13, fontWeight: '600' },
            tabBarActiveTintColor: colors.primary,
            tabBarInactiveTintColor: colors.textLight,
          }}
        >
          <Tab.Screen
            name="Session"
            component={ChatStack}
            options={{ tabBarIcon: ({ focused }) => <TabIcon label="💬" focused={focused} /> }}
          />
          <Tab.Screen
            name="Dashboard"
            options={{
              headerShown: true,
              tabBarIcon: ({ focused }) => <TabIcon label="📊" focused={focused} />,
            }}
          >
            {() => <DashboardScreen />}
          </Tab.Screen>
          <Tab.Screen
            name="Settings"
            options={{
              headerShown: true,
              tabBarIcon: ({ focused }) => <TabIcon label="⚙️" focused={focused} />,
            }}
          >
            {() => <SettingsScreen />}
          </Tab.Screen>
        </Tab.Navigator>
      </NavigationContainer>
    </>
  );
}

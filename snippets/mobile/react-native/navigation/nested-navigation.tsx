import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { Ionicons } from '@expo/vector-icons';

// Type definitions
type RootStackParamList = {
  Main: undefined;
  Modal: { id: string };
  Details: { itemId: string };
};

type MainTabParamList = {
  HomeStack: undefined;
  ProfileStack: undefined;
  SettingsStack: undefined;
};

type HomeStackParamList = {
  HomeScreen: undefined;
  HomeDetails: { id: string };
};

// Create navigators
const RootStack = createNativeStackNavigator<RootStackParamList>();
const MainTab = createBottomTabNavigator<MainTabParamList>();
const HomeStack = createNativeStackNavigator<HomeStackParamList>();
const Drawer = createDrawerNavigator();

// Home Stack Navigator
const HomeStackNavigator: React.FC = () => {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen name="HomeScreen" component={HomeScreen} />
      <HomeStack.Screen name="HomeDetails" component={HomeDetailsScreen} />
    </HomeStack.Navigator>
  );
};

// Profile Stack Navigator
const ProfileStackNavigator: React.FC = () => {
  return (
    <ProfileStack.Navigator>
      <ProfileStack.Screen name="ProfileScreen" component={ProfileScreen} />
      <ProfileStack.Screen name="EditProfile" component={EditProfileScreen} />
    </ProfileStack.Navigator>
  );
};

// Settings Stack Navigator
const SettingsStackNavigator: React.FC = () => {
  return (
    <SettingsStack.Navigator>
      <SettingsStack.Screen name="SettingsScreen" component={SettingsScreen} />
      <SettingsStack.Screen name="SettingsDetails" component={SettingsDetailsScreen} />
    </SettingsStack.Navigator>
  );
};

// Main Tab Navigator
const MainTabNavigator: React.FC = () => {
  return (
    <MainTab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'HomeStack') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'ProfileStack') {
            iconName = focused ? 'person' : 'person-outline';
          } else {
            iconName = focused ? 'settings' : 'settings-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6200ee',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <MainTab.Screen
        name="HomeStack"
        component={HomeStackNavigator}
        options={{ title: 'Home' }}
      />
      <MainTab.Screen
        name="ProfileStack"
        component={ProfileStackNavigator}
        options={{ title: 'Profile' }}
      />
      <MainTab.Screen
        name="SettingsStack"
        component={SettingsStackNavigator}
        options={{ title: 'Settings' }}
      />
    </MainTab.Navigator>
  );
};

// Root Navigator with Modal
export const RootNavigator: React.FC = () => {
  return (
    <RootStack.Navigator>
      <RootStack.Screen
        name="Main"
        component={MainTabNavigator}
        options={{ headerShown: false }}
      />
      <RootStack.Screen
        name="Modal"
        component={ModalScreen}
        options={{
          presentation: 'modal',
          headerTitle: 'Modal Screen',
        }}
      />
      <RootStack.Screen
        name="Details"
        component={DetailsScreen}
        options={({ route }) => ({
          title: `Details ${route.params.itemId}`,
        })}
      />
    </RootStack.Navigator>
  );
};

// Drawer Navigator Example
export const DrawerNavigatorExample: React.FC = () => {
  return (
    <Drawer.Navigator>
      <Drawer.Screen name="Main" component={MainTabNavigator} />
      <Drawer.Screen name="Notifications" component={NotificationsScreen} />
      <Drawer.Screen name="Help" component={HelpScreen} />
    </Drawer.Navigator>
  );
};

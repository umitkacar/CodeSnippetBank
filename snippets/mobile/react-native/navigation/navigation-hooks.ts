import { useNavigation, useRoute, useFocusEffect, useIsFocused } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';
import { useCallback } from 'react';

type RootStackParamList = {
  Home: undefined;
  Details: { id: string; title: string };
  Profile: { userId: string };
};

// Type-safe navigation hook
export const useAppNavigation = () => {
  return useNavigation<NativeStackNavigationProp<RootStackParamList>>();
};

// Type-safe route hook
export const useDetailsRoute = () => {
  return useRoute<RouteProp<RootStackParamList, 'Details'>>();
};

// Navigation with params
export const navigateToDetails = (navigation: any, id: string, title: string) => {
  navigation.navigate('Details', { id, title });
};

// Go back with fallback
export const goBackOrHome = (navigation: any) => {
  if (navigation.canGoBack()) {
    navigation.goBack();
  } else {
    navigation.navigate('Home');
  }
};

// Reset navigation stack
export const resetToHome = (navigation: any) => {
  navigation.reset({
    index: 0,
    routes: [{ name: 'Home' }],
  });
};

// Focus effect hook usage
export const useFocusHandler = (callback: () => void, cleanup?: () => void) => {
  useFocusEffect(
    useCallback(() => {
      callback();
      return () => {
        cleanup?.();
      };
    }, [callback, cleanup])
  );
};

// Check if screen is focused
export const useScreenFocus = () => {
  return useIsFocused();
};

// Navigate and pass callback
export const navigateWithCallback = (
  navigation: any,
  screen: string,
  callback: () => void
) => {
  navigation.navigate(screen, { onGoBack: callback });
};

// Deep linking helper
export const handleDeepLink = (navigation: any, url: string) => {
  const route = url.replace(/.*?:\/\//g, '');
  const routeName = route.split('/')[0];
  const params = route.split('/').slice(1);

  if (routeName && params) {
    navigation.navigate(routeName, { id: params[0] });
  }
};

import * as Linking from 'expo-linking';
import { useEffect } from 'react';
import { useNavigation } from '@react-navigation/native';
import { Platform } from 'react-native';

const prefix = Linking.createURL('/');

export const linkingConfig = {
  prefixes: [prefix, 'myapp://', 'https://myapp.com'],
  config: {
    screens: {
      Home: '',
      Profile: 'profile/:userId',
      Details: 'details/:id',
      Article: 'article/:slug',
      Settings: 'settings',
      NotFound: '*',
    },
  },
};

export class DeepLinkService {
  static async getInitialURL(): Promise<string | null> {
    return await Linking.getInitialURL();
  }

  static parseURL(url: string): Linking.ParsedURL {
    return Linking.parse(url);
  }

  static createURL(path: string, queryParams?: Record<string, string>): string {
    return Linking.createURL(path, { queryParams });
  }

  static async canOpenURL(url: string): Promise<boolean> {
    return await Linking.canOpenURL(url);
  }

  static async openURL(url: string): Promise<void> {
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      await Linking.openURL(url);
    } else {
      console.log("Don't know how to open URI: " + url);
    }
  }

  static async openSettings(): Promise<void> {
    await Linking.openSettings();
  }

  static async openMap(address: string): Promise<void> {
    const url = Platform.select({
      ios: `maps:0,0?q=${address}`,
      android: `geo:0,0?q=${address}`,
    });
    if (url) {
      await this.openURL(url);
    }
  }

  static async openEmail(email: string, subject?: string, body?: string): Promise<void> {
    let url = `mailto:${email}`;
    const params = [];
    if (subject) params.push(`subject=${encodeURIComponent(subject)}`);
    if (body) params.push(`body=${encodeURIComponent(body)}`);
    if (params.length > 0) url += `?${params.join('&')}`;
    await this.openURL(url);
  }

  static async openPhone(phoneNumber: string): Promise<void> {
    await this.openURL(`tel:${phoneNumber}`);
  }

  static async openSMS(phoneNumber: string, body?: string): Promise<void> {
    const url = `sms:${phoneNumber}${body ? `?body=${encodeURIComponent(body)}` : ''}`;
    await this.openURL(url);
  }
}

// React hook for deep linking
export const useDeepLinking = () => {
  const navigation = useNavigation();

  useEffect(() => {
    const handleDeepLink = (event: { url: string }) => {
      const parsed = Linking.parse(event.url);
      const { path, queryParams } = parsed;

      // Handle different deep link paths
      if (path === 'profile' && queryParams?.userId) {
        navigation.navigate('Profile', { userId: queryParams.userId });
      } else if (path === 'details' && queryParams?.id) {
        navigation.navigate('Details', { id: queryParams.id });
      }
    };

    // Handle deep link when app is opened from link
    Linking.getInitialURL().then((url) => {
      if (url) {
        handleDeepLink({ url });
      }
    });

    // Handle deep link when app is already open
    const subscription = Linking.addEventListener('url', handleDeepLink);

    return () => {
      subscription.remove();
    };
  }, [navigation]);
};

// Universal link validator
export const validateUniversalLink = (url: string): boolean => {
  const validDomains = ['myapp.com', 'www.myapp.com'];
  try {
    const parsed = new URL(url);
    return validDomains.includes(parsed.hostname);
  } catch {
    return false;
  }
};

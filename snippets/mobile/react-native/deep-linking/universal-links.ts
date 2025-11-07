import { Linking, Platform } from 'react-native';
import branch from 'react-native-branch';

export class UniversalLinkService {
  static async initializeBranch(): Promise<void> {
    if (Platform.OS === 'ios') {
      // iOS configuration
      await branch.initSessionTtl(10000);
    }

    branch.subscribe(({ error, params, uri }) => {
      if (error) {
        console.error('Branch error:', error);
        return;
      }

      if (params['+non_branch_link']) {
        const nonBranchUrl = params['+non_branch_link'];
        // Handle non-branch link
        return;
      }

      if (!params['+clicked_branch_link']) {
        // Not a Branch link
        return;
      }

      // Handle Branch deep link
      this.handleBranchLink(params);
    });
  }

  static handleBranchLink(params: any): void {
    const { screen, data } = params;

    switch (screen) {
      case 'product':
        // Navigate to product screen
        break;
      case 'profile':
        // Navigate to profile screen
        break;
      default:
        console.log('Unknown screen:', screen);
    }
  }

  static async createBranchLink(
    screen: string,
    data: any
  ): Promise<string> {
    const branchUniversalObject = await branch.createBranchUniversalObject(
      'canonicalIdentifier',
      {
        locallyIndex: true,
        title: data.title,
        contentDescription: data.description,
        contentImageUrl: data.imageUrl,
        contentMetadata: {
          customMetadata: {
            screen,
            ...data,
          },
        },
      }
    );

    const linkProperties = {
      feature: 'share',
      channel: 'app',
    };

    const controlParams = {
      $desktop_url: 'https://myapp.com',
      $ios_url: 'https://apps.apple.com/app/myapp',
      $android_url: 'https://play.google.com/store/apps/details?id=com.myapp',
    };

    const { url } = await branchUniversalObject.generateShortUrl(
      linkProperties,
      controlParams
    );

    return url;
  }

  static async trackEvent(eventName: string, metadata?: any): Promise<void> {
    const event = await branch.createBranchEvent(eventName, metadata);
    event.logEvent();
  }

  static async setUserIdentity(userId: string): Promise<void> {
    await branch.setIdentity(userId);
  }

  static async logout(): Promise<void> {
    await branch.logout();
  }
}

// Dynamic link parameters
export interface DynamicLinkParams {
  link: string;
  domainUriPrefix: string;
  androidInfo?: {
    androidPackageName: string;
    androidFallbackLink?: string;
    androidMinPackageVersionCode?: string;
  };
  iosInfo?: {
    iosBundleId: string;
    iosFallbackLink?: string;
    iosAppStoreId?: string;
  };
  socialMetaTagInfo?: {
    socialTitle?: string;
    socialDescription?: string;
    socialImageLink?: string;
  };
}

export const buildDynamicLink = (params: DynamicLinkParams): string => {
  // Build Firebase Dynamic Link
  const baseUrl = `https://${params.domainUriPrefix}`;
  const queryParams = new URLSearchParams({
    link: params.link,
  });

  if (params.androidInfo) {
    queryParams.append('apn', params.androidInfo.androidPackageName);
    if (params.androidInfo.androidFallbackLink) {
      queryParams.append('afl', params.androidInfo.androidFallbackLink);
    }
  }

  if (params.iosInfo) {
    queryParams.append('ibi', params.iosInfo.iosBundleId);
    if (params.iosInfo.iosAppStoreId) {
      queryParams.append('isi', params.iosInfo.iosAppStoreId);
    }
  }

  return `${baseUrl}?${queryParams.toString()}`;
};

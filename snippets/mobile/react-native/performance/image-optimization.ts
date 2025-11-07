import FastImage from 'react-native-fast-image';
import { Image, Platform } from 'react-native';
import * as FileSystem from 'expo-file-system';

export const OptimizedImage: React.FC<{
  uri: string;
  style?: any;
  resizeMode?: 'contain' | 'cover' | 'stretch' | 'center';
}> = ({ uri, style, resizeMode = 'cover' }) => {
  return (
    <FastImage
      style={style}
      source={{
        uri,
        priority: FastImage.priority.normal,
        cache: FastImage.cacheControl.immutable,
      }}
      resizeMode={FastImage.resizeMode[resizeMode]}
    />
  );
};

export class ImageCache {
  private static cache: Map<string, string> = new Map();
  private static cacheDir = `${FileSystem.cacheDirectory}images/`;

  static async initialize(): Promise<void> {
    const dirInfo = await FileSystem.getInfoAsync(this.cacheDir);
    if (!dirInfo.exists) {
      await FileSystem.makeDirectoryAsync(this.cacheDir, { intermediates: true });
    }
  }

  static async getCachedImage(url: string): Promise<string> {
    if (this.cache.has(url)) {
      return this.cache.get(url)!;
    }

    const filename = this.getFilename(url);
    const filepath = `${this.cacheDir}${filename}`;

    const fileInfo = await FileSystem.getInfoAsync(filepath);
    if (fileInfo.exists) {
      this.cache.set(url, filepath);
      return filepath;
    }

    // Download and cache
    const { uri } = await FileSystem.downloadAsync(url, filepath);
    this.cache.set(url, uri);
    return uri;
  }

  private static getFilename(url: string): string {
    return url.split('/').pop() || `${Date.now()}.jpg`;
  }

  static async clearCache(): Promise<void> {
    await FileSystem.deleteAsync(this.cacheDir, { idempotent: true });
    await this.initialize();
    this.cache.clear();
  }

  static async getCacheSize(): Promise<number> {
    const dirInfo = await FileSystem.getInfoAsync(this.cacheDir);
    return dirInfo.exists ? dirInfo.size || 0 : 0;
  }
}

// Preload images
export const preloadImages = async (urls: string[]): Promise<void> => {
  const promises = urls.map(url =>
    FastImage.preload([{ uri: url, priority: FastImage.priority.high }])
  );
  await Promise.all(promises);
};

// Progressive image loading
export const ProgressiveImage: React.FC<{
  thumbnailUri: string;
  fullUri: string;
  style?: any;
}> = ({ thumbnailUri, fullUri, style }) => {
  const [loaded, setLoaded] = React.useState(false);

  return (
    <View style={style}>
      <Image
        source={{ uri: thumbnailUri }}
        style={[style, StyleSheet.absoluteFill]}
        blurRadius={1}
      />
      <Image
        source={{ uri: fullUri }}
        style={style}
        onLoad={() => setLoaded(true)}
        fadeDuration={300}
      />
    </View>
  );
};

import * as MediaLibrary from 'expo-media-library';
import { Alert } from 'react-native';

export class MediaLibraryService {
  static async requestPermissions(): Promise<boolean> {
    const { status } = await MediaLibrary.requestPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission denied', 'Media library permission is required');
      return false;
    }
    return true;
  }

  static async saveToLibrary(uri: string, albumName?: string): Promise<void> {
    const hasPermission = await this.requestPermissions();
    if (!hasPermission) return;

    try {
      const asset = await MediaLibrary.createAssetAsync(uri);

      if (albumName) {
        const album = await MediaLibrary.getAlbumAsync(albumName);
        if (album) {
          await MediaLibrary.addAssetsToAlbumAsync([asset], album, false);
        } else {
          await MediaLibrary.createAlbumAsync(albumName, asset, false);
        }
      }

      Alert.alert('Success', 'Media saved to library');
    } catch (error) {
      Alert.alert('Error', 'Failed to save media');
      console.error(error);
    }
  }

  static async getAlbums(): Promise<MediaLibrary.Album[]> {
    const hasPermission = await this.requestPermissions();
    if (!hasPermission) return [];

    const albums = await MediaLibrary.getAlbumsAsync();
    return albums;
  }

  static async getAssets(
    options: MediaLibrary.AssetsOptions = {}
  ): Promise<MediaLibrary.PagedInfo<MediaLibrary.Asset>> {
    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      return { assets: [], endCursor: '', hasNextPage: false, totalCount: 0 };
    }

    return await MediaLibrary.getAssetsAsync({
      first: 20,
      mediaType: MediaLibrary.MediaType.photo,
      sortBy: MediaLibrary.SortBy.creationTime,
      ...options,
    });
  }

  static async getRecentPhotos(count: number = 20): Promise<MediaLibrary.Asset[]> {
    const result = await this.getAssets({
      first: count,
      mediaType: MediaLibrary.MediaType.photo,
      sortBy: MediaLibrary.SortBy.creationTime,
    });
    return result.assets;
  }

  static async deleteAsset(assetId: string): Promise<boolean> {
    try {
      await MediaLibrary.deleteAssetsAsync([assetId]);
      return true;
    } catch (error) {
      console.error('Error deleting asset:', error);
      return false;
    }
  }

  static async getAssetInfo(assetId: string): Promise<MediaLibrary.AssetInfo | null> {
    try {
      return await MediaLibrary.getAssetInfoAsync(assetId);
    } catch (error) {
      console.error('Error getting asset info:', error);
      return null;
    }
  }
}

export const useMediaLibrary = () => {
  const [assets, setAssets] = React.useState<MediaLibrary.Asset[]>([]);
  const [loading, setLoading] = React.useState(false);

  const loadAssets = async () => {
    setLoading(true);
    const result = await MediaLibraryService.getAssets();
    setAssets(result.assets);
    setLoading(false);
  };

  React.useEffect(() => {
    loadAssets();
  }, []);

  return { assets, loading, loadAssets };
};

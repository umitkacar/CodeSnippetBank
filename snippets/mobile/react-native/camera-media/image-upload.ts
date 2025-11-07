import * as FileSystem from 'expo-file-system';
import * as ImageManipulator from 'expo-image-manipulator';

interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export class ImageUploader {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async compressImage(uri: string, quality: number = 0.7): Promise<string> {
    const manipResult = await ImageManipulator.manipulateAsync(
      uri,
      [{ resize: { width: 1024 } }],
      { compress: quality, format: ImageManipulator.SaveFormat.JPEG }
    );
    return manipResult.uri;
  }

  async uploadImage(
    uri: string,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<{ url: string; id: string }> {
    const compressedUri = await this.compressImage(uri);

    const uploadResult = await FileSystem.uploadAsync(
      `${this.baseURL}/upload`,
      compressedUri,
      {
        fieldName: 'image',
        httpMethod: 'POST',
        uploadType: FileSystem.FileSystemUploadType.MULTIPART,
      }
    );

    if (uploadResult.status !== 200) {
      throw new Error('Upload failed');
    }

    return JSON.parse(uploadResult.body);
  }

  async uploadMultipleImages(
    uris: string[],
    onProgress?: (index: number, total: number) => void
  ): Promise<Array<{ url: string; id: string }>> {
    const results = [];

    for (let i = 0; i < uris.length; i++) {
      onProgress?.(i + 1, uris.length);
      const result = await this.uploadImage(uris[i]);
      results.push(result);
    }

    return results;
  }

  async downloadImage(url: string, filename: string): Promise<string> {
    const downloadDir = FileSystem.documentDirectory + 'images/';
    await FileSystem.makeDirectoryAsync(downloadDir, { intermediates: true });

    const downloadResult = await FileSystem.downloadAsync(
      url,
      downloadDir + filename
    );

    return downloadResult.uri;
  }

  async getImageInfo(uri: string): Promise<FileSystem.FileInfo> {
    return await FileSystem.getInfoAsync(uri);
  }
}

export const imageUploader = new ImageUploader('https://api.example.com');

// React hook for image upload
export const useImageUpload = () => {
  const [uploading, setUploading] = React.useState(false);
  const [progress, setProgress] = React.useState(0);

  const uploadImage = async (uri: string) => {
    setUploading(true);
    setProgress(0);

    try {
      const result = await imageUploader.uploadImage(uri, (progress) => {
        setProgress(progress.percentage);
      });
      return result;
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  return { uploadImage, uploading, progress };
};

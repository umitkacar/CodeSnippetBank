import 'dart:io';
import 'package:firebase_storage/firebase_storage.dart';

class FirebaseStorageService {
  final FirebaseStorage _storage = FirebaseStorage.instance;

  // Upload file
  Future<String> uploadFile({
    required File file,
    required String path,
    Function(double)? onProgress,
  }) async {
    final ref = _storage.ref().child(path);
    final uploadTask = ref.putFile(file);

    uploadTask.snapshotEvents.listen((snapshot) {
      final progress = snapshot.bytesTransferred / snapshot.totalBytes;
      onProgress?.call(progress);
    });

    await uploadTask;
    return await ref.getDownloadURL();
  }

  // Upload data
  Future<String> uploadData({
    required List<int> data,
    required String path,
  }) async {
    final ref = _storage.ref().child(path);
    await ref.putData(data as Uint8List);
    return await ref.getDownloadURL();
  }

  // Download file
  Future<void> downloadFile({
    required String path,
    required File destinationFile,
  }) async {
    final ref = _storage.ref().child(path);
    await ref.writeToFile(destinationFile);
  }

  // Get download URL
  Future<String> getDownloadURL(String path) async {
    final ref = _storage.ref().child(path);
    return await ref.getDownloadURL();
  }

  // Delete file
  Future<void> deleteFile(String path) async {
    final ref = _storage.ref().child(path);
    await ref.delete();
  }

  // List files in directory
  Future<List<String>> listFiles(String path) async {
    final ref = _storage.ref().child(path);
    final result = await ref.listAll();
    return result.items.map((item) => item.name).toList();
  }

  // Get metadata
  Future<FullMetadata> getMetadata(String path) async {
    final ref = _storage.ref().child(path);
    return await ref.getMetadata();
  }

  // Update metadata
  Future<void> updateMetadata({
    required String path,
    required Map<String, String> customMetadata,
  }) async {
    final ref = _storage.ref().child(path);
    await ref.updateMetadata(
      SettableMetadata(customMetadata: customMetadata),
    );
  }
}

// Image upload service
class ImageUploadService {
  final FirebaseStorageService _storageService = FirebaseStorageService();

  Future<String> uploadProfileImage({
    required File imageFile,
    required String userId,
  }) async {
    final path = 'users/$userId/profile.jpg';
    return await _storageService.uploadFile(
      file: imageFile,
      path: path,
    );
  }

  Future<String> uploadPostImage({
    required File imageFile,
    required String postId,
  }) async {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final path = 'posts/$postId/$timestamp.jpg';
    return await _storageService.uploadFile(
      file: imageFile,
      path: path,
    );
  }

  Future<void> deleteProfileImage(String userId) async {
    final path = 'users/$userId/profile.jpg';
    await _storageService.deleteFile(path);
  }
}

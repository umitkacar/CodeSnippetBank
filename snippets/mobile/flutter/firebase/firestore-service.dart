import 'package:cloud_firestore/cloud_firestore.dart';

class FirestoreService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Create
  Future<String> addDocument(String collection, Map<String, dynamic> data) async {
    final docRef = await _firestore.collection(collection).add(data);
    return docRef.id;
  }

  Future<void> setDocument(
    String collection,
    String docId,
    Map<String, dynamic> data,
  ) async {
    await _firestore.collection(collection).doc(docId).set(data);
  }

  // Read
  Future<Map<String, dynamic>?> getDocument(
    String collection,
    String docId,
  ) async {
    final doc = await _firestore.collection(collection).doc(docId).get();
    return doc.data();
  }

  Stream<DocumentSnapshot> getDocumentStream(
    String collection,
    String docId,
  ) {
    return _firestore.collection(collection).doc(docId).snapshots();
  }

  Future<List<Map<String, dynamic>>> getCollection(String collection) async {
    final snapshot = await _firestore.collection(collection).get();
    return snapshot.docs.map((doc) => doc.data()).toList();
  }

  Stream<QuerySnapshot> getCollectionStream(String collection) {
    return _firestore.collection(collection).snapshots();
  }

  // Update
  Future<void> updateDocument(
    String collection,
    String docId,
    Map<String, dynamic> data,
  ) async {
    await _firestore.collection(collection).doc(docId).update(data);
  }

  // Delete
  Future<void> deleteDocument(String collection, String docId) async {
    await _firestore.collection(collection).doc(docId).delete();
  }

  // Query operations
  Future<List<Map<String, dynamic>>> queryDocuments({
    required String collection,
    String? field,
    dynamic isEqualTo,
    dynamic isLessThan,
    dynamic isGreaterThan,
    int? limit,
  }) async {
    Query query = _firestore.collection(collection);

    if (field != null) {
      if (isEqualTo != null) {
        query = query.where(field, isEqualTo: isEqualTo);
      }
      if (isLessThan != null) {
        query = query.where(field, isLessThan: isLessThan);
      }
      if (isGreaterThan != null) {
        query = query.where(field, isGreaterThan: isGreaterThan);
      }
    }

    if (limit != null) {
      query = query.limit(limit);
    }

    final snapshot = await query.get();
    return snapshot.docs.map((doc) => doc.data() as Map<String, dynamic>).toList();
  }

  // Batch write
  Future<void> batchWrite(List<BatchOperation> operations) async {
    final batch = _firestore.batch();

    for (var operation in operations) {
      final docRef = _firestore.collection(operation.collection).doc(operation.docId);

      switch (operation.type) {
        case BatchOperationType.set:
          batch.set(docRef, operation.data!);
          break;
        case BatchOperationType.update:
          batch.update(docRef, operation.data!);
          break;
        case BatchOperationType.delete:
          batch.delete(docRef);
          break;
      }
    }

    await batch.commit();
  }

  // Transaction
  Future<T> runTransaction<T>(
    Future<T> Function(Transaction transaction) updateFunction,
  ) async {
    return await _firestore.runTransaction<T>(updateFunction);
  }

  // Pagination
  Future<List<Map<String, dynamic>>> getPaginatedDocuments({
    required String collection,
    int limit = 10,
    DocumentSnapshot? startAfter,
  }) async {
    Query query = _firestore.collection(collection).limit(limit);

    if (startAfter != null) {
      query = query.startAfterDocument(startAfter);
    }

    final snapshot = await query.get();
    return snapshot.docs.map((doc) => doc.data() as Map<String, dynamic>).toList();
  }
}

// User service example
class UserFirestoreService {
  final FirestoreService _firestoreService = FirestoreService();
  static const String collection = 'users';

  Future<String> createUser(UserData user) async {
    return await _firestoreService.addDocument(collection, user.toMap());
  }

  Future<UserData?> getUser(String userId) async {
    final data = await _firestoreService.getDocument(collection, userId);
    return data != null ? UserData.fromMap(data) : null;
  }

  Stream<UserData?> getUserStream(String userId) {
    return _firestoreService.getDocumentStream(collection, userId).map(
          (snapshot) => snapshot.exists
              ? UserData.fromMap(snapshot.data() as Map<String, dynamic>)
              : null,
        );
  }

  Future<void> updateUser(String userId, Map<String, dynamic> updates) async {
    await _firestoreService.updateDocument(collection, userId, updates);
  }

  Future<void> deleteUser(String userId) async {
    await _firestoreService.deleteDocument(collection, userId);
  }

  Future<List<UserData>> getAllUsers() async {
    final docs = await _firestoreService.getCollection(collection);
    return docs.map((doc) => UserData.fromMap(doc)).toList();
  }

  Stream<List<UserData>> getUsersStream() {
    return _firestoreService.getCollectionStream(collection).map(
          (snapshot) => snapshot.docs
              .map((doc) => UserData.fromMap(doc.data() as Map<String, dynamic>))
              .toList(),
        );
  }
}

// Models
class UserData {
  final String? id;
  final String name;
  final String email;
  final DateTime createdAt;

  UserData({
    this.id,
    required this.name,
    required this.email,
    required this.createdAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'email': email,
      'createdAt': Timestamp.fromDate(createdAt),
    };
  }

  factory UserData.fromMap(Map<String, dynamic> map) {
    return UserData(
      id: map['id'],
      name: map['name'],
      email: map['email'],
      createdAt: (map['createdAt'] as Timestamp).toDate(),
    );
  }
}

enum BatchOperationType { set, update, delete }

class BatchOperation {
  final String collection;
  final String docId;
  final BatchOperationType type;
  final Map<String, dynamic>? data;

  BatchOperation({
    required this.collection,
    required this.docId,
    required this.type,
    this.data,
  });
}

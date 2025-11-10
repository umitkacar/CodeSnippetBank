import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

// Simple state provider
final counterProvider = StateProvider<int>((ref) => 0);

// Computed provider
final doubleCounterProvider = Provider<int>((ref) {
  final count = ref.watch(counterProvider);
  return count * 2;
});

// Async provider
final userProvider = FutureProvider<User>((ref) async {
  final response = await Dio().get('https://api.example.com/user');
  return User.fromJson(response.data);
});

// Stream provider
final messagesProvider = StreamProvider<List<Message>>((ref) {
  return MessageService().messagesStream();
});

// StateNotifier provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});

class AuthState {
  final User? user;
  final bool isLoading;
  final String? error;

  AuthState({
    this.user,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({
    User? user,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState());

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final user = await AuthService().login(email, password);
      state = state.copyWith(user: user, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }

  void logout() {
    state = AuthState();
  }
}

// ChangeNotifier provider
final cartProvider = ChangeNotifierProvider<CartNotifier>((ref) {
  return CartNotifier();
});

class CartNotifier extends ChangeNotifier {
  final List<CartItem> _items = [];

  List<CartItem> get items => _items;

  double get total => _items.fold(0, (sum, item) => sum + item.price * item.quantity);

  void addItem(CartItem item) {
    _items.add(item);
    notifyListeners();
  }

  void removeItem(String id) {
    _items.removeWhere((item) => item.id == id);
    notifyListeners();
  }

  void clear() {
    _items.clear();
    notifyListeners();
  }
}

// Family provider
final productProvider = FutureProvider.family<Product, String>((ref, id) async {
  final response = await Dio().get('https://api.example.com/products/$id');
  return Product.fromJson(response.data);
});

// AutoDispose provider
final searchProvider = FutureProvider.autoDispose.family<List<Product>, String>(
  (ref, query) async {
    final response = await Dio().get(
      'https://api.example.com/search',
      queryParameters: {'q': query},
    );
    return (response.data as List)
        .map((json) => Product.fromJson(json))
        .toList();
  },
);

// Provider with dependency
final apiClientProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: 'https://api.example.com',
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 3),
  ));

  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) {
      // Add auth token
      final token = ref.read(authProvider).user?.token;
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
      handler.next(options);
    },
  ));

  return dio;
});

// Models
class User {
  final String id;
  final String name;
  final String email;
  final String? token;

  User({required this.id, required this.name, required this.email, this.token});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      token: json['token'],
    );
  }
}

class Product {
  final String id;
  final String name;
  final double price;

  Product({required this.id, required this.name, required this.price});

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      name: json['name'],
      price: json['price'].toDouble(),
    );
  }
}

class CartItem {
  final String id;
  final String name;
  final double price;
  final int quantity;

  CartItem({
    required this.id,
    required this.name,
    required this.price,
    required this.quantity,
  });
}

class Message {
  final String id;
  final String text;
  final DateTime timestamp;

  Message({required this.id, required this.text, required this.timestamp});
}

// Service classes
class AuthService {
  Future<User> login(String email, String password) async {
    // Simulate API call
    await Future.delayed(const Duration(seconds: 1));
    return User(
      id: '1',
      name: 'Test User',
      email: email,
      token: 'sample_token',
    );
  }
}

class MessageService {
  Stream<List<Message>> messagesStream() {
    return Stream.periodic(const Duration(seconds: 1), (count) {
      return [
        Message(
          id: count.toString(),
          text: 'Message $count',
          timestamp: DateTime.now(),
        ),
      ];
    });
  }
}

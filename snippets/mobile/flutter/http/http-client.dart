import 'dart:convert';
import 'package:http/http.dart' as http;

class HttpClient {
  final String baseUrl;
  final Map<String, String> defaultHeaders;

  HttpClient({
    required this.baseUrl,
    this.defaultHeaders = const {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });

  Future<Map<String, String>> _getHeaders([Map<String, String>? headers]) async {
    final token = await getAuthToken();
    final allHeaders = Map<String, String>.from(defaultHeaders);

    if (token != null) {
      allHeaders['Authorization'] = 'Bearer $token';
    }

    if (headers != null) {
      allHeaders.addAll(headers);
    }

    return allHeaders;
  }

  Future<String?> getAuthToken() async {
    // Get token from secure storage
    return null;
  }

  Future<http.Response> get(
    String endpoint, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint').replace(
      queryParameters: queryParameters,
    );

    final response = await http.get(
      uri,
      headers: await _getHeaders(headers),
    );

    return _handleResponse(response);
  }

  Future<http.Response> post(
    String endpoint, {
    Map<String, String>? headers,
    dynamic body,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');

    final response = await http.post(
      uri,
      headers: await _getHeaders(headers),
      body: jsonEncode(body),
    );

    return _handleResponse(response);
  }

  Future<http.Response> put(
    String endpoint, {
    Map<String, String>? headers,
    dynamic body,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');

    final response = await http.put(
      uri,
      headers: await _getHeaders(headers),
      body: jsonEncode(body),
    );

    return _handleResponse(response);
  }

  Future<http.Response> patch(
    String endpoint, {
    Map<String, String>? headers,
    dynamic body,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');

    final response = await http.patch(
      uri,
      headers: await _getHeaders(headers),
      body: jsonEncode(body),
    );

    return _handleResponse(response);
  }

  Future<http.Response> delete(
    String endpoint, {
    Map<String, String>? headers,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');

    final response = await http.delete(
      uri,
      headers: await _getHeaders(headers),
    );

    return _handleResponse(response);
  }

  http.Response _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response;
    } else if (response.statusCode == 401) {
      throw UnauthorizedException('Unauthorized');
    } else if (response.statusCode == 404) {
      throw NotFoundException('Not found');
    } else {
      throw ApiException('Error: ${response.statusCode}');
    }
  }

  Future<T> getData<T>(
    String endpoint,
    T Function(dynamic json) fromJson, {
    Map<String, dynamic>? queryParameters,
  }) async {
    final response = await get(endpoint, queryParameters: queryParameters);
    final json = jsonDecode(response.body);
    return fromJson(json);
  }

  Future<List<T>> getList<T>(
    String endpoint,
    T Function(Map<String, dynamic> json) fromJson, {
    Map<String, dynamic>? queryParameters,
  }) async {
    final response = await get(endpoint, queryParameters: queryParameters);
    final List<dynamic> jsonList = jsonDecode(response.body);
    return jsonList.map((json) => fromJson(json)).toList();
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}

class UnauthorizedException extends ApiException {
  UnauthorizedException(String message) : super(message);
}

class NotFoundException extends ApiException {
  NotFoundException(String message) : super(message);
}

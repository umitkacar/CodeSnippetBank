import 'package:flutter/services.dart';

class NativeMethodChannel {
  static const MethodChannel _channel = MethodChannel('com.example.app/native');

  // Call native method
  static Future<String?> callNativeMethod(String method,
      [Map<String, dynamic>? arguments]) async {
    try {
      final result = await _channel.invokeMethod<String>(method, arguments);
      return result;
    } on PlatformException catch (e) {
      print('Error: ${e.message}');
      return null;
    }
  }

  // Get device info
  static Future<Map<String, dynamic>?> getDeviceInfo() async {
    try {
      final result = await _channel.invokeMethod<Map>('getDeviceInfo');
      return result?.cast<String, dynamic>();
    } on PlatformException catch (e) {
      print('Error: ${e.message}');
      return null;
    }
  }

  // Get battery level
  static Future<int?> getBatteryLevel() async {
    try {
      return await _channel.invokeMethod<int>('getBatteryLevel');
    } on PlatformException catch (e) {
      print('Error: ${e.message}');
      return null;
    }
  }

  // Open native settings
  static Future<void> openSettings() async {
    try {
      await _channel.invokeMethod('openSettings');
    } on PlatformException catch (e) {
      print('Error: ${e.message}');
    }
  }

  // Share content
  static Future<bool> shareText(String text) async {
    try {
      final result = await _channel.invokeMethod<bool>('shareText', {
        'text': text,
      });
      return result ?? false;
    } on PlatformException catch (e) {
      print('Error: ${e.message}');
      return false;
    }
  }

  // Vibrate device
  static Future<void> vibrate({int duration = 500}) async {
    try {
      await _channel.invokeMethod('vibrate', {'duration': duration});
    } on PlatformException catch (e) {
      print('Error: ${e.message}');
    }
  }
}

// Event Channel for streaming data
class NativeEventChannel {
  static const EventChannel _eventChannel =
      EventChannel('com.example.app/events');

  static Stream<dynamic> get eventStream {
    return _eventChannel.receiveBroadcastStream();
  }

  static Stream<int> get batteryLevelStream {
    return eventStream.map((event) => event as int);
  }
}

// Basic Message Channel
class NativeBasicMessageChannel {
  static const BasicMessageChannel<String> _channel =
      BasicMessageChannel<String>(
    'com.example.app/messages',
    StringCodec(),
  );

  static Future<String?> sendMessage(String message) async {
    return await _channel.send(message);
  }

  static void setMessageHandler(
    Future<String> Function(String? message)? handler,
  ) {
    _channel.setMessageHandler(handler);
  }
}

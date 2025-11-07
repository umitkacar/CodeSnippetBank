import 'package:flutter/services.dart';

class BatteryChannel {
  static const MethodChannel _channel = MethodChannel('battery');

  static Future<int?> getBatteryLevel() async {
    try {
      final int batteryLevel = await _channel.invokeMethod('getBatteryLevel');
      return batteryLevel;
    } on PlatformException catch (e) {
      print('Failed to get battery level: ${e.message}');
      return null;
    }
  }

  static Future<bool> isCharging() async {
    try {
      final bool charging = await _channel.invokeMethod('isCharging');
      return charging;
    } on PlatformException catch (e) {
      print('Failed to check charging status: ${e.message}');
      return false;
    }
  }

  static Stream<int> get batteryStream {
    const EventChannel eventChannel = EventChannel('batteryStream');
    return eventChannel.receiveBroadcastStream().map((level) => level as int);
  }
}

import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

export class LocalNotificationService {
  static async scheduleImmediateNotification(
    title: string,
    body: string,
    data?: any
  ): Promise<string> {
    return await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data,
        sound: true,
        badge: 1,
      },
      trigger: null, // immediate
    });
  }

  static async scheduleDelayedNotification(
    title: string,
    body: string,
    seconds: number,
    data?: any
  ): Promise<string> {
    return await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data,
      },
      trigger: {
        seconds,
      },
    });
  }

  static async scheduleWeeklyNotification(
    title: string,
    body: string,
    weekday: number, // 1-7 (Sunday = 1)
    hour: number,
    minute: number
  ): Promise<string> {
    return await Notifications.scheduleNotificationAsync({
      content: { title, body },
      trigger: {
        weekday,
        hour,
        minute,
        repeats: true,
      },
    });
  }

  static async scheduleReminderNotification(
    title: string,
    body: string,
    date: Date
  ): Promise<string> {
    return await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        sound: true,
      },
      trigger: date,
    });
  }

  static async createNotificationChannel(
    id: string,
    name: string,
    importance: Notifications.AndroidImportance = Notifications.AndroidImportance.HIGH
  ): Promise<void> {
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync(id, {
        name,
        importance,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
        sound: 'default',
        enableVibrate: true,
      });
    }
  }

  static async getPermissions(): Promise<boolean> {
    const { status } = await Notifications.getPermissionsAsync();
    return status === 'granted';
  }

  static async requestPermissions(): Promise<boolean> {
    const { status } = await Notifications.requestPermissionsAsync();
    return status === 'granted';
  }
}

// Notification action buttons
export const addNotificationActions = async () => {
  await Notifications.setNotificationCategoryAsync('message', [
    {
      identifier: 'reply',
      buttonTitle: 'Reply',
      options: {
        opensAppToForeground: true,
      },
    },
    {
      identifier: 'dismiss',
      buttonTitle: 'Dismiss',
      options: {
        opensAppToForeground: false,
      },
    },
  ]);
};

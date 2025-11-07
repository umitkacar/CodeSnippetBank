import 'package:hive/hive.dart';
import 'package:hive_flutter/hive_flutter.dart';

part 'hive-database.g.dart';

@HiveType(typeId: 0)
class User extends HiveObject {
  @HiveField(0)
  late String id;

  @HiveField(1)
  late String name;

  @HiveField(2)
  late String email;

  @HiveField(3)
  late DateTime createdAt;

  User({
    required this.id,
    required this.name,
    required this.email,
    required this.createdAt,
  });
}

@HiveType(typeId: 1)
class Task extends HiveObject {
  @HiveField(0)
  late String id;

  @HiveField(1)
  late String title;

  @HiveField(2)
  late bool isCompleted;

  @HiveField(3)
  late DateTime createdAt;

  Task({
    required this.id,
    required this.title,
    this.isCompleted = false,
    required this.createdAt,
  });
}

class HiveService {
  static const String userBoxName = 'users';
  static const String taskBoxName = 'tasks';
  static const String settingsBoxName = 'settings';

  static Future<void> init() async {
    await Hive.initFlutter();

    Hive.registerAdapter(UserAdapter());
    Hive.registerAdapter(TaskAdapter());

    await Hive.openBox<User>(userBoxName);
    await Hive.openBox<Task>(taskBoxName);
    await Hive.openBox(settingsBoxName);
  }

  static Box<User> getUserBox() => Hive.box<User>(userBoxName);
  static Box<Task> getTaskBox() => Hive.box<Task>(taskBoxName);
  static Box getSettingsBox() => Hive.box(settingsBoxName);

  // User operations
  static Future<void> saveUser(User user) async {
    final box = getUserBox();
    await box.put(user.id, user);
  }

  static User? getUser(String id) {
    final box = getUserBox();
    return box.get(id);
  }

  static List<User> getAllUsers() {
    final box = getUserBox();
    return box.values.toList();
  }

  static Future<void> deleteUser(String id) async {
    final box = getUserBox();
    await box.delete(id);
  }

  static Future<void> updateUser(String id, Map<String, dynamic> updates) async {
    final user = getUser(id);
    if (user != null) {
      if (updates.containsKey('name')) user.name = updates['name'];
      if (updates.containsKey('email')) user.email = updates['email'];
      await user.save();
    }
  }

  // Task operations
  static Future<void> saveTask(Task task) async {
    final box = getTaskBox();
    await box.put(task.id, task);
  }

  static Task? getTask(String id) {
    final box = getTaskBox();
    return box.get(id);
  }

  static List<Task> getAllTasks() {
    final box = getTaskBox();
    return box.values.toList();
  }

  static List<Task> getCompletedTasks() {
    final box = getTaskBox();
    return box.values.where((task) => task.isCompleted).toList();
  }

  static List<Task> getPendingTasks() {
    final box = getTaskBox();
    return box.values.where((task) => !task.isCompleted).toList();
  }

  static Future<void> deleteTask(String id) async {
    final box = getTaskBox();
    await box.delete(id);
  }

  static Future<void> toggleTaskCompletion(String id) async {
    final task = getTask(id);
    if (task != null) {
      task.isCompleted = !task.isCompleted;
      await task.save();
    }
  }

  // Settings operations
  static Future<void> saveSetting(String key, dynamic value) async {
    final box = getSettingsBox();
    await box.put(key, value);
  }

  static T? getSetting<T>(String key) {
    final box = getSettingsBox();
    return box.get(key) as T?;
  }

  static Future<void> deleteSetting(String key) async {
    final box = getSettingsBox();
    await box.delete(key);
  }

  // Clear all data
  static Future<void> clearAll() async {
    await getUserBox().clear();
    await getTaskBox().clear();
    await getSettingsBox().clear();
  }

  // Watch for changes
  static Stream<BoxEvent> watchUsers() {
    return getUserBox().watch();
  }

  static Stream<BoxEvent> watchTasks() {
    return getTaskBox().watch();
  }
}

// Usage in widget
class HiveExample extends StatelessWidget {
  const HiveExample({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder(
      valueListenable: HiveService.getTaskBox().listenable(),
      builder: (context, Box<Task> box, _) {
        final tasks = box.values.toList();

        return ListView.builder(
          itemCount: tasks.length,
          itemBuilder: (context, index) {
            final task = tasks[index];
            return ListTile(
              title: Text(task.title),
              trailing: Checkbox(
                value: task.isCompleted,
                onChanged: (_) => HiveService.toggleTaskCompletion(task.id),
              ),
            );
          },
        );
      },
    );
  }
}

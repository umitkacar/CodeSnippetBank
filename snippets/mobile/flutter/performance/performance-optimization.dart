import 'package:flutter/material.dart';

// Const constructors for better performance
class ConstWidgetExample extends StatelessWidget {
  const ConstWidgetExample({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Column(
      children: [
        Text('Use const constructors'),
        Icon(Icons.check),
        SizedBox(height: 16),
      ],
    );
  }
}

// RepaintBoundary to isolate repaints
class RepaintBoundaryExample extends StatelessWidget {
  const RepaintBoundaryExample({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      child: Container(
        width: 200,
        height: 200,
        color: Colors.blue,
      ),
    );
  }
}

// ListView.builder for large lists
class OptimizedListView extends StatelessWidget {
  final List<String> items;

  const OptimizedListView({Key? key, required this.items}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        return ListTile(
          title: Text(items[index]),
        );
      },
      cacheExtent: 100, // Preload items
    );
  }
}

// AutomaticKeepAliveClientMixin to preserve state
class KeepAliveExample extends StatefulWidget {
  const KeepAliveExample({Key? key}) : super(key: key);

  @override
  State<KeepAliveExample> createState() => _KeepAliveExampleState();
}

class _KeepAliveExampleState extends State<KeepAliveExample>
    with AutomaticKeepAliveClientMixin {
  int _counter = 0;

  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context); // Must call super.build
    return Column(
      children: [
        Text('Counter: $_counter'),
        ElevatedButton(
          onPressed: () => setState(() => _counter++),
          child: const Text('Increment'),
        ),
      ],
    );
  }
}

// Image caching
class CachedImageExample extends StatelessWidget {
  final String imageUrl;

  const CachedImageExample({Key? key, required this.imageUrl})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Image.network(
      imageUrl,
      cacheWidth: 400,
      cacheHeight: 400,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return const CircularProgressIndicator();
      },
    );
  }
}

// Selective rebuilds with ValueListenableBuilder
class ValueListenableExample extends StatefulWidget {
  const ValueListenableExample({Key? key}) : super(key: key);

  @override
  State<ValueListenableExample> createState() =>
      _ValueListenableExampleState();
}

class _ValueListenableExampleState extends State<ValueListenableExample> {
  final ValueNotifier<int> _counter = ValueNotifier<int>(0);

  @override
  void dispose() {
    _counter.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Text('This widget does not rebuild'),
        ValueListenableBuilder<int>(
          valueListenable: _counter,
          builder: (context, value, child) {
            return Text('Counter: $value');
          },
        ),
        ElevatedButton(
          onPressed: () => _counter.value++,
          child: const Text('Increment'),
        ),
      ],
    );
  }
}

// FutureBuilder optimization
class OptimizedFutureBuilder extends StatefulWidget {
  const OptimizedFutureBuilder({Key? key}) : super(key: key);

  @override
  State<OptimizedFutureBuilder> createState() =>
      _OptimizedFutureBuilderState();
}

class _OptimizedFutureBuilderState extends State<OptimizedFutureBuilder> {
  late final Future<String> _future;

  @override
  void initState() {
    super.initState();
    _future = fetchData(); // Initialize once
  }

  Future<String> fetchData() async {
    await Future.delayed(const Duration(seconds: 2));
    return 'Data loaded';
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const CircularProgressIndicator();
        }
        if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        }
        return Text(snapshot.data ?? '');
      },
    );
  }
}

// Keys for list performance
class KeyedList extends StatelessWidget {
  final List<Item> items;

  const KeyedList({Key? key, required this.items}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return ListTile(
          key: ValueKey(item.id),
          title: Text(item.title),
        );
      },
    );
  }
}

class Item {
  final String id;
  final String title;

  Item({required this.id, required this.title});
}

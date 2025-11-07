import 'package:flutter/material.dart';

class CustomListTile extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;

  const CustomListTile({
    Key? key,
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: leading,
      title: Text(title,
 style: const TextStyle(fontWeight: FontWeight.w500)),
      subtitle: subtitle != null ? Text(subtitle!) : null,
      trailing: trailing ?? const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
}

class DismissibleListItem extends StatelessWidget {
  final String itemKey;
  final Widget child;
  final VoidCallback onDismissed;

  const DismissibleListItem({
    Key? key,
    required this.itemKey,
    required this.child,
    required this.onDismissed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: Key(itemKey),
      background: Container(
        color: Colors.red,
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      direction: DismissDirection.endToStart,
      onDismissed: (direction) => onDismissed(),
      child: child,
    );
  }
}

class ReorderableListExample extends StatefulWidget {
  const ReorderableListExample({Key? key}) : super(key: key);

  @override
  State<ReorderableListExample> createState() =>
      _ReorderableListExampleState();
}

class _ReorderableListExampleState extends State<ReorderableListExample> {
  final List<String> _items = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];

  @override
  Widget build(BuildContext context) {
    return ReorderableListView(
      onReorder: (oldIndex, newIndex) {
        setState(() {
          if (newIndex > oldIndex) {
            newIndex -= 1;
          }
          final item = _items.removeAt(oldIndex);
          _items.insert(newIndex, item);
        });
      },
      children: _items.map((item) {
        return ListTile(
          key: ValueKey(item),
          title: Text(item),
          trailing: const Icon(Icons.drag_handle),
        );
      }).toList(),
    );
  }
}

class SliverListExample extends StatelessWidget {
  final List<String> items;

  const SliverListExample({Key? key, required this.items}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverAppBar(
          expandedHeight: 200,
          flexibleSpace: FlexibleSpaceBar(
            title: const Text('Sliver List'),
            background: Image.network(
              'https://picsum.photos/400/200',
              fit: BoxFit.cover,
            ),
          ),
        ),
        SliverList(
          delegate: SliverChildBuilderDelegate(
            (context, index) => ListTile(
              title: Text(items[index]),
            ),
            childCount: items.length,
          ),
        ),
      ],
    );
  }
}

class GridViewExample extends StatelessWidget {
  final List<String> items;

  const GridViewExample({Key? key, required this.items}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
        childAspectRatio: 1,
      ),
      itemCount: items.length,
      padding: const EdgeInsets.all(10),
      itemBuilder: (context, index) {
        return Card(
          child: Center(child: Text(items[index])),
        );
      },
    );
  }
}

class ExpansionTileExample extends StatelessWidget {
  const ExpansionTileExample({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ExpansionTile(
      leading: const Icon(Icons.folder),
      title: const Text('Folder'),
      children: [
        ListTile(
          leading: const Icon(Icons.insert_drive_file),
          title: const Text('File 1'),
        ),
        ListTile(
          leading: const Icon(Icons.insert_drive_file),
          title: const Text('File 2'),
        ),
      ],
    );
  }
}

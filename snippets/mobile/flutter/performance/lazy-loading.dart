import 'package:flutter/material.dart';

class LazyLoadingList extends StatefulWidget {
  const LazyLoadingList({Key? key}) : super(key: key);

  @override
  State<LazyLoadingList> createState() => _LazyLoadingListState();
}

class _LazyLoadingListState extends State<LazyLoadingList> {
  final List<String> _items = [];
  bool _isLoading = false;
  int _page = 1;
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _loadMore();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels ==
        _scrollController.position.maxScrollExtent) {
      _loadMore();
    }
  }

  Future<void> _loadMore() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
    });

    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));

    final newItems = List.generate(20, (index) {
      return 'Item ${(_page - 1) * 20 + index + 1}';
    });

    setState(() {
      _items.addAll(newItems);
      _page++;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: _scrollController,
      itemCount: _items.length + (_isLoading ? 1 : 0),
      itemBuilder: (context, index) {
        if (index == _items.length) {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(16.0),
              child: CircularProgressIndicator(),
            ),
          );
        }

        return ListTile(
          title: Text(_items[index]),
        );
      },
    );
  }
}

class PaginatedList extends StatefulWidget {
  const PaginatedList({Key? key}) : super(key: key);

  @override
  State<PaginatedList> createState() => _PaginatedListState();
}

class _PaginatedListState extends State<PaginatedList> {
  final List<String> _items = [];
  bool _isLoading = false;
  bool _hasMore = true;
  int _page = 1;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    if (_isLoading || !_hasMore) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 1));

      final newItems = List.generate(20, (index) {
        return 'Item ${(_page - 1) * 20 + index + 1}';
      });

      setState(() {
        _items.addAll(newItems);
        _page++;
        _hasMore = newItems.length == 20;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      onNotification: (ScrollNotification scrollInfo) {
        if (!_isLoading &&
            _hasMore &&
            scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
          _loadData();
        }
        return false;
      },
      child: ListView.builder(
        itemCount: _items.length + (_isLoading ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == _items.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: CircularProgressIndicator(),
              ),
            );
          }

          return ListTile(
            title: Text(_items[index]),
          );
        },
      ),
    );
  }
}

class InfiniteScrollList extends StatelessWidget {
  final Future<List<String>> Function(int page) loadData;

  const InfiniteScrollList({Key? key, required this.loadData})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const PaginatedList();
  }
}

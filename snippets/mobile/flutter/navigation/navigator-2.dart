import 'package:flutter/material.dart';

// Navigator 2.0 implementation
class AppRouterDelegate extends RouterDelegate<AppRoute>
    with ChangeNotifier, PopNavigatorRouterDelegateMixin<AppRoute> {
  @override
  final GlobalKey<NavigatorState> navigatorKey;

  final List<AppRoute> _routeStack = [AppRoute.home()];

  AppRouterDelegate() : navigatorKey = GlobalKey<NavigatorState>();

  AppRoute get currentConfiguration => _routeStack.last;

  @override
  Widget build(BuildContext context) {
    return Navigator(
      key: navigatorKey,
      pages: _routeStack.map((route) => route.toPage()).toList(),
      onPopPage: (route, result) {
        if (!route.didPop(result)) {
          return false;
        }
        if (_routeStack.length > 1) {
          _routeStack.removeLast();
          notifyListeners();
        }
        return true;
      },
    );
  }

  @override
  Future<void> setNewRoutePath(AppRoute configuration) async {
    _routeStack
      ..clear()
      ..add(configuration);
    notifyListeners();
  }

  void push(AppRoute route) {
    _routeStack.add(route);
    notifyListeners();
  }

  void pop() {
    if (_routeStack.length > 1) {
      _routeStack.removeLast();
      notifyListeners();
    }
  }
}

class AppRouteInformationParser extends RouteInformationParser<AppRoute> {
  @override
  Future<AppRoute> parseRouteInformation(
      RouteInformation routeInformation) async {
    final uri = Uri.parse(routeInformation.location ?? '/');

    if (uri.pathSegments.isEmpty) {
      return AppRoute.home();
    }

    if (uri.pathSegments.length == 2) {
      if (uri.pathSegments[0] == 'details') {
        final id = uri.pathSegments[1];
        return AppRoute.details(id);
      }
    }

    if (uri.pathSegments[0] == 'profile') {
      return AppRoute.profile();
    }

    return AppRoute.home();
  }

  @override
  RouteInformation? restoreRouteInformation(AppRoute configuration) {
    if (configuration is HomeRoute) {
      return const RouteInformation(location: '/');
    }
    if (configuration is DetailsRoute) {
      return RouteInformation(location: '/details/${configuration.id}');
    }
    if (configuration is ProfileRoute) {
      return const RouteInformation(location: '/profile');
    }
    return null;
  }
}

// Route configuration
abstract class AppRoute {
  factory AppRoute.home() = HomeRoute;
  factory AppRoute.details(String id) = DetailsRoute;
  factory AppRoute.profile() = ProfileRoute;

  Page toPage();
}

class HomeRoute implements AppRoute {
  @override
  Page toPage() {
    return const MaterialPage(
      key: ValueKey('home'),
      child: HomeScreen(),
    );
  }
}

class DetailsRoute implements AppRoute {
  final String id;

  DetailsRoute(this.id);

  @override
  Page toPage() {
    return MaterialPage(
      key: ValueKey('details-$id'),
      child: DetailsScreen(id: id),
    );
  }
}

class ProfileRoute implements AppRoute {
  @override
  Page toPage() {
    return const MaterialPage(
      key: ValueKey('profile'),
      child: ProfileScreen(),
    );
  }
}

// Screens
class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Home')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () {
                // Navigate using router delegate
              },
              child: const Text('Go to Details'),
            ),
          ],
        ),
      ),
    );
  }
}

class DetailsScreen extends StatelessWidget {
  final String id;

  const DetailsScreen({Key? key, required this.id}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Details $id')),
      body: Center(child: Text('Details for item $id')),
    );
  }
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: const Center(child: Text('Profile Screen')),
    );
  }
}

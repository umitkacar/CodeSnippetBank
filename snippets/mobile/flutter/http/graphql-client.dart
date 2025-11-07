import 'package:graphql_flutter/graphql_flutter.dart';

class GraphQLService {
  late final GraphQLClient _client;

  GraphQLService({required String endpoint}) {
    final HttpLink httpLink = HttpLink(endpoint);

    final AuthLink authLink = AuthLink(
      getToken: () async => 'Bearer ${await getAuthToken()}',
    );

    final Link link = authLink.concat(httpLink);

    _client = GraphQLClient(
      link: link,
      cache: GraphQLCache(store: InMemoryStore()),
    );
  }

  Future<String?> getAuthToken() async {
    // Get token from secure storage
    return null;
  }

  Future<QueryResult> query(String queryString,
      {Map<String, dynamic>? variables}) async {
    final options = QueryOptions(
      document: gql(queryString),
      variables: variables ?? {},
    );

    return await _client.query(options);
  }

  Future<QueryResult> mutate(String mutationString,
      {Map<String, dynamic>? variables}) async {
    final options = MutationOptions(
      document: gql(mutationString),
      variables: variables ?? {},
    );

    return await _client.mutate(options);
  }

  Stream<QueryResult> subscribe(String subscriptionString,
      {Map<String, dynamic>? variables}) {
    final options = SubscriptionOptions(
      document: gql(subscriptionString),
      variables: variables ?? {},
    );

    return _client.subscribe(options);
  }
}

// User GraphQL service
class UserGraphQLService {
  final GraphQLService _graphQLService;

  UserGraphQLService(this._graphQLService);

  Future<List<User>> getUsers() async {
    const query = '''
      query GetUsers {
        users {
          id
          name
          email
        }
      }
    ''';

    final result = await _graphQLService.query(query);

    if (result.hasException) {
      throw result.exception!;
    }

    final List users = result.data?['users'] ?? [];
    return users.map((json) => User.fromJson(json)).toList();
  }

  Future<User> getUserById(String id) async {
    const query = '''
      query GetUser(\$id: ID!) {
        user(id: \$id) {
          id
          name
          email
        }
      }
    ''';

    final result = await _graphQLService.query(
      query,
      variables: {'id': id},
    );

    if (result.hasException) {
      throw result.exception!;
    }

    return User.fromJson(result.data?['user']);
  }

  Future<User> createUser(String name, String email) async {
    const mutation = '''
      mutation CreateUser(\$name: String!, \$email: String!) {
        createUser(name: \$name, email: \$email) {
          id
          name
          email
        }
      }
    ''';

    final result = await _graphQLService.mutate(
      mutation,
      variables: {'name': name, 'email': email},
    );

    if (result.hasException) {
      throw result.exception!;
    }

    return User.fromJson(result.data?['createUser']);
  }

  Future<void> deleteUser(String id) async {
    const mutation = '''
      mutation DeleteUser(\$id: ID!) {
        deleteUser(id: \$id) {
          success
        }
      }
    ''';

    final result = await _graphQLService.mutate(
      mutation,
      variables: {'id': id},
    );

    if (result.hasException) {
      throw result.exception!;
    }
  }

  Stream<User> subscribeToUserUpdates(String id) {
    const subscription = '''
      subscription OnUserUpdated(\$id: ID!) {
        userUpdated(id: \$id) {
          id
          name
          email
        }
      }
    ''';

    return _graphQLService
        .subscribe(subscription, variables: {'id': id})
        .map((result) => User.fromJson(result.data?['userUpdated']));
  }
}

class User {
  final String id;
  final String name;
  final String email;

  User({required this.id, required this.name, required this.email});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
    );
  }
}

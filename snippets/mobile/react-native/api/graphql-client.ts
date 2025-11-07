import { ApolloClient, InMemoryCache, HttpLink, ApolloLink, from, gql } from '@apollo/client';
import { onError } from '@apollo/client/link/error';
import { setContext } from '@apollo/client/link/context';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Create HTTP link
const httpLink = new HttpLink({
  uri: 'https://api.example.com/graphql',
});

// Auth link
const authLink = setContext(async (_, { headers }) => {
  const token = await AsyncStorage.getItem('auth_token');
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  };
});

// Error link
const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`
      );
    });
  }
  if (networkError) {
    console.error(`[Network error]: ${networkError}`);
  }
});

// Create Apollo Client
export const apolloClient = new ApolloClient({
  link: from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network',
    },
  },
});

// GraphQL Queries
export const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
      email
      avatar
    }
  }
`;

export const GET_POSTS = gql`
  query GetPosts($limit: Int, $offset: Int) {
    posts(limit: $limit, offset: $offset) {
      id
      title
      content
      author {
        id
        name
      }
      createdAt
    }
  }
`;

// GraphQL Mutations
export const CREATE_POST = gql`
  mutation CreatePost($input: CreatePostInput!) {
    createPost(input: $input) {
      id
      title
      content
      createdAt
    }
  }
`;

export const UPDATE_USER = gql`
  mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
    updateUser(id: $id, input: $input) {
      id
      name
      email
    }
  }
`;

export const DELETE_POST = gql`
  mutation DeletePost($id: ID!) {
    deletePost(id: $id) {
      success
      message
    }
  }
`;

// GraphQL Subscriptions
export const POST_ADDED = gql`
  subscription OnPostAdded {
    postAdded {
      id
      title
      content
      author {
        id
        name
      }
    }
  }
`;

// React hooks for GraphQL
import { useQuery, useMutation, useSubscription } from '@apollo/client';

export const useGetUser = (id: string) => {
  return useQuery(GET_USER, {
    variables: { id },
    skip: !id,
  });
};

export const useGetPosts = (limit: number = 10, offset: number = 0) => {
  return useQuery(GET_POSTS, {
    variables: { limit, offset },
  });
};

export const useCreatePost = () => {
  return useMutation(CREATE_POST, {
    refetchQueries: [{ query: GET_POSTS }],
    awaitRefetchQueries: true,
  });
};

export const useUpdateUser = () => {
  return useMutation(UPDATE_USER, {
    update(cache, { data: { updateUser } }) {
      cache.modify({
        id: cache.identify(updateUser),
        fields: {
          name: () => updateUser.name,
          email: () => updateUser.email,
        },
      });
    },
  });
};

export const usePostSubscription = () => {
  return useSubscription(POST_ADDED);
};

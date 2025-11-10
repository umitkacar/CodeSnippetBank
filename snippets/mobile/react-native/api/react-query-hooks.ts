import { useQuery, useMutation, useQueryClient, UseQueryOptions, useInfiniteQuery } from '@tanstack/react-query';
import { apiClient } from './api-client';

interface User {
  id: string;
  name: string;
  email: string;
}

interface Post {
  id: string;
  title: string;
  content: string;
  userId: string;
}

// Fetch users
export const useUsers = (options?: UseQueryOptions<User[]>) => {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: () => apiClient.get<User[]>('/users'),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
};

// Fetch user by ID
export const useUser = (userId: string, options?: UseQueryOptions<User>) => {
  return useQuery<User>({
    queryKey: ['user', userId],
    queryFn: () => apiClient.get<User>(`/users/${userId}`),
    enabled: !!userId,
    ...options,
  });
};

// Fetch posts with pagination
export const usePosts = (page: number = 1, limit: number = 10) => {
  return useQuery<{ posts: Post[]; total: number }>({
    queryKey: ['posts', page, limit],
    queryFn: () => apiClient.get(`/posts?page=${page}&limit=${limit}`),
    keepPreviousData: true,
  });
};

// Create user mutation
export const useCreateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: Omit<User, 'id'>) =>
      apiClient.post<User>('/users', userData),
    onSuccess: (newUser) => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.setQueryData(['user', newUser.id], newUser);
    },
  });
};

// Update user mutation
export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<User> }) =>
      apiClient.patch<User>(`/users/${id}`, data),
    onSuccess: (updatedUser, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.setQueryData(['user', variables.id], updatedUser);
    },
  });
};

// Delete user mutation
export const useDeleteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => apiClient.delete(`/users/${userId}`),
    onSuccess: (_, deletedUserId) => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.removeQueries({ queryKey: ['user', deletedUserId] });
    },
  });
};

// Infinite query for posts
export const useInfinitePosts = () => {
  return useInfiniteQuery({
    queryKey: ['posts', 'infinite'],
    queryFn: ({ pageParam = 1 }) =>
      apiClient.get<{ posts: Post[]; nextPage: number | null }>(
        `/posts?page=${pageParam}`
      ),
    getNextPageParam: (lastPage) => lastPage.nextPage,
  });
};

// Optimistic update example
export const useOptimisticUpdate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<User> }) =>
      apiClient.patch<User>(`/users/${id}`, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ['user', id] });
      const previousUser = queryClient.getQueryData(['user', id]);

      queryClient.setQueryData(['user', id], (old: User | undefined) => ({
        ...old!,
        ...data,
      }));

      return { previousUser };
    },
    onError: (err, { id }, context) => {
      queryClient.setQueryData(['user', id], context?.previousUser);
    },
    onSettled: (data, error, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['user', id] });
    },
  });
};

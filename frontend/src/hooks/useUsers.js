import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { usersApi } from '../api/users';

export const userKeys = {
  all: ['users'],
  details: () => [...userKeys.all, 'detail'],
  detail: (id) => [...userKeys.details(), id],
  recipes: (id) => [...userKeys.detail(id), 'recipes'],
  followers: (id) => [...userKeys.detail(id), 'followers'],
  following: (id) => [...userKeys.detail(id), 'following'],
};

export function useUser(id) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => usersApi.get(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useUserRecipes(userId) {
  return useQuery({
    queryKey: userKeys.recipes(userId),
    queryFn: () => usersApi.getRecipes(userId),
    enabled: !!userId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFollowers(userId) {
  return useInfiniteQuery({
    queryKey: userKeys.followers(userId),
    queryFn: ({ pageParam = 1 }) => usersApi.getFollowers(userId, pageParam),
    getNextPageParam: (lastPage) => {
      if (lastPage.next) {
        try {
          const url = new URL(lastPage.next);
          return url.searchParams.get('page');
        } catch {
          return undefined;
        }
      }
      return undefined;
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFollowing(userId) {
  return useInfiniteQuery({
    queryKey: userKeys.following(userId),
    queryFn: ({ pageParam = 1 }) => usersApi.getFollowing(userId, pageParam),
    getNextPageParam: (lastPage) => {
      if (lastPage.next) {
        try {
          const url = new URL(lastPage.next);
          return url.searchParams.get('page');
        } catch {
          return undefined;
        }
      }
      return undefined;
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFollowUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: usersApi.follow,
    onSuccess: (_, userId) => {
      queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
      queryClient.invalidateQueries({ queryKey: userKeys.followers(userId) });
      queryClient.invalidateQueries({ queryKey: userKeys.following(userId) });
    },
  });
}

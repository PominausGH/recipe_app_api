import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recipesApi } from '../api/recipes';

export const recipeKeys = {
  all: ['recipes'],
  lists: () => [...recipeKeys.all, 'list'],
  list: (filters) => [...recipeKeys.lists(), filters],
  details: () => [...recipeKeys.all, 'detail'],
  detail: (id) => [...recipeKeys.details(), id],
  comments: (id) => [...recipeKeys.detail(id), 'comments'],
  myRecipes: () => [...recipeKeys.all, 'my'],
};

export function useRecipes(filters = {}) {
  return useQuery({
    queryKey: recipeKeys.list(filters),
    queryFn: () => recipesApi.list(filters),
    staleTime: 5 * 60 * 1000,
  });
}

export function useRecipe(id) {
  return useQuery({
    queryKey: recipeKeys.detail(id),
    queryFn: () => recipesApi.get(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000,
  });
}

export function useRecipeComments(id) {
  return useQuery({
    queryKey: recipeKeys.comments(id),
    queryFn: () => recipesApi.getComments(id),
    enabled: !!id,
  });
}

export function useCreateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: recipesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
    },
  });
}

export function useUpdateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => recipesApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
    },
  });
}

export function useDeleteRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: recipesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
    },
  });
}

export function useRateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, score, review }) => recipesApi.rate(id, score, review),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.detail(id) });
    },
  });
}

export function useToggleFavorite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: recipesApi.toggleFavorite,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.detail(id) });
    },
  });
}

export function useAddComment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ recipeId, text, parentId }) => recipesApi.addComment(recipeId, text, parentId),
    onSuccess: (_, { recipeId }) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.comments(recipeId) });
    },
  });
}

export function useUploadRecipeImage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, file }) => recipesApi.uploadImage(id, file),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.detail(id) });
    },
  });
}

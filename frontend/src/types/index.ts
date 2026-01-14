// User types
export interface User {
  id: number;
  email: string;
  name: string;
  bio?: string;
  profile_photo?: string;
  is_verified: boolean;
  is_private: boolean;
  follower_count?: number;
  following_count?: number;
  recipe_count?: number;
}

export interface AuthUser extends User {
  tokens: {
    access: string;
    refresh: string;
  };
}

// Recipe types
export interface Ingredient {
  id: number;
  name: string;
  quantity: string;
  unit: string;
}

export interface Recipe {
  id: number;
  title: string;
  description?: string;
  instructions?: string;
  prep_time?: number;
  cook_time?: number;
  servings?: number;
  difficulty?: "easy" | "medium" | "hard";
  image?: string;
  is_published: boolean;
  created_at: string;
  updated_at: string;
  author: User;
  ingredients?: Ingredient[];
  categories?: Category[];
  tags?: Tag[];
  average_rating?: number;
  rating_count: number;
  is_favorited?: boolean;
}

export interface Category {
  id: number;
  name: string;
  parent?: number;
}

export interface Tag {
  id: number;
  name: string;
}

// Interaction types
export interface Rating {
  id: number;
  recipe: number;
  user: User;
  score: number;
  review?: string;
  created_at: string;
}

export interface Comment {
  id: number;
  recipe: number;
  user: User;
  content: string;
  parent?: number;
  replies?: Comment[];
  created_at: string;
}

export type FollowState = "not_following" | "following" | "requested";

// API response types
export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}

// Form types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  name: string;
  password: string;
  password_confirm: string;
}

export interface RecipeFormData {
  title: string;
  description?: string;
  instructions?: string;
  prep_time?: number;
  cook_time?: number;
  servings?: number;
  difficulty?: "easy" | "medium" | "hard";
  ingredients?: Omit<Ingredient, "id">[];
  categories?: number[];
  tags?: number[];
}

# Social Features Frontend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add user profiles and following functionality to the Recipe App frontend.

**Architecture:** Create a users API module and hooks following existing patterns. Build UserLink, FollowButton, and FollowersModal components. Add UserProfilePage displaying user info, follow stats, and recipes.

**Tech Stack:** React, React Router, TanStack Query, Tailwind CSS, Heroicons, Axios

---

## Phase 1: API & Hooks

### Task 1.1: Create Users API Module

**Files:**
- Create: `frontend/src/api/users.js`

**Step 1: Create the users API module**

```javascript
import client from './client';

export const usersApi = {
  async get(id) {
    const response = await client.get(`/interaction/users/${id}/`);
    return response.data;
  },

  async getRecipes(userId, params = {}) {
    const response = await client.get('/recipe/recipes/', {
      params: { ...params, author: userId },
    });
    return response.data;
  },

  async follow(userId) {
    const response = await client.post(`/interaction/users/${userId}/follow/`);
    return response.data;
  },

  async getFollowers(userId, page = 1) {
    const response = await client.get(`/interaction/users/${userId}/followers/`, {
      params: { page },
    });
    return response.data;
  },

  async getFollowing(userId, page = 1) {
    const response = await client.get(`/interaction/users/${userId}/following/`, {
      params: { page },
    });
    return response.data;
  },
};
```

**Step 2: Commit**

```bash
git add frontend/src/api/users.js
git commit -m "feat(frontend): add users API module"
```

---

### Task 1.2: Create User Hooks

**Files:**
- Create: `frontend/src/hooks/useUsers.js`

**Step 1: Create the users hooks module**

```javascript
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
        const url = new URL(lastPage.next);
        return url.searchParams.get('page');
      }
      return undefined;
    },
    enabled: !!userId,
  });
}

export function useFollowing(userId) {
  return useInfiniteQuery({
    queryKey: userKeys.following(userId),
    queryFn: ({ pageParam = 1 }) => usersApi.getFollowing(userId, pageParam),
    getNextPageParam: (lastPage) => {
      if (lastPage.next) {
        const url = new URL(lastPage.next);
        return url.searchParams.get('page');
      }
      return undefined;
    },
    enabled: !!userId,
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
```

**Step 2: Commit**

```bash
git add frontend/src/hooks/useUsers.js
git commit -m "feat(frontend): add user hooks with TanStack Query"
```

---

## Phase 2: Reusable Components

### Task 2.1: Create UserLink Component

**Files:**
- Create: `frontend/src/components/UserLink.jsx`

**Step 1: Create the UserLink component**

```javascript
import { Link } from 'react-router-dom';
import { CheckBadgeIcon } from '@heroicons/react/24/solid';

const sizes = {
  sm: {
    photo: 'w-6 h-6',
    text: 'text-sm',
    badge: 'h-3 w-3',
  },
  md: {
    photo: 'w-8 h-8',
    text: 'text-base',
    badge: 'h-4 w-4',
  },
};

export function UserLink({ user, showPhoto = true, size = 'sm' }) {
  if (!user) return null;

  const sizeClasses = sizes[size];

  return (
    <Link
      to={`/users/${user.id}`}
      className="inline-flex items-center gap-1.5 hover:underline"
      onClick={(e) => e.stopPropagation()}
    >
      {showPhoto && (
        user.profile_photo ? (
          <img
            src={user.profile_photo}
            alt={user.name}
            className={`${sizeClasses.photo} rounded-full object-cover`}
          />
        ) : (
          <div
            className={`${sizeClasses.photo} rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-medium text-xs`}
          >
            {user.name?.[0]?.toUpperCase() || '?'}
          </div>
        )
      )}
      <span className={`font-medium text-gray-900 ${sizeClasses.text}`}>
        {user.name || 'Unknown'}
      </span>
      {user.is_verified && (
        <CheckBadgeIcon className={`${sizeClasses.badge} text-primary-500`} />
      )}
    </Link>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/UserLink.jsx
git commit -m "feat(frontend): add UserLink component"
```

---

### Task 2.2: Create FollowButton Component

**Files:**
- Create: `frontend/src/components/FollowButton.jsx`

**Step 1: Create the FollowButton component**

```javascript
import { useState } from 'react';
import { useFollowUser } from '../hooks/useUsers';
import { useAuth } from '../hooks/useAuth';
import { Button } from './ui';

export function FollowButton({ userId, isPrivate, initialState = 'not_following', onStateChange }) {
  const [followState, setFollowState] = useState(initialState);
  const [isHovering, setIsHovering] = useState(false);
  const { isAuthenticated } = useAuth();
  const followMutation = useFollowUser();

  const handleClick = async () => {
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }

    try {
      const result = await followMutation.mutateAsync(userId);

      let newState;
      if (result.status === 'removed from followers' || result.status === 'unfollowed') {
        newState = 'not_following';
      } else if (result.status === 'pending') {
        newState = 'requested';
      } else {
        newState = 'following';
      }

      setFollowState(newState);
      onStateChange?.(newState);
    } catch (error) {
      console.error('Follow action failed:', error);
    }
  };

  const getButtonProps = () => {
    switch (followState) {
      case 'following':
        return {
          variant: isHovering ? 'danger' : 'secondary',
          children: isHovering ? 'Unfollow' : 'Following',
        };
      case 'requested':
        return {
          variant: 'secondary',
          children: 'Requested',
        };
      case 'not_following':
      default:
        return {
          variant: 'primary',
          children: isPrivate ? 'Request' : 'Follow',
        };
    }
  };

  const buttonProps = getButtonProps();

  return (
    <Button
      onClick={handleClick}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      disabled={followMutation.isPending}
      variant={buttonProps.variant}
      size="sm"
    >
      {followMutation.isPending ? 'Loading...' : buttonProps.children}
    </Button>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/FollowButton.jsx
git commit -m "feat(frontend): add FollowButton component"
```

---

### Task 2.3: Create FollowersModal Component

**Files:**
- Create: `frontend/src/components/FollowersModal.jsx`

**Step 1: Create the FollowersModal component**

```javascript
import { Fragment, useEffect, useRef } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { useFollowers, useFollowing } from '../hooks/useUsers';
import { useAuth } from '../hooks/useAuth';
import { UserLink } from './UserLink';
import { FollowButton } from './FollowButton';
import { Spinner, Button } from './ui';

export function FollowersModal({ userId, type, isOpen, onClose }) {
  const { user: currentUser } = useAuth();
  const modalRef = useRef(null);
  const listRef = useRef(null);

  const {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = type === 'followers' ? useFollowers(userId) : useFollowing(userId);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  // Close on backdrop click
  const handleBackdropClick = (e) => {
    if (e.target === modalRef.current) onClose();
  };

  // Infinite scroll
  const handleScroll = () => {
    if (!listRef.current || !hasNextPage || isFetchingNextPage) return;
    const { scrollTop, scrollHeight, clientHeight } = listRef.current;
    if (scrollTop + clientHeight >= scrollHeight - 100) {
      fetchNextPage();
    }
  };

  if (!isOpen) return null;

  const users = data?.pages?.flatMap((page) => page.results) || [];
  const title = type === 'followers' ? 'Followers' : 'Following';

  return (
    <div
      ref={modalRef}
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg w-full max-w-md max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-full"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div
          ref={listRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto p-4"
        >
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : users.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              {type === 'followers' ? 'No followers yet' : 'Not following anyone'}
            </p>
          ) : (
            <div className="space-y-3">
              {users.map((item) => {
                const user = type === 'followers' ? item.follower : item.following;
                const isCurrentUser = currentUser?.id === user.id;

                return (
                  <div key={user.id} className="flex items-center justify-between">
                    <UserLink user={user} size="md" />
                    {!isCurrentUser && (
                      <FollowButton
                        userId={user.id}
                        isPrivate={user.is_private}
                        initialState={user.is_following ? 'following' : 'not_following'}
                      />
                    )}
                  </div>
                );
              })}
              {isFetchingNextPage && (
                <div className="flex justify-center py-4">
                  <Spinner size="sm" />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/FollowersModal.jsx
git commit -m "feat(frontend): add FollowersModal component"
```

---

## Phase 3: User Profile Page

### Task 3.1: Create UserProfilePage

**Files:**
- Create: `frontend/src/pages/UserProfilePage.jsx`

**Step 1: Create the UserProfilePage component**

```javascript
import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckBadgeIcon } from '@heroicons/react/24/solid';
import { useUser, useUserRecipes } from '../hooks/useUsers';
import { useAuth } from '../hooks/useAuth';
import { FollowButton } from '../components/FollowButton';
import { FollowersModal } from '../components/FollowersModal';
import { RecipeCard } from '../components/RecipeCard';
import { Card, Button, Spinner } from '../components/ui';

export function UserProfilePage() {
  const { id } = useParams();
  const { user: currentUser } = useAuth();
  const { data: user, isLoading, error } = useUser(id);
  const { data: recipesData, isLoading: recipesLoading } = useUserRecipes(id);
  const [modalType, setModalType] = useState(null);

  const isOwnProfile = currentUser?.id === parseInt(id);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">User Not Found</h2>
        <p className="text-gray-600 mb-4">This user doesn't exist or has been removed.</p>
        <Link to="/">
          <Button>Go Home</Button>
        </Link>
      </div>
    );
  }

  const getInitialFollowState = () => {
    if (user.is_following) return 'following';
    if (user.has_pending_request) return 'requested';
    return 'not_following';
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Profile Header */}
      <Card className="mb-6">
        <Card.Body className="flex items-start gap-6">
          {/* Profile Photo */}
          <div className="flex-shrink-0">
            {user.profile_photo ? (
              <img
                src={user.profile_photo}
                alt={user.name}
                className="w-24 h-24 rounded-full object-cover"
              />
            ) : (
              <div className="w-24 h-24 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-3xl font-bold">
                {user.name?.[0]?.toUpperCase() || '?'}
              </div>
            )}
          </div>

          {/* Profile Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-2xl font-bold truncate">{user.name}</h1>
              {user.is_verified && (
                <CheckBadgeIcon className="h-6 w-6 text-primary-500 flex-shrink-0" />
              )}
            </div>

            {user.bio && (
              <p className="text-gray-600 mb-3">{user.bio}</p>
            )}

            {/* Stats */}
            <div className="flex items-center gap-4 text-sm">
              <button
                onClick={() => setModalType('followers')}
                className="hover:underline"
              >
                <span className="font-semibold">{user.followers_count || 0}</span>{' '}
                <span className="text-gray-600">followers</span>
              </button>
              <button
                onClick={() => setModalType('following')}
                className="hover:underline"
              >
                <span className="font-semibold">{user.following_count || 0}</span>{' '}
                <span className="text-gray-600">following</span>
              </button>
            </div>
          </div>

          {/* Action Button */}
          <div className="flex-shrink-0">
            {isOwnProfile ? (
              <Link to="/profile">
                <Button variant="secondary">Edit Profile</Button>
              </Link>
            ) : (
              <FollowButton
                userId={user.id}
                isPrivate={user.is_private}
                initialState={getInitialFollowState()}
              />
            )}
          </div>
        </Card.Body>
      </Card>

      {/* Private Account Notice */}
      {user.is_private && !user.is_following && !isOwnProfile && (
        <Card className="mb-6">
          <Card.Body className="text-center py-8">
            <p className="text-gray-600">This account is private.</p>
            <p className="text-gray-500 text-sm">Follow to see their recipes.</p>
          </Card.Body>
        </Card>
      )}

      {/* Recipes Grid */}
      {(!user.is_private || user.is_following || isOwnProfile) && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Recipes</h2>
          {recipesLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : recipesData?.results?.length === 0 ? (
            <Card>
              <Card.Body className="text-center py-8 text-gray-500">
                No recipes yet.
              </Card.Body>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recipesData?.results?.map((recipe) => (
                <RecipeCard key={recipe.id} recipe={recipe} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Followers Modal */}
      <FollowersModal
        userId={parseInt(id)}
        type={modalType}
        isOpen={!!modalType}
        onClose={() => setModalType(null)}
      />
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/pages/UserProfilePage.jsx
git commit -m "feat(frontend): add UserProfilePage component"
```

---

## Phase 4: Integration

### Task 4.1: Add Route to App.jsx

**Files:**
- Modify: `frontend/src/App.jsx`

**Step 1: Import UserProfilePage**

Add import at top of file after other page imports:

```javascript
import { UserProfilePage } from './pages/UserProfilePage';
```

**Step 2: Add route**

Add the route inside the MainLayout routes, after `/recipes/:id` and before the protected routes:

```javascript
<Route path="/users/:id" element={<UserProfilePage />} />
```

**Step 3: Commit**

```bash
git add frontend/src/App.jsx
git commit -m "feat(frontend): add user profile route"
```

---

### Task 4.2: Update RecipeCard with UserLink

**Files:**
- Modify: `frontend/src/components/RecipeCard.jsx`

**Step 1: Import UserLink**

Add import at top:

```javascript
import { UserLink } from './UserLink';
```

**Step 2: Replace author text with UserLink**

Find the line (around line 41-43):

```javascript
<p className="text-gray-600 text-sm mb-3">
  by {recipe.author?.name || 'Unknown'}
</p>
```

Replace with:

```javascript
<div className="text-gray-600 text-sm mb-3">
  by <UserLink user={recipe.author} showPhoto={false} />
</div>
```

**Step 3: Commit**

```bash
git add frontend/src/components/RecipeCard.jsx
git commit -m "feat(frontend): add UserLink to RecipeCard"
```

---

### Task 4.3: Update CommentThread with UserLink

**Files:**
- Modify: `frontend/src/components/CommentThread.jsx`

**Step 1: Import UserLink**

Add import at top:

```javascript
import { UserLink } from './UserLink';
```

**Step 2: Replace username in Comment component**

Find the section (around lines 27-34) that renders the user avatar and name:

```javascript
<div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-medium">
  {comment.user?.name?.[0]?.toUpperCase() || '?'}
</div>
<div className="flex-1">
  <div className="flex items-center gap-2">
    <span className="font-medium">{comment.user?.name || 'Anonymous'}</span>
```

Replace the avatar div and the username span with UserLink:

```javascript
<div className="flex-1">
  <div className="flex items-center gap-2">
    <UserLink user={comment.user} size="sm" />
```

Remove the separate avatar div since UserLink includes the photo.

**Step 3: Commit**

```bash
git add frontend/src/components/CommentThread.jsx
git commit -m "feat(frontend): add UserLink to CommentThread"
```

---

## Phase 5: Verification

### Task 5.1: Test the Implementation

**Step 1: Start the frontend dev server**

```bash
cd frontend && npm run dev
```

**Step 2: Manual testing checklist**

- [ ] Navigate to `/users/1` - should show user profile
- [ ] Click followers/following counts - should open modal
- [ ] Click Follow button - should toggle state (requires login)
- [ ] Visit recipe list - author names should be clickable
- [ ] Visit recipe detail - comments should have clickable usernames
- [ ] Test on own profile - should show "Edit Profile" button

**Step 3: Commit any fixes if needed**

```bash
git add -A
git commit -m "fix(frontend): address testing feedback"
```

---

## Summary

This plan covers:

1. **Phase 1**: API module and TanStack Query hooks for users
2. **Phase 2**: Reusable components (UserLink, FollowButton, FollowersModal)
3. **Phase 3**: UserProfilePage with profile header, stats, and recipe grid
4. **Phase 4**: Integration with existing components
5. **Phase 5**: Manual verification

Total: 8 tasks across 5 phases

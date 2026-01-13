# Social Features Frontend Design

## Overview

Add social features UI to the Recipe App frontend, starting with user profiles and following functionality.

## Goals

- Allow users to view other users' profiles
- Enable follow/unfollow functionality with support for private accounts
- Display followers/following lists in modals
- Make usernames clickable throughout the app

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Profile visibility | Public | Anyone can view profiles, follower counts, recipes |
| Profile content | Minimal | Name, photo, bio, stats, recipes (YAGNI) |
| Follow button | Stateful | Shows Follow/Following/Request/Requested |
| Followers list | Modal | Instagram-style, keeps user on current page |
| Navigation to profiles | Clickable usernames | Intuitive, works everywhere |

---

## Component Architecture

### New Pages

#### UserProfilePage (`/users/:id`)

**Layout:**
```
+--------------------------------------------------+
|  [Photo]  Name [Verified]           [Follow Btn] |
|           Bio text here                          |
|           X followers  |  Y following            |
+--------------------------------------------------+
|  [Recipe Grid - reuse RecipeCard]                |
|  [Card] [Card] [Card]                            |
|  [Card] [Card] [Card]                            |
+--------------------------------------------------+
```

**Props/State:**
- `userId` from route params
- Fetch user profile data
- Fetch user's public recipes
- Follow state (not_following, following, requested)

### New Components

#### FollowButton

**States:**
| State | Label | Style | Action |
|-------|-------|-------|--------|
| `not_following` | "Follow" | Primary filled | POST follow |
| `following` | "Following" | Outlined | DELETE follow (on click) |
| `following` (hover) | "Unfollow" | Red outlined | DELETE follow |
| `requested` | "Requested" | Muted outlined | Cancel request |
| `is_private` + `not_following` | "Request" | Primary filled | POST follow request |

**Props:**
```jsx
<FollowButton
  userId={number}
  isPrivate={boolean}
  initialState="not_following" | "following" | "requested"
  onStateChange={(newState) => void}
/>
```

#### FollowersModal

**Props:**
```jsx
<FollowersModal
  userId={number}
  type="followers" | "following"
  isOpen={boolean}
  onClose={() => void}
/>
```

**Content:**
- Title based on type
- Scrollable user list with pagination
- Each row: UserLink + FollowButton
- Empty states

#### UserLink

**Props:**
```jsx
<UserLink
  user={{ id, name, photo, isVerified }}
  showPhoto={boolean} // default true
  size="sm" | "md"    // default "sm"
/>
```

**Renders:** Clickable row with photo + name + verified badge

---

## API Integration

### New API Module: `api/users.js`

```javascript
// Get user profile
getUser(userId)
GET /api/interaction/users/{id}/

// Get user's recipes
getUserRecipes(userId)
GET /api/recipe/recipes/?author={userId}

// Follow/unfollow
followUser(userId)
POST /api/interaction/users/{id}/follow/

// Get followers
getFollowers(userId, page)
GET /api/interaction/users/{id}/followers/

// Get following
getFollowing(userId, page)
GET /api/interaction/users/{id}/following/
```

### New Hook: `useUser.js`

```javascript
useUser(userId) -> { user, isLoading, error }
useUserRecipes(userId) -> { recipes, isLoading, fetchMore }
useFollowers(userId) -> { followers, isLoading, fetchMore }
useFollowing(userId) -> { following, isLoading, fetchMore }
useFollowMutation() -> { follow, unfollow, isLoading }
```

---

## File Changes

### New Files

```
src/
  api/
    users.js              # User API calls
  hooks/
    useUser.js            # User data hooks
  components/
    FollowButton.jsx      # Follow/unfollow button
    FollowersModal.jsx    # Followers/following modal
    UserLink.jsx          # Clickable username component
  pages/
    UserProfilePage.jsx   # User profile page
```

### Modified Files

```
src/
  App.jsx                 # Add /users/:id route
  components/
    RecipeCard.jsx        # Wrap author with UserLink
    CommentThread.jsx     # Wrap commenter with UserLink
  pages/
    RecipeDetailPage.jsx  # Wrap author with UserLink
```

---

## Routes

| Route | Component | Auth Required |
|-------|-----------|---------------|
| `/users/:id` | UserProfilePage | No |

---

## Edge Cases

1. **Viewing own profile**: Show "Edit Profile" instead of Follow button
2. **Blocked users**: API returns 404, show "User not found"
3. **Private profile not following**: Show limited info (name, photo, bio, "This account is private")
4. **User not found**: Show 404 page
5. **Loading states**: Skeleton loaders for profile and recipe grid

---

## Out of Scope (Future)

- Follow requests management (accept/reject UI)
- Block/mute UI
- Notifications
- Activity feed
- User search/discovery page

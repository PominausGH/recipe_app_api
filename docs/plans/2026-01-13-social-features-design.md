# Social Features Design

## Overview

Add social features to the Recipe App, enabling users to follow others, discover new chefs, receive personalized activity feeds, and build community through notifications and badges.

## Scope

- One-way following (Twitter-style)
- Private accounts with follow approval
- Configurable activity feed (chronological or algorithmic)
- Granular notification preferences (in-app + email)
- Block and mute functionality
- User discovery: search, suggestions, social graph, popular chefs
- Verified badges (manual) + achievement badges (automatic)

---

## Data Model

### Follow
The central relationship for the social graph.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `follower` | FK (User) | User doing the following |
| `following` | FK (User) | User being followed |
| `created_at` | DateTime | When the follow happened |

*Constraint:* Unique together on `follower` + `following`, prevent self-follows.

### FollowRequest
For private accounts - pending approval.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `requester` | FK (User) | User requesting to follow |
| `target` | FK (User) | Private account user |
| `created_at` | DateTime | Request timestamp |
| `status` | CharField | pending, approved, rejected |

### Block

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `user` | FK (User) | User performing the action |
| `blocked_user` | FK (User) | Target user |
| `created_at` | DateTime | Timestamp |

### Mute

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `user` | FK (User) | User performing the action |
| `muted_user` | FK (User) | Target user |
| `created_at` | DateTime | Timestamp |

### User Model Extension
Add to existing User:

| Field | Type | Description |
|-------|------|-------------|
| `is_private` | Boolean | Require follow approval |
| `is_verified` | Boolean | Manual verification badge |

---

## Notifications & Preferences

### Notification
Stores all notification events.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `recipient` | FK (User) | User receiving notification |
| `actor` | FK (User) | User who triggered it |
| `verb` | CharField | followed, rated, commented, favorited, posted_recipe |
| `target_type` | CharField | recipe, user, comment (nullable) |
| `target_id` | UUID | ID of the related object (nullable) |
| `is_read` | Boolean | Has user seen it |
| `created_at` | DateTime | Timestamp |

### NotificationPreference
Granular per-user settings.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `user` | FK (User) | One-to-one with User |
| `notify_new_follower` | Boolean | Default: True |
| `notify_follow_request` | Boolean | Default: True |
| `notify_recipe_comment` | Boolean | Default: True |
| `notify_recipe_rating` | Boolean | Default: True |
| `notify_comment_reply` | Boolean | Default: True |
| `notify_following_new_recipe` | Boolean | Default: True |
| `email_digest` | CharField | none, daily, weekly |

### FeedPreference
What appears in user's feed.

| Field | Type | Description |
|-------|------|-------------|
| `user` | FK (User) | One-to-one |
| `show_recipes` | Boolean | Default: True |
| `show_ratings` | Boolean | Default: True |
| `show_comments` | Boolean | Default: False |
| `show_favorites` | Boolean | Default: False |
| `feed_order` | CharField | chronological, algorithmic |

---

## Badges & Achievements

### Badge
Definition of available badges (both verified and achievement types).

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `name` | CharField | "Verified", "Top Contributor", "Century Chef" |
| `slug` | SlugField | URL-safe identifier |
| `description` | CharField | What it means / how to earn |
| `icon` | CharField | Icon name or emoji |
| `badge_type` | CharField | verified, achievement |
| `criteria` | JSONField | Auto-award rules (nullable for manual) |

Example criteria for automatic badges:
```json
{"type": "recipe_count", "threshold": 100}
{"type": "follower_count", "threshold": 1000}
{"type": "total_ratings_received", "threshold": 500}
```

### UserBadge
Junction table - badges a user has earned.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `user` | FK (User) | Badge holder |
| `badge` | FK (Badge) | The badge |
| `awarded_at` | DateTime | When earned |
| `awarded_by` | FK (User) | Admin who granted (null for auto) |

### Suggested Achievement Badges
- **Rising Chef** - 10 recipes published
- **Century Chef** - 100 recipes published
- **Crowd Favorite** - 100 total favorites on your recipes
- **Top Contributor** - 500 ratings/comments given
- **Community Star** - 1,000 followers

---

## API Endpoints

### Follow Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/users/{id}/follow/` | Follow a user (or send request if private) |
| `DELETE` | `/api/users/{id}/follow/` | Unfollow a user |
| `GET` | `/api/users/{id}/followers/` | List user's followers |
| `GET` | `/api/users/{id}/following/` | List who user follows |
| `GET` | `/api/me/follow-requests/` | Pending requests (for private accounts) |
| `POST` | `/api/me/follow-requests/{id}/accept/` | Approve request |
| `POST` | `/api/me/follow-requests/{id}/reject/` | Reject request |

### Block & Mute

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/users/{id}/block/` | Block user |
| `DELETE` | `/api/users/{id}/block/` | Unblock user |
| `POST` | `/api/users/{id}/mute/` | Mute user |
| `DELETE` | `/api/users/{id}/mute/` | Unmute user |
| `GET` | `/api/me/blocked/` | List blocked users |
| `GET` | `/api/me/muted/` | List muted users |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/me/notifications/` | List notifications (paginated) |
| `POST` | `/api/me/notifications/read/` | Mark all as read |
| `POST` | `/api/me/notifications/{id}/read/` | Mark one as read |
| `GET` | `/api/me/notifications/unread-count/` | Badge count |

### Activity Feed

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/feed/` | Main feed from followed users |
| `GET` | `/api/feed/?order=chronological` | Force chronological order |
| `GET` | `/api/feed/?order=algorithmic` | Force algorithmic order |

Feed returns mixed content types with a `type` field:
```json
{
  "results": [
    {"type": "recipe", "actor": {...}, "recipe": {...}, "created_at": "..."},
    {"type": "rating", "actor": {...}, "recipe": {...}, "score": 5, "created_at": "..."}
  ]
}
```

### Discovery

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/search/?q=` | Search users by name |
| `GET` | `/api/users/suggested/` | Users you might like (based on interests) |
| `GET` | `/api/users/followed-by-network/` | Followed by people you follow |
| `GET` | `/api/users/popular/` | Popular chefs leaderboard |
| `GET` | `/api/users/popular/?period=week` | Filter by week, month, all-time |

### Preferences

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/me/preferences/notifications/` | Get notification settings |
| `PATCH` | `/api/me/preferences/notifications/` | Update notification settings |
| `GET` | `/api/me/preferences/feed/` | Get feed settings |
| `PATCH` | `/api/me/preferences/feed/` | Update feed settings |
| `PATCH` | `/api/me/privacy/` | Update is_private setting |

### Badges

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/{id}/badges/` | List user's badges |
| `GET` | `/api/badges/` | List all available badges |
| `POST` | `/api/admin/users/{id}/badges/` | Award badge (admin only) |

---

## Frontend Pages

### `/feed` - Activity Feed
- Toggle switch: "Latest" (chronological) / "For You" (algorithmic)
- Feed cards showing followed users' activity (recipes, ratings, etc.)
- Pull-to-refresh behavior
- Infinite scroll pagination
- Empty state: "Follow some chefs to see their activity"

### `/explore` - Discovery Hub
- Search bar at top
- Tabs: "Suggested" | "Popular" | "Network"
- User cards with avatar, name, bio preview, follower count, follow button
- Popular section shows time period filter (week/month/all-time)

### `/users/{id}` - Enhanced Profile Page
- Header: avatar, name, bio, badges row, verified checkmark if applicable
- Stats bar: recipes count, followers, following
- Follow/Unfollow button (or "Requested" for pending)
- Three-dot menu: Mute, Block, Share Profile
- Tabs: "Recipes" | "Ratings" | "Favorites" (if public)
- Private account shows lock icon, "Follow to see recipes"

### `/settings/notifications` - Notification Preferences
- Toggle switches for each notification type
- Email digest dropdown (none/daily/weekly)

### `/settings/privacy` - Privacy Settings
- Private account toggle
- Blocked users list with unblock buttons
- Muted users list with unmute buttons

---

## Frontend Components

### Core Components

| Component | Description |
|-----------|-------------|
| `FollowButton` | States: Follow, Following, Requested, disabled (blocked). Handles private account requests. |
| `UserCard` | Avatar, name, bio snippet, follower count, badges, follow button. Used in discovery lists. |
| `UserAvatar` | Profile photo with optional verified badge overlay and size variants (sm/md/lg). |
| `BadgeRow` | Horizontal scroll of badge icons with tooltips showing badge names. |

### Feed Components

| Component | Description |
|-----------|-------------|
| `FeedCard` | Wrapper with actor info, timestamp, content based on type (recipe/rating/comment/favorite). |
| `FeedToggle` | "Latest" / "For You" switch, persists preference. |
| `FeedEmpty` | Empty state with suggested users to follow. |
| `FeedFilter` | Dropdown to temporarily filter: All, Recipes Only, Ratings Only. |

### Notification Components

| Component | Description |
|-----------|-------------|
| `NotificationBell` | Icon with unread count badge, opens dropdown. |
| `NotificationDropdown` | Recent notifications list, "Mark all read", link to full page. |
| `NotificationItem` | Avatar, action text ("Jane rated your recipe"), timestamp, unread dot. |

### Profile Components

| Component | Description |
|-----------|-------------|
| `ProfileHeader` | Full profile header with stats, badges, follow button, menu. |
| `ProfileTabs` | Tab navigation for recipes/ratings/favorites. |
| `PrivateProfileLock` | Shown for private accounts you don't follow. |
| `ProfileMenu` | Three-dot menu: Mute, Block, Share, Report. |

---

## Error Handling & Edge Cases

### API Errors

| Error | Handling |
|-------|----------|
| Network failure | Toast "Couldn't complete action. Check connection." + revert optimistic update |
| 401 Unauthorized | Redirect to login |
| 403 on follow | "This account is private" or "You are blocked by this user" |
| 404 User not found | Redirect to explore with "User not found" message |
| 429 Rate limited | Toast "Too many requests. Try again shortly." |

### Business Logic Edge Cases

| Scenario | Handling |
|----------|----------|
| Follow yourself | API returns 400, button hidden on own profile |
| Follow someone who blocked you | API returns 403, show "Unable to follow this user" |
| Unfollow then re-follow private account | Requires new request approval |
| User goes private with existing followers | Existing followers retained, new ones need approval |
| User deletes account | Remove from followers/following lists, feed items show "Deleted User" |
| Blocked user tries to view your profile | 404 - profile appears not to exist |
| Muted user's content | Filtered client-side from feed, still exists on their profile |

### Notification Edge Cases

| Scenario | Handling |
|----------|----------|
| Notification target deleted | Show "This content is no longer available" |
| Bulk follows (spam) | Rate limit: max 50 follows per hour |
| Notification flood | Aggregate: "Jane and 12 others rated your recipe" |
| User disables notification type | Stop creating those notifications, don't delete old ones |

### Feed Edge Cases

| Scenario | Handling |
|----------|----------|
| Following no one | Show discovery suggestions instead of empty feed |
| All followed users inactive | "No recent activity" + suggestions |
| Algorithmic feed cold start | Fall back to chronological until enough engagement data |

---

## Testing Strategy

### Backend Tests (pytest)

#### Model Tests
- `test_follow_creates_relationship` - Basic follow works
- `test_cannot_follow_self` - Validation prevents self-follow
- `test_unique_follow_constraint` - No duplicate follows
- `test_block_prevents_follow` - Blocked users can't follow
- `test_private_account_requires_request` - Follow creates pending request
- `test_mute_does_not_affect_follow` - Muted users remain followed

#### API Tests
- `test_follow_public_user` - Returns 201, creates Follow
- `test_follow_private_user` - Returns 202, creates FollowRequest
- `test_accept_follow_request` - Creates Follow, deletes request
- `test_reject_follow_request` - Deletes request, no Follow created
- `test_unfollow` - Removes relationship
- `test_block_removes_existing_follow` - Blocking unfollows in both directions
- `test_followers_list_pagination` - Returns paginated results
- `test_blocked_user_gets_404_on_profile` - Profile hidden from blocked users

#### Feed Tests
- `test_feed_shows_followed_user_recipes` - New recipes appear
- `test_feed_respects_preferences` - Disabled types don't appear
- `test_feed_excludes_muted_users` - Muted content filtered
- `test_feed_chronological_order` - Newest first when selected
- `test_feed_empty_when_following_none` - Returns empty with suggestions

#### Notification Tests
- `test_notification_created_on_follow` - Follow triggers notification
- `test_notification_respects_preferences` - Disabled types not created
- `test_notification_aggregation` - Multiple actions aggregate
- `test_mark_read` - Updates is_read flag
- `test_unread_count` - Returns correct count

#### Badge Tests
- `test_auto_badge_awarded_on_threshold` - Achievement triggers at count
- `test_manual_badge_requires_admin` - Non-admin can't award verified
- `test_badge_not_duplicated` - Same badge not awarded twice

### Frontend Tests (Vitest + React Testing Library)

#### Component Tests

**FollowButton**
- Renders "Follow" for unfollowed user
- Renders "Following" for followed user
- Renders "Requested" for pending private account
- Calls follow API on click
- Shows loading state during request
- Reverts on API error

**UserCard**
- Displays avatar, name, bio, follower count
- Shows verified badge when applicable
- Shows badge row when user has achievements
- Follow button works within card

**NotificationBell**
- Shows count badge when unread > 0
- Hides count when all read
- Opens dropdown on click
- Marks as read when dropdown closes

**FeedCard**
- Renders recipe type with image and title
- Renders rating type with stars and recipe link
- Renders favorite type with recipe thumbnail
- Shows relative timestamp ("2h ago")
- Links to actor profile and target content

#### Integration Tests

**Follow Flow**
- Visit user profile → click Follow → button changes to "Following" → follower count increments → appears in following list

**Private Account Flow**
- Follow private user → see "Requested" → owner approves → button changes to "Following" → can view recipes

**Block Flow**
- Block user → removed from following → their content gone from feed → can unblock from settings

**Feed Preferences Flow**
- Toggle off ratings → refresh feed → no rating cards appear → toggle on → ratings return

**Notification Flow**
- Receive follow → bell shows count → open dropdown → see notification → click → navigate to profile → count decreases

---

## File Structure

### Backend (app/interaction/)
Add to existing interaction app:

```
app/interaction/
├── models.py          # Add Follow, FollowRequest, Block, Mute, Notification, etc.
├── serializers.py     # Add new serializers
├── views.py           # Add new ViewSets
├── urls.py            # Add new routes
├── services/
│   ├── __init__.py
│   ├── feed.py        # Feed generation logic
│   ├── notifications.py  # Notification creation/aggregation
│   └── badges.py      # Badge award logic
└── tests/
    ├── test_follow.py
    ├── test_notifications.py
    ├── test_feed.py
    └── test_badges.py
```

### Frontend (frontend/src/)

```
frontend/src/
├── pages/
│   ├── Feed.jsx
│   ├── Explore.jsx
│   ├── UserProfile.jsx       # Enhanced
│   ├── NotificationSettings.jsx
│   └── PrivacySettings.jsx
├── components/
│   ├── social/
│   │   ├── FollowButton.jsx
│   │   ├── UserCard.jsx
│   │   ├── UserAvatar.jsx
│   │   └── BadgeRow.jsx
│   ├── feed/
│   │   ├── FeedCard.jsx
│   │   ├── FeedToggle.jsx
│   │   ├── FeedEmpty.jsx
│   │   └── FeedFilter.jsx
│   ├── notifications/
│   │   ├── NotificationBell.jsx
│   │   ├── NotificationDropdown.jsx
│   │   └── NotificationItem.jsx
│   └── profile/
│       ├── ProfileHeader.jsx
│       ├── ProfileTabs.jsx
│       ├── PrivateProfileLock.jsx
│       └── ProfileMenu.jsx
├── contexts/
│   ├── NotificationContext.jsx
│   └── FeedContext.jsx
└── api/
    ├── social.js
    ├── notifications.js
    └── feed.js
```

---

## Future Considerations

- **Recipe importing** - Import recipes from other cooking websites (noted for separate feature)
- **Push notifications** - Add when mobile app is built
- **Direct messaging** - Private messages between users
- **Collections/Lists** - Curated recipe lists users can share

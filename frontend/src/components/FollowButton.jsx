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

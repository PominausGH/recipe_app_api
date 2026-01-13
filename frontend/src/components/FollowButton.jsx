import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFollowUser } from '../hooks/useUsers';
import { useAuth } from '../hooks/useAuth';
import { Button } from './ui';

export function FollowButton({ userId, isPrivate, initialState = 'not_following', onStateChange }) {
  const [followState, setFollowState] = useState(initialState);
  const [isHovering, setIsHovering] = useState(false);
  const [error, setError] = useState(null);
  const { isAuthenticated } = useAuth();
  const followMutation = useFollowUser();
  const navigate = useNavigate();

  useEffect(() => {
    setFollowState(initialState);
  }, [initialState]);

  const handleClick = async () => {
    if (!isAuthenticated) {
      navigate('/login');
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
    } catch (err) {
      console.error('Follow action failed:', err);
      setError('Failed. Try again.');
      setTimeout(() => setError(null), 3000);
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
      {error ? error : (followMutation.isPending ? 'Loading...' : buttonProps.children)}
    </Button>
  );
}

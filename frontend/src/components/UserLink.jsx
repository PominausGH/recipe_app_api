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

export function UserLink({ user, showPhoto = true, size = 'sm', disableLink = false }) {
  if (!user) return null;

  const sizeClasses = sizes[size] || sizes.sm;

  const content = (
    <>
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
            role="img"
            aria-label={user.name || 'Unknown user'}
          >
            {user.name?.[0]?.toUpperCase() || '?'}
          </div>
        )
      )}
      <span className={`font-medium text-gray-900 ${sizeClasses.text}`}>
        {user.name || 'Unknown'}
      </span>
      {user.is_verified && (
        <>
          <CheckBadgeIcon
            className={`${sizeClasses.badge} text-primary-500`}
            aria-hidden="true"
          />
          <span className="sr-only">(verified)</span>
        </>
      )}
    </>
  );

  if (disableLink) {
    return (
      <span className="inline-flex items-center gap-1.5">
        {content}
      </span>
    );
  }

  return (
    <Link
      to={`/users/${user.id}`}
      className="inline-flex items-center gap-1.5 hover:underline"
      onClick={(e) => e.stopPropagation()}
    >
      {content}
    </Link>
  );
}

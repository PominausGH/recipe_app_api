import { useEffect, useRef } from "react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import { useFollowers, useFollowing } from "../hooks/useUsers";
import { useAuth } from "../hooks/useAuth";
import { UserLink } from "./UserLink";
import { FollowButton } from "./FollowButton";
import { Spinner } from "./ui";

export function FollowersModal({ userId, type, isOpen, onClose }) {
  const { user: currentUser } = useAuth();
  const modalRef = useRef(null);
  const listRef = useRef(null);

  // Call both hooks unconditionally to comply with Rules of Hooks
  const followers = useFollowers(type === "followers" ? userId : null);
  const following = useFollowing(type === "following" ? userId : null);

  const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } =
    type === "followers" ? followers : following;

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "";
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
  const title = type === "followers" ? "Followers" : "Following";

  return (
    <div
      ref={modalRef}
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className="bg-white rounded-lg w-full max-w-md max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 id="modal-title" className="text-lg font-semibold">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-full"
            aria-label="Close modal"
          >
            <XMarkIcon className="h-5 w-5" aria-hidden="true" />
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
              {type === "followers"
                ? "No followers yet"
                : "Not following anyone"}
            </p>
          ) : (
            <div className="space-y-3">
              {users.map((item) => {
                const user =
                  type === "followers" ? item.follower : item.following;
                const isCurrentUser = currentUser?.id === user.id;

                return (
                  <div
                    key={user.id}
                    className="flex items-center justify-between"
                  >
                    <UserLink user={user} size="md" />
                    {!isCurrentUser && (
                      <FollowButton
                        userId={user.id}
                        isPrivate={user.is_private}
                        initialState={
                          user.is_following ? "following" : "not_following"
                        }
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

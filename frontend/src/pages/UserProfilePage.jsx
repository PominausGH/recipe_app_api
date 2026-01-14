import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { CheckBadgeIcon } from "@heroicons/react/24/solid";
import { useUser, useUserRecipes } from "../hooks/useUsers";
import { useAuth } from "../hooks/useAuth";
import { FollowButton } from "../components/FollowButton";
import { FollowersModal } from "../components/FollowersModal";
import { RecipeCard } from "../components/RecipeCard";
import { Card, Button, Spinner } from "../components/ui";

export function UserProfilePage() {
  const { id } = useParams();
  const { user: currentUser } = useAuth();
  const { data: user, isLoading, error } = useUser(id);
  const { data: recipesData, isLoading: recipesLoading } = useUserRecipes(id);
  const [modalType, setModalType] = useState(null);

  const isOwnProfile = currentUser?.id === parseInt(id, 10);

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
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          User Not Found
        </h2>
        <p className="text-gray-600 mb-4">
          This user doesn't exist or has been removed.
        </p>
        <Link to="/">
          <Button>Go Home</Button>
        </Link>
      </div>
    );
  }

  const getInitialFollowState = () => {
    if (user.is_following) return "following";
    if (user.has_pending_request) return "requested";
    return "not_following";
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
                alt={`${user.name}'s profile photo`}
                className="w-24 h-24 rounded-full object-cover"
              />
            ) : (
              <div className="w-24 h-24 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-3xl font-bold">
                {user.name?.[0]?.toUpperCase() || "?"}
              </div>
            )}
          </div>

          {/* Profile Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-2xl font-bold truncate">{user.name}</h1>
              {user.is_verified && (
                <>
                  <CheckBadgeIcon
                    className="h-6 w-6 text-primary-500 flex-shrink-0"
                    aria-hidden="true"
                  />
                  <span className="sr-only">Verified account</span>
                </>
              )}
            </div>

            {user.bio && <p className="text-gray-600 mb-3">{user.bio}</p>}

            {/* Stats */}
            <div className="flex items-center gap-4 text-sm">
              <button
                type="button"
                onClick={() => setModalType("followers")}
                className="hover:underline"
                aria-label={`${user.followers_count || 0} followers, click to view`}
              >
                <span className="font-semibold">
                  {user.followers_count || 0}
                </span>{" "}
                <span className="text-gray-600">followers</span>
              </button>
              <button
                type="button"
                onClick={() => setModalType("following")}
                className="hover:underline"
                aria-label={`${user.following_count || 0} following, click to view`}
              >
                <span className="font-semibold">
                  {user.following_count || 0}
                </span>{" "}
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
            <p className="text-gray-500 text-sm">
              Follow to see their recipes.
            </p>
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
        userId={parseInt(id, 10)}
        type={modalType}
        isOpen={!!modalType}
        onClose={() => setModalType(null)}
      />
    </div>
  );
}

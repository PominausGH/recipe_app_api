import { useParams, useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useRecipe, useRecipeComments, useRateRecipe, useToggleFavorite, useDeleteRecipe } from '../hooks/useRecipes';
import { useAuth } from '../hooks/useAuth';
import { RatingStars } from '../components/RatingStars';
import { IngredientList } from '../components/IngredientList';
import { CommentThread } from '../components/CommentThread';
import { Button, Card, Spinner } from '../components/ui';
import { HeartIcon, ClockIcon, UserGroupIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

export function RecipeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const { data: recipe, isLoading, error } = useRecipe(id);
  const { data: comments } = useRecipeComments(id);
  const rateRecipe = useRateRecipe();
  const toggleFavorite = useToggleFavorite();
  const deleteRecipe = useDeleteRecipe();
  const [showRatingForm, setShowRatingForm] = useState(false);

  const isOwner = user?.id === recipe?.author?.id;
  const totalTime = (recipe?.prep_time || 0) + (recipe?.cook_time || 0);

  const handleRate = async (score) => {
    await rateRecipe.mutateAsync({ id, score });
    setShowRatingForm(false);
  };

  const handleFavorite = async () => {
    await toggleFavorite.mutateAsync(id);
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this recipe?')) {
      await deleteRecipe.mutateAsync(id);
      navigate('/my-recipes');
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !recipe) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Recipe Not Found</h2>
        <Link to="/recipes">
          <Button>Browse Recipes</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header Image */}
      {recipe.image && (
        <div className="aspect-video rounded-lg overflow-hidden mb-6">
          <img src={recipe.image} alt={recipe.title} className="w-full h-full object-cover" />
        </div>
      )}

      {/* Title and Actions */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">{recipe.title}</h1>
          <p className="text-gray-600">by {recipe.author?.name || 'Unknown'}</p>
        </div>
        <div className="flex gap-2">
          {isAuthenticated && !isOwner && (
            <Button
              variant="ghost"
              onClick={handleFavorite}
              disabled={toggleFavorite.isPending}
            >
              {recipe.is_favorited ? (
                <HeartSolidIcon className="h-5 w-5 text-red-500" />
              ) : (
                <HeartIcon className="h-5 w-5" />
              )}
            </Button>
          )}
          {isOwner && (
            <>
              <Link to={`/recipes/${id}/edit`}>
                <Button variant="secondary">
                  <PencilIcon className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </Link>
              <Button variant="danger" onClick={handleDelete}>
                <TrashIcon className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="flex flex-wrap gap-6 mb-6">
        <div className="flex items-center gap-2">
          <RatingStars rating={recipe.average_rating || 0} count={recipe.rating_count} />
        </div>
        {totalTime > 0 && (
          <div className="flex items-center gap-2 text-gray-600">
            <ClockIcon className="h-5 w-5" />
            <span>{totalTime} min</span>
          </div>
        )}
        {recipe.servings && (
          <div className="flex items-center gap-2 text-gray-600">
            <UserGroupIcon className="h-5 w-5" />
            <span>{recipe.servings} servings</span>
          </div>
        )}
        {recipe.difficulty && (
          <span className="px-2 py-1 bg-gray-100 rounded text-sm capitalize">
            {recipe.difficulty}
          </span>
        )}
      </div>

      {/* Rate Button */}
      {isAuthenticated && !isOwner && (
        <div className="mb-6">
          {showRatingForm ? (
            <div className="flex items-center gap-4">
              <span>Your rating:</span>
              <RatingStars interactive onRate={handleRate} size="lg" />
              <Button variant="ghost" size="sm" onClick={() => setShowRatingForm(false)}>
                Cancel
              </Button>
            </div>
          ) : (
            <Button variant="secondary" onClick={() => setShowRatingForm(true)}>
              Rate this recipe
            </Button>
          )}
        </div>
      )}

      {/* Description */}
      {recipe.description && (
        <Card className="mb-6">
          <Card.Body>
            <p className="text-gray-700">{recipe.description}</p>
          </Card.Body>
        </Card>
      )}

      {/* Ingredients */}
      <Card className="mb-6">
        <Card.Header>
          <h2 className="text-xl font-semibold">Ingredients</h2>
        </Card.Header>
        <Card.Body>
          <IngredientList ingredients={recipe.ingredients} />
        </Card.Body>
      </Card>

      {/* Instructions */}
      <Card className="mb-6">
        <Card.Header>
          <h2 className="text-xl font-semibold">Instructions</h2>
        </Card.Header>
        <Card.Body>
          <div className="prose max-w-none whitespace-pre-wrap">
            {recipe.instructions}
          </div>
        </Card.Body>
      </Card>

      {/* Comments */}
      <Card>
        <Card.Header>
          <h2 className="text-xl font-semibold">
            Comments ({comments?.length || 0})
          </h2>
        </Card.Header>
        <Card.Body>
          <CommentThread comments={comments} recipeId={id} />
        </Card.Body>
      </Card>
    </div>
  );
}

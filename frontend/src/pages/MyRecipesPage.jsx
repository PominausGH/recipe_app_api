import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useRecipes } from '../hooks/useRecipes';
import { useAuth } from '../hooks/useAuth';
import { RecipeCard } from '../components/RecipeCard';
import { Button, Spinner } from '../components/ui';

export function MyRecipesPage() {
  const { user } = useAuth();
  const [showDrafts, setShowDrafts] = useState(false);

  const { data, isLoading } = useRecipes({
    author: user?.id,
  });

  const recipes = data?.results || [];
  const publishedRecipes = recipes.filter((r) => r.is_published);
  const draftRecipes = recipes.filter((r) => !r.is_published);
  const displayedRecipes = showDrafts ? draftRecipes : publishedRecipes;

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">My Recipes</h1>
        <Link to="/recipes/new">
          <Button>Create Recipe</Button>
        </Link>
      </div>

      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setShowDrafts(false)}
          className={`px-4 py-2 rounded-md ${
            !showDrafts
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          Published ({publishedRecipes.length})
        </button>
        <button
          onClick={() => setShowDrafts(true)}
          className={`px-4 py-2 rounded-md ${
            showDrafts
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          Drafts ({draftRecipes.length})
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : displayedRecipes.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          {showDrafts
            ? 'No draft recipes.'
            : 'No published recipes yet. Create your first recipe!'}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayedRecipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}
    </div>
  );
}

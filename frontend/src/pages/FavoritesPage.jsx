import { useRecipes } from '../hooks/useRecipes';
import { RecipeCard } from '../components/RecipeCard';
import { Spinner } from '../components/ui';

export function FavoritesPage() {
  // Note: Backend needs to support favorites filter - this assumes it does
  const { data, isLoading } = useRecipes({ favorited: true });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">My Favorites</h1>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : !data?.results?.length ? (
        <div className="text-center py-12 text-gray-500">
          No favorite recipes yet. Browse recipes and click the heart to save them!
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.results.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}
    </div>
  );
}

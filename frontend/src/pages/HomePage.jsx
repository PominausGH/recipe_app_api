import { Link } from "react-router-dom";
import { useRecipes } from "../hooks/useRecipes";
import { RecipeCard } from "../components/RecipeCard";
import { Button, Spinner } from "../components/ui";

export function HomePage() {
  const { data: featuredData, isLoading: loadingFeatured } = useRecipes({
    ordering: "-avg_rating",
    page_size: 4,
  });
  const { data: recentData, isLoading: loadingRecent } = useRecipes({
    ordering: "-created_at",
    page_size: 4,
  });

  return (
    <div>
      {/* Hero Section */}
      <section className="text-center py-12 bg-gradient-to-r from-primary-500 to-primary-600 -mx-4 sm:-mx-6 lg:-mx-8 px-4 mb-12 rounded-b-3xl">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
          Discover Delicious Recipes
        </h1>
        <p className="text-xl text-primary-100 mb-8">
          Share your culinary creations with the world
        </p>
        <Link to="/recipes">
          <Button size="lg" variant="secondary">
            Browse Recipes
          </Button>
        </Link>
      </section>

      {/* Featured Recipes */}
      <section className="mb-12">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Top Rated</h2>
          <Link
            to="/recipes?ordering=-avg_rating"
            className="text-primary-600 hover:text-primary-700"
          >
            View all
          </Link>
        </div>
        {loadingFeatured ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredData?.results?.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>
        )}
      </section>

      {/* Recent Recipes */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Recently Added</h2>
          <Link
            to="/recipes?ordering=-created_at"
            className="text-primary-600 hover:text-primary-700"
          >
            View all
          </Link>
        </div>
        {loadingRecent ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {recentData?.results?.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

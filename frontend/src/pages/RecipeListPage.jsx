import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useRecipes } from '../hooks/useRecipes';
import { useDebounce } from '../hooks/useDebounce';
import { RecipeCard } from '../components/RecipeCard';
import { RecipeFilters } from '../components/RecipeFilters';
import { Spinner, Button } from '../components/ui';

export function RecipeListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    difficulty: searchParams.get('difficulty') || '',
    max_time: searchParams.get('max_time') || '',
    ordering: searchParams.get('ordering') || '-created_at',
    page: parseInt(searchParams.get('page') || '1', 10),
  });

  const debouncedSearch = useDebounce(filters.search, 300);

  const queryFilters = {
    ...filters,
    search: debouncedSearch,
  };
  Object.keys(queryFilters).forEach((key) => {
    if (!queryFilters[key]) delete queryFilters[key];
  });

  const { data, isLoading, error } = useRecipes(queryFilters);

  const handleFilterChange = (newFilters) => {
    setFilters({ ...newFilters, page: 1 });
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    setSearchParams(params);
  };

  const handleClearFilters = () => {
    setFilters({
      search: '',
      difficulty: '',
      max_time: '',
      ordering: '-created_at',
      page: 1,
    });
    setSearchParams({});
  };

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
    searchParams.set('page', newPage.toString());
    setSearchParams(searchParams);
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Browse Recipes</h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <aside className="lg:col-span-1">
          <RecipeFilters
            filters={filters}
            onChange={handleFilterChange}
            onClear={handleClearFilters}
          />
        </aside>

        <main className="lg:col-span-3">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner size="lg" />
            </div>
          ) : error ? (
            <div className="text-center py-12 text-red-600">
              Error loading recipes. Please try again.
            </div>
          ) : data?.results?.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No recipes found. Try adjusting your filters.
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                {data?.results?.map((recipe) => (
                  <RecipeCard key={recipe.id} recipe={recipe} />
                ))}
              </div>

              {/* Pagination */}
              {(data?.next || data?.previous) && (
                <div className="mt-8 flex justify-center gap-2">
                  <Button
                    variant="secondary"
                    disabled={!data?.previous}
                    onClick={() => handlePageChange(filters.page - 1)}
                  >
                    Previous
                  </Button>
                  <span className="px-4 py-2">Page {filters.page}</span>
                  <Button
                    variant="secondary"
                    disabled={!data?.next}
                    onClick={() => handlePageChange(filters.page + 1)}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

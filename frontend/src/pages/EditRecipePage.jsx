import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useRecipe, useUpdateRecipe } from "../hooks/useRecipes";
import { RecipeForm } from "../features/recipes/RecipeForm";
import { Spinner } from "../components/ui";

export function EditRecipePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: recipe, isLoading } = useRecipe(id);
  const updateRecipe = useUpdateRecipe();
  const [error, setError] = useState(null);

  const handleSubmit = async (data) => {
    try {
      setError(null);
      await updateRecipe.mutateAsync({ id, data });
      navigate(`/recipes/${id}`);
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to update recipe. Please try again.";
      setError(message);
      console.error("Failed to update recipe:", err);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!recipe) {
    return <div className="text-center py-12">Recipe not found.</div>;
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Edit Recipe</h1>
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      )}
      <RecipeForm
        initialData={recipe}
        onSubmit={handleSubmit}
        isSubmitting={updateRecipe.isPending}
      />
    </div>
  );
}

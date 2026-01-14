import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCreateRecipe } from "../hooks/useRecipes";
import { RecipeForm } from "../features/recipes/RecipeForm";

export function CreateRecipePage() {
  const navigate = useNavigate();
  const createRecipe = useCreateRecipe();
  const [error, setError] = useState(null);

  const handleSubmit = async (data) => {
    try {
      setError(null);
      const recipe = await createRecipe.mutateAsync(data);
      navigate(`/recipes/${recipe.id}`);
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to create recipe. Please try again.";
      setError(message);
      console.error("Failed to create recipe:", err);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Create New Recipe</h1>
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      )}
      <RecipeForm
        onSubmit={handleSubmit}
        isSubmitting={createRecipe.isPending}
      />
    </div>
  );
}

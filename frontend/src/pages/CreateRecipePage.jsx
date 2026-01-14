import { useNavigate } from "react-router-dom";
import { useCreateRecipe } from "../hooks/useRecipes";
import { RecipeForm } from "../features/recipes/RecipeForm";

export function CreateRecipePage() {
  const navigate = useNavigate();
  const createRecipe = useCreateRecipe();

  const handleSubmit = async (data) => {
    try {
      const recipe = await createRecipe.mutateAsync(data);
      navigate(`/recipes/${recipe.id}`);
    } catch (error) {
      console.error("Failed to create recipe:", error);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Create New Recipe</h1>
      <RecipeForm
        onSubmit={handleSubmit}
        isSubmitting={createRecipe.isPending}
      />
    </div>
  );
}

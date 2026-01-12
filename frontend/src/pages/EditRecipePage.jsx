import { useParams, useNavigate } from 'react-router-dom';
import { useRecipe, useUpdateRecipe } from '../hooks/useRecipes';
import { RecipeForm } from '../features/recipes/RecipeForm';
import { Spinner } from '../components/ui';

export function EditRecipePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: recipe, isLoading } = useRecipe(id);
  const updateRecipe = useUpdateRecipe();

  const handleSubmit = async (data) => {
    try {
      await updateRecipe.mutateAsync({ id, data });
      navigate(`/recipes/${id}`);
    } catch (error) {
      console.error('Failed to update recipe:', error);
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
      <RecipeForm
        initialData={recipe}
        onSubmit={handleSubmit}
        isSubmitting={updateRecipe.isPending}
      />
    </div>
  );
}

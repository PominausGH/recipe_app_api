import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button, Input, Card } from '../../components/ui';
import { IngredientForm } from './IngredientForm';

const difficulties = [
  { value: '', label: 'Select difficulty' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

export function RecipeForm({ initialData, onSubmit, isSubmitting }) {
  const [ingredients, setIngredients] = useState(
    initialData?.ingredients || [{ name: '', quantity: '', unit: 'pieces' }]
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      title: initialData?.title || '',
      description: initialData?.description || '',
      instructions: initialData?.instructions || '',
      prep_time: initialData?.prep_time || '',
      cook_time: initialData?.cook_time || '',
      servings: initialData?.servings || '',
      difficulty: initialData?.difficulty || '',
      is_published: initialData?.is_published ?? true,
    },
  });

  const handleFormSubmit = (data) => {
    const validIngredients = ingredients.filter((ing) => ing.name.trim());
    onSubmit({
      ...data,
      prep_time: data.prep_time ? parseInt(data.prep_time, 10) : null,
      cook_time: data.cook_time ? parseInt(data.cook_time, 10) : null,
      servings: data.servings ? parseInt(data.servings, 10) : null,
      ingredients: validIngredients.map((ing, index) => ({
        ...ing,
        quantity: ing.quantity ? parseFloat(ing.quantity) : null,
        order: index,
      })),
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <Card>
        <Card.Header>
          <h2 className="text-lg font-semibold">Basic Information</h2>
        </Card.Header>
        <Card.Body className="space-y-4">
          <Input
            label="Recipe Title"
            {...register('title', { required: 'Title is required' })}
            error={errors.title?.message}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Brief description of your recipe"
            />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Input
              label="Prep Time (min)"
              type="number"
              {...register('prep_time')}
            />
            <Input
              label="Cook Time (min)"
              type="number"
              {...register('cook_time')}
            />
            <Input
              label="Servings"
              type="number"
              {...register('servings')}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Difficulty
              </label>
              <select
                {...register('difficulty')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                {difficulties.map((d) => (
                  <option key={d.value} value={d.value}>
                    {d.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </Card.Body>
      </Card>

      <Card>
        <Card.Header>
          <h2 className="text-lg font-semibold">Ingredients</h2>
        </Card.Header>
        <Card.Body>
          <IngredientForm ingredients={ingredients} onChange={setIngredients} />
        </Card.Body>
      </Card>

      <Card>
        <Card.Header>
          <h2 className="text-lg font-semibold">Instructions</h2>
        </Card.Header>
        <Card.Body>
          <textarea
            {...register('instructions', { required: 'Instructions are required' })}
            rows={10}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Step by step instructions..."
          />
          {errors.instructions && (
            <p className="mt-1 text-sm text-red-600">{errors.instructions.message}</p>
          )}
        </Card.Body>
      </Card>

      <Card>
        <Card.Body className="flex items-center justify-between">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              {...register('is_published')}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span>Publish recipe (visible to others)</span>
          </label>

          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : 'Save Recipe'}
          </Button>
        </Card.Body>
      </Card>
    </form>
  );
}

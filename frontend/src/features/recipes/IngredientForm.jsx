import { Button, Input } from '../../components/ui';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline';

const unitOptions = [
  { value: 'cups', label: 'Cups' },
  { value: 'tbsp', label: 'Tablespoons' },
  { value: 'tsp', label: 'Teaspoons' },
  { value: 'oz', label: 'Ounces' },
  { value: 'g', label: 'Grams' },
  { value: 'kg', label: 'Kilograms' },
  { value: 'ml', label: 'Milliliters' },
  { value: 'l', label: 'Liters' },
  { value: 'pieces', label: 'Pieces' },
  { value: 'pinch', label: 'Pinch' },
  { value: 'to taste', label: 'To Taste' },
];

export function IngredientForm({ ingredients, onChange }) {
  const handleAdd = () => {
    onChange([...ingredients, { name: '', quantity: '', unit: 'pieces' }]);
  };

  const handleRemove = (index) => {
    onChange(ingredients.filter((_, i) => i !== index));
  };

  const handleChange = (index, field, value) => {
    const updated = ingredients.map((ing, i) =>
      i === index ? { ...ing, [field]: value } : ing
    );
    onChange(updated);
  };

  return (
    <div className="space-y-3">
      {ingredients.map((ing, index) => (
        <div key={index} className="flex gap-2 items-start">
          <div className="flex-1">
            <Input
              placeholder="Ingredient name"
              value={ing.name}
              onChange={(e) => handleChange(index, 'name', e.target.value)}
            />
          </div>
          <div className="w-24">
            <Input
              type="number"
              step="0.1"
              placeholder="Qty"
              value={ing.quantity}
              onChange={(e) => handleChange(index, 'quantity', e.target.value)}
            />
          </div>
          <div className="w-32">
            <select
              value={ing.unit}
              onChange={(e) => handleChange(index, 'unit', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              {unitOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <Button
            type="button"
            variant="ghost"
            onClick={() => handleRemove(index)}
            className="text-red-500"
          >
            <TrashIcon className="h-5 w-5" />
          </Button>
        </div>
      ))}
      <Button type="button" variant="secondary" onClick={handleAdd}>
        <PlusIcon className="h-4 w-4 mr-2" />
        Add Ingredient
      </Button>
    </div>
  );
}

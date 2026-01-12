export function IngredientList({ ingredients }) {
  if (!ingredients?.length) {
    return <p className="text-gray-500">No ingredients listed.</p>;
  }

  return (
    <ul className="space-y-2">
      {ingredients.map((ing, index) => (
        <li key={index} className="flex items-start gap-2">
          <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
          <span>
            {ing.quantity && <strong>{ing.quantity}</strong>}{' '}
            {ing.unit && ing.unit !== 'to taste' && <span>{ing.unit}</span>}{' '}
            {ing.name}
            {ing.unit === 'to taste' && <span className="text-gray-500"> (to taste)</span>}
          </span>
        </li>
      ))}
    </ul>
  );
}

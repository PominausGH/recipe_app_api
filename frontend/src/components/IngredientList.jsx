export function IngredientList({ ingredients }) {
  if (!ingredients?.length) {
    return <p className="text-gray-500">No ingredients listed.</p>;
  }

  const isImportedIngredient = (ing) => {
    // Check if quantity is 0 or 1 with "pieces" unit (imported ingredient markers)
    const qty = Number(ing.quantity);
    if (qty === 0) return true;
    if (qty === 1 && ing.unit === "pieces") {
      // Check if name starts with a number (raw imported text like "2 cups flour")
      return /^\d/.test(ing.name) || /^[½¼¾⅓⅔]/.test(ing.name);
    }
    return false;
  };

  const formatIngredient = (ing) => {
    // Imported ingredient - display name only (contains full text like "2 cups flour")
    if (isImportedIngredient(ing)) {
      return <span>{ing.name}</span>;
    }

    // Manual ingredient with structured data
    return (
      <span>
        <strong>{ing.quantity}</strong>{" "}
        {ing.unit && ing.unit !== "to taste" && <span>{ing.unit}</span>}{" "}
        {ing.name}
        {ing.unit === "to taste" && (
          <span className="text-gray-500"> (to taste)</span>
        )}
      </span>
    );
  };

  return (
    <ul className="space-y-2">
      {ingredients.map((ing, index) => (
        <li key={index} className="flex items-start gap-2">
          <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
          {formatIngredient(ing)}
        </li>
      ))}
    </ul>
  );
}

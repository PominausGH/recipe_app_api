import { Link } from 'react-router-dom';
import { ClockIcon, StarIcon } from '@heroicons/react/24/solid';
import { Card } from './ui';
import { UserLink } from './UserLink';

const difficultyColors = {
  easy: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  hard: 'bg-red-100 text-red-800',
};

export function RecipeCard({ recipe }) {
  const totalTime = (recipe.prep_time || 0) + (recipe.cook_time || 0);

  return (
    <Link to={`/recipes/${recipe.id}`}>
      <Card className="h-full hover:shadow-lg transition-shadow">
        <div className="aspect-video bg-gray-200 relative">
          {recipe.image ? (
            <img
              src={recipe.image}
              alt={recipe.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No Image
            </div>
          )}
          {recipe.difficulty && (
            <span
              className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium ${
                difficultyColors[recipe.difficulty]
              }`}
            >
              {recipe.difficulty}
            </span>
          )}
        </div>
        <Card.Body>
          <h3 className="font-semibold text-lg mb-2 line-clamp-2">{recipe.title}</h3>
          <div className="text-gray-600 text-sm mb-3">
            by <UserLink user={recipe.author} showPhoto={false} />
          </div>
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <StarIcon className="h-4 w-4 text-yellow-400" />
              <span>
                {recipe.average_rating?.toFixed(1) || 'N/A'}
                {recipe.rating_count > 0 && ` (${recipe.rating_count})`}
              </span>
            </div>
            {totalTime > 0 && (
              <div className="flex items-center gap-1">
                <ClockIcon className="h-4 w-4" />
                <span>{totalTime} min</span>
              </div>
            )}
          </div>
        </Card.Body>
      </Card>
    </Link>
  );
}

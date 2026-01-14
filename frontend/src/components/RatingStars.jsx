import { useState } from "react";
import { StarIcon } from "@heroicons/react/24/solid";
import { StarIcon as StarOutlineIcon } from "@heroicons/react/24/outline";

export function RatingStars({
  rating = 0,
  count,
  interactive = false,
  onRate,
  size = "md",
}) {
  const [hoverRating, setHoverRating] = useState(0);

  const sizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6",
  };

  const handleClick = (star) => {
    if (interactive && onRate) {
      onRate(star);
    }
  };

  return (
    <div className="flex items-center gap-1">
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => {
          const filled = interactive
            ? star <= (hoverRating || rating)
            : star <= rating;

          return (
            <button
              key={star}
              type="button"
              disabled={!interactive}
              onClick={() => handleClick(star)}
              onMouseEnter={() => interactive && setHoverRating(star)}
              onMouseLeave={() => interactive && setHoverRating(0)}
              className={`${interactive ? "cursor-pointer" : "cursor-default"}`}
            >
              {filled ? (
                <StarIcon className={`${sizes[size]} text-yellow-400`} />
              ) : (
                <StarOutlineIcon className={`${sizes[size]} text-gray-300`} />
              )}
            </button>
          );
        })}
      </div>
      {count !== undefined && (
        <span className="text-sm text-gray-500 ml-1">({count})</span>
      )}
    </div>
  );
}

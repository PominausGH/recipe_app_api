import { Input, Button } from "./ui";

const difficulties = [
  { value: "", label: "All Difficulties" },
  { value: "easy", label: "Easy" },
  { value: "medium", label: "Medium" },
  { value: "hard", label: "Hard" },
];

const sortOptions = [
  { value: "-created_at", label: "Newest First" },
  { value: "created_at", label: "Oldest First" },
  { value: "-avg_rating", label: "Highest Rated" },
  { value: "prep_time", label: "Quickest" },
];

export function RecipeFilters({ filters, onChange, onClear }) {
  const handleChange = (key, value) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Search
        </label>
        <Input
          type="text"
          placeholder="Search recipes..."
          value={filters.search || ""}
          onChange={(e) => handleChange("search", e.target.value)}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Difficulty
        </label>
        <select
          value={filters.difficulty || ""}
          onChange={(e) => handleChange("difficulty", e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        >
          {difficulties.map((d) => (
            <option key={d.value} value={d.value}>
              {d.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Max Time (minutes)
        </label>
        <Input
          type="number"
          placeholder="e.g., 30"
          value={filters.max_time || ""}
          onChange={(e) => handleChange("max_time", e.target.value)}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Sort By
        </label>
        <select
          value={filters.ordering || "-created_at"}
          onChange={(e) => handleChange("ordering", e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        >
          {sortOptions.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      <Button variant="ghost" onClick={onClear} className="w-full">
        Clear Filters
      </Button>
    </div>
  );
}

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useImportRecipe } from "../hooks/useRecipes";
import { Button, Input } from "../components/ui";

export function ImportRecipePage() {
  const navigate = useNavigate();
  const importRecipe = useImportRecipe();
  const [url, setUrl] = useState("");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!url.trim()) {
      setError("Please enter a URL");
      return;
    }

    try {
      const recipe = await importRecipe.mutateAsync(url);
      navigate(`/recipes/${recipe.id}/edit`);
    } catch (err) {
      const message =
        err.response?.data?.error ||
        err.response?.data?.url?.[0] ||
        "Failed to import recipe. Please try again.";
      setError(message);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Import Recipe from URL</h1>
      <p className="text-gray-600 mb-8">
        Paste a link to a recipe from a supported website and we'll import it
        for you. The recipe will be saved as a draft so you can review and edit
        it before publishing.
      </p>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="url"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Recipe URL
          </label>
          <Input
            id="url"
            type="url"
            placeholder="https://www.allrecipes.com/recipe/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full"
          />
        </div>

        <div className="flex gap-4">
          <Button type="submit" disabled={importRecipe.isPending}>
            {importRecipe.isPending ? "Importing..." : "Import Recipe"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate(-1)}
          >
            Cancel
          </Button>
        </div>
      </form>

      <div className="mt-12">
        <h2 className="text-lg font-semibold mb-4">Supported Websites</h2>
        <p className="text-gray-600 mb-4">
          We support importing from hundreds of popular recipe websites
          including:
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm text-gray-600">
          <span>AllRecipes</span>
          <span>Food Network</span>
          <span>Epicurious</span>
          <span>Bon Appetit</span>
          <span>Serious Eats</span>
          <span>NYT Cooking</span>
          <span>BBC Good Food</span>
          <span>Taste of Home</span>
          <span>Budget Bytes</span>
          <span>Minimalist Baker</span>
          <span>Pinch of Yum</span>
          <span>And many more...</span>
        </div>
      </div>
    </div>
  );
}

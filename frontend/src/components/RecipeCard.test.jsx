import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { RecipeCard } from "./RecipeCard";

const renderRecipeCard = (recipe) => {
  return render(
    <BrowserRouter>
      <RecipeCard recipe={recipe} />
    </BrowserRouter>,
  );
};

const mockRecipe = {
  id: 1,
  title: "Delicious Pasta",
  image: "/pasta.jpg",
  difficulty: "medium",
  prep_time: 15,
  cook_time: 30,
  average_rating: 4.5,
  rating_count: 42,
  author: {
    id: 10,
    name: "Chef John",
    profile_photo: null,
    is_verified: false,
  },
};

describe("RecipeCard", () => {
  describe("basic rendering", () => {
    it("renders recipe title", () => {
      renderRecipeCard(mockRecipe);
      expect(screen.getByText("Delicious Pasta")).toBeInTheDocument();
    });

    it("links to recipe detail page", () => {
      renderRecipeCard(mockRecipe);
      const links = screen.getAllByRole("link");
      const cardLink = links.find(
        (link) => link.getAttribute("href") === "/recipes/1",
      );
      expect(cardLink).toBeInTheDocument();
    });
  });

  describe("image display", () => {
    it("renders recipe image when provided", () => {
      renderRecipeCard(mockRecipe);
      const img = screen.getByRole("img", { name: "Delicious Pasta" });
      expect(img).toHaveAttribute("src", "/pasta.jpg");
    });

    it('shows "No Image" placeholder when image is missing', () => {
      const recipeWithoutImage = { ...mockRecipe, image: null };
      renderRecipeCard(recipeWithoutImage);
      expect(screen.getByText("No Image")).toBeInTheDocument();
    });
  });

  describe("difficulty badge", () => {
    it("renders difficulty badge", () => {
      renderRecipeCard(mockRecipe);
      expect(screen.getByText("medium")).toBeInTheDocument();
    });

    it("applies green styling for easy difficulty", () => {
      const easyRecipe = { ...mockRecipe, difficulty: "easy" };
      renderRecipeCard(easyRecipe);
      const badge = screen.getByText("easy");
      expect(badge).toHaveClass("bg-green-100", "text-green-800");
    });

    it("applies yellow styling for medium difficulty", () => {
      renderRecipeCard(mockRecipe);
      const badge = screen.getByText("medium");
      expect(badge).toHaveClass("bg-yellow-100", "text-yellow-800");
    });

    it("applies red styling for hard difficulty", () => {
      const hardRecipe = { ...mockRecipe, difficulty: "hard" };
      renderRecipeCard(hardRecipe);
      const badge = screen.getByText("hard");
      expect(badge).toHaveClass("bg-red-100", "text-red-800");
    });

    it("does not render difficulty badge when not provided", () => {
      const recipeWithoutDifficulty = { ...mockRecipe, difficulty: null };
      renderRecipeCard(recipeWithoutDifficulty);
      expect(screen.queryByText("easy")).not.toBeInTheDocument();
      expect(screen.queryByText("medium")).not.toBeInTheDocument();
      expect(screen.queryByText("hard")).not.toBeInTheDocument();
    });
  });

  describe("author display", () => {
    it("renders author name", () => {
      renderRecipeCard(mockRecipe);
      expect(screen.getByText("Chef John")).toBeInTheDocument();
    });

    it('renders "by" text before author', () => {
      renderRecipeCard(mockRecipe);
      expect(screen.getByText(/by/)).toBeInTheDocument();
    });

    it("renders author as text (not link) to avoid nested links", () => {
      renderRecipeCard(mockRecipe);
      // Only one link should exist - the card link to recipe detail
      const links = screen.getAllByRole("link");
      expect(links).toHaveLength(1);
      expect(links[0]).toHaveAttribute("href", "/recipes/1");
    });
  });

  describe("rating display", () => {
    it("renders average rating", () => {
      renderRecipeCard(mockRecipe);
      expect(screen.getByText(/4\.5/)).toBeInTheDocument();
    });

    it("renders rating count in parentheses", () => {
      renderRecipeCard(mockRecipe);
      expect(screen.getByText(/\(42\)/)).toBeInTheDocument();
    });

    it('shows "N/A" when no average rating', () => {
      const unratedRecipe = {
        ...mockRecipe,
        average_rating: null,
        rating_count: 0,
      };
      renderRecipeCard(unratedRecipe);
      expect(screen.getByText("N/A")).toBeInTheDocument();
    });

    it("does not show rating count when zero", () => {
      const unratedRecipe = {
        ...mockRecipe,
        average_rating: 3.0,
        rating_count: 0,
      };
      renderRecipeCard(unratedRecipe);
      expect(screen.getByText("3.0")).toBeInTheDocument();
      expect(screen.queryByText(/\(0\)/)).not.toBeInTheDocument();
    });

    it("formats rating to one decimal place", () => {
      const preciseRatingRecipe = { ...mockRecipe, average_rating: 4.567 };
      renderRecipeCard(preciseRatingRecipe);
      expect(screen.getByText(/4\.6/)).toBeInTheDocument();
    });
  });

  describe("time display", () => {
    it("renders total time (prep + cook)", () => {
      renderRecipeCard(mockRecipe);
      expect(screen.getByText("45 min")).toBeInTheDocument();
    });

    it("shows only prep time when cook time is missing", () => {
      const prepOnlyRecipe = { ...mockRecipe, prep_time: 20, cook_time: null };
      renderRecipeCard(prepOnlyRecipe);
      expect(screen.getByText("20 min")).toBeInTheDocument();
    });

    it("shows only cook time when prep time is missing", () => {
      const cookOnlyRecipe = { ...mockRecipe, prep_time: null, cook_time: 25 };
      renderRecipeCard(cookOnlyRecipe);
      expect(screen.getByText("25 min")).toBeInTheDocument();
    });

    it("does not render time when both prep and cook time are zero", () => {
      const noTimeRecipe = { ...mockRecipe, prep_time: 0, cook_time: 0 };
      renderRecipeCard(noTimeRecipe);
      expect(screen.queryByText(/min/)).not.toBeInTheDocument();
    });

    it("does not render time when both prep and cook time are null", () => {
      const noTimeRecipe = { ...mockRecipe, prep_time: null, cook_time: null };
      renderRecipeCard(noTimeRecipe);
      expect(screen.queryByText(/min/)).not.toBeInTheDocument();
    });
  });
});

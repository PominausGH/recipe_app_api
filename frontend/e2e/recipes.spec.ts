import { test, expect } from '@playwright/test';

test.describe('Recipe Browsing', () => {
  test('recipes page displays recipe list', async ({ page }) => {
    await page.goto('/recipes');
    // Wait for the page to load
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('recipe cards are clickable', async ({ page }) => {
    await page.goto('/recipes');
    // If there are recipes, clicking one should navigate to detail page
    const recipeCard = page.locator('a[href^="/recipes/"]').first();
    if (await recipeCard.isVisible()) {
      await recipeCard.click();
      await expect(page).toHaveURL(/\/recipes\/\d+/);
    }
  });

  test('recipe filters are visible', async ({ page }) => {
    await page.goto('/recipes');
    // Check for filter elements (search, difficulty, etc.)
    await expect(page.locator('input[type="search"], input[placeholder*="earch"]').first()).toBeVisible();
  });
});

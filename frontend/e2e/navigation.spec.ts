import { test, expect } from "@playwright/test";

test.describe("Navigation", () => {
  test("homepage loads successfully", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/Recipe/i);
  });

  test("can navigate to recipes page", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Recipes");
    await expect(page).toHaveURL(/\/recipes/);
  });

  test("can navigate to login page", async ({ page }) => {
    await page.goto("/");
    await page.click("text=Login");
    await expect(page).toHaveURL(/\/login/);
  });

  test("can navigate to register page", async ({ page }) => {
    await page.goto("/login");
    await page.click("text=Sign up");
    await expect(page).toHaveURL(/\/register/);
  });

  test("404 page shows for invalid routes", async ({ page }) => {
    await page.goto("/invalid-route-that-does-not-exist");
    await expect(page.locator("text=Page Not Found")).toBeVisible();
  });
});

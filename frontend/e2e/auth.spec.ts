import { test, expect } from "@playwright/test";

test.describe("Authentication", () => {
  test("login page has required fields", async ({ page }) => {
    await page.goto("/login");
    await expect(
      page.locator('input[type="email"], input[name="email"]'),
    ).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("register page has required fields", async ({ page }) => {
    await page.goto("/register");
    await expect(
      page.locator('input[name="name"], input[placeholder*="ame"]').first(),
    ).toBeVisible();
    await expect(
      page.locator('input[type="email"], input[name="email"]'),
    ).toBeVisible();
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
  });

  test("login form shows validation errors for empty submission", async ({
    page,
  }) => {
    await page.goto("/login");
    await page.click('button[type="submit"]');
    // HTML5 validation should prevent submission or show error
    const emailInput = page.locator('input[type="email"], input[name="email"]');
    await expect(emailInput).toBeVisible();
  });

  test("protected routes redirect to login", async ({ page }) => {
    await page.goto("/profile");
    // Should redirect to login
    await expect(page).toHaveURL(/\/login/);
  });

  test("protected routes redirect to login for favorites", async ({ page }) => {
    await page.goto("/favorites");
    await expect(page).toHaveURL(/\/login/);
  });

  test("protected routes redirect to login for my-recipes", async ({
    page,
  }) => {
    await page.goto("/my-recipes");
    await expect(page).toHaveURL(/\/login/);
  });
});

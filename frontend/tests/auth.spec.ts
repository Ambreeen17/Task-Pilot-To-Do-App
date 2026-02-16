import { expect, test } from "@playwright/test";

test("landing page links", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("2do")).toBeVisible();
  await expect(page.getByRole("link", { name: "Sign in" })).toHaveAttribute("href", "/login");
  await expect(page.getByRole("link", { name: "Create account" })).toHaveAttribute("href", "/signup");
});

test("tasks page prompts for login when signed out", async ({ page }) => {
  await page.goto("/tasks");
  await expect(page.getByText("Not signed in")).toBeVisible();
  await expect(page.getByRole("button", { name: "Go to login" })).toBeVisible();
});

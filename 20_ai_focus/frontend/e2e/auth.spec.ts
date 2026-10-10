import { test, expect } from '@playwright/test';

test.describe('Authentication Journey', () => {
  test('validates required form fields and shows error states', async ({ page }) => {
    await page.goto('/login');

    // Click Sign In without entering data
    await page.getByTestId('login-submit-btn').click();

    // Verify Zod validation messages
    await expect(page.getByText(/username must be at least 3 characters/i)).toBeVisible();
    await expect(page.getByText(/password must be at least 6 characters/i)).toBeVisible();
  });

  test('successfully signs in with test credentials and navigates home', async ({ page }) => {
    await page.goto('/login');

    await page.getByTestId('username-input').fill('admin');
    await page.getByTestId('password-input').fill('secret123');
    await page.getByTestId('login-submit-btn').click();

    // Wait for redirect to home or admin dashboard
    await page.waitForURL(/.*5173(\/admin|\/)?$/);

    // Verify logged in user is displayed in navbar
    await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
  });
});

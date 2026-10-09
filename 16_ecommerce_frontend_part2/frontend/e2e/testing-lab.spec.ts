import { test, expect } from '@playwright/test';

test.describe('Testing Lab Interactive Features', () => {
  test('navigates to Testing Lab and cycles union state transitions', async ({ page }) => {
    await page.goto('/testing-lab');

    // Verify main heading
    await expect(
      page.getByRole('heading', { name: /typescript & component testing showcase lab/i })
    ).toBeVisible();

    // Verify state machine starts idle
    await expect(page.getByText(/state is idle/i)).toBeVisible();

    // Click "Loading" state
    await page.getByRole('button', { name: 'Loading', exact: true }).click();
    await expect(page.getByText(/executing background operation/i)).toBeVisible();

    // Click "Success" state
    await page.getByRole('button', { name: 'Success', exact: true }).click();
    await expect(page.getByText(/transaction processed type-safely/i)).toBeVisible();

    // Click "Error" state
    await page.getByRole('button', { name: 'Error', exact: true }).click();
    await expect(page.getByText(/validation failed with schema mismatch/i)).toBeVisible();
  });

  test('verifies test suite matrix table is rendered with passing status', async ({ page }) => {
    await page.goto('/testing-lab');

    // Verify test table headers
    await expect(page.getByRole('cell', { name: 'Button.test.tsx' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'ProductCard.test.tsx' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'LoginForm.test.tsx' })).toBeVisible();
  });
});

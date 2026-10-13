import { test, expect } from '@playwright/test';

test.describe('Product Catalog & Navigation', () => {
  test('loads product catalog and renders products', async ({ page }) => {
    await page.goto('/');

    // Check header
    await expect(page.getByRole('heading', { name: /sivora|e-commerce/i }).first()).toBeVisible();

    // Verify search input is visible
    const searchInput = page.getByTestId('search-input');
    await expect(searchInput).toBeVisible();

    // Verify at least one product card renders
    const productCard = page.locator('[data-testid^="product-card-"]').first();
    await expect(productCard).toBeVisible();
  });

  test('searches products and filters grid', async ({ page }) => {
    await page.goto('/');

    const searchInput = page.getByTestId('search-input');
    await searchInput.fill('Keyboard');

    // Wait for debounced search to filter
    await page.waitForTimeout(1000);

    // Verify keyboard is displayed
    await expect(page.getByRole('link', { name: /keyboard/i })).toBeVisible({ timeout: 10000 });
  });

  test('navigates to product detail page and back', async ({ page }) => {
    await page.goto('/');

    // Click on the first product link
    const firstProductLink = page.locator('[data-testid^="product-card-"] a').first();
    await firstProductLink.click();

    // Verify on detail page
    await expect(page.getByTestId('detail-add-to-cart-btn')).toBeVisible();

    // Click back to products
    await page.getByRole('link', { name: /back to products/i }).click();
    await expect(page).toHaveURL(/.*5173\/?$/);
  });
});

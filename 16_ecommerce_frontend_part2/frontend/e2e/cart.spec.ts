import { test, expect } from '@playwright/test';

test.describe('Shopping Cart Flow', () => {
  test('adds product to cart, updates badge, and modifies quantity', async ({ page }) => {
    await page.goto('/');

    // Wait for product cards to load
    const firstAddBtn = page.locator('[data-testid^="add-to-cart-btn-"]').first();
    await expect(firstAddBtn).toBeVisible();

    // Click "Add to Cart"
    await firstAddBtn.click();

    // Verify nav cart badge displays "1"
    const cartBadge = page.getByTestId('cart-badge-count');
    await expect(cartBadge).toHaveText('1');

    // Navigate to Cart Page
    await page.getByTestId('nav-cart-link').click();
    await expect(page).toHaveURL(/.*\/cart/);

    // Verify cart subtotal is greater than 0
    const subtotal = page.getByTestId('cart-subtotal');
    await expect(subtotal).toBeVisible();

    // Verify Checkout CTA is visible
    const checkoutBtn = page.getByTestId('checkout-button');
    await expect(checkoutBtn).toBeVisible();
  });

  test('clears cart and displays empty cart view', async ({ page }) => {
    await page.goto('/');

    // Add item to cart
    const firstAddBtn = page.locator('[data-testid^="add-to-cart-btn-"]').first();
    await firstAddBtn.click();

    // Navigate to cart
    await page.goto('/cart');

    // Click Clear Cart
    const clearBtn = page.getByTestId('clear-cart-btn');
    await clearBtn.click();

    // Verify empty state is displayed
    await expect(page.getByTestId('empty-cart-state')).toBeVisible();
    await expect(page.getByText(/your cart is empty/i)).toBeVisible();
  });
});

# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: catalog.spec.ts >> Product Catalog & Navigation >> loads product catalog and renders products
- Location: e2e\catalog.spec.ts:4:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('heading', { name: /type-safe react e-commerce/i })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('heading', { name: /type-safe react e-commerce/i }) with timeout 5000ms
  - waiting for getByRole('heading', { name: /type-safe react e-commerce/i })

```

```yaml
- banner:
  - link "Gunturu TypeScript & Vitest E-Shop":
    - /url: /
    - img
    - text: Gunturu TypeScript & Vitest E-Shop
  - navigation "Main Navigation":
    - link "Products":
      - /url: /
    - link "Orders":
      - /url: /orders
    - link "Wishlist":
      - /url: /wishlist
      - img
      - text: Wishlist
  - button "Toggle theme":
    - img
  - link "Shopping cart with 0 items":
    - /url: /cart
    - img
  - link "Sign In":
    - /url: /login
    - button "Sign In"
- main:
  - img
  - text: Welcome to Gunturu Store
  - heading "Gunturu E-Commerce" [level=1]
  - paragraph: Premium Electronics & Everyday Essentials delivered directly to your doorstep. Use coupon SAVE10 for 10% instant discount at checkout!
  - img
  - text: Free Shipping above ₹100
  - img
  - text: 100% Genuine Verified Products
  - img
  - textbox "Search products":
    - /placeholder: Search products by title...
  - button "All Products"
  - button "Accessories"
  - button "Audio"
  - button "Cameras & Drones"
  - button "Gaming & VR"
  - button "Laptops & Computers"
  - button "Peripherals"
  - button "Smart Home"
  - button "Wearables"
  - button "bottel"
  - button "friuts"
  - button "table"
  - button "Save samsung tv to wishlist":
    - img
  - text: Smart Home In Stock
  - paragraph: Smart Home
  - link "samsung tv":
    - /url: /products/17
  - paragraph: good quality
  - text: Price $64.00
  - button "Add samsung tv to cart":
    - img
    - text: Add to Cart
  - button "Save Apple MacBook Pro 16\" M3 Max to wishlist":
    - img
  - img "Apple MacBook Pro 16\" M3 Max"
  - text: In Stock
  - paragraph: Laptops & Computers
  - link "Apple MacBook Pro 16\" M3 Max":
    - /url: /products/7
  - paragraph: 36GB unified memory, 1TB SSD, Liquid Retina XDR display with ProMotion.
  - text: Price $3499.00
  - button "Add Apple MacBook Pro 16\" M3 Max to cart":
    - img
    - text: Add to Cart
  - button "Save Dell XPS 15 InfinityEdge OLED Laptop to wishlist":
    - img
  - img "Dell XPS 15 InfinityEdge OLED Laptop"
  - text: In Stock
  - paragraph: Laptops & Computers
  - link "Dell XPS 15 InfinityEdge OLED Laptop":
    - /url: /products/8
  - paragraph: Intel Core i9 13th Gen, 32GB RAM, NVIDIA RTX 4070, 3.5K OLED touch display.
  - text: Price $2299.99
  - button "Add Dell XPS 15 InfinityEdge OLED Laptop to cart":
    - img
    - text: Add to Cart
  - button "Save Sony PlayStation 5 Slim Console to wishlist":
    - img
  - img "Sony PlayStation 5 Slim Console"
  - text: In Stock
  - paragraph: Gaming & VR
  - link "Sony PlayStation 5 Slim Console":
    - /url: /products/9
  - paragraph: Experience lightning-fast loading with an ultra-high speed SSD and 4K 120Hz support.
  - text: Price $499.99
  - button "Add Sony PlayStation 5 Slim Console to cart":
    - img
    - text: Add to Cart
  - button "Save Meta Quest 3 512GB VR Headset to wishlist":
    - img
  - img "Meta Quest 3 512GB VR Headset"
  - text: In Stock
  - paragraph: Gaming & VR
  - link "Meta Quest 3 512GB VR Headset":
    - /url: /products/10
  - paragraph: Breakthrough mixed reality headset with 4K+ Infinite Display and 3D spatial audio.
  - text: Price $649.99
  - button "Add Meta Quest 3 512GB VR Headset to cart":
    - img
    - text: Add to Cart
  - button "Save Xbox Wireless Controller - Carbon Black to wishlist":
    - img
  - img "Xbox Wireless Controller - Carbon Black"
  - text: In Stock
  - paragraph: Gaming & VR
  - link "Xbox Wireless Controller - Carbon Black":
    - /url: /products/11
  - paragraph: Sculpted surfaces, hybrid D-pad, textured grip, and Bluetooth compatibility.
  - text: Price $59.99
  - button "Add Xbox Wireless Controller - Carbon Black to cart":
    - img
    - text: Add to Cart
  - button "Save DJI Mini 4 Pro 4K Drone to wishlist":
    - img
  - img "DJI Mini 4 Pro 4K Drone"
  - text: In Stock
  - paragraph: Cameras & Drones
  - link "DJI Mini 4 Pro 4K Drone":
    - /url: /products/12
  - paragraph: Under 249g folding drone with omnidirectional active obstacle sensing and 4K/60fps HDR.
  - text: Price $759.00
  - button "Add DJI Mini 4 Pro 4K Drone to cart":
    - img
    - text: Add to Cart
  - button "Save Fujifilm X-T5 Mirrorless Camera Body to wishlist":
    - img
  - img "Fujifilm X-T5 Mirrorless Camera Body"
  - text: In Stock
  - paragraph: Cameras & Drones
  - link "Fujifilm X-T5 Mirrorless Camera Body":
    - /url: /products/13
  - paragraph: 40.2MP X-Trans CMOS 5 HR sensor, 6.2K movie recording, and 5-axis IBIS.
  - text: Price $1699.99
  - button "Add Fujifilm X-T5 Mirrorless Camera Body to cart":
    - img
    - text: Add to Cart
  - button "Save Amazon Echo Studio Smart Hi-Fi Speaker to wishlist":
    - img
  - img "Amazon Echo Studio Smart Hi-Fi Speaker"
  - text: In Stock
  - paragraph: Smart Home
  - link "Amazon Echo Studio Smart Hi-Fi Speaker":
    - /url: /products/14
  - paragraph: Immersive 3D audio with Dolby Atmos, Alexa built-in, and spatial room adaptation.
  - text: Price $199.99
  - button "Add Amazon Echo Studio Smart Hi-Fi Speaker to cart":
    - img
    - text: Add to Cart
  - button "Save Bose QuietComfort Ultra Wireless Earbuds to wishlist":
    - img
  - img "Bose QuietComfort Ultra Wireless Earbuds"
  - text: In Stock
  - paragraph: Audio
  - link "Bose QuietComfort Ultra Wireless Earbuds":
    - /url: /products/15
  - paragraph: World-class noise cancellation, CustomTune technology, and immersive spatial audio.
  - text: Price $299.00
  - button "Add Bose QuietComfort Ultra Wireless Earbuds to cart":
    - img
    - text: Add to Cart
- contentinfo:
  - img
  - text: Day 16 Architecture
  - img
  - text: Zustand Cart + Zod Checkout
  - img
  - text: Orders + Admin Dashboard
  - img
  - text: TanStack React Query + Dark/Light Theme
  - img
  - text: Live FastAPI Fullstack
  - paragraph: © 2026 Gunturu E-Commerce Fullstack Hub. All rights reserved.
  - link "Store Catalog":
    - /url: /
  - link "FastAPI Swagger Docs":
    - /url: http://127.0.0.1:8000/docs
- region "Notifications alt+T"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Product Catalog & Navigation', () => {
  4  |   test('loads product catalog and renders products', async ({ page }) => {
  5  |     await page.goto('/');
  6  | 
  7  |     // Check header
> 8  |     await expect(page.getByRole('heading', { name: /type-safe react e-commerce/i })).toBeVisible();
     |                                                                                      ^ Error: expect(locator).toBeVisible() failed
  9  | 
  10 |     // Verify search input is visible
  11 |     const searchInput = page.getByTestId('search-input');
  12 |     await expect(searchInput).toBeVisible();
  13 | 
  14 |     // Verify at least one product card renders
  15 |     const productCard = page.locator('[data-testid^="product-card-"]').first();
  16 |     await expect(productCard).toBeVisible();
  17 |   });
  18 | 
  19 |   test('searches products and filters grid', async ({ page }) => {
  20 |     await page.goto('/');
  21 | 
  22 |     const searchInput = page.getByTestId('search-input');
  23 |     await searchInput.fill('Keyboard');
  24 | 
  25 |     // Wait for debounced search to filter
  26 |     await page.waitForTimeout(1000);
  27 | 
  28 |     // Verify keyboard is displayed
  29 |     await expect(page.getByRole('link', { name: /keyboard/i })).toBeVisible({ timeout: 10000 });
  30 |   });
  31 | 
  32 |   test('navigates to product detail page and back', async ({ page }) => {
  33 |     await page.goto('/');
  34 | 
  35 |     // Click on the first product link
  36 |     const firstProductLink = page.locator('[data-testid^="product-card-"] a').first();
  37 |     await firstProductLink.click();
  38 | 
  39 |     // Verify on detail page
  40 |     await expect(page.getByTestId('detail-add-to-cart-btn')).toBeVisible();
  41 | 
  42 |     // Click back to products
  43 |     await page.getByRole('link', { name: /back to products/i }).click();
  44 |     await expect(page).toHaveURL(/.*5173\/?$/);
  45 |   });
  46 | });
  47 | 
```
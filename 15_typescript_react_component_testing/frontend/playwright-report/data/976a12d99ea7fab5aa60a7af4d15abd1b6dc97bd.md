# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: testing-lab.spec.ts >> Testing Lab Interactive Features >> verifies test suite matrix table is rendered with passing status
- Location: e2e\testing-lab.spec.ts:28:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.goto: Test timeout of 30000ms exceeded.
Call log:
  - navigating to "http://localhost:5173/testing-lab", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Testing Lab Interactive Features', () => {
  4  |   test('navigates to Testing Lab and cycles union state transitions', async ({ page }) => {
  5  |     await page.goto('/testing-lab');
  6  | 
  7  |     // Verify main heading
  8  |     await expect(
  9  |       page.getByRole('heading', { name: /typescript & component testing showcase lab/i })
  10 |     ).toBeVisible();
  11 | 
  12 |     // Verify state machine starts idle
  13 |     await expect(page.getByText(/state is idle/i)).toBeVisible();
  14 | 
  15 |     // Click "Loading" state
  16 |     await page.getByRole('button', { name: /loading/i }).click();
  17 |     await expect(page.getByText(/executing background operation/i)).toBeVisible();
  18 | 
  19 |     // Click "Success" state
  20 |     await page.getByRole('button', { name: /success/i }).click();
  21 |     await expect(page.getByText(/transaction processed type-safely/i)).toBeVisible();
  22 | 
  23 |     // Click "Error" state
  24 |     await page.getByRole('button', { name: /error/i }).click();
  25 |     await expect(page.getByText(/validation failed with schema mismatch/i)).toBeVisible();
  26 |   });
  27 | 
  28 |   test('verifies test suite matrix table is rendered with passing status', async ({ page }) => {
> 29 |     await page.goto('/testing-lab');
     |                ^ Error: page.goto: Test timeout of 30000ms exceeded.
  30 | 
  31 |     // Verify test table headers
  32 |     await expect(page.getByRole('cell', { name: 'Button.test.tsx' })).toBeVisible();
  33 |     await expect(page.getByRole('cell', { name: 'ProductCard.test.tsx' })).toBeVisible();
  34 |     await expect(page.getByRole('cell', { name: 'LoginForm.test.tsx' })).toBeVisible();
  35 |   });
  36 | });
  37 | 
```
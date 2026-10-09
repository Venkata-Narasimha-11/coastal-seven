# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Authentication Journey >> successfully signs in with test credentials and navigates home
- Location: e2e\auth.spec.ts:15:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.waitForURL: Test timeout of 30000ms exceeded.
=========================== logs ===========================
waiting for navigation until "load"
  navigated to "http://127.0.0.1:5173/admin"
============================================================
```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e4]:
    - generic [ref=e6]:
      - generic [ref=e7]:
        - link "Gunturu TypeScript & Vitest E-Shop" [ref=e8] [cursor=pointer]:
          - /url: /
          - generic [ref=e15]: Gunturu
          - generic [ref=e16]: TypeScript & Vitest E-Shop
        - navigation "Main Navigation" [ref=e17]:
          - link "Admin Dashboard" [ref=e18] [cursor=pointer]:
            - /url: /admin
          - link "Storefront View" [ref=e23] [cursor=pointer]:
            - /url: /
          - link "Admin Profile" [ref=e24] [cursor=pointer]:
            - /url: /profile
      - generic [ref=e29]:
        - button "Toggle theme" [ref=e30] [cursor=pointer]
        - generic [ref=e33]:
          - link "admin Admin" [ref=e34] [cursor=pointer]:
            - /url: /profile
            - generic [ref=e39]: admin
            - generic [ref=e40]: Admin
          - button "Logout" [ref=e41] [cursor=pointer]
  - main [ref=e46]:
    - generic [ref=e48]:
      - generic [ref=e49]:
        - generic [ref=e50]:
          - heading "Admin Control Hub" [level=1] [ref=e56]
          - paragraph [ref=e57]: Centralized product catalog CRUD operations and real-time customer order management.
        - generic [ref=e58]:
          - button "Products (17)" [ref=e59] [cursor=pointer]
          - button "Orders (3)" [ref=e65] [cursor=pointer]
          - button "Analytics & KPIs" [ref=e71] [cursor=pointer]
      - generic [ref=e76]:
        - generic [ref=e77]:
          - textbox "Search products by name or category..." [ref=e82]
          - button "Add New Product" [ref=e83] [cursor=pointer]
        - table [ref=e88]:
          - rowgroup [ref=e89]:
            - row [ref=e90]:
              - columnheader "Product" [ref=e91]
              - columnheader "Category" [ref=e92]
              - columnheader "Price" [ref=e93]
              - columnheader "Stock" [ref=e94]
              - columnheader "Actions" [ref=e95]
          - rowgroup [ref=e96]:
            - row [ref=e97]:
              - cell [ref=e98]:
                - generic [ref=e99]:
                  - img "samsung tv" [ref=e100]
                  - generic [ref=e101]:
                    - paragraph [ref=e102]: samsung tv
                    - paragraph [ref=e103]: "ID: #17"
              - cell "Smart Home" [ref=e104]
              - cell "₹64.00" [ref=e105]
              - cell "57 in stock" [ref=e106]
              - cell [ref=e108]:
                - generic [ref=e109]:
                  - button "Edit" [ref=e110] [cursor=pointer]
                  - button "Delete" [ref=e115] [cursor=pointer]
            - row [ref=e120]:
              - cell [ref=e121]:
                - generic [ref=e122]:
                  - img "Apple MacBook Pro 16\" M3 Max" [ref=e123]
                  - generic [ref=e124]:
                    - paragraph [ref=e125]: Apple MacBook Pro 16" M3 Max
                    - paragraph [ref=e126]: "ID: #7"
              - cell "Laptops & Computers" [ref=e127]
              - cell "₹3499.00" [ref=e128]
              - cell "88 in stock" [ref=e129]
              - cell [ref=e131]:
                - generic [ref=e132]:
                  - button "Edit" [ref=e133] [cursor=pointer]
                  - button "Delete" [ref=e138] [cursor=pointer]
            - row [ref=e143]:
              - cell [ref=e144]:
                - generic [ref=e145]:
                  - img "Dell XPS 15 InfinityEdge OLED Laptop" [ref=e146]
                  - generic [ref=e147]:
                    - paragraph [ref=e148]: Dell XPS 15 InfinityEdge OLED Laptop
                    - paragraph [ref=e149]: "ID: #8"
              - cell "Laptops & Computers" [ref=e150]
              - cell "₹2299.99" [ref=e151]
              - cell "14 in stock" [ref=e152]
              - cell [ref=e154]:
                - generic [ref=e155]:
                  - button "Edit" [ref=e156] [cursor=pointer]
                  - button "Delete" [ref=e161] [cursor=pointer]
            - row [ref=e166]:
              - cell [ref=e167]:
                - generic [ref=e168]:
                  - img "Sony PlayStation 5 Slim Console" [ref=e169]
                  - generic [ref=e170]:
                    - paragraph [ref=e171]: Sony PlayStation 5 Slim Console
                    - paragraph [ref=e172]: "ID: #9"
              - cell "Gaming & VR" [ref=e173]
              - cell "₹499.99" [ref=e174]
              - cell "10 in stock" [ref=e175]
              - cell [ref=e177]:
                - generic [ref=e178]:
                  - button "Edit" [ref=e179] [cursor=pointer]
                  - button "Delete" [ref=e184] [cursor=pointer]
            - row [ref=e189]:
              - cell [ref=e190]:
                - generic [ref=e191]:
                  - img "Meta Quest 3 512GB VR Headset" [ref=e192]
                  - generic [ref=e193]:
                    - paragraph [ref=e194]: Meta Quest 3 512GB VR Headset
                    - paragraph [ref=e195]: "ID: #10"
              - cell "Gaming & VR" [ref=e196]
              - cell "₹649.99" [ref=e197]
              - cell "15 in stock" [ref=e198]
              - cell [ref=e200]:
                - generic [ref=e201]:
                  - button "Edit" [ref=e202] [cursor=pointer]
                  - button "Delete" [ref=e207] [cursor=pointer]
            - row [ref=e212]:
              - cell [ref=e213]:
                - generic [ref=e214]:
                  - img "Xbox Wireless Controller - Carbon Black" [ref=e215]
                  - generic [ref=e216]:
                    - paragraph [ref=e217]: Xbox Wireless Controller - Carbon Black
                    - paragraph [ref=e218]: "ID: #11"
              - cell "Gaming & VR" [ref=e219]
              - cell "₹59.99" [ref=e220]
              - cell "45 in stock" [ref=e221]
              - cell [ref=e223]:
                - generic [ref=e224]:
                  - button "Edit" [ref=e225] [cursor=pointer]
                  - button "Delete" [ref=e230] [cursor=pointer]
            - row [ref=e235]:
              - cell [ref=e236]:
                - generic [ref=e237]:
                  - img "DJI Mini 4 Pro 4K Drone" [ref=e238]
                  - generic [ref=e239]:
                    - paragraph [ref=e240]: DJI Mini 4 Pro 4K Drone
                    - paragraph [ref=e241]: "ID: #12"
              - cell "Cameras & Drones" [ref=e242]
              - cell "₹759.00" [ref=e243]
              - cell "8 in stock" [ref=e244]
              - cell [ref=e246]:
                - generic [ref=e247]:
                  - button "Edit" [ref=e248] [cursor=pointer]
                  - button "Delete" [ref=e253] [cursor=pointer]
            - row [ref=e258]:
              - cell [ref=e259]:
                - generic [ref=e260]:
                  - img "Fujifilm X-T5 Mirrorless Camera Body" [ref=e261]
                  - generic [ref=e262]:
                    - paragraph [ref=e263]: Fujifilm X-T5 Mirrorless Camera Body
                    - paragraph [ref=e264]: "ID: #13"
              - cell "Cameras & Drones" [ref=e265]
              - cell "₹1699.99" [ref=e266]
              - cell "6 in stock" [ref=e267]
              - cell [ref=e269]:
                - generic [ref=e270]:
                  - button "Edit" [ref=e271] [cursor=pointer]
                  - button "Delete" [ref=e276] [cursor=pointer]
            - row [ref=e281]:
              - cell [ref=e282]:
                - generic [ref=e283]:
                  - img "Amazon Echo Studio Smart Hi-Fi Speaker" [ref=e284]
                  - generic [ref=e285]:
                    - paragraph [ref=e286]: Amazon Echo Studio Smart Hi-Fi Speaker
                    - paragraph [ref=e287]: "ID: #14"
              - cell "Smart Home" [ref=e288]
              - cell "₹199.99" [ref=e289]
              - cell "30 in stock" [ref=e290]
              - cell [ref=e292]:
                - generic [ref=e293]:
                  - button "Edit" [ref=e294] [cursor=pointer]
                  - button "Delete" [ref=e299] [cursor=pointer]
            - row [ref=e304]:
              - cell [ref=e305]:
                - generic [ref=e306]:
                  - img "Bose QuietComfort Ultra Wireless Earbuds" [ref=e307]
                  - generic [ref=e308]:
                    - paragraph [ref=e309]: Bose QuietComfort Ultra Wireless Earbuds
                    - paragraph [ref=e310]: "ID: #15"
              - cell "Audio" [ref=e311]
              - cell "₹299.00" [ref=e312]
              - cell "22 in stock" [ref=e313]
              - cell [ref=e315]:
                - generic [ref=e316]:
                  - button "Edit" [ref=e317] [cursor=pointer]
                  - button "Delete" [ref=e322] [cursor=pointer]
            - row [ref=e327]:
              - cell [ref=e328]:
                - generic [ref=e329]:
                  - img "Samsung Galaxy Watch 6 Classic" [ref=e330]
                  - generic [ref=e331]:
                    - paragraph [ref=e332]: Samsung Galaxy Watch 6 Classic
                    - paragraph [ref=e333]: "ID: #16"
              - cell "Wearables" [ref=e334]
              - cell "₹329.99" [ref=e335]
              - cell "16 in stock" [ref=e336]
              - cell [ref=e338]:
                - generic [ref=e339]:
                  - button "Edit" [ref=e340] [cursor=pointer]
                  - button "Delete" [ref=e345] [cursor=pointer]
            - row [ref=e350]:
              - cell [ref=e351]:
                - generic [ref=e352]:
                  - img "Sony WH-1000XM5 Wireless Headphones" [ref=e353]
                  - generic [ref=e354]:
                    - paragraph [ref=e355]: Sony WH-1000XM5 Wireless Headphones
                    - paragraph [ref=e356]: "ID: #1"
              - cell "Audio" [ref=e357]
              - cell "₹349.99" [ref=e358]
              - cell "15 in stock" [ref=e359]
              - cell [ref=e361]:
                - generic [ref=e362]:
                  - button "Edit" [ref=e363] [cursor=pointer]
                  - button "Delete" [ref=e368] [cursor=pointer]
            - row [ref=e373]:
              - cell [ref=e374]:
                - generic [ref=e375]:
                  - img "Apple Watch Series 9 GPS 45mm" [ref=e376]
                  - generic [ref=e377]:
                    - paragraph [ref=e378]: Apple Watch Series 9 GPS 45mm
                    - paragraph [ref=e379]: "ID: #2"
              - cell "Wearables" [ref=e380]
              - cell "₹399.00" [ref=e381]
              - cell "12 in stock" [ref=e382]
              - cell [ref=e384]:
                - generic [ref=e385]:
                  - button "Edit" [ref=e386] [cursor=pointer]
                  - button "Delete" [ref=e391] [cursor=pointer]
            - row [ref=e396]:
              - cell [ref=e397]:
                - generic [ref=e398]:
                  - img "RGB Mechanical Gaming Keyboard" [ref=e399]
                  - generic [ref=e400]:
                    - paragraph [ref=e401]: RGB Mechanical Gaming Keyboard
                    - paragraph [ref=e402]: "ID: #3"
              - cell "Peripherals" [ref=e403]
              - cell "₹129.50" [ref=e404]
              - cell "25 in stock" [ref=e405]
              - cell [ref=e407]:
                - generic [ref=e408]:
                  - button "Edit" [ref=e409] [cursor=pointer]
                  - button "Delete" [ref=e414] [cursor=pointer]
            - row [ref=e419]:
              - cell [ref=e420]:
                - generic [ref=e421]:
                  - img "Ultra-Wide 34-Inch Curved Gaming Monitor" [ref=e422]
                  - generic [ref=e423]:
                    - paragraph [ref=e424]: Ultra-Wide 34-Inch Curved Gaming Monitor
                    - paragraph [ref=e425]: "ID: #4"
              - cell "Peripherals" [ref=e426]
              - cell "₹549.99" [ref=e427]
              - cell "8 in stock" [ref=e428]
              - cell [ref=e430]:
                - generic [ref=e431]:
                  - button "Edit" [ref=e432] [cursor=pointer]
                  - button "Delete" [ref=e437] [cursor=pointer]
            - row [ref=e442]:
              - cell [ref=e443]:
                - generic [ref=e444]:
                  - img "Ergonomic Precision Wireless Mouse" [ref=e445]
                  - generic [ref=e446]:
                    - paragraph [ref=e447]: Ergonomic Precision Wireless Mouse
                    - paragraph [ref=e448]: "ID: #5"
              - cell "Peripherals" [ref=e449]
              - cell "₹59.99" [ref=e450]
              - cell "35 in stock" [ref=e451]
              - cell [ref=e453]:
                - generic [ref=e454]:
                  - button "Edit" [ref=e455] [cursor=pointer]
                  - button "Delete" [ref=e460] [cursor=pointer]
            - row [ref=e465]:
              - cell [ref=e466]:
                - generic [ref=e467]:
                  - img "100W GaN 4-Port Fast Charging Hub" [ref=e468]
                  - generic [ref=e469]:
                    - paragraph [ref=e470]: 100W GaN 4-Port Fast Charging Hub
                    - paragraph [ref=e471]: "ID: #6"
              - cell "Accessories" [ref=e472]
              - cell "₹5000.00" [ref=e473]
              - cell "50 in stock" [ref=e474]
              - cell [ref=e476]:
                - generic [ref=e477]:
                  - button "Edit" [ref=e478] [cursor=pointer]
                  - button "Delete" [ref=e483] [cursor=pointer]
  - contentinfo [ref=e488]:
    - generic [ref=e489]:
      - generic [ref=e490]:
        - generic [ref=e491]: Day 16 Architecture
        - generic [ref=e494]: Zustand Cart + Zod Checkout
        - generic [ref=e498]: Orders + Admin Dashboard
        - generic [ref=e501]: TanStack React Query + Dark/Light Theme
        - generic [ref=e504]: Live FastAPI Fullstack
      - generic [ref=e510]:
        - paragraph [ref=e511]: © 2026 Gunturu E-Commerce Fullstack Hub. All rights reserved.
        - generic [ref=e512]:
          - link "Store Catalog" [ref=e513] [cursor=pointer]:
            - /url: /
          - link "FastAPI Swagger Docs" [ref=e514] [cursor=pointer]:
            - /url: http://127.0.0.1:8000/docs
  - region "Notifications alt+T"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Authentication Journey', () => {
  4  |   test('validates required form fields and shows error states', async ({ page }) => {
  5  |     await page.goto('/login');
  6  | 
  7  |     // Click Sign In without entering data
  8  |     await page.getByTestId('login-submit-btn').click();
  9  | 
  10 |     // Verify Zod validation messages
  11 |     await expect(page.getByText(/username must be at least 3 characters/i)).toBeVisible();
  12 |     await expect(page.getByText(/password must be at least 6 characters/i)).toBeVisible();
  13 |   });
  14 | 
  15 |   test('successfully signs in with test credentials and navigates home', async ({ page }) => {
  16 |     await page.goto('/login');
  17 | 
  18 |     await page.getByTestId('username-input').fill('admin');
  19 |     await page.getByTestId('password-input').fill('secret123');
  20 |     await page.getByTestId('login-submit-btn').click();
  21 | 
  22 |     // Wait for redirect to home
> 23 |     await page.waitForURL(/.*5173\/?$/);
     |                ^ Error: page.waitForURL: Test timeout of 30000ms exceeded.
  24 | 
  25 |     // Verify logged in user is displayed in navbar
  26 |     await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
  27 |   });
  28 | });
  29 | 
```
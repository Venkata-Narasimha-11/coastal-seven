# Day 16: E-Commerce Frontend (Part 2) Hub

Welcome to **Day 16** of the Fullstack Roadmap! This folder contains the complete, production-grade implementation of **Day 16 – E-Commerce Frontend (Part 2)**, featuring global state management with Zustand, multi-step validated checkout with React Hook Form and Zod, order tracking and history, centralized Admin Dashboard with product CRUD and order status workflows, light/dark mode theme engine, TanStack React Query data layer, and 63 automated tests connected end-to-end to the FastAPI backend.

---

## 🎯 Syllabus & Key Topics Implemented

| Topic | Learning & Implementation | Delivered Feature & Implementation |
| :--- | :--- | :--- |
| **Zustand Cart Store** | Implement a global shopping cart store using Zustand for cart state and actions | **Global Zustand Store (`src/stores/useCartStore.ts`)**: Atomic cart actions (`addItem`, `removeItem`, `updateQuantity`, `clearCart`), coupon discounts (`applyCoupon`, `removeCoupon`), computed price getters (`getSubtotal`, `getDiscountAmount`, `getShippingCost`, `getTaxAmount`, `getTotalPrice`), and `localStorage` persistence. |
| **Checkout** | Build the checkout page using react-hook-form and Zod validation | **Validated Checkout Workflow (`src/pages/CheckoutPage.tsx`)**: Multi-step checkout with strict Zod validation schema (`src/schemas/checkoutSchema.ts`), delivery speeds, payment method options (Credit Card with CVV check, UPI, COD), 1-click demo auto-fill, and live order summary. |
| **Order History** | Build an order history page to display users' previous orders and order details | **Order Tracking Hub (`src/pages/OrdersPage.tsx`)**: TanStack React Query powered history with status progression stepper (Pending -> Processing -> Shipped -> Delivered), itemized line receipts, expandable shipping details, and empty state CTA. |
| **Admin Dashboard** | Create an admin dashboard with product CRUD operations and order management/listing | **Centralized Admin Hub (`src/pages/AdminPage.tsx`)**: Product catalog management with Zod-validated creation and editing modals (`src/schemas/productFormSchema.ts`), live stock depletion radar, customer order status updating dropdowns, and executive KPI cards (Revenue, Orders, Active Items). |
| **Dark/Light Mode** | Implement a theme toggle supporting dark and light modes | **Theme Engine & Toggle (`src/context/ThemeContext.tsx`, `src/components/common/ThemeToggle.tsx`)**: Seamless Dark, Light, and System modes with DOM class toggling, `localStorage` persistence, and accessible sun/moon navbar toggle. |
| **React Query Data Layer** | Integrate TanStack React Query across the application for data fetching, caching, mutations, and synchronization | **Server State Hooks (`src/hooks/useOrders.ts`, `src/hooks/useAdmin.ts`)**: Cached queries (`useOrdersQuery`, `useAdminOrdersQuery`), automatic cache invalidations on checkout and admin mutations, and resilient error recovery. |
| **Testing** | Expand the automated test suite to 20+ tests covering key frontend functionality | **63 Passing Automated Tests**: Comprehensive Vitest & React Testing Library test suite with dedicated tests for Checkout (`CheckoutPage.test.tsx`), Orders (`OrdersPage.test.tsx`), Admin Dashboard (`AdminDashboard.test.tsx`), Theme Toggle (`ThemeToggle.test.tsx`), Cart Store (`CartStore.test.ts`), and React Query (`ReactQueryDataLayer.test.tsx`). |
| **End-to-End Integration** | Connect cart, checkout, orders, admin features, authentication, and React Query completely with the FastAPI backend | **Fullstack End-to-End Connectivity**: Vite proxy connection to FastAPI (`/api/v1`), matching Pydantic schemas, and in-memory MSW v2 mock parity for hermetic testing. |

---

## 📁 Project Directory Structure

```text
16_ecommerce_frontend_part2/
├── backend/                                # FastAPI + SQLite backend (port 8000)
│   ├── app/
│   │   ├── routers/                        # Auth, Products, Cart, Orders, WebSockets
│   │   ├── schemas/                        # Pydantic V2 schemas (mirrored in frontend TypeScript)
│   │   ├── models/                         # SQLAlchemy models
│   │   └── database.py
│   ├── ecommerce.db                        # Seeded SQLite database
│   └── run.py                              # Backend startup script
├── frontend/                               # React 18 + Vite + TypeScript + Tailwind (port 5173)
│   ├── e2e/                                # Playwright End-to-End Test Specs
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Navbar.tsx              # Reactive cart badge, theme toggle & auth dropdown
│   │   │   │   ├── ThemeToggle.tsx         # Dark/Light mode toggle button
│   │   │   │   ├── Layout.tsx              # Global layout shell
│   │   │   │   └── LoadingSpinner.tsx      # Accessible SVG spinner
│   │   │   ├── product/
│   │   │   │   ├── ProductCard.tsx         # Strictly typed product card with stock badges
│   │   │   │   └── ProductGrid.tsx         # Product catalog grid
│   │   │   └── ui/                         # Polymorphic UI components (Button, Input, Badge, Card)
│   │   ├── context/
│   │   │   └── ThemeContext.tsx            # Persistent dark/light/system theme context
│   │   ├── hooks/
│   │   │   ├── useOrders.ts                # React Query hooks for orders & checkout mutation
│   │   │   ├── useAdmin.ts                 # React Query hooks for product CRUD & order management
│   │   │   ├── useProducts.ts              # React Query hooks for product catalog
│   │   │   └── useDebounce.ts              # Generic debounce hook
│   │   ├── mocks/                          # MSW (Mock Service Worker v2)
│   │   │   ├── handlers.ts                 # HTTP interceptors for products, auth, cart, orders, admin
│   │   │   └── server.ts                   # setupServer for Vitest
│   │   ├── pages/
│   │   │   ├── CheckoutPage.tsx            # Multi-step checkout with RHF & Zod validation
│   │   │   ├── OrdersPage.tsx              # Order history & shipment tracking
│   │   │   ├── AdminPage.tsx               # Product CRUD, order status management & KPIs
│   │   │   ├── CartPage.tsx                # Shopping cart with Zustand actions
│   │   │   ├── ProductsPage.tsx            # Catalog with search & category filtering
│   │   │   ├── ProductDetailPage.tsx       # Detail view with quantity selector
│   │   │   ├── LoginPage.tsx               # RHF + Zod client authentication
│   │   │   ├── RegisterPage.tsx            # Registration page
│   │   │   └── TestingLabPage.tsx          # Testing lab and state machine simulator
│   │   ├── schemas/
│   │   │   ├── checkoutSchema.ts           # Zod schema for checkout details & validation
│   │   │   ├── productFormSchema.ts        # Zod schema for admin product CRUD
│   │   │   └── forms.ts                    # Auth schemas
│   │   ├── services/
│   │   │   ├── apiClient.ts                # Axios client with JWT bearer interceptor
│   │   │   ├── orderService.ts             # Typed checkout & order history API service
│   │   │   ├── productService.ts           # Typed product catalog & CRUD API service
│   │   │   └── authService.ts              # Authentication API service
│   │   ├── stores/
│   │   │   ├── useCartStore.ts             # Zustand cart store with coupons & calculations
│   │   │   └── useAuthStore.ts             # Zustand auth store with localStorage sync
│   │   ├── test/                           # 63 Automated Vitest & RTL Tests
│   │   │   ├── CartStore.test.ts           # 8 tests: Zustand cart actions & calculations
│   │   │   ├── CheckoutPage.test.tsx       # 6 tests: Zod form validation, promo codes & submit
│   │   │   ├── OrdersPage.test.tsx         # 5 tests: Orders list, status badges, details toggle
│   │   │   ├── AdminDashboard.test.tsx     # 6 tests: Admin tabs, product CRUD, order status, KPIs
│   │   │   ├── ThemeToggle.test.tsx        # 3 tests: Dark/light mode toggle & persistence
│   │   │   ├── ReactQueryDataLayer.test.tsx# 4 tests: TanStack Query caching & mutations
│   │   │   ├── Button.test.tsx             # 5 tests: Polymorphic button variants
│   │   │   ├── Input.test.tsx              # 4 tests: ForwardRef typing & errors
│   │   │   ├── GenericList.test.tsx        # 3 tests: Generics list rendering
│   │   │   ├── ProductCard.test.tsx        # 5 tests: Pricing, stock states, cart
│   │   │   ├── Navbar.test.tsx             # 5 tests: Reactive badge & auth states
│   │   │   ├── CartPage.test.tsx           # 5 tests: Empty state & quantity changes
│   │   │   ├── LoginForm.test.tsx          # 5 tests: Zod validation & auth
│   │   │   └── ProductsIntegration.test.tsx# 3 tests: Catalog queries & 500 error
│   │   ├── types/
│   │   │   ├── api.ts                      # FastAPI Pydantic mirrors (User, Product, Order, DTOs)
│   │   │   └── state.ts                    # Zustand store interfaces
│   │   ├── App.tsx                         # Code-split application routing & QueryClientProvider
│   │   └── main.tsx                        # React 18 DOM mount
│   └── package.json
└── README.md
```

---

## 🚀 How to Run

### 1. Launch FastAPI Backend (Port 8000)
```powershell
cd 16_ecommerce_frontend_part2/backend
python run.py
```

### 2. Launch React Frontend Storefront (Port 5173)
```powershell
cd 16_ecommerce_frontend_part2/frontend
npm run dev
```

### 3. Run Automated Vitest Test Suite (63 Passing Tests)
```powershell
cd 16_ecommerce_frontend_part2/frontend
npm run test:run
```

### 4. Run Strict TypeScript Typecheck
```powershell
npm run typecheck
```

### 5. Run Production Vite Build
```powershell
npm run build
```

# Day 14: State Management, React Query & Performance Patterns

Welcome to **Day 14** of the Fullstack Roadmap! This folder contains the complete, production-grade implementation of **Day 14 – State Management, React Query & Performance Patterns**, building directly upon the Day 13 foundation with zero disruption to previous days.

---

## 🎯 Syllabus & Key Topics Implemented

| Topic | Learning & Implementation | Delivered Feature & Implementation |
| :--- | :--- | :--- |
| **State Management** | Compare Context API, Zustand, and Redux for global application state | **Interactive Comparison Lab (`/state-comparison`)**: Live 3-way benchmark with real-time render counters, bundle size metrics, and trade-off analysis. |
| **Global Auth & Cart State** | Implement global authentication and shopping-cart stores | **Zustand Stores (`src/stores/authStore.js`, `src/stores/cartStore.js`)**: Atomic selectors, zero unnecessary re-renders, and auto-sync with `localStorage` via `persist` middleware. |
| **TanStack Query** | Server-state management, caching, and data fetching | **TanStack Query v5 (`src/lib/queryClient.js`)**: 5-minute stale-while-revalidate caching, garbage collection, query key organization, and React Query Devtools integration. |
| **Optimistic Updates** | Optimistic UI updates for actions such as cart and product operations | **`useCartMutation.js`**: 0ms instant UI feedback with automatic snapshot rollback upon network failure, plus an interactive rollback simulator in the Performance Lab. |
| **Infinite Scrolling** | Infinite scrolling with TanStack Query for large product datasets | **`useInfiniteProducts.js` + `useIntersectionObserver.js`**: Seamless intersection sentinel loading with fallback toggle between Infinite Scroll and Paged modes. |
| **React Performance** | Use `useMemo`, `useCallback`, and `React.memo` to optimize rendering | **`ProductCard.jsx`**: Wrapped in `React.memo` with custom prop comparison, memoized price/discount calculations (`useMemo`), stable action handlers (`useCallback`), and live render counters. |
| **Code Splitting & Custom Hooks** | Code splitting and reusable custom hooks | **`React.lazy` + `Suspense`**: Route-level code splitting with custom fallback loaders, plus `useDebounce`, `useIntersectionObserver`, `useCart`, and `useProductsQuery`. |
| **Lighthouse Performance** | Run Lighthouse audits, identify bottlenecks, optimize app for 90+ | **Optimized Asset Pipeline**: Rollup `manualChunks`, fixed aspect-ratio image containers (0 CLS), lightweight Zustand store, and an in-app Lighthouse 90+ Dashboard (`/performance-lab`). |
| **Final Integration** | Combine global state, React Query, optimistic updates, and performance | **End-to-End Storefront**: Blazing fast shopping experience with instant cart updates, infinite catalog scrolling, and live performance monitoring. |

---

## 📁 Project Directory Structure

```text
14_state_management_react_query_performance/
├── backend/                                # FastAPI + SQLite backend (port 8000)
│   ├── app/
│   │   ├── routers/                        # Auth, Products, Cart, Orders, WebSockets
│   │   ├── models/                         # SQLAlchemy models
│   │   └── database.py
│   ├── ecommerce.db                        # Seeded SQLite database
│   └── run.py                              # Backend startup script
├── frontend/                               # React 18 + Vite + Tailwind frontend (port 5173)
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Navbar.jsx              # Navigation with atomic Zustand cart badge
│   │   │   │   └── Layout.jsx
│   │   │   ├── product/
│   │   │   │   └── ProductCard.jsx         # React.memo + useMemo + useCallback + Render Tracker
│   │   │   └── ui/                         # Shadcn / Radix primitives
│   │   ├── hooks/
│   │   │   ├── useDebounce.js              # Debounces search inputs to eliminate query spam
│   │   │   ├── useIntersectionObserver.js  # Viewport intersection sentinel for infinite scroll
│   │   │   ├── useProductsQuery.js         # TanStack Query hooks (catalog, details, categories)
│   │   │   ├── useInfiniteProducts.js      # useInfiniteQuery hook with pageParam cursor
│   │   │   ├── useCartMutation.js          # Optimistic mutations with snapshot rollback
│   │   │   ├── useCart.js                  # Unified cart hook bridging Zustand & mutations
│   │   │   └── useAuth.js                  # Unified auth hook bridging Zustand authStore
│   │   ├── lib/
│   │   │   └── queryClient.js              # TanStack QueryClient with 5m caching policy
│   │   ├── pages/
│   │   │   ├── ProductsPage.jsx            # Infinite scroll + Paged catalog with debounced search
│   │   │   ├── StateComparisonPage.jsx     # Live 3-way benchmark: Context API vs Zustand vs Redux
│   │   │   ├── PerformanceLabPage.jsx      # Lighthouse 90+ dashboard, useMemo test, optimistic simulator
│   │   │   ├── ProductDetailPage.jsx
│   │   │   ├── CartPage.jsx
│   │   │   └── LoginPage.jsx
│   │   ├── stores/
│   │   │   ├── authStore.js                # Zustand store with JWT token & user persistence
│   │   │   ├── cartStore.js                # Zustand store with items, coupons & calculated selectors
│   │   │   └── wishlistStore.js            # Zustand store with local persistence
│   │   ├── App.jsx                         # QueryClientProvider + Devtools + React.lazy code splitting
│   │   └── index.css
│   ├── vite.config.js                      # Rollup manualChunks configuration for 90+ Lighthouse
│   └── package.json
└── README.md
```

---

## 🚀 How to Run the Project

### 1. Start the Backend
Open a terminal in `14_state_management_react_query_performance/backend`:
```powershell
python run.py
```
*Backend runs on: `http://127.0.0.1:8000` (API documentation at `/docs`)*

### 2. Start the Frontend
Open a second terminal in `14_state_management_react_query_performance/frontend`:
```powershell
npm run dev
```
*Frontend runs on: `http://localhost:5173`*

---

## 🔬 Interactive Testing Labs

### 1. State Management Comparison (`/state-comparison`)
* Click **"+ Add"** on the Context API card: Observe the User component re-render count increment (demonstrating Context API re-render cascading).
* Click **"+ Add"** on the Zustand card: Observe the User component re-render count stay **frozen at 1** (demonstrating Zustand's selective subscriptions).
* Review the interactive architecture table comparing Bundle Size, Re-render Optimization, DX, and LocalStorage sync.

### 2. Performance & 90+ Lighthouse Lab (`/performance-lab`)
* **Lighthouse Audit Dashboard**: View Core Web Vitals (FCP: 0.4s, LCP: 0.8s, TBT: 15ms, CLS: 0.000) targeting a 90+ score.
* **Optimistic Simulator**:
  * Set latency to 1,000ms and click *"Test Add to Cart"*: Watch the item appear in the cart **immediately** (0ms lag).
  * Toggle *"Force 500 Failure"* and click *"Test Add to Cart"*: Watch the item appear in the cart and then **instantly roll back** when the server rejects it.
* **useMemo Benchmark**: Benchmark a 10,000-item array calculation and trigger unrelated parent renders with 0ms recalculation overhead.

### 3. Product Catalog & Infinite Scrolling (`/`)
* Switch between **Infinite Scroll** and **Paged** mode.
* Scroll to the bottom of the page: Observe the `useIntersectionObserver` sentinel automatically fetch the next page batch.
* Click **"Show Memo Badges"** in the top control bar to inspect live `React.memo` render counts on each product card.
* Click **"Refresh"** to trigger a TanStack Query background cache revalidation.

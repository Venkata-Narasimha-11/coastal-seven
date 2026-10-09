# Day 15: TypeScript for React & Component Testing

Welcome to **Day 15** of the Fullstack Roadmap! This folder contains the complete, production-grade implementation of **Day 15 – TypeScript for React & Component Testing**, integrating strict TypeScript contracts with FastAPI, comprehensive component testing with Vitest & React Testing Library, API mocking with MSW (Mock Service Worker), end-to-end testing with Playwright, and automated Continuous Integration (CI).

---

## 🎯 Syllabus & Key Topics Implemented

| Topic | Learning & Implementation | Delivered Feature & Implementation |
| :--- | :--- | :--- |
| **TypeScript Fundamentals** | TypeScript interfaces, generics, and type definitions for React applications | **Generic Types & Utility Explorer (`src/types/`)**: Generic wrappers `ApiResponse<T>`, `PaginatedResponse<T>`, `<GenericList<T>>`, discriminated union state machines, and utility types (`Omit`, `Pick`, `Partial`, `Record`). |
| **Typed React Components** | Implement typed props, state, refs, and component-level types | **Type-Safe Component Suite (`src/components/ui/`)**: Polymorphic `Button` (`as="button" \| "a"`), compound component `Card` (`Card.Header`, `Card.Title`, etc.), forwardRef typed `Input` with ARIA accessibility, and status `Badge`. |
| **Typed API Responses** | Define TypeScript types/interfaces for API request and response data | **FastAPI Contract Parity (`src/types/api.ts`)**: Strict 1:1 type definitions mirroring FastAPI Pydantic schemas (`User`, `Product`, `Category`, `CartItem`, `Order`) + generic `ApiClient` with automated JWT injection. |
| **React Component Testing** | Use React Testing Library and Vitest to test components and user interactions | **41 Automated Tests (`src/test/`)**: 100% passing Vitest test suites verifying user clicks, keyboard typing, accessible roles (`getByRole`), loading spinners, stock indicators, and Zod client validation. |
| **API Mocking** | Use MSW (Mock Service Worker) to mock API requests during testing | **MSW v2 Architecture (`src/mocks/`)**: In-memory HTTP interception for Vitest via `setupServer`. Intercepts `/api/v1/*` endpoints and reliably simulates 500 internal server errors, 401 token expirations, and network latency. |
| **E2E Testing** | Use Playwright to test critical end-to-end application flows | **Playwright Test Suite (`e2e/`)**: Full multi-page user journeys verifying catalog search, product detail navigation, cart badge counter reactivity, checkout CTA, and login authentication. |
| **CI Test Integration** | Configure the complete test suite to run automatically in CI | **GitHub Actions Workflow (`.github/workflows/day15-ci.yml`)**: Automated pipeline running TypeScript typecheck (`tsc --noEmit`), Vitest tests with V8 coverage, Vite bundle build, and Playwright tests + Local PowerShell runner (`scripts/run-ci.ps1`). |
| **Final Integration** | Combine TypeScript, component testing, API mocking, Playwright E2E testing, and CI | **End-to-End Type-Safe App + Master Testing Lab (`/testing-lab`)**: Interactive showcase with live union state machine, network failure simulator, and test matrix explorer. |

---

## 📁 Project Directory Structure

```text
15_typescript_react_component_testing/
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
│   │   ├── catalog.spec.ts                 # Product catalog & search flows
│   │   ├── cart.spec.ts                    # Add-to-cart, quantity modifier & clear cart
│   │   ├── auth.spec.ts                    # Zod validation & test login flow
│   │   └── testing-lab.spec.ts             # Interactive lab state transitions
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Navbar.tsx              # Reactive cart badge & auth session dropdown
│   │   │   │   ├── Layout.tsx              # Global application layout shell
│   │   │   │   ├── ErrorMessage.tsx        # Accessible error alert with retry button
│   │   │   │   └── LoadingSpinner.tsx      # Accessible SVG spinner with ARIA attributes
│   │   │   ├── product/
│   │   │   │   ├── ProductCard.tsx         # Strictly typed props, stock badges, add-to-cart
│   │   │   │   └── ProductGrid.tsx         # Skeleton loading states and empty messages
│   │   │   └── ui/
│   │   │       ├── Button.tsx              # Polymorphic button (as="button" | "a"), variants, sizes
│   │   │       ├── Input.tsx               # ForwardRef input with label & ARIA error linking
│   │   │       ├── Badge.tsx               # Status badges (default, success, warning, danger, info)
│   │   │       ├── Card.tsx                # Compound component (Header, Title, Content, Footer)
│   │   │       ├── Skeleton.tsx            # Animated pulse loading placeholder
│   │   │       └── GenericList.tsx         # TypeScript Generics in React: <GenericList<T>>
│   │   ├── hooks/
│   │   │   ├── useDebounce.ts              # Generic debounce hook: <T>(value: T, delay: number): T
│   │   │   └── useProducts.ts              # Typed TanStack Query hooks
│   │   ├── mocks/                          # MSW (Mock Service Worker v2)
│   │   │   ├── handlers.ts                 # Interceptors for products, auth, cart endpoints
│   │   │   ├── server.ts                   # setupServer for Vitest / Node test runner
│   │   │   └── browser.ts                  # setupWorker for browser mocking
│   │   ├── pages/
│   │   │   ├── ProductsPage.tsx            # Catalog with search & category filtering
│   │   │   ├── ProductDetailPage.tsx       # Detail view with quantity counter & stock check
│   │   │   ├── CartPage.tsx                # Shopping cart with price calculations & checkout
│   │   │   ├── LoginPage.tsx               # React Hook Form + Zod client validation
│   │   │   ├── RegisterPage.tsx            # Registration with password confirmation check
│   │   │   └── TestingLabPage.tsx          # Interactive TypeScript & Testing Showcase Lab
│   │   ├── services/
│   │   │   ├── apiClient.ts                # Generic type-safe Axios client with JWT interceptor
│   │   │   ├── productService.ts           # Typed product catalog API queries
│   │   │   ├── authService.ts              # Typed login, register, and user profile API calls
│   │   │   └── cartService.ts              # Typed cart mutations
│   │   ├── stores/
│   │   │   ├── useAuthStore.ts             # Typed Zustand auth store with localStorage sync
│   │   │   ├── useCartStore.ts             # Typed Zustand cart store with computed totals
│   │   │   └── useUIStore.ts               # UI state for Testing Lab simulation controls
│   │   ├── test/                           # Vitest & React Testing Library Suite
│   │   │   ├── setup.ts                    # Global MSW server lifecycle + RTL cleanup
│   │   │   ├── test-utils.tsx              # Custom renderWithProviders wrapper
│   │   │   ├── Button.test.tsx             # 5 tests: variants, loading, clicks, polymorphic
│   │   │   ├── Input.test.tsx              # 4 tests: typing, errors, forwardRef
│   │   │   ├── GenericList.test.tsx        # 3 tests: generics, complex objects, empty state
│   │   │   ├── ProductCard.test.tsx        # 5 tests: prices, stock states, add-to-cart
│   │   │   ├── Navbar.test.tsx             # 5 tests: reactive badge, auth states, logout
│   │   │   ├── CartPage.test.tsx           # 5 tests: empty state, quantity modifiers, clear cart
│   │   │   ├── CartStore.test.ts           # 6 tests: Zustand state transitions
│   │   │   ├── LoginForm.test.tsx          # 5 tests: Zod validation & MSW auth
│   │   │   └── ProductsIntegration.test.tsx# 3 tests: MSW catalog query, search, 500 error
│   │   ├── types/
│   │   │   ├── api.ts                      # FastAPI Pydantic mirrors (User, Product, Cart, Order)
│   │   │   ├── components.ts               # Component prop types & polymorphic interfaces
│   │   │   ├── state.ts                    # Zustand store interfaces
│   │   │   └── forms.ts                    # Zod schemas & inferred types (Login, Register)
│   │   ├── App.tsx                         # QueryClientProvider + BrowserRouter setup
│   │   ├── main.tsx                        # React 18 DOM mount
│   │   └── index.css                       # Tailwind CSS directives
│   ├── playwright.config.ts                # Playwright configuration with webServer
│   ├── vitest.config.ts                    # Vitest configuration with jsdom & v8 coverage
│   ├── tsconfig.json                       # Strict TypeScript configuration
│   └── package.json
├── scripts/
│   └── run-ci.ps1                          # Local one-click CI pipeline runner for Windows
└── README.md
```

---

## 🔬 Core Learning Concepts & Code Examples

### 1. TypeScript Generics in React Components
Instead of hardcoding components for a specific model, generics allow writing reusable, type-safe components:

```tsx
// src/components/ui/GenericList.tsx
export interface GenericListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T, index: number) => string | number;
  emptyMessage?: string;
}

export function GenericList<T>({ items, renderItem, keyExtractor, emptyMessage }: GenericListProps<T>) {
  if (items.length === 0) return <p>{emptyMessage}</p>;
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item, index)}>{renderItem(item, index)}</li>
      ))}
    </ul>
  );
}
```

### 2. Polymorphic React Components
The `Button` component can render as either a standard `<button>` or a navigation `<a>` link while maintaining HTML attribute type-safety:

```tsx
// src/components/ui/Button.tsx
export const Button = React.forwardRef<any, ButtonProps>(
  ({ as, children, variant = 'primary', ...rest }, ref) => {
    const Component = as || 'button';
    return <Component ref={ref} className={...} {...rest}>{children}</Component>;
  }
);

// Usage:
<Button variant="primary">Standard Button</Button>
<Button as="a" href="/external" variant="outline">Hyperlink Button</Button>
```

### 3. API Mocking with MSW v2 (Mock Service Worker)
MSW intercepts network calls at the HTTP layer, giving real confidence without needing a live backend during tests:

```ts
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('*/api/v1/products/', ({ request }) => {
    return HttpResponse.json({ items: mockProducts, total: mockProducts.length });
  }),
];

// src/test/setup.ts
beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
afterEach(() => { server.resetHandlers(); cleanup(); });
afterAll(() => server.close());
```

---

## 🚀 How to Run the Application

### 1. Start the Backend (Optional - Live API)
Open a terminal in `15_typescript_react_component_testing/backend`:
```powershell
python run.py
```
*Backend runs on: `http://127.0.0.1:8000` (OpenAPI Swagger docs at `http://127.0.0.1:8000/docs`)*

### 2. Start the Frontend Dev Server
Open a terminal in `15_typescript_react_component_testing/frontend`:
```powershell
npm run dev
```
*Frontend runs on: `http://localhost:5173`*

---

## 🧪 How to Run Automated Tests

Navigate to `15_typescript_react_component_testing/frontend`:

### 1. Strict TypeScript Typecheck
Verify zero type errors across the entire project:
```powershell
npm run typecheck
```

### 2. Run Vitest Unit & Component Tests
Run all 41 component, store, and MSW integration tests:
```powershell
npm run test:run
```

### 3. Run Test Coverage Report
Generate a detailed V8 test coverage breakdown:
```powershell
npm run test:coverage
```

### 4. Run Playwright End-to-End Tests
Execute all 9 browser user journeys with automatic Vite server startup:
```powershell
npm run test:e2e
```

### 5. Run Complete Local CI Pipeline
Execute the full CI verification in one command:
```powershell
npm run test:ci
```
Or execute the PowerShell script:
```powershell
..\scripts\run-ci.ps1
```


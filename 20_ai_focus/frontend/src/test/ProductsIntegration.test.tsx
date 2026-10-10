import { describe, it, expect } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { renderWithProviders } from './test-utils';
import { server } from '../mocks/server';
import ProductsPage from '../pages/ProductsPage';

describe('ProductsPage & MSW Integration', () => {
  it('renders product catalog fetched from MSW mock server', async () => {
    renderWithProviders(<ProductsPage />);

    // Initially displays loading state or skeletons
    expect(screen.getByTestId('product-grid-loading')).toBeInTheDocument();

    // After MSW responds, products should appear
    expect(
      await screen.findByText(/wireless noise-canceling headphones/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/ergonomic mechanical keyboard/i)
    ).toBeInTheDocument();
  });

  it('filters product catalog when user types into search input', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ProductsPage />);

    // Wait for initial load
    expect(
      await screen.findByText(/wireless noise-canceling headphones/i)
    ).toBeInTheDocument();

    const searchInput = screen.getByLabelText(/search products/i);
    await user.type(searchInput, 'keyboard');

    // Debounce wait & filter
    await waitFor(
      () => {
        expect(
          screen.getByText(/ergonomic mechanical keyboard/i)
        ).toBeInTheDocument();
        expect(
          screen.queryByText(/wireless noise-canceling headphones/i)
        ).not.toBeInTheDocument();
      },
      { timeout: 2500 }
    );
  });

  it('handles simulated MSW 500 server error and displays ErrorMessage component', async () => {
    // Override MSW handler for this test only to simulate server crash
    server.use(
      http.get('*/api/v1/products/', () => {
        return new HttpResponse(
          JSON.stringify({ detail: 'Internal Server Error (Database Connection Failed)' }),
          { status: 500, headers: { 'Content-Type': 'application/json' } }
        );
      })
    );

    renderWithProviders(<ProductsPage />);

    // Expect ErrorMessage component to be displayed
    expect(
      await screen.findByRole('alert')
    ).toBeInTheDocument();
    expect(
      screen.getByText(/failed to load products/i)
    ).toBeInTheDocument();
  });
});

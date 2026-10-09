import { describe, it, expect } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';
import { renderWithProviders } from './test-utils';
import OrdersPage from '../pages/OrdersPage';

describe('OrdersPage & TanStack React Query Integration', () => {
  it('renders order history page and loads orders from backend', async () => {
    renderWithProviders(<OrdersPage />);

    await waitFor(() => {
      expect(screen.getByText(/Order History & Tracking/i)).toBeInTheDocument();
      expect(screen.getByText(/Order #101/i)).toBeInTheDocument();
      expect(screen.getAllByText(/SHIPPED/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/Order #102/i)).toBeInTheDocument();
      expect(screen.getAllByText(/PENDING/i).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders items list and line subtotals for each order', async () => {
    renderWithProviders(<OrdersPage />);

    await waitFor(() => {
      expect(screen.getAllByText(/Wireless Noise-Canceling Headphones/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/Ergonomic Mechanical Keyboard/i)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/₹399.98/i).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/₹129.50/i).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('toggles expandable order details including shipping address', async () => {
    const user = userEvent.setup();
    renderWithProviders(<OrdersPage />);

    await waitFor(() => {
      expect(screen.getByText(/Order #101/i)).toBeInTheDocument();
    });

    const toggleBtn = screen.getByRole('button', { name: /Toggle details for order 101/i });
    expect(screen.queryByText(/42 MG Road, Bengaluru/i)).not.toBeInTheDocument();

    await user.click(toggleBtn);

    await waitFor(() => {
      expect(screen.getByText(/42 MG Road, Bengaluru/i)).toBeInTheDocument();
      expect(screen.getByText(/Hide Details/i)).toBeInTheDocument();
    });

    await user.click(toggleBtn);

    await waitFor(() => {
      expect(screen.queryByText(/42 MG Road, Bengaluru/i)).not.toBeInTheDocument();
    });
  });

  it('renders empty orders state when customer has no orders', async () => {
    server.use(
      http.get('*/api/v1/orders', () => {
        return HttpResponse.json([]);
      })
    );

    renderWithProviders(<OrdersPage />);

    await waitFor(() => {
      expect(screen.getByText(/No Orders Placed Yet/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /Explore Products/i })).toBeInTheDocument();
    });
  });

  it('displays error state with retry button upon server failure', async () => {
    server.use(
      http.get('*/api/v1/orders', () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    renderWithProviders(<OrdersPage />);

    await waitFor(() => {
      expect(screen.getByText(/Unable to Load Order History/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Try Again/i })).toBeInTheDocument();
    });
  });
});

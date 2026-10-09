import { describe, it, expect, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from './test-utils';
import AdminPage from '../pages/AdminPage';
import useAuthStore from '../stores/useAuthStore';
import { mockUser } from '../mocks/handlers';

describe('AdminPage & Admin Dashboard Operations', () => {
  beforeEach(() => {
    useAuthStore.getState().login(mockUser, 'mock-jwt-token');
  });

  it('renders admin control hub and default Products tab with catalog items', async () => {
    renderWithProviders(<AdminPage />);

    expect(screen.getByText(/Admin Control Hub/i)).toBeInTheDocument();
    expect(screen.getByTestId('admin-tab-products')).toBeInTheDocument();
    expect(screen.getByTestId('admin-tab-orders')).toBeInTheDocument();
    expect(screen.getByTestId('admin-tab-analytics')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/Wireless Noise-Canceling Headphones/i)).toBeInTheDocument();
      expect(screen.getByText(/Ergonomic Mechanical Keyboard/i)).toBeInTheDocument();
      expect(screen.getByTestId('add-product-btn')).toBeInTheDocument();
    });
  });

  it('filters product table rows when typing in the search box', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AdminPage />);

    await waitFor(() => {
      expect(screen.getByText(/Wireless Noise-Canceling Headphones/i)).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/Search products by name/i);
    await user.type(searchInput, 'Headphones');

    await waitFor(() => {
      expect(screen.getByText(/Wireless Noise-Canceling Headphones/i)).toBeInTheDocument();
      expect(screen.queryByText(/Ergonomic Mechanical Keyboard/i)).not.toBeInTheDocument();
    });
  });

  it('switches to Orders tab and lists all customer orders', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AdminPage />);

    const ordersTabBtn = screen.getByTestId('admin-tab-orders');
    await user.click(ordersTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/#ORD-101/i)).toBeInTheDocument();
      expect(screen.getByText(/#ORD-102/i)).toBeInTheDocument();
      expect(screen.getByTestId('status-select-101')).toBeInTheDocument();
    });
  });

  it('updates customer order status using the status selector', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AdminPage />);

    const ordersTabBtn = screen.getByTestId('admin-tab-orders');
    await user.click(ordersTabBtn);

    await waitFor(() => {
      expect(screen.getByTestId('status-select-102')).toBeInTheDocument();
    });

    const selectDropdown = screen.getByTestId('status-select-102');
    await user.selectOptions(selectDropdown, 'delivered');

    await waitFor(() => {
      expect((selectDropdown as HTMLSelectElement).value).toBe('delivered');
    });
  });

  it('switches to Analytics tab and displays KPI summary cards and inventory alerts', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AdminPage />);

    const analyticsTabBtn = screen.getByTestId('admin-tab-analytics');
    await user.click(analyticsTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Total Revenue/i)).toBeInTheDocument();
      expect(screen.getByText(/Total Orders/i)).toBeInTheDocument();
      expect(screen.getByText(/Active Catalog/i)).toBeInTheDocument();
      expect(screen.getByText(/Low Stock Alerts/i)).toBeInTheDocument();
      expect(screen.getByText(/Inventory Depletion Radar/i)).toBeInTheDocument();
    });
  });

  it('opens Add New Product modal and validates inputs via Zod', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AdminPage />);

    await waitFor(() => {
      expect(screen.getByTestId('add-product-btn')).toBeInTheDocument();
    });

    const addBtn = screen.getByTestId('add-product-btn');
    await user.click(addBtn);

    await waitFor(() => {
      expect(screen.getByText(/Add New Product to Catalog/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Product Title/i)).toBeInTheDocument();
    });

    const saveBtn = screen.getByTestId('save-new-product-btn');
    await user.click(saveBtn);

    await waitFor(() => {
      expect(screen.getByText(/Product name must be at least 2 characters/i)).toBeInTheDocument();
    });
  });
});

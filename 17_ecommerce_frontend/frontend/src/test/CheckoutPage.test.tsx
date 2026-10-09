import { describe, it, expect, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from './test-utils';
import CheckoutPage from '../pages/CheckoutPage';
import useCartStore from '../stores/useCartStore';
import { mockProducts } from '../mocks/handlers';

describe('CheckoutPage & Zod Form Validation', () => {
  beforeEach(() => {
    useCartStore.getState().clearCart();
  });

  it('renders empty cart state when shopping cart has no items', () => {
    renderWithProviders(<CheckoutPage />);

    expect(screen.getByText(/Your Shopping Cart is Empty/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Browse Catalog/i })).toBeInTheDocument();
  });

  it('renders checkout form and order summary when items are in cart', () => {
    useCartStore.getState().addItem(mockProducts[0], 2);

    renderWithProviders(<CheckoutPage />);

    expect(screen.getByText(/Checkout & Order Finalization/i)).toBeInTheDocument();
    expect(screen.getByText(/Shipping Destination/i)).toBeInTheDocument();
    expect(screen.getByText(/Delivery Method/i)).toBeInTheDocument();
    expect(screen.getByText(/Payment Method/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Order Summary/i })).toBeInTheDocument();
    expect(screen.getByText(mockProducts[0].name)).toBeInTheDocument();
  });

  it('displays Zod validation errors when submitting an empty form', async () => {
    const user = userEvent.setup();
    useCartStore.getState().addItem(mockProducts[0], 1);

    renderWithProviders(<CheckoutPage />);

    const submitBtn = screen.getByTestId('place-order-button');
    await user.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Full name must be at least 2 characters/i)).toBeInTheDocument();
      expect(screen.getByText(/Please enter a valid email address/i)).toBeInTheDocument();
      expect(screen.getByText(/Phone number must be exactly 10 digits/i)).toBeInTheDocument();
      expect(screen.getByText(/Street address must be at least 5 characters/i)).toBeInTheDocument();
      expect(screen.getByText(/City must be at least 2 characters/i)).toBeInTheDocument();
      expect(screen.getByText(/State must be at least 2 characters/i)).toBeInTheDocument();
      expect(screen.getByText(/Postal code must be 5 or 6 digits/i)).toBeInTheDocument();
      expect(screen.getByText(/You must accept the terms and conditions/i)).toBeInTheDocument();
    });
  });

  it('populates fields using the auto-fill demo button', async () => {
    const user = userEvent.setup();
    useCartStore.getState().addItem(mockProducts[0], 1);

    renderWithProviders(<CheckoutPage />);

    const autoFillBtn = screen.getByRole('button', { name: /Auto-fill Demo Details/i });
    await user.click(autoFillBtn);

    const nameInput = screen.getByLabelText(/Full Name/i) as HTMLInputElement;
    const emailInput = screen.getByLabelText(/Email Address/i) as HTMLInputElement;

    expect(nameInput.value).toBe('John Doe');
    expect(emailInput.value).toBe('john.doe@example.com');
  });

  it('allows applying and removing promo coupons in the summary', async () => {
    const user = userEvent.setup();
    useCartStore.getState().addItem(mockProducts[0], 1);

    renderWithProviders(<CheckoutPage />);

    const promoInput = screen.getByPlaceholderText(/Promo Code/i);
    const applyBtn = screen.getByRole('button', { name: /^Apply$/i });

    await user.type(promoInput, 'SAVE10');
    await user.click(applyBtn);

    await waitFor(() => {
      expect(screen.getByText(/Coupon SAVE10 applied/i)).toBeInTheDocument();
      expect(screen.getByText(/Discount \(SAVE10\)/i)).toBeInTheDocument();
    });

    const removeBtn = screen.getByRole('button', { name: /Remove/i });
    await user.click(removeBtn);

    await waitFor(() => {
      expect(screen.queryByText(/Discount \(SAVE10\)/i)).not.toBeInTheDocument();
    });
  });

  it('submits order successfully and redirects when valid details are provided', async () => {
    const user = userEvent.setup();
    useCartStore.getState().addItem(mockProducts[0], 1);

    renderWithProviders(<CheckoutPage />);

    // Auto-fill valid data
    const autoFillBtn = screen.getByRole('button', { name: /Auto-fill Demo Details/i });
    await user.click(autoFillBtn);

    const submitBtn = screen.getByTestId('place-order-button');
    await user.click(submitBtn);

    await waitFor(() => {
      // Cart should be cleared on success
      expect(useCartStore.getState().items).toHaveLength(0);
    });
  });
});

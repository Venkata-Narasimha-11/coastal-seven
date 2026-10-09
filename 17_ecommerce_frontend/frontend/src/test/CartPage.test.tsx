import { describe, it, expect, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from './test-utils';
import CartPage from '../pages/CartPage';
import useCartStore from '../stores/useCartStore';
import { mockProducts } from '../mocks/handlers';

describe('CartPage Component', () => {
  beforeEach(() => {
    useCartStore.getState().clearCart();
  });

  it('renders empty cart state with "Start Shopping" call-to-action', () => {
    renderWithProviders(<CartPage />);

    expect(screen.getByTestId('empty-cart-state')).toBeInTheDocument();
    expect(screen.getByText(/your cart is empty/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /start shopping/i })).toBeInTheDocument();
  });

  it('renders cart items and summary when cart contains items', () => {
    useCartStore.getState().addItem(mockProducts[0], 2);

    renderWithProviders(<CartPage />);

    expect(screen.getByText(mockProducts[0].name)).toBeInTheDocument();
    expect(screen.getByTestId(`item-qty-${mockProducts[0].id}`)).toHaveTextContent('2');
    expect(screen.getByTestId('cart-subtotal')).toHaveTextContent(
      `$${(mockProducts[0].price * 2).toFixed(2)}`
    );
    expect(screen.getByTestId('checkout-button')).toBeInTheDocument();
  });

  it('increments quantity and updates subtotal on user click', async () => {
    const user = userEvent.setup();
    useCartStore.getState().addItem(mockProducts[0], 1);

    renderWithProviders(<CartPage />);

    const increaseBtn = screen.getByTestId(`increase-qty-${mockProducts[0].id}`);
    await user.click(increaseBtn);

    expect(screen.getByTestId(`item-qty-${mockProducts[0].id}`)).toHaveTextContent('2');
    expect(screen.getByTestId('cart-subtotal')).toHaveTextContent(
      `$${(mockProducts[0].price * 2).toFixed(2)}`
    );
  });

  it('decrements quantity and removes item when decreased to 0', async () => {
    const user = userEvent.setup();
    useCartStore.getState().addItem(mockProducts[0], 1);

    renderWithProviders(<CartPage />);

    const decreaseBtn = screen.getByTestId(`decrease-qty-${mockProducts[0].id}`);
    await user.click(decreaseBtn);

    // After decreasing to 0, cart is empty
    expect(screen.getByTestId('empty-cart-state')).toBeInTheDocument();
  });

  it('clears entire cart when "Clear Cart" is clicked', async () => {
    const user = userEvent.setup();
    useCartStore.getState().addItem(mockProducts[0], 1);
    useCartStore.getState().addItem(mockProducts[1], 1);

    renderWithProviders(<CartPage />);

    const clearBtn = screen.getByTestId('clear-cart-btn');
    await user.click(clearBtn);

    expect(screen.getByTestId('empty-cart-state')).toBeInTheDocument();
  });
});

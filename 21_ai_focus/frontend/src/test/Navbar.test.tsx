import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from './test-utils';
import Navbar from '../components/common/Navbar';
import useAuthStore from '../stores/useAuthStore';
import useCartStore from '../stores/useCartStore';
import { mockUser, mockProducts } from '../mocks/handlers';

describe('Navbar Component', () => {
  it('renders branding and primary navigation links', () => {
    renderWithProviders(<Navbar />);

    expect(screen.getByText(/typescript & vitest e-shop/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^products$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^wishlist$/i })).toBeInTheDocument();
  });

  it('displays empty cart icon without badge when cart has no items', () => {
    useCartStore.getState().clearCart();
    renderWithProviders(<Navbar />);

    expect(screen.queryByTestId('cart-badge-count')).not.toBeInTheDocument();
  });

  it('updates cart badge count reactively when items are in cart', () => {
    useCartStore.getState().addItem(mockProducts[0], 3);
    renderWithProviders(<Navbar />);

    const badge = screen.getByTestId('cart-badge-count');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent('3');
  });

  it('renders "Sign In" button when unauthenticated', () => {
    useAuthStore.getState().logout();
    renderWithProviders(<Navbar />);

    expect(screen.getByRole('link', { name: /sign in/i })).toBeInTheDocument();
  });

  it('renders username and handles logout when authenticated', async () => {
    const user = userEvent.setup();
    useAuthStore.getState().login(mockUser, 'test-jwt-token');

    renderWithProviders(<Navbar />);

    expect(screen.getByText(mockUser.username)).toBeInTheDocument();

    const logoutBtn = screen.getByRole('button', { name: /logout/i });
    await user.click(logoutBtn);

    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});

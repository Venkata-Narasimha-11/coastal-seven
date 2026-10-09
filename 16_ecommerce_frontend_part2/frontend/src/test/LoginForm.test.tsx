import { describe, it, expect } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from './test-utils';
import LoginPage from '../pages/LoginPage';

describe('LoginPage & Form Validation', () => {
  it('renders login form with username, password, and submit button', () => {
    renderWithProviders(<LoginPage />);

    expect(screen.getByRole('heading', { name: /sign in to your account/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/username or email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('displays client-side Zod validation errors on empty submission', async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginPage />);

    const submitBtn = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitBtn);

    expect(
      await screen.findByText(/username must be at least 3 characters/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/password must be at least 6 characters/i)
    ).toBeInTheDocument();
  });

  it('clears validation error once valid input is entered', async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginPage />);

    const submitBtn = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitBtn);

    const usernameInput = screen.getByLabelText(/username or email/i);
    await user.type(usernameInput, 'admin');

    await user.click(submitBtn);

    await waitFor(() => {
      expect(
        screen.queryByText(/username must be at least 3 characters/i)
      ).not.toBeInTheDocument();
    });
  });

  it('displays server error alert when incorrect credentials are submitted', async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginPage />);

    const usernameInput = screen.getByLabelText(/username or email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitBtn = screen.getByRole('button', { name: /sign in/i });

    await user.type(usernameInput, 'wronguser');
    await user.type(passwordInput, 'wrongpassword123');
    await user.click(submitBtn);

    expect(
      await screen.findByRole('alert')
    ).toBeInTheDocument();
    expect(
      screen.getByText(/incorrect username or password/i)
    ).toBeInTheDocument();
  });

  it('submits valid credentials and receives token response from MSW', async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginPage />);

    const usernameInput = screen.getByLabelText(/username or email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitBtn = screen.getByRole('button', { name: /sign in/i });

    await user.type(usernameInput, 'admin');
    await user.type(passwordInput, 'secret123');
    await user.click(submitBtn);

    // After success, token is stored in localStorage
    await waitFor(() => {
      expect(localStorage.getItem('auth_token')).toBe('mock-jwt-token-xyz-12345');
    });
  });
});

import { describe, it, expect, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from './test-utils';
import ThemeToggle from '../components/common/ThemeToggle';
import { ThemeProvider } from '../context/ThemeContext';

describe('ThemeToggle & Dark/Light Mode Engine', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.className = '';
  });

  it('renders theme toggle button with accessible aria-label', () => {
    renderWithProviders(
      <ThemeProvider defaultTheme="light">
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggleBtn = screen.getByTestId('theme-toggle-btn');
    expect(toggleBtn).toBeInTheDocument();
    expect(toggleBtn).toHaveAttribute('aria-label', 'Switch to dark mode');
  });

  it('switches between light and dark modes upon click', async () => {
    const user = userEvent.setup();

    renderWithProviders(
      <ThemeProvider defaultTheme="light">
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggleBtn = screen.getByTestId('theme-toggle-btn');
    expect(document.documentElement.classList.contains('light')).toBe(true);

    await user.click(toggleBtn);

    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(true);
      expect(toggleBtn).toHaveAttribute('aria-label', 'Switch to light mode');
    });

    await user.click(toggleBtn);

    await waitFor(() => {
      expect(document.documentElement.classList.contains('light')).toBe(true);
    });
  });

  it('persists theme selection to localStorage', async () => {
    const user = userEvent.setup();

    renderWithProviders(
      <ThemeProvider defaultTheme="light" storageKey="test-theme-key">
        <ThemeToggle />
      </ThemeProvider>
    );

    const toggleBtn = screen.getByTestId('theme-toggle-btn');
    await user.click(toggleBtn);

    await waitFor(() => {
      expect(localStorage.getItem('test-theme-key')).toBe('dark');
    });
  });
});

import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Input from '../components/ui/Input';

describe('Input Component', () => {
  it('renders label, input, and helper text properly', () => {
    render(
      <Input
        label="Username"
        placeholder="Enter your username"
        helperText="Must be unique"
      />
    );

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter your username/i)).toBeInTheDocument();
    expect(screen.getByText(/must be unique/i)).toBeInTheDocument();
  });

  it('updates value as the user types', async () => {
    const user = userEvent.setup();
    render(<Input label="Email" placeholder="user@example.com" />);

    const input = screen.getByLabelText(/email/i);
    await user.type(input, 'test@domain.com');

    expect(input).toHaveValue('test@domain.com');
  });

  it('renders error message and sets aria-invalid attribute', () => {
    render(
      <Input
        label="Password"
        error="Password must be at least 8 characters"
      />
    );

    const input = screen.getByLabelText(/password/i);
    expect(input).toHaveAttribute('aria-invalid', 'true');

    const errorMessage = screen.getByRole('alert');
    expect(errorMessage).toHaveTextContent(/password must be at least 8 characters/i);
  });

  it('forwards ref correctly to the HTMLInputElement', () => {
    const ref = React.createRef<HTMLInputElement>();
    render(<Input ref={ref} label="Search" />);

    expect(ref.current).toBeInstanceOf(HTMLInputElement);
    expect(ref.current).toBe(screen.getByLabelText(/search/i));
  });
});

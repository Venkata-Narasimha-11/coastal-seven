import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Button from '../components/ui/Button';

describe('Button Component', () => {
  it('renders correctly with default props', () => {
    render(<Button>Click Me</Button>);
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('bg-blue-600');
  });

  it('renders different variants correctly', () => {
    const { rerender } = render(<Button variant="danger">Delete</Button>);
    expect(screen.getByRole('button', { name: /delete/i })).toHaveClass('bg-red-600');

    rerender(<Button variant="outline">Cancel</Button>);
    expect(screen.getByRole('button', { name: /cancel/i })).toHaveClass('border-slate-300');
  });

  it('triggers onClick handler on user click', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Submit</Button>);

    await user.click(screen.getByRole('button', { name: /submit/i }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables the button and shows loading spinner when isLoading is true', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    render(
      <Button isLoading onClick={handleClick}>
        Saving
      </Button>
    );

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

    await user.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('renders as a polymorphic anchor tag when as="a" is passed', () => {
    render(
      <Button as="a" href="https://example.com">
        External Link
      </Button>
    );

    const link = screen.getByRole('link', { name: /external link/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://example.com');
  });
});

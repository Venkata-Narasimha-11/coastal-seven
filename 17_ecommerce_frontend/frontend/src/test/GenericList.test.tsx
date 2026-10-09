import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import GenericList from '../components/ui/GenericList';

describe('GenericList Component (TypeScript Generics)', () => {
  it('renders a primitive list of strings correctly', () => {
    const items = ['React', 'TypeScript', 'Vitest', 'Playwright'];

    render(
      <GenericList<string>
        items={items}
        keyExtractor={(item) => item}
        renderItem={(item) => <span>{item}</span>}
      />
    );

    expect(screen.getByRole('list')).toBeInTheDocument();
    items.forEach((tech) => {
      expect(screen.getByText(tech)).toBeInTheDocument();
    });
  });

  it('renders complex typed objects using generic parameters', () => {
    interface UserRow {
      id: number;
      name: string;
      role: string;
    }

    const users: UserRow[] = [
      { id: 1, name: 'Alice', role: 'Engineer' },
      { id: 2, name: 'Bob', role: 'Architect' },
    ];

    render(
      <GenericList<UserRow>
        items={users}
        keyExtractor={(user) => user.id}
        renderItem={(user) => (
          <div>
            <span data-testid="user-name">{user.name}</span> - {user.role}
          </div>
        )}
      />
    );

    const renderedNames = screen.getAllByTestId('user-name');
    expect(renderedNames).toHaveLength(2);
    expect(renderedNames[0]).toHaveTextContent('Alice');
    expect(renderedNames[1]).toHaveTextContent('Bob');
  });

  it('renders empty fallback message when items array is empty', () => {
    render(
      <GenericList<string>
        items={[]}
        keyExtractor={(item) => item}
        renderItem={(item) => <span>{item}</span>}
        emptyMessage="No items in this collection"
      />
    );

    expect(screen.getByTestId('generic-list-empty')).toHaveTextContent(
      'No items in this collection'
    );
    expect(screen.queryByRole('list')).not.toBeInTheDocument();
  });
});

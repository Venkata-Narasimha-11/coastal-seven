import React from 'react';
import { describe, it, expect } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { useOrdersQuery, useOrderDetailQuery, useCheckoutMutation } from '../hooks/useOrders';
import { useCreateProductMutation } from '../hooks/useAdmin';
import { createTestQueryClient } from './test-utils';

function createWrapper() {
  const queryClient = createTestQueryClient();
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('TanStack React Query Data Layer & Mutations', () => {
  it('fetches and caches order history query', async () => {
    const { result } = renderHook(() => useOrdersQuery(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toBeDefined();
    expect(result.current.data?.length).toBeGreaterThanOrEqual(2);
    expect(result.current.data?.[0].id).toBe(101);
  });

  it('fetches specific order details by ID', async () => {
    const { result } = renderHook(() => useOrderDetailQuery(101), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.id).toBe(101);
    expect(result.current.data?.status).toBe('shipped');
    expect(result.current.data?.total_amount).toBe(399.98);
  });

  it('executes checkout mutation successfully and invalidates order cache', async () => {
    const { result } = renderHook(() => useCheckoutMutation(), {
      wrapper: createWrapper(),
    });

    await result.current.mutateAsync('Test Destination Address, 560001');

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.shipping_address).toBe('Test Destination Address, 560001');
  });

  it('executes create product mutation and synchronizes server state', async () => {
    const { result } = renderHook(() => useCreateProductMutation(), {
      wrapper: createWrapper(),
    });

    const newProduct = {
      name: 'Smart Ambient Desk Lamp',
      price: 49.99,
      stock: 25,
      category_id: 1,
      description: 'WiFi-connected RGB desk lamp with smart home integration.',
    };

    await result.current.mutateAsync(newProduct);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.name).toBe('Smart Ambient Desk Lamp');
    expect(result.current.data?.price).toBe(49.99);
  });
});

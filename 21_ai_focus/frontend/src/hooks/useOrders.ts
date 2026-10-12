import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import orderService from '../services/orderService';
import { Order, OrderStatus } from '../types/api';

export const ORDER_KEYS = {
  all: ['orders'] as const,
  detail: (id: number) => ['orders', id] as const,
};

/**
 * Hook to fetch the current user's order history.
 */
export const useOrdersQuery = () => {
  return useQuery<Order[], Error>({
    queryKey: ORDER_KEYS.all,
    queryFn: () => orderService.getOrders(),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};

/**
 * Hook to fetch a single order's details by ID.
 */
export const useOrderDetailQuery = (orderId: number) => {
  return useQuery<Order, Error>({
    queryKey: ORDER_KEYS.detail(orderId),
    queryFn: () => orderService.getOrderById(orderId),
    enabled: !!orderId && !isNaN(orderId),
  });
};

/**
 * Mutation to submit an order during checkout.
 */
export const useCheckoutMutation = () => {
  const queryClient = useQueryClient();

  return useMutation<Order, Error, string>({
    mutationFn: (shippingAddress: string) => orderService.checkout(shippingAddress),
    onSuccess: () => {
      // Invalidate orders list, cart, and products so stock count updates immediately
      queryClient.invalidateQueries({ queryKey: ORDER_KEYS.all });
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
};

/**
 * Mutation to update an order's status (Admin only).
 */
export const useUpdateOrderStatusMutation = () => {
  const queryClient = useQueryClient();

  return useMutation<Order, Error, { orderId: number; status: OrderStatus }>({
    mutationFn: ({ orderId, status }) => orderService.updateOrderStatus(orderId, status),
    onSuccess: (updatedOrder) => {
      queryClient.invalidateQueries({ queryKey: ORDER_KEYS.all });
      queryClient.invalidateQueries({ queryKey: ORDER_KEYS.detail(updatedOrder.id) });
    },
  });
};

export default {
  useOrdersQuery,
  useOrderDetailQuery,
  useCheckoutMutation,
  useUpdateOrderStatusMutation,
};

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import productService from '../services/productService';
import orderService from '../services/orderService';
import { Product, ProductCreate, ProductUpdate, Order, OrderStatus } from '../types/api';
import { PRODUCT_KEYS } from './useProducts';
import { ORDER_KEYS } from './useOrders';

export const ADMIN_KEYS = {
  products: ['admin', 'products'] as const,
  orders: ['admin', 'orders'] as const,
};

/**
 * Hook for admin to fetch all products without client-side pagination limits.
 */
export const useAdminProductsQuery = () => {
  return useQuery<{ items: Product[]; total: number }, Error>({
    queryKey: ADMIN_KEYS.products,
    queryFn: async () => {
      const res = await productService.getProducts({ size: 100 });
      return res;
    },
    staleTime: 1000 * 30, // 30 seconds
  });
};

/**
 * Mutation for admin to create a new product.
 */
export const useCreateProductMutation = () => {
  const queryClient = useQueryClient();

  return useMutation<Product, Error, ProductCreate>({
    mutationFn: (newProduct) => productService.createProduct(newProduct),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ADMIN_KEYS.products });
      queryClient.invalidateQueries({ queryKey: PRODUCT_KEYS.all });
    },
  });
};

/**
 * Mutation for admin to update an existing product.
 */
export const useUpdateProductMutation = () => {
  const queryClient = useQueryClient();

  return useMutation<Product, Error, { id: number; data: ProductUpdate }>({
    mutationFn: ({ id, data }) => productService.updateProduct(id, data),
    onSuccess: (updatedProduct) => {
      queryClient.invalidateQueries({ queryKey: ADMIN_KEYS.products });
      queryClient.invalidateQueries({ queryKey: PRODUCT_KEYS.all });
      queryClient.invalidateQueries({ queryKey: PRODUCT_KEYS.detail(updatedProduct.id) });
    },
  });
};

/**
 * Mutation for admin to delete a product.
 */
export const useDeleteProductMutation = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, number>({
    mutationFn: (productId) => productService.deleteProduct(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ADMIN_KEYS.products });
      queryClient.invalidateQueries({ queryKey: PRODUCT_KEYS.all });
    },
  });
};

/**
 * Hook for admin to fetch all orders across all customers.
 */
export const useAdminOrdersQuery = () => {
  return useQuery<Order[], Error>({
    queryKey: ADMIN_KEYS.orders,
    queryFn: () => orderService.getOrders(),
    staleTime: 1000 * 30,
  });
};

/**
 * Mutation for admin to change an order status.
 */
export const useAdminUpdateOrderStatusMutation = () => {
  const queryClient = useQueryClient();

  return useMutation<Order, Error, { orderId: number; status: OrderStatus }>({
    mutationFn: ({ orderId, status }) => orderService.updateOrderStatus(orderId, status),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ADMIN_KEYS.orders });
      queryClient.invalidateQueries({ queryKey: ORDER_KEYS.all });
      queryClient.invalidateQueries({ queryKey: ORDER_KEYS.detail(updated.id) });
    },
  });
};

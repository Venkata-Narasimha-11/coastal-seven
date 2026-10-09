import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productService } from '../services/productService';

/**
 * Hook to fetch paginated products using TanStack Query.
 * Includes query key caching with filters.
 */
export function useProducts(params = {}) {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => productService.getProducts(params),
    placeholderData: (previousData) => previousData, // smooth pagination transition without blank flash
  });
}

/**
 * Hook to fetch a single product by ID with caching.
 */
export function useProduct(productId) {
  return useQuery({
    queryKey: ['product', productId],
    queryFn: () => productService.getProductById(productId),
    enabled: Boolean(productId),
  });
}

/**
 * Hook to fetch categories with extended 10-minute caching.
 */
export function useCategories() {
  return useQuery({
    queryKey: ['categories'],
    queryFn: () => productService.getCategories(),
    staleTime: 10 * 60 * 1000, // Categories change rarely, keep fresh for 10m
  });
}

/**
 * Invalidation hook to refresh product catalog on admin mutations.
 */
export function useInvalidateProducts() {
  const queryClient = useQueryClient();
  return () => {
    queryClient.invalidateQueries({ queryKey: ['products'] });
    queryClient.invalidateQueries({ queryKey: ['categories'] });
  };
}

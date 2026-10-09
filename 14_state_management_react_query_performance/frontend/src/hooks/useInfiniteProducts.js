import { useInfiniteQuery } from '@tanstack/react-query';
import { productService } from '../services/productService';

/**
 * Infinite scrolling query hook for large product datasets.
 * Powered by TanStack Query useInfiniteQuery.
 *
 * @param {Object} filters Catalog filter parameters (search, category_id, sort_by, etc.)
 * @param {number} pageSize Items per batch (default 8)
 */
export function useInfiniteProducts(filters = {}, pageSize = 8) {
  return useInfiniteQuery({
    queryKey: ['products', 'infinite', filters, pageSize],
    queryFn: async ({ pageParam = 1 }) => {
      const data = await productService.getProducts({
        ...filters,
        page: pageParam,
        size: pageSize,
      });
      return data;
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (!lastPage || lastPage.page >= lastPage.pages) {
        return undefined; // No more pages left to load
      }
      return lastPage.page + 1;
    },
    staleTime: 5 * 60 * 1000,
  });
}

import { useQuery } from '@tanstack/react-query';
import productService, { ProductQueryParams } from '../services/productService';
import { ProductListResponse, Product, Category } from '../types/api';

export const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (params: ProductQueryParams) => [...productKeys.lists(), params] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (id: number) => [...productKeys.details(), id] as const,
  categories: () => ['categories'] as const,
};

export const PRODUCT_KEYS = productKeys;


export function useProductsQuery(params: ProductQueryParams = {}) {
  return useQuery<ProductListResponse, Error>({
    queryKey: productKeys.list(params),
    queryFn: () => productService.getProducts(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useProductQuery(id: number) {
  return useQuery<Product, Error>({
    queryKey: productKeys.detail(id),
    queryFn: () => productService.getProduct(id),
    enabled: Boolean(id),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCategoriesQuery() {
  return useQuery<Category[], Error>({
    queryKey: productKeys.categories(),
    queryFn: () => productService.getCategories(),
    staleTime: 1000 * 60 * 10,
  });
}

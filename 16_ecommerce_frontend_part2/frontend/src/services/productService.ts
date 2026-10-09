import apiClient from './apiClient';
import { Product, ProductListResponse, Category } from '../types/api';

export interface ProductQueryParams {
  page?: number;
  size?: number;
  category_id?: number | null;
  search?: string;
  min_price?: number;
  max_price?: number;
  sort_by?: string | null;
}

export const productService = {
  /**
   * Fetch paginated list of products with optional filtering.
   */
  async getProducts(params: ProductQueryParams = {}): Promise<ProductListResponse> {
    const cleanParams: Record<string, string | number> = {};
    if (params.page) cleanParams.page = params.page;
    if (params.size) cleanParams.size = params.size;
    if (params.category_id) cleanParams.category_id = params.category_id;
    if (params.search && params.search.trim()) cleanParams.search = params.search.trim();
    if (params.min_price !== null && params.min_price !== undefined) cleanParams.min_price = params.min_price;
    if (params.max_price !== null && params.max_price !== undefined) cleanParams.max_price = params.max_price;
    if (params.sort_by) cleanParams.sort_by = params.sort_by;

    return apiClient.get<ProductListResponse>('/products/', { params: cleanParams });
  },

  /**
   * Fetch single product by ID.
   */
  async getProduct(id: number): Promise<Product> {
    return apiClient.get<Product>(`/products/${id}`);
  },

  /**
   * Backward-compatible alias for getProduct.
   */
  async getProductById(id: number): Promise<Product> {
    return this.getProduct(id);
  },

  /**
   * Fetch all product categories.
   */
  async getCategories(): Promise<Category[]> {
    return apiClient.get<Category[]>('/products/categories');
  },

  /**
   * Create a new product (Admin only).
   */
  async createProduct(data: any): Promise<Product> {
    return apiClient.post<Product>('/products/', data);
  },

  /**
   * Upload an image file for a product (Admin only).
   */
  async uploadProductImage(productId: number, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/products/${productId}/upload-image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Update product details (Admin only).
   */
  async updateProduct(productId: number, data: any): Promise<Product> {
    return apiClient.put<Product>(`/products/${productId}`, data);
  },

  /**
   * Delete a product (Admin only).
   */
  async deleteProduct(productId: number): Promise<void> {
    return apiClient.delete<void>(`/products/${productId}`);
  },
};

export default productService;

import api from './api';

export const productService = {
  /**
   * Fetch paginated products with optional search and category filters.
   */
  async getProducts({ page = 1, size = 12, category_id = null, search = '', sort_by = null, min_price = null, max_price = null } = {}) {
    const params = { page, size };
    if (category_id) params.category_id = category_id;
    if (search && search.trim()) params.search = search.trim();
    if (sort_by) params.sort_by = sort_by;
    if (min_price !== null && min_price !== undefined && min_price !== '') params.min_price = Number(min_price);
    if (max_price !== null && max_price !== undefined && max_price !== '') params.max_price = Number(max_price);

    const response = await api.get('/products', { params });
    return response.data;
  },

  /**
   * Fetch a single product by ID.
   */
  async getProductById(productId) {
    const response = await api.get(`/products/${productId}`);
    return response.data;
  },

  /**
   * Fetch all product categories.
   */
  async getCategories() {
    const response = await api.get('/products/categories');
    return response.data;
  },

  /**
   * Create a new product (Admin only).
   */
  async createProduct(data) {
    const response = await api.post('/products', data);
    return response.data;
  },

  /**
   * Upload an image file for a product (Admin only).
   */
  async uploadProductImage(productId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/products/${productId}/upload-image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Update product details (Admin only).
   */
  async updateProduct(productId, data) {
    const response = await api.put(`/products/${productId}`, data);
    return response.data;
  },

  /**
   * Delete a product (Admin only).
   */
  async deleteProduct(productId) {
    await api.delete(`/products/${productId}`);
  },
};

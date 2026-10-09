import apiClient from './apiClient';
import { CartResponse } from '../types/api';

export const cartService = {
  /**
   * Fetch current user's shopping cart.
   */
  async getCart(): Promise<CartResponse> {
    return apiClient.get<CartResponse>('/cart/');
  },

  /**
   * Add item to cart.
   */
  async addItem(productId: number, quantity: number = 1): Promise<CartResponse> {
    return apiClient.post<CartResponse>('/cart/items', {
      product_id: Number(productId),
      quantity: Number(quantity),
    });
  },

  /**
   * Backward-compatible alias for addItem.
   */
  async addToCart(productId: number, quantity: number = 1): Promise<CartResponse> {
    return this.addItem(productId, quantity);
  },

  /**
   * Update quantity of an item in the cart.
   */
  async updateQuantity(productId: number, quantity: number): Promise<CartResponse> {
    return apiClient.put<CartResponse>(`/cart/items/${productId}`, {
      quantity: Number(quantity),
    });
  },

  /**
   * Remove item from cart.
   */
  async removeItem(productId: number): Promise<void> {
    return apiClient.delete<void>(`/cart/items/${productId}`);
  },

  /**
   * Clear the entire cart.
   */
  async clearCart(): Promise<void> {
    return apiClient.delete<void>('/cart/');
  },
};

export default cartService;

import api from './api';

export const cartService = {
  /**
   * Fetch all items currently in the user's Redis cart.
   */
  async getCart() {
    const response = await api.get('/cart');
    return response.data;
  },

  /**
   * Add a product to the cart or increment quantity.
   */
  async addToCart(productId, quantity = 1) {
    const response = await api.post('/cart/items', {
      product_id: Number(productId),
      quantity: Number(quantity),
    });
    return response.data;
  },

  /**
   * Update quantity of a product line item in cart.
   */
  async updateQuantity(productId, quantity) {
    const response = await api.put(`/cart/items/${productId}`, {
      quantity: Number(quantity),
    });
    return response.data;
  },

  /**
   * Remove a line item from the cart.
   */
  async removeItem(productId) {
    const response = await api.delete(`/cart/items/${productId}`);
    return response.data;
  },

  /**
   * Clear the entire shopping cart in Redis.
   */
  async clearCart() {
    await api.delete('/cart');
    return { items: [], total_items: 0, total_amount: '0.00' };
  },
};

import api from './api';

export const orderService = {
  /**
   * Execute atomic order checkout from current Redis cart.
   */
  async checkout(shippingAddress) {
    const response = await api.post('/orders/checkout', {
      shipping_address: shippingAddress,
    });
    return response.data;
  },

  /**
   * Fetch all past orders placed by the current user.
   */
  async getOrders() {
    const response = await api.get('/orders');
    return response.data;
  },

  /**
   * Fetch a single order by ID.
   */
  async getOrderById(orderId) {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },

  /**
   * Update order status (Admin only).
   */
  async updateOrderStatus(orderId, status) {
    const response = await api.put(`/orders/${orderId}/status`, { status });
    return response.data;
  },
};

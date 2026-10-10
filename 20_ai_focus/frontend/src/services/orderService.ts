import apiClient from './apiClient';
import { Order, OrderStatus } from '../types/api';
import useCartStore from '../stores/useCartStore';

export const orderService = {
  /**
   * Execute atomic order checkout from current cart.
   * Synchronizes local Zustand cart items to FastAPI Redis cart if needed before placing order.
   */
  async checkout(shippingAddress: string): Promise<Order> {
    const localItems = useCartStore.getState().items;
    if (localItems && localItems.length > 0) {
      try {
        // Clear existing Redis cart to prevent duplicate counts
        await apiClient.delete('/cart').catch(() => {});
        // Push each local item to backend Redis cart
        for (const item of localItems) {
          await apiClient.post('/cart/items', {
            product_id: item.product.id,
            quantity: item.quantity,
          }).catch((err) => {
            console.warn('Pre-checkout item sync error:', err);
          });
        }
      } catch (syncErr) {
        console.warn('Pre-checkout cart sync warning:', syncErr);
      }
    }

    return apiClient.post<Order>('/orders/checkout', {
      shipping_address: shippingAddress,
    });
  },

  /**
   * Fetch all past orders placed by the current user (or all if admin).
   */
  async getOrders(): Promise<Order[]> {
    return apiClient.get<Order[]>('/orders');
  },

  /**
   * Fetch a single order by ID.
   */
  async getOrderById(orderId: number): Promise<Order> {
    return apiClient.get<Order>(`/orders/${orderId}`);
  },

  /**
   * Update order status (Admin only).
   */
  async updateOrderStatus(orderId: number, status: OrderStatus): Promise<Order> {
    return apiClient.put<Order>(`/orders/${orderId}/status`, { status });
  },
};

export default orderService;

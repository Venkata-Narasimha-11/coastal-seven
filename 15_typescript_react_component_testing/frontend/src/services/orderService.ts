import apiClient from './apiClient';
import { Order, OrderStatus } from '../types/api';

export const orderService = {
  /**
   * Execute atomic order checkout from current cart.
   */
  async checkout(shippingAddress: string): Promise<Order> {
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

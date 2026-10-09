import { useCartStore } from '../stores/cartStore';
import { useCartMutation } from './useCartMutation';

/**
 * Universal Cart Hook.
 * Seamlessly interfaces with Zustand store and TanStack Query optimistic mutations.
 */
export function useCart() {
  const store = useCartStore();
  const mutations = useCartMutation();

  const totalItems = store.getItemCount();
  const subtotal = store.getSubtotal();
  const discountAmount = store.getDiscountAmount();
  const shippingFee = store.getShippingFee();
  const totalPrice = store.getTotalPrice();

  return {
    // Zustand raw store & items
    store,
    items: store.items,
    appliedCoupon: store.coupon,
    notes: store.notes,

    // Backward-compatibility wrapper object matching Day 13 API
    cart: {
      items: store.items,
      total_items: totalItems,
      total_amount: totalPrice.toFixed(2),
    },

    // Numerical stats
    totalItems,
    subtotal,
    discountAmount,
    shippingFee,
    totalPrice,

    // Actions
    addToCart: mutations.addToCart,
    updateQuantity: mutations.updateQuantity,
    removeItem: mutations.removeItem,
    clearCart: store.clearCart,
    applyCoupon: store.applyCoupon,
    removeCoupon: store.removeCoupon,
    setNotes: store.setNotes,

    // Loading indicators
    loading: mutations.isAdding || mutations.isUpdating || mutations.isRemoving,
    isAdding: mutations.isAdding,
    isUpdating: mutations.isUpdating,
    isRemoving: mutations.isRemoving,
  };
}

import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';

const VALID_COUPONS = {
  SAVE10: 10,
  REACT20: 20,
  PERF30: 30,
  ZUSTAND50: 50,
};

/**
 * Zustand Global Shopping Cart Store.
 * Supports optimistic sync, local persistence, coupon calculation, and atomic subscriptions.
 */
export const useCartStore = create(
  devtools(
    persist(
      (set, get) => ({
        items: [],
        coupon: null,
        notes: '',

        // -----------------------------------------------------------
        // ACTIONS
        // -----------------------------------------------------------
        addItem: (product, quantity = 1) => {
          set((state) => {
            const existingIndex = state.items.findIndex(
              (item) => (item.id || item.product_id) === (product.id || product.product_id)
            );

            let newItems;
            if (existingIndex > -1) {
              newItems = state.items.map((item, idx) => {
                if (idx === existingIndex) {
                  const maxStock = item.stock ?? 99;
                  const newQty = Math.min(item.quantity + quantity, maxStock);
                  return { ...item, quantity: newQty };
                }
                return item;
              });
            } else {
              const newItem = {
                id: product.id,
                product_id: product.id,
                title: product.title || product.name,
                name: product.title || product.name,
                price: Number(product.price) || 0,
                image: product.image_url || product.image || 'https://via.placeholder.com/300',
                stock: product.stock ?? 99,
                category: product.category?.name || product.category || 'General',
                quantity: Math.min(quantity, product.stock ?? 99),
              };
              newItems = [...state.items, newItem];
            }

            return { items: newItems };
          }, false, 'cart/addItem');
        },

        updateQuantity: (productId, quantity) => {
          if (quantity <= 0) {
            get().removeItem(productId);
            return;
          }

          set((state) => {
            const newItems = state.items.map((item) => {
              if ((item.id || item.product_id) === productId) {
                const maxStock = item.stock ?? 99;
                return { ...item, quantity: Math.min(quantity, maxStock) };
              }
              return item;
            });
            return { items: newItems };
          }, false, 'cart/updateQuantity');
        },

        removeItem: (productId) => {
          set((state) => ({
            items: state.items.filter(
              (item) => (item.id || item.product_id) !== productId
            ),
          }), false, 'cart/removeItem');
        },

        clearCart: () => {
          set({ items: [], coupon: null, notes: '' }, false, 'cart/clearCart');
        },

        // Overwrite full items (used by optimistic rollback and server sync)
        setItems: (newItems) => {
          set({ items: newItems }, false, 'cart/setItems');
        },

        applyCoupon: (code) => {
          const normalized = code.trim().toUpperCase();
          if (VALID_COUPONS[normalized]) {
            const discountPercent = VALID_COUPONS[normalized];
            const couponObj = { code: normalized, discountPercent };
            set({ coupon: couponObj }, false, 'cart/applyCoupon');
            return { success: true, discountPercent };
          }
          return { success: false, message: 'Invalid coupon code. Try REACT20 or ZUSTAND50' };
        },

        removeCoupon: () => {
          set({ coupon: null }, false, 'cart/removeCoupon');
        },

        setNotes: (notes) => {
          set({ notes }, false, 'cart/setNotes');
        },

        // -----------------------------------------------------------
        // COMPUTED SELECTORS
        // -----------------------------------------------------------
        getItemCount: () => {
          return get().items.reduce((total, item) => total + (item.quantity || 0), 0);
        },

        getTotalItems: () => {
          return get().items.reduce((total, item) => total + (item.quantity || 0), 0);
        },

        getSubtotal: () => {
          return get().items.reduce(
            (total, item) => total + (Number(item.price) || 0) * (item.quantity || 0),
            0
          );
        },

        getTotalPrice: () => {
          return get().items.reduce(
            (total, item) => total + (Number(item.price) || 0) * (item.quantity || 0),
            0
          );
        },

        getDiscountAmount: () => {
          const subtotal = get().getSubtotal();
          const { coupon } = get();
          if (!coupon) return 0;
          return (subtotal * coupon.discountPercent) / 100;
        },

        getShippingFee: () => {
          const subtotal = get().getSubtotal();
          if (subtotal === 0) return 0;
          return subtotal > 1000 ? 0 : 50; // Free shipping over ₹1000
        },

        getTotalPrice: () => {
          const subtotal = get().getSubtotal();
          if (subtotal === 0) return 0;
          const discount = get().getDiscountAmount();
          const shipping = get().getShippingFee();
          return Math.max(0, subtotal - discount + shipping);
        },
      }),
      {
        name: 'ecommerce-cart-storage',
        partialize: (state) => ({
          items: state.items,
          coupon: state.coupon,
          notes: state.notes,
        }),
      }
    ),
    { name: 'CartStore' }
  )
);

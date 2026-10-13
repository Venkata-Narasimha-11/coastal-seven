import { create } from 'zustand';
import { CartState, CartStoreItem } from '../types/state';
import { Product } from '../types/api';

const getInitialCart = (): CartStoreItem[] => {
  try {
    // Migration: One-time clear of legacy dummy test electronics from cart
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      if (!localStorage.getItem('sivora_cart_v3_clean')) {
        localStorage.removeItem('local_cart');
        localStorage.setItem('sivora_cart_v3_clean', 'true');
        return [];
      }
    }
    const raw = typeof localStorage !== 'undefined' ? localStorage.getItem('local_cart') : null;
    if (!raw) return [];
    const parsed: CartStoreItem[] = JSON.parse(raw);
    return parsed.filter((item) => item && item.product && item.quantity > 0);
  } catch {
    return [];
  }
};

const getInitialCoupon = (): { coupon: string | null; discountPercent: number } => {
  try {
    const code = localStorage.getItem('local_cart_coupon');
    const discount = Number(localStorage.getItem('local_cart_discount') || '0');
    return { coupon: code || null, discountPercent: discount || 0 };
  } catch {
    return { coupon: null, discountPercent: 0 };
  }
};

const persistCart = (items: CartStoreItem[]) => {
  try {
    localStorage.setItem('local_cart', JSON.stringify(items));
  } catch {
    // Ignore storage quota limits
  }
};

const persistCoupon = (coupon: string | null, discountPercent: number) => {
  try {
    if (coupon) {
      localStorage.setItem('local_cart_coupon', coupon);
      localStorage.setItem('local_cart_discount', discountPercent.toString());
    } else {
      localStorage.removeItem('local_cart_coupon');
      localStorage.removeItem('local_cart_discount');
    }
  } catch {
    // Ignore storage quota limits
  }
};

const COUPON_DISCOUNTS: Record<string, number> = {
  SAVE10: 10,
  WELCOME20: 20,
  SUPER50: 50,
  FREESHIP: 5,
};

export const useCartStore = create<CartState>((set, get) => {
  const initialCouponData = getInitialCoupon();

  return {
    items: getInitialCart(),
    coupon: initialCouponData.coupon,
    discountPercent: initialCouponData.discountPercent,

    addItem: (product: Product, quantity = 1) => {
      set((state) => {
        const existing = state.items.find((item) => item.product.id === product.id);
        let updated: CartStoreItem[];

        if (existing) {
          updated = state.items.map((item) =>
            item.product.id === product.id
              ? { ...item, quantity: item.quantity + quantity }
              : item
          );
        } else {
          updated = [...state.items, { product, quantity }];
        }

        persistCart(updated);
        return { items: updated };
      });
    },

    removeItem: (productId: number) => {
      set((state) => {
        const updated = state.items.filter((item) => item.product.id !== productId);
        persistCart(updated);
        return { items: updated };
      });
    },

    updateQuantity: (productId: number, quantity: number) => {
      set((state) => {
        if (quantity <= 0) {
          const updated = state.items.filter((item) => item.product.id !== productId);
          persistCart(updated);
          return { items: updated };
        }

        const updated = state.items.map((item) =>
          item.product.id === productId ? { ...item, quantity } : item
        );
        persistCart(updated);
        return { items: updated };
      });
    },

    clearCart: () => {
      persistCart([]);
      persistCoupon(null, 0);
      set({ items: [], coupon: null, discountPercent: 0 });
    },

    applyCoupon: (code: string) => {
      const normalizedCode = code.trim().toUpperCase();
      const discount = COUPON_DISCOUNTS[normalizedCode];

      if (discount !== undefined) {
        persistCoupon(normalizedCode, discount);
        set({ coupon: normalizedCode, discountPercent: discount });
        return {
          success: true,
          message: `Coupon ${normalizedCode} applied: ${discount}% OFF!`,
        };
      }

      return {
        success: false,
        message: `Invalid or expired coupon code "${code}". Try SAVE10 or WELCOME20.`,
      };
    },

    removeCoupon: () => {
      persistCoupon(null, 0);
      set({ coupon: null, discountPercent: 0 });
    },

    getTotalItems: () => {
      return get().items.reduce((sum, item) => sum + item.quantity, 0);
    },

    getSubtotal: () => {
      return Number(
        get()
          .items.reduce((sum, item) => sum + item.product.price * item.quantity, 0)
          .toFixed(2)
      );
    },

    getDiscountAmount: () => {
      const subtotal = get().getSubtotal();
      const discount = get().discountPercent;
      return Number(((subtotal * discount) / 100).toFixed(2));
    },

    getShippingCost: () => {
      const subtotal = get().getSubtotal();
      if (subtotal === 0) return 0;
      if (get().coupon === 'FREESHIP' || subtotal >= 100) return 0;
      return 10.0;
    },

    getTaxAmount: () => {
      const discountedSubtotal = Math.max(0, get().getSubtotal() - get().getDiscountAmount());
      return Number((discountedSubtotal * 0.08).toFixed(2)); // 8% sales tax
    },

    getTotalPrice: () => {
      return get().getGrandTotal();
    },

    getGrandTotal: () => {
      const subtotal = get().getSubtotal();
      if (subtotal === 0) return 0;
      const discount = get().getDiscountAmount();
      const shipping = get().getShippingCost();
      const tax = get().getTaxAmount();
      return Number((subtotal - discount + shipping + tax).toFixed(2));
    },
  };
});

export default useCartStore;

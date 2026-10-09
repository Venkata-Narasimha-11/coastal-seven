import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';

/**
 * Zustand Global Wishlist Store.
 */
export const useWishlistStore = create(
  devtools(
    persist(
      (set, get) => ({
        items: [],

        toggleWishlist: (product) => {
          set((state) => {
            const exists = state.items.some((item) => item.id === product.id);
            if (exists) {
              return { items: state.items.filter((item) => item.id !== product.id) };
            }
            return { items: [...state.items, product] };
          }, false, 'wishlist/toggle');
        },

        isInWishlist: (productId) => {
          return get().items.some((item) => item.id === productId);
        },

        removeFromWishlist: (productId) => {
          set(
            (state) => ({ items: state.items.filter((item) => item.id !== productId) }),
            false,
            'wishlist/remove'
          );
        },

        clearWishlist: () => set({ items: [] }, false, 'wishlist/clear'),
      }),
      {
        name: 'ecommerce-wishlist-storage',
      }
    ),
    { name: 'WishlistStore' }
  )
);

import { useWishlistStore } from '../stores/wishlistStore';

export function useWishlist() {
  const store = useWishlistStore();

  return {
    wishlist: store.items,
    items: store.items,
    toggleWishlist: store.toggleWishlist,
    isInWishlist: store.isInWishlist,
    removeFromWishlist: store.removeFromWishlist,
    clearWishlist: store.clearWishlist,
    totalItems: store.items.length,
  };
}

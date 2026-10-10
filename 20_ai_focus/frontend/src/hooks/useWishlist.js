import { useWishlistStore } from '../stores/wishlistStore';
import useCartStore from '../stores/useCartStore';

export function useWishlist() {
  const store = useWishlistStore();
  const addItemToCart = useCartStore((state) => state.addItem);

  const moveToCart = (product) => {
    if (product) {
      addItemToCart(product, 1);
      store.removeFromWishlist(product.id);
    }
  };

  return {
    wishlist: store.items,
    items: store.items,
    toggleWishlist: store.toggleWishlist,
    isInWishlist: store.isInWishlist,
    removeFromWishlist: store.removeFromWishlist,
    clearWishlist: store.clearWishlist,
    moveToCart,
    totalItems: store.items.length,
  };
}

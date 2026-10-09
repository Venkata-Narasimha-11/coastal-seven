import React, { createContext, useState, useEffect, useContext } from 'react';
import { AuthContext } from './AuthContext';
import { CartContext } from './CartContext';
import { toast } from '../components/ui/sonner';

export const WishlistContext = createContext(null);

export const WishlistProvider = ({ children }) => {
  const { user, isAuthenticated, isAdmin } = useContext(AuthContext);
  const { addToCart } = useContext(CartContext);

  const getStorageKey = () => `guntur_store_wishlist_${user?.id || 'guest'}`;

  const [wishlist, setWishlist] = useState(() => {
    try {
      const stored = localStorage.getItem(`guntur_store_wishlist_${user?.id || 'guest'}`);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // Re-sync wishlist when user switches
  useEffect(() => {
    try {
      const stored = localStorage.getItem(getStorageKey());
      setWishlist(stored ? JSON.parse(stored) : []);
    } catch {
      setWishlist([]);
    }
  }, [user?.id]);

  const saveWishlist = (items) => {
    setWishlist(items);
    try {
      localStorage.setItem(getStorageKey(), JSON.stringify(items));
    } catch (e) {
      console.error('Failed to save wishlist:', e);
    }
  };

  const isInWishlist = (productId) => {
    return wishlist.some((item) => item.id === productId);
  };

  const toggleWishlist = (product) => {
    if (isAdmin) {
      toast.warning('Admin Access Detected', {
        description: 'Store administrators cannot maintain customer wishlists.',
      });
      return false;
    }

    if (!isAuthenticated) {
      toast.info('Sign In Required', {
        description: 'Please sign in to save items to your wishlist.',
      });
      return false;
    }

    const exists = isInWishlist(product.id);
    let updated;
    if (exists) {
      updated = wishlist.filter((item) => item.id !== product.id);
      saveWishlist(updated);
      toast.info('Removed from Wishlist', {
        description: `"${product.name}" was removed from your saved items.`,
      });
    } else {
      updated = [
        ...wishlist,
        {
          id: product.id,
          name: product.name,
          price: product.price,
          image_url: product.image_url,
          stock: product.stock,
          category: product.category,
        },
      ];
      saveWishlist(updated);
      toast.success('Saved to Wishlist! ❤️', {
        description: `"${product.name}" added to your wishlist.`,
      });
    }
    return !exists;
  };

  const removeFromWishlist = (productId) => {
    const updated = wishlist.filter((item) => item.id !== productId);
    saveWishlist(updated);
    toast.info('Removed from Wishlist');
  };

  const moveToCart = async (product) => {
    if (isAdmin) return;
    try {
      await addToCart(product.id, 1);
      removeFromWishlist(product.id);
      toast.success('Moved to Cart! 🛒', {
        description: `"${product.name}" moved from Wishlist into your shopping cart.`,
      });
    } catch (err) {
      toast.error('Could not move to cart', {
        description: err.response?.data?.detail || 'Item unavailable',
      });
    }
  };

  const value = {
    wishlist,
    totalItems: wishlist.length,
    isInWishlist,
    toggleWishlist,
    removeFromWishlist,
    moveToCart,
  };

  return <WishlistContext.Provider value={value}>{children}</WishlistContext.Provider>;
};

export default WishlistContext;

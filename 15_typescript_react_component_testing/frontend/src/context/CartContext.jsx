import React, { createContext, useState, useEffect, useContext } from 'react';
import { cartService } from '../services/cartService';
import { AuthContext } from './AuthContext';

export const CartContext = createContext(null);

// Amazon-style promotional coupon directory with single-use per customer rules
export const AVAILABLE_COUPONS = {
  FESTIVE10: {
    code: 'FESTIVE10',
    discountType: 'percentage',
    value: 10,
    minOrder: 40,
    description: '10% Festive Discount on Peripherals & Audio',
    expiryDate: '2026-10-31',
    terms: 'Single-use per customer account. Min cart subtotal $40.00.',
  },
  SAVE20: {
    code: 'SAVE20',
    discountType: 'percentage',
    value: 20,
    minOrder: 100,
    description: '20% Mega Savings on Top Tech Gear',
    expiryDate: '2026-11-15',
    terms: 'Single-use per customer account. Min cart subtotal $100.00.',
  },
  GUNTUR50: {
    code: 'GUNTUR50',
    discountType: 'flat',
    value: 50,
    minOrder: 150,
    description: 'Flat $50 Guntur Store Grand Launch Voucher',
    expiryDate: '2026-12-31',
    terms: 'Single-use per customer account. Min cart subtotal $150.00.',
  },
  AMAZON50: {
    code: 'AMAZON50',
    discountType: 'flat',
    value: 50,
    minOrder: 150,
    description: 'Flat $50 Prime Super Saver Offer',
    expiryDate: '2026-12-31',
    terms: 'Single-use per customer account. Min cart subtotal $150.00.',
  },
};

export const CartProvider = ({ children }) => {
  const { isAuthenticated, user } = useContext(AuthContext);
  const [cart, setCart] = useState({
    items: [],
    total_items: 0,
    total_amount: '0.00',
  });
  const [loading, setLoading] = useState(false);
  const [appliedCoupon, setAppliedCoupon] = useState(null);

  // Dynamic custom coupons created by admin, persisted in localStorage
  const [customCoupons, setCustomCoupons] = useState(() => {
    try {
      const stored = localStorage.getItem('guntur_store_custom_coupons');
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  });

  const allCoupons = { ...AVAILABLE_COUPONS, ...customCoupons };

  const createCoupon = (newCoupon) => {
    const code = newCoupon.code.trim().toUpperCase();
    const updated = {
      ...customCoupons,
      [code]: {
        ...newCoupon,
        code,
        value: Number(newCoupon.value),
        minOrder: Number(newCoupon.minOrder || 0),
      },
    };
    setCustomCoupons(updated);
    localStorage.setItem('guntur_store_custom_coupons', JSON.stringify(updated));
    return true;
  };

  const deleteCoupon = (code) => {
    const upper = code.trim().toUpperCase();
    const updated = { ...customCoupons };
    delete updated[upper];
    setCustomCoupons(updated);
    localStorage.setItem('guntur_store_custom_coupons', JSON.stringify(updated));
  };

  // Storage key for per-user coupon redemption history
  const getRedeemedStorageKey = () => `guntur_store_redeemed_coupons_${user?.id || 'guest'}`;

  // Get list of already used coupons for this user account
  const getUsedCoupons = () => {
    try {
      const data = localStorage.getItem(getRedeemedStorageKey());
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  };

  // Mark coupon as redeemed permanently after order placement
  const markCouponRedeemed = (code) => {
    if (!code) return;
    const upper = code.trim().toUpperCase();
    const used = getUsedCoupons();
    if (!used.includes(upper)) {
      used.push(upper);
      localStorage.setItem(getRedeemedStorageKey(), JSON.stringify(used));
    }
    setAppliedCoupon(null);
  };

  // Fetch cart whenever user authentication status becomes true
  const refreshCart = async () => {
    if (!isAuthenticated) {
      setCart({ items: [], total_items: 0, total_amount: '0.00' });
      setAppliedCoupon(null);
      return;
    }
    setLoading(true);
    try {
      const data = await cartService.getCart();
      setCart(data);
    } catch (err) {
      console.error('Error fetching cart:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshCart();
  }, [isAuthenticated]);

  const addToCart = async (productId, quantity = 1) => {
    const updated = await cartService.addToCart(productId, quantity);
    setCart(updated);
    return updated;
  };

  const updateQuantity = async (productId, quantity) => {
    const updated = await cartService.updateQuantity(productId, quantity);
    setCart(updated);
    return updated;
  };

  const removeItem = async (productId) => {
    const updated = await cartService.removeItem(productId);
    setCart(updated);
    return updated;
  };

  const clearCart = async () => {
    await cartService.clearCart();
    setCart({ items: [], total_items: 0, total_amount: '0.00' });
    setAppliedCoupon(null);
  };

  // Amazon-Style Coupon Validation & Application Logic
  const applyCoupon = (code) => {
    if (!code || !code.trim()) {
      return { success: false, message: 'Please enter a promotional code.' };
    }

    const upper = code.trim().toUpperCase();
    const rawTotal = parseFloat(cart.total_amount) || 0;
    const coupon = allCoupons[upper];

    // 1. Check if coupon code exists
    if (!coupon) {
      const availableCodes = Object.keys(allCoupons).join(', ');
      return {
        success: false,
        message: `The promotional code "${upper}" you entered is invalid. Try: ${availableCodes}.`,
      };
    }

    // 2. Check if user already used this coupon (Amazon rule: 1-time per customer)
    const usedCoupons = getUsedCoupons();
    if (usedCoupons.includes(upper)) {
      return {
        success: false,
        message: `This promotional code ("${upper}") has already been redeemed on your account. Each offer can only be used once per customer.`,
      };
    }

    // 3. Check coupon expiration
    const today = new Date().toISOString().split('T')[0];
    if (today > coupon.expiryDate) {
      return {
        success: false,
        message: `The promotional code "${upper}" expired on ${coupon.expiryDate}.`,
      };
    }

    // 4. Check minimum cart subtotal requirement
    if (rawTotal < coupon.minOrder) {
      return {
        success: false,
        message: `Coupon "${upper}" requires a minimum cart subtotal of $${coupon.minOrder.toFixed(2)}. Your current subtotal is $${rawTotal.toFixed(2)}.`,
      };
    }

    // 5. Calculate discount
    let discount = 0;
    if (coupon.discountType === 'percentage') {
      discount = Number(((rawTotal * coupon.value) / 100).toFixed(2));
    } else {
      discount = Number(coupon.value.toFixed(2));
    }

    const couponObj = {
      code: upper,
      discount,
      description: coupon.description,
      terms: coupon.terms,
      expiryDate: coupon.expiryDate,
    };

    setAppliedCoupon(couponObj);
    return {
      success: true,
      message: `Promotional code "${upper}" applied! You saved $${discount.toFixed(2)}.`,
      coupon: couponObj,
    };
  };

  const removeCoupon = () => {
    setAppliedCoupon(null);
  };

  // Calculate final totals
  const rawSubtotal = parseFloat(cart.total_amount) || 0;
  const discountAmount = appliedCoupon ? Math.min(rawSubtotal, appliedCoupon.discount) : 0;
  const finalPayable = Math.max(0, rawSubtotal - discountAmount);

  const value = {
    cart,
    loading,
    refreshCart,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    appliedCoupon,
    applyCoupon,
    removeCoupon,
    markCouponRedeemed,
    getUsedCoupons,
    discountAmount,
    finalPayable,
    allCoupons,
    createCoupon,
    deleteCoupon,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

export default CartContext;

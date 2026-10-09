import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Trash2,
  ShoppingBag,
  ArrowRight,
  ShieldCheck,
  Tag,
  Check,
  X,
  Sparkles,
  AlertCircle,
  Clock,
  Settings,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';
import { toast } from '../components/ui/sonner';

export const CartPage = () => {
  const {
    cart,
    updateQuantity,
    removeItem,
    clearCart,
    loading,
    appliedCoupon,
    applyCoupon,
    removeCoupon,
    getUsedCoupons,
    discountAmount,
    finalPayable,
    allCoupons,
  } = useCart();
  const { isAdmin } = useAuth();
  const navigate = useNavigate();

  const [couponCode, setCouponCode] = useState('');
  const [couponError, setCouponError] = useState('');

  const usedCoupons = getUsedCoupons ? getUsedCoupons() : [];

  const handleApplyCoupon = (codeToApply) => {
    const targetCode = codeToApply || couponCode;
    if (!targetCode.trim()) {
      setCouponError('Please enter a coupon code.');
      return;
    }
    setCouponError('');
    const res = applyCoupon(targetCode);
    if (res.success) {
      toast.success(res.message, {
        description: `${res.coupon.description} (${res.coupon.terms})`,
      });
      setCouponCode('');
    } else {
      setCouponError(res.message);
      toast.error('Coupon Not Applied', { description: res.message });
    }
  };

  const handleRemoveCoupon = () => {
    removeCoupon();
    toast.info('Coupon removed');
  };

  if (isAdmin) {
    return (
      <div className="card" style={{ maxWidth: '560px', margin: '4rem auto', textAlign: 'center', padding: '3.5rem 2rem', border: '1px solid rgba(234, 179, 8, 0.4)' }}>
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: 'rgba(234, 179, 8, 0.15)',
            color: '#eab308',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.5rem',
          }}
        >
          <ShieldCheck size={32} />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.75rem', color: '#eab308' }}>
          Admin Mode: Shopping Disabled
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', lineHeight: '1.6' }}>
          In accordance with store policy, administrators cannot add items to a personal cart or place retail orders. Please use the Admin Hub to manage products, inventory, and customer orders.
        </p>
        <Link
          to="/admin"
          className="btn"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#eab308',
            color: '#000000',
            fontWeight: 700,
            padding: '0.65rem 1.25rem',
            borderRadius: '8px',
            textDecoration: 'none',
          }}
        >
          <Settings size={18} />
          <span>Open Admin Hub</span>
        </Link>
      </div>
    );
  }

  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="card" style={{ maxWidth: '540px', margin: '4rem auto', textAlign: 'center', padding: '3.5rem 2rem' }}>
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: 'var(--bg-elevated)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem auto',
          }}
        >
          <ShoppingBag size={28} color="var(--text-muted)" />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          Your Cart is Empty
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          Your shopping cart has no items. Browse Guntur Store to find top deals!
        </p>
        <Link to="/" className="btn btn-primary" style={{ padding: '0.75rem 1.5rem' }}>
          Explore Products
        </Link>
      </div>
    );
  }

  const rawSubtotal = Number(cart.total_amount || 0);

  return (
    <div>
      <div className="flex justify-between items-center" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Shopping Cart</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            {cart.total_items} items in your basket
          </p>
        </div>
        <button
          onClick={clearCart}
          className="btn btn-secondary"
          style={{ fontSize: '0.85rem', color: 'var(--danger)' }}
        >
          Clear Entire Cart
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items List (2 Cols) */}
        <div className="lg:col-span-2">
          <div className="card" style={{ padding: '1rem' }}>
            {cart.items.map((item) => (
              <div
                key={item.product_id}
                className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 border-b last:border-b-0"
                style={{ borderColor: 'var(--border-color)' }}
              >
                {/* Product Info */}
                <div className="flex items-center gap-4">
                  <div
                    style={{
                      width: '64px',
                      height: '64px',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: 'var(--bg-elevated)',
                      overflow: 'hidden',
                      flexShrink: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {item.image_url ? (
                      <img
                        src={item.image_url}
                        alt={item.name}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    ) : (
                      <ShoppingBag size={24} color="var(--text-muted)" />
                    )}
                  </div>
                  <div>
                    <h4 style={{ fontWeight: 600, fontSize: '0.95rem' }}>{item.name}</h4>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                      Unit Price: ${Number(item.unit_price).toFixed(2)}
                    </p>
                  </div>
                </div>

                {/* Quantity Controls */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                    className="btn btn-secondary"
                    style={{ width: '28px', height: '28px', padding: 0 }}
                  >
                    -
                  </button>
                  <span style={{ minWidth: '24px', textAlign: 'center', fontWeight: 600 }}>
                    {item.quantity}
                  </span>
                  <button
                    onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                    className="btn btn-secondary"
                    style={{ width: '28px', height: '28px', padding: 0 }}
                  >
                    +
                  </button>
                </div>

                {/* Subtotal & Delete action */}
                <div className="flex items-center justify-between sm:justify-end gap-6" style={{ minWidth: '130px' }}>
                  <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>
                    ${Number(item.subtotal).toFixed(2)}
                  </span>
                  <button
                    onClick={() => removeItem(item.product_id)}
                    className="btn btn-secondary"
                    style={{ padding: '0.45rem', borderRadius: '50%', color: 'var(--danger)' }}
                    title="Remove item"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Order Summary & Amazon-Style Promo Engine (1 Col) */}
        <div>
          <div className="card" style={{ position: 'sticky', top: '90px', padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem' }}>
              Order Summary
            </h3>

            {/* Price Breakdown */}
            <div className="space-y-2" style={{ fontSize: '0.9rem' }}>
              <div className="flex justify-between" style={{ color: 'var(--text-secondary)' }}>
                <span>Subtotal ({cart.total_items} items):</span>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                  ${rawSubtotal.toFixed(2)}
                </span>
              </div>

              {appliedCoupon && (
                <div className="flex justify-between items-center text-emerald-500 font-semibold animate-in fade-in-50">
                  <span className="flex items-center gap-1">
                    <Tag size={13} /> {appliedCoupon.code} Discount:
                  </span>
                  <div className="flex items-center gap-1.5">
                    <span>-${Number(discountAmount || 0).toFixed(2)}</span>
                    <button
                      onClick={handleRemoveCoupon}
                      className="text-xs text-muted-foreground hover:text-destructive underline"
                      title="Remove promo code"
                    >
                      (Remove)
                    </button>
                  </div>
                </div>
              )}

              <div className="flex justify-between" style={{ color: 'var(--text-secondary)' }}>
                <span>Shipping:</span>
                <span style={{ color: 'var(--success)', fontWeight: 600 }}>FREE</span>
              </div>
            </div>

            <div
              style={{
                borderTop: '1px solid var(--border-color)',
                margin: '1rem 0',
              }}
            />

            {/* Total Payable */}
            <div className="flex justify-between items-baseline" style={{ marginBottom: '1.25rem' }}>
              <span style={{ fontSize: '1.05rem', fontWeight: 700 }}>Total Payable:</span>
              <div className="text-right">
                {appliedCoupon && (
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textDecoration: 'line-through', marginRight: '6px' }}>
                    ${rawSubtotal.toFixed(2)}
                  </span>
                )}
                <span style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary)' }}>
                  ${Number(finalPayable || rawSubtotal).toFixed(2)}
                </span>
              </div>
            </div>

            {/* Amazon-Style Promo Code Input Section */}
            <div
              className="rounded-lg border p-3 mb-4 space-y-2.5"
              style={{ borderColor: 'var(--border-color)', backgroundColor: 'var(--bg-elevated)' }}
            >
              <div className="flex items-center gap-1.5 text-xs font-bold text-foreground">
                <Tag size={13} className="text-primary" />
                <span>Have a Promo Code? (Amazon Style)</span>
              </div>

              {appliedCoupon ? (
                <div className="rounded bg-emerald-500/10 border border-emerald-500/30 p-2 text-xs text-emerald-600 dark:text-emerald-400 space-y-1">
                  <div className="flex items-center justify-between font-bold">
                    <span>✓ Code "{appliedCoupon.code}" Active</span>
                    <button
                      onClick={handleRemoveCoupon}
                      className="text-[11px] underline text-muted-foreground hover:text-destructive"
                    >
                      Remove
                    </button>
                  </div>
                  <p className="text-[11px] text-muted-foreground">{appliedCoupon.description}</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="e.g. FESTIVE10"
                      value={couponCode}
                      onChange={(e) => {
                        setCouponCode(e.target.value.toUpperCase());
                        setCouponError('');
                      }}
                      className="input flex-1 uppercase text-xs"
                      style={{ padding: '0.45rem 0.65rem' }}
                    />
                    <button
                      onClick={() => handleApplyCoupon()}
                      className="btn btn-secondary text-xs"
                      style={{ padding: '0.45rem 0.85rem', fontWeight: 700 }}
                    >
                      Apply
                    </button>
                  </div>

                  {couponError && (
                    <p className="text-[11px] text-destructive flex items-center gap-1">
                      <AlertCircle size={12} />
                      <span>{couponError}</span>
                    </p>
                  )}
                </div>
              )}

              {/* Quick 1-Click Deals Chips */}
              <div className="pt-1">
                <span className="text-[10px] text-muted-foreground font-semibold block mb-1">
                  Available Offers (Single-Use per Customer):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {Object.values(allCoupons || {}).map((deal) => {
                    const isUsed = usedCoupons.includes(deal.code);
                    const isActive = appliedCoupon?.code === deal.code;
                    const discountText = deal.discountType === 'percentage' ? `${deal.value}% OFF` : `$${deal.value} OFF`;
                    const label = `${discountText} ($${deal.minOrder}+ min)`;

                    return (
                      <button
                        key={deal.code}
                        type="button"
                        disabled={isUsed || isActive}
                        onClick={() => handleApplyCoupon(deal.code)}
                        className={`text-[10px] px-2 py-1 rounded border transition-all flex items-center gap-1 ${
                          isActive
                            ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400 font-bold'
                            : isUsed
                            ? 'bg-muted/40 border-border text-muted-foreground line-through opacity-60 cursor-not-allowed'
                            : 'bg-background hover:bg-primary/10 border-primary/30 text-primary hover:border-primary font-medium'
                        }`}
                        title={
                          isUsed
                            ? `Redeemed on your account`
                            : `Click to apply ${deal.code} (${label})`
                        }
                      >
                        {isActive && <Check size={10} />}
                        <span>{deal.code}</span>
                        <span className="text-[9px] opacity-75">
                          {isUsed ? '(Redeemed)' : label}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Proceed to Checkout Button */}
            <button
              onClick={() => navigate('/checkout')}
              className="btn btn-primary"
              style={{ width: '100%', padding: '0.85rem' }}
            >
              <span>Proceed to Checkout</span>
              <ArrowRight size={18} />
            </button>

            <div
              className="flex items-center gap-2"
              style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.78rem', justifyContent: 'center' }}
            >
              <ShieldCheck size={15} />
              <span>Guntur Store 256-Bit Encrypted Checkout</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;

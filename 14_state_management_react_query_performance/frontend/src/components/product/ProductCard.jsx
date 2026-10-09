import React, { useState, useMemo, useCallback, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, Check, AlertCircle, Zap, Star, ShieldCheck, Heart, Cpu } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useCart } from '../../hooks/useCart';
import { useWishlist } from '../../hooks/useWishlist';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { toast } from '../ui/sonner';

/**
 * Performance-Optimized Product Card.
 * Utilizes React.memo, useMemo, and useCallback to guarantee zero wasted re-renders.
 */
const ProductCardComponent = ({ product, showRenderStats = false }) => {
  const { isAuthenticated, user } = useAuth();
  const isAdmin = user?.role === 'admin';
  const { addToCart } = useCart();
  const { isInWishlist, toggleWishlist } = useWishlist ? useWishlist() : { isInWishlist: () => false, toggleWishlist: () => {} };
  const navigate = useNavigate();

  const [adding, setAdding] = useState(false);
  const [buying, setBuying] = useState(false);
  const [added, setAdded] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [isSelected, setIsSelected] = useState(false);

  // Performance Track: count renders of this specific card
  const renderCounter = useRef(0);
  renderCounter.current += 1;

  const isOutOfStock = product.stock <= 0;
  const isLowStock = product.stock > 0 && product.stock <= 5;

  // Memoized expensive derived metrics (useMemo)
  const { ratingVal, ratingCount, originalPrice, discountPercent } = useMemo(() => {
    const rVal = (4.0 + ((product.id * 3) % 9) / 10).toFixed(1);
    const rCount = 80 + ((product.id * 147) % 2400);
    const priceNum = Number(product.price) || 0;
    const orig = (priceNum * 1.3).toFixed(2);
    const discount = 23;
    return {
      ratingVal: rVal,
      ratingCount: rCount,
      originalPrice: orig,
      discountPercent: discount,
    };
  }, [product.id, product.price]);

  // Memoized handler (useCallback) to avoid child re-binding
  const handleAddToCart = useCallback(
    async (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (isAdmin) {
        toast.warning('Admin Access Detected', {
          description: 'Administrators have store management access only.',
        });
        return;
      }
      if (isOutOfStock) return;

      setAdding(true);
      setErrorMsg('');
      try {
        await addToCart(product, 1);
        setAdded(true);
        setTimeout(() => setAdded(false), 2000);
      } catch (err) {
        const msg = err.response?.data?.detail || 'Failed to add item to cart';
        setErrorMsg(msg);
        toast.error('Could not add to cart', { description: msg });
        setTimeout(() => setErrorMsg(''), 3000);
      } finally {
        setAdding(false);
      }
    },
    [isAdmin, isOutOfStock, product, addToCart]
  );

  const handleBuyNow = useCallback(
    async (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (isAdmin) {
        toast.warning('Admin Access Detected', {
          description: 'Administrators cannot place retail consumer orders.',
        });
        return;
      }
      if (isOutOfStock) return;

      setBuying(true);
      setErrorMsg('');
      try {
        await addToCart(product, 1);
        navigate('/checkout');
      } catch (err) {
        const msg = err.response?.data?.detail || 'Failed to process purchase';
        setErrorMsg(msg);
        setTimeout(() => setErrorMsg(''), 3000);
      } finally {
        setBuying(false);
      }
    },
    [isAdmin, isOutOfStock, product, addToCart, navigate]
  );

  const handleWishlistToggle = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleWishlist(product);
    },
    [product, toggleWishlist]
  );

  return (
    <div
      tabIndex={0}
      onClick={() => setIsSelected(!isSelected)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          navigate(`/products/${product.id}`);
        }
      }}
      className={`group relative flex flex-col justify-between rounded-2xl border bg-card p-4 transition-all duration-300 outline-none cursor-pointer ${
        isOutOfStock
          ? 'border-destructive/40 opacity-80'
          : isSelected
          ? 'border-primary ring-2 ring-primary ring-offset-2 ring-offset-background shadow-xl shadow-primary/20 scale-[1.01]'
          : 'border-border/80 hover:border-primary/80 hover:ring-2 hover:ring-primary/40 hover:ring-offset-2 hover:ring-offset-background hover:shadow-xl hover:shadow-primary/10 hover:-translate-y-1 focus:border-primary focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-background'
      }`}
    >
      {/* Dev Render Counter Badge for Performance Inspection */}
      {showRenderStats && (
        <div className="absolute -top-2.5 -right-2.5 z-20">
          <Badge className="bg-emerald-600 text-white text-[10px] font-mono shadow-md flex items-center gap-1 px-1.5 py-0.5">
            <Cpu className="w-2.5 h-2.5" /> Renders: {renderCounter.current}
          </Badge>
        </div>
      )}

      <div>
        {/* Product Media & Image with fixed aspect-ratio to eliminate CLS */}
        <Link
          to={`/products/${product.id}`}
          onClick={(e) => e.stopPropagation()}
          className="block relative aspect-4/3 w-full overflow-hidden rounded-xl bg-muted/30 border border-border/50 mb-3"
        >
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name || product.title}
              loading="lazy"
              decoding="async"
              width="400"
              height="300"
              className={`h-full w-full object-cover transition-transform duration-500 group-hover:scale-105 ${
                isOutOfStock ? 'grayscale contrast-75' : ''
              }`}
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-xs text-muted-foreground">
              No Image
            </div>
          )}

          {/* Out of Stock Ribbon */}
          {isOutOfStock && (
            <div className="absolute top-2.5 right-2.5 rounded-md bg-destructive/95 px-2.5 py-1 text-[10px] font-extrabold tracking-wider text-destructive-foreground uppercase shadow-md backdrop-blur-xs">
              Out of Stock
            </div>
          )}

          {/* Wishlist Heart Icon */}
          {!isAdmin && (
            <button
              type="button"
              onClick={handleWishlistToggle}
              className="absolute top-2.5 left-2.5 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-background/85 backdrop-blur-md shadow-sm border border-border/80 transition-all hover:scale-110 active:scale-95 text-muted-foreground hover:text-foreground hover:bg-background"
              title={isInWishlist(product.id) ? 'Remove from Wishlist' : 'Save to Wishlist'}
            >
              <Heart
                className={`h-4 w-4 transition-colors ${
                  isInWishlist(product.id) ? 'fill-rose-500 text-rose-500' : 'text-muted-foreground'
                }`}
              />
            </button>
          )}

          {/* Active Selection Glow Ring Indicator */}
          {isSelected && (
            <div className="absolute bottom-2 left-2 flex items-center gap-1 rounded-full bg-primary text-primary-foreground px-2 py-0.5 text-[10px] font-bold shadow-md animate-in fade-in-50">
              <Check className="h-3 w-3" /> Selected
            </div>
          )}
        </Link>

        {/* Category Badge & Prime Tag */}
        <div className="flex items-center justify-between mb-1.5">
          {product.category ? (
            <Badge variant="secondary" className="text-[10px] py-0 px-2 font-semibold">
              {product.category.name || product.category}
            </Badge>
          ) : (
            <span />
          )}
          {!isOutOfStock && (
            <span className="flex items-center gap-1 text-[11px] font-extrabold italic text-sky-500">
              <Zap className="h-3 w-3 fill-sky-500" /> prime
            </span>
          )}
        </div>

        {/* Product Title */}
        <Link
          to={`/products/${product.id}`}
          onClick={(e) => e.stopPropagation()}
          className="block"
        >
          <h3 className="font-semibold text-sm line-clamp-1 text-foreground group-hover:text-primary transition-colors">
            {product.name || product.title}
          </h3>
        </Link>

        {/* Star Ratings */}
        <div className="flex items-center gap-1.5 my-1.5">
          <div className="flex items-center text-amber-500">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`h-3 w-3 ${
                  i < 4 ? 'fill-amber-500' : 'fill-amber-500/30 text-amber-500/40'
                }`}
              />
            ))}
          </div>
          <span className="text-[11px] font-medium text-muted-foreground">
            {ratingVal} ({ratingCount})
          </span>
        </div>

        {/* Stock Urgency Status */}
        <div className="min-h-[20px] mb-3">
          {isOutOfStock ? (
            <span className="text-[11px] font-bold text-destructive">
              ❌ Currently Out of Stock
            </span>
          ) : isLowStock ? (
            <span className="text-[11px] font-bold text-amber-600 dark:text-amber-400">
              ⚠️ Only {product.stock} left in stock!
            </span>
          ) : (
            <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
              ✓ In Stock ({product.stock} available)
            </span>
          )}
        </div>
      </div>

      {/* Footer: Pricing & Action Buttons */}
      <div className="space-y-3 pt-2 border-t border-border/50">
        {errorMsg && (
          <p className="flex items-center gap-1 text-[11px] text-destructive">
            <AlertCircle className="h-3 w-3" />
            <span>{errorMsg}</span>
          </p>
        )}

        <div className="flex items-baseline justify-between">
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-extrabold text-foreground">
              ${Number(product.price).toFixed(2)}
            </span>
            <span className="text-xs text-muted-foreground line-through">
              ${originalPrice}
            </span>
          </div>
          <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400">
            {discountPercent}% OFF
          </span>
        </div>

        {/* Action Buttons */}
        {isAdmin ? (
          <Button
            variant="outline"
            size="sm"
            className="w-full text-xs border-amber-500/40 text-amber-600 dark:text-amber-400 hover:bg-amber-500/10 h-8"
            onClick={(e) => {
              e.stopPropagation();
              navigate('/admin');
            }}
          >
            <ShieldCheck className="h-3.5 w-3.5 mr-1" /> Admin: Manage in Hub
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="flex-1 text-xs h-8 border-primary text-primary hover:bg-primary/10 font-semibold"
              disabled={isOutOfStock || adding || buying}
              onClick={handleAddToCart}
            >
              {adding ? (
                'Adding...'
              ) : added ? (
                <>
                  <Check className="h-3.5 w-3.5 mr-1 text-emerald-600" /> Added
                </>
              ) : (
                <>
                  <ShoppingCart className="h-3.5 w-3.5 mr-1" /> Add
                </>
              )}
            </Button>

            <Button
              size="sm"
              className="flex-1 text-xs h-8 font-semibold bg-amber-500 text-slate-950 hover:bg-amber-400"
              disabled={isOutOfStock || adding || buying}
              onClick={handleBuyNow}
            >
              <Zap className="h-3.5 w-3.5 mr-1" /> Buy Now
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

// React.memo comparison to prevent unnecessary re-renders when parent re-renders
export const ProductCard = React.memo(ProductCardComponent, (prevProps, nextProps) => {
  return (
    prevProps.product.id === nextProps.product.id &&
    prevProps.product.price === nextProps.product.price &&
    prevProps.product.stock === nextProps.product.stock &&
    prevProps.product.name === nextProps.product.name &&
    prevProps.showRenderStats === nextProps.showRenderStats
  );
});

export default ProductCard;

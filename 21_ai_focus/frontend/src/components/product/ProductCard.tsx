import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingBag, Check, Heart, Star, Sparkles } from 'lucide-react';
import { Product } from '../../types/api';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import Button from '../ui/Button';
import { useWishlist } from '../../hooks/useWishlist';
import useAuthStore from '../../stores/useAuthStore';

const getFallbackImageUrl = (name: string): string => {
  const n = (name || '').toLowerCase();
  // SIVORA Luxury Fashion Fallbacks
  if (n.includes('lehenga') || n.includes('bridal') || n.includes('wedding'))
    return 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80';
  if (n.includes('saree') || n.includes('silk') || n.includes('banarasi'))
    return 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80';
  if (n.includes('gown') || n.includes('dress') || n.includes('sequin') || n.includes('slip'))
    return 'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=800&auto=format&fit=crop&q=80';
  if (n.includes('blazer') || n.includes('corset') || n.includes('anarkali') || n.includes('kurta'))
    return 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop&q=80';
  if (n.includes('sherwani') || n.includes('tuxedo') || n.includes('gentleman') || n.includes('nehru') || n.includes('boy'))
    return 'https://images.unsplash.com/photo-1597983073493-88cd35cf93b0?w=800&auto=format&fit=crop&q=80';
  if (n.includes('princess') || n.includes('tulle') || n.includes('frock') || n.includes('butterfly') || n.includes('girl'))
    return 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80';
  if (n.includes('bag') || n.includes('tote') || n.includes('clutch') || n.includes('minaudière') || n.includes('crossbody'))
    return 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&auto=format&fit=crop&q=80';
  if (n.includes('choker') || n.includes('jewel') || n.includes('bracelet') || n.includes('jhumka') || n.includes('ring'))
    return 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80';
  if (n.includes('pump') || n.includes('stiletto') || n.includes('heel') || n.includes('jutti') || n.includes('sandal'))
    return 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800&auto=format&fit=crop&q=80';
  if (n.includes('parfum') || n.includes('oud') || n.includes('serum') || n.includes('lip') || n.includes('oil'))
    return 'https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=800&auto=format&fit=crop&q=80';
  // Legacy fallbacks
  if (n.includes('headphone') || n.includes('audio') || n.includes('sony') || n.includes('bose'))
    return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80';
  if (n.includes('airpod') || n.includes('earbud'))
    return 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&auto=format&fit=crop&q=80';
  if (n.includes('monitor') || n.includes('display'))
    return 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80';
  if (n.includes('mouse') || n.includes('keyboard'))
    return 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80';
  return 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80';
};

export interface ProductCardProps {
  product: Product;
  onAddToCart?: (product: Product) => void;
  showStock?: boolean;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onAddToCart,
  showStock = true,
}) => {
  const { user } = useAuthStore();
  const [isAdded, setIsAdded] = React.useState(false);
  const [imgSrc, setImgSrc] = React.useState<string>(
    product.image_url || getFallbackImageUrl(product.name)
  );

  React.useEffect(() => {
    setImgSrc(product.image_url || getFallbackImageUrl(product.name));
  }, [product.image_url, product.name]);

  const { isInWishlist, toggleWishlist } = useWishlist();
  const isFavorite = isInWishlist(product.id);
  const isOutOfStock = product.stock <= 0;
  const isLowStock = product.stock > 0 && product.stock <= 5;

  // Nykaa Fashion MRP & Discount calculations
  const priceNum = Number(product.price) || 0;
  const mrpNum = Math.round(priceNum * 1.25);
  const discountPercent = 20;

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (isOutOfStock) return;

    if (onAddToCart) {
      onAddToCart(product);
    }

    setIsAdded(true);
    setTimeout(() => setIsAdded(false), 1200);
  };

  return (
    <div
      data-testid={`product-card-${product.id}`}
      className="group relative flex flex-col h-full bg-white dark:bg-slate-900 rounded-2xl overflow-hidden border border-slate-200/80 dark:border-slate-800 hover:border-pink-300 dark:hover:border-pink-900 hover:shadow-xl hover:shadow-pink-500/10 transition-all duration-300"
    >
      {/* Product Image in Nykaa Fashion 3:4 Portrait Aspect Ratio */}
      <div className="relative aspect-[3/4] w-full overflow-hidden bg-slate-50 dark:bg-slate-800/50 flex items-center justify-center">
        {/* Wishlist Heart Toggle Button */}
        {user?.role !== 'admin' && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              toggleWishlist(product);
            }}
            data-testid={`wishlist-toggle-btn-${product.id}`}
            className={`absolute top-3 right-3 p-2.5 rounded-full transition-all duration-200 z-10 shadow-md ${
              isFavorite
                ? 'bg-rose-500 text-white scale-110'
                : 'bg-white/90 dark:bg-slate-900/90 text-slate-400 hover:text-rose-500 hover:scale-110 backdrop-blur-sm'
            }`}
            aria-label={isFavorite ? `Remove ${product.name} from wishlist` : `Save ${product.name} to wishlist`}
            title={isFavorite ? 'Remove from Wishlist' : 'Save to Wishlist'}
          >
            <Heart className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
          </button>
        )}

        {/* Nykaa Bestseller / Exclusive Tag */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5 z-10">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black tracking-wider uppercase bg-gradient-to-r from-pink-600 to-rose-600 text-white shadow-sm">
            <Sparkles className="h-2.5 w-2.5" />
            SIVORA LUXE
          </span>
          {discountPercent > 0 && (
            <span className="inline-block px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-400/90 text-slate-950 shadow-sm">
              {discountPercent}% OFF
            </span>
          )}
        </div>

        <Link to={`/products/${product.id}`} className="block h-full w-full">
          <img
            src={imgSrc}
            alt={product.name}
            className="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
            onError={() => {
              const fallback = getFallbackImageUrl(product.name);
              if (imgSrc !== fallback) {
                setImgSrc(fallback);
              }
            }}
          />
        </Link>

        {/* Rating Floating Tag */}
        <div className="absolute bottom-2.5 left-2.5 px-2 py-0.5 rounded-md bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200/50 dark:border-slate-800 text-[11px] font-bold text-slate-800 dark:text-slate-100 flex items-center gap-1 shadow-sm">
          <Star className="h-3 w-3 text-amber-500 fill-amber-500" />
          <span>4.8</span>
          <span className="text-[10px] text-muted-foreground font-normal">| 1.2k</span>
        </div>

        {/* Stock Badge Overlay */}
        {showStock && (
          <div className="absolute bottom-2.5 right-2.5">
            {isOutOfStock ? (
              <Badge variant="danger" data-testid="out-of-stock-badge">
                Out of Stock
              </Badge>
            ) : isLowStock ? (
              <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-500 text-white shadow-sm animate-pulse" data-testid="low-stock-badge">
                Only {product.stock} left!
              </span>
            ) : (
              <Badge variant="success" data-testid="in-stock-badge" className="text-[10px] font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                In Stock ({product.stock})
              </Badge>
            )}
          </div>
        )}
      </div>

      {/* Product Details (Nykaa Fashion Luxury Typography) */}
      <div className="flex-1 flex flex-col justify-between p-4 space-y-2.5">
        <div>
          {/* Brand & Category Subtitle */}
          <div className="flex items-center justify-between text-[11px] font-bold tracking-widest uppercase text-pink-600 dark:text-pink-400 mb-1">
            <span>{product.category?.name || 'SIVORA COLLECTION'}</span>
            {product.stock > 0 && (
              <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium lowercase">
                ● in stock
              </span>
            )}
          </div>

          {/* Product Title */}
          <Link
            to={`/products/${product.id}`}
            className="block text-sm font-bold text-slate-900 dark:text-white group-hover:text-pink-600 transition-colors line-clamp-1 leading-snug"
          >
            {product.name}
          </Link>

          {/* Description Preview */}
          {product.description && (
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
              {product.description}
            </p>
          )}
        </div>

        {/* Pricing & Add to Bag Row */}
        <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 space-y-2">
          {/* Nykaa Fashion Price Display */}
          <div className="flex items-baseline gap-2">
            <span
              data-testid="product-price"
              className="text-lg font-black text-slate-900 dark:text-white"
            >
              ₹{priceNum.toLocaleString('en-IN')}
              <span className="sr-only">${priceNum.toFixed(2)}</span>
            </span>
            <span className="text-xs text-slate-400 line-through">
              ₹{mrpNum.toLocaleString('en-IN')}
            </span>
            <span className="text-xs font-black text-pink-600 dark:text-pink-400">
              ({discountPercent}% OFF)
            </span>
          </div>

          {/* Add to Bag Action Button */}
          <Button
            size="sm"
            variant={isAdded ? 'secondary' : 'primary'}
            disabled={isOutOfStock}
            onClick={handleAddToCart}
            data-testid={`add-to-cart-btn-${product.id}`}
            aria-label={`Add ${product.name} to cart`}
            className={`w-full font-bold tracking-wider uppercase text-xs transition-all duration-200 ${
              isAdded
                ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                : 'bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-700 hover:to-rose-700 text-white shadow-md shadow-pink-500/20'
            }`}
            leftIcon={
              isAdded ? (
                <Check className="h-3.5 w-3.5 text-white" />
              ) : (
                <ShoppingBag className="h-3.5 w-3.5" />
              )
            }
          >
            {isOutOfStock ? 'Sold Out' : isAdded ? 'Added to Bag ✨' : 'Add to Bag'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;

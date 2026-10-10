import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, Check, Heart } from 'lucide-react';
import { Product } from '../../types/api';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import Button from '../ui/Button';
import { useWishlist } from '../../hooks/useWishlist';
import useAuthStore from '../../stores/useAuthStore';

const getFallbackImageUrl = (name: string): string => {
  const n = (name || '').toLowerCase();
  if (n.includes('headphone') || n.includes('audio'))
    return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80';
  if (n.includes('monitor') || n.includes('display'))
    return 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80';
  if (n.includes('mouse'))
    return 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80';
  if (n.includes('keyboard'))
    return 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80';
  if (n.includes('phone') || n.includes('iphone') || n.includes('galaxy'))
    return 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop&q=80';
  if (n.includes('laptop') || n.includes('macbook') || n.includes('dell'))
    return 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80';
  if (n.includes('watch') || n.includes('fitness'))
    return 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&auto=format&fit=crop&q=80';
  if (n.includes('soundbar') || n.includes('speaker'))
    return 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80';
  return 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=600&auto=format&fit=crop&q=80';
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
    <Card
      data-testid={`product-card-${product.id}`}
      className="flex flex-col h-full group hover:border-slate-300"
    >
      {/* Product Image */}
      <div className="relative aspect-square w-full overflow-hidden bg-slate-100 flex items-center justify-center">
        {/* Wishlist Heart Toggle Button (Only for shoppers, hidden for admin) */}
        {user?.role !== 'admin' && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              toggleWishlist(product);
            }}
            data-testid={`wishlist-toggle-btn-${product.id}`}
            className={`absolute top-2.5 left-2.5 p-2 rounded-full transition-all duration-200 z-10 shadow-md ${
              isFavorite
                ? 'bg-rose-500 text-white hover:bg-rose-600 scale-110'
                : 'bg-white/90 dark:bg-slate-900/90 text-slate-400 hover:text-rose-500 hover:scale-110'
            }`}
            aria-label={isFavorite ? `Remove ${product.name} from wishlist` : `Save ${product.name} to wishlist`}
            title={isFavorite ? 'Remove from Wishlist' : 'Save to Wishlist'}
          >
            <Heart className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
          </button>
        )}

        <img
          src={imgSrc}
          alt={product.name}
          className="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
          onError={() => {
            const fallback = getFallbackImageUrl(product.name);
            if (imgSrc !== fallback) {
              setImgSrc(fallback);
            }
          }}
        />

        {/* Stock Badge Overlay */}
        {showStock && (
          <div className="absolute top-2.5 right-2.5">
            {isOutOfStock ? (
              <Badge variant="danger" data-testid="out-of-stock-badge">
                Out of Stock
              </Badge>
            ) : isLowStock ? (
              <Badge variant="warning" data-testid="low-stock-badge">
                Only {product.stock} left!
              </Badge>
            ) : (
              <Badge variant="success" data-testid="in-stock-badge">
                In Stock ({product.stock})
              </Badge>
            )}
          </div>
        )}
      </div>

      {/* Product Details */}
      <Card.Content className="flex-1 flex flex-col justify-between p-4 space-y-3">
        <div>
          {product.category && (
            <p className="text-xs font-semibold text-blue-600 tracking-wide uppercase mb-1">
              {product.category.name}
            </p>
          )}
          <Link
            to={`/products/${product.id}`}
            className="block font-semibold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-1"
          >
            {product.name}
          </Link>
          {product.description && (
            <p className="mt-1 text-xs text-slate-500 line-clamp-2">
              {product.description}
            </p>
          )}
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-100">
          <div>
            <span className="text-xs text-slate-500 block">Price</span>
            <span
              data-testid="product-price"
              className="text-lg font-bold text-slate-900"
            >
              ${Number(product.price).toFixed(2)}
            </span>
          </div>

          <Button
            size="sm"
            variant={isAdded ? 'secondary' : 'primary'}
            disabled={isOutOfStock}
            onClick={handleAddToCart}
            data-testid={`add-to-cart-btn-${product.id}`}
            aria-label={`Add ${product.name} to cart`}
            leftIcon={
              isAdded ? (
                <Check className="h-4 w-4 text-emerald-600" />
              ) : (
                <ShoppingCart className="h-4 w-4" />
              )
            }
          >
            {isOutOfStock ? 'Sold Out' : isAdded ? 'Added' : 'Add to Cart'}
          </Button>
        </div>
      </Card.Content>
    </Card>
  );
};

export default ProductCard;

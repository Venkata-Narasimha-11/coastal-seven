import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ShoppingCart, Check, ShieldCheck, Truck, Heart } from 'lucide-react';
import { useProductQuery } from '../hooks/useProducts';
import useCartStore from '../stores/useCartStore';
import { useWishlist } from '../hooks/useWishlist';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Skeleton from '../components/ui/Skeleton';
import ErrorMessage from '../components/common/ErrorMessage';

export const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const productId = Number(id);
  const [quantity, setQuantity] = useState(1);
  const [isAdded, setIsAdded] = useState(false);

  const addItemToCart = useCartStore((state) => state.addItem);
  const { isInWishlist, toggleWishlist } = useWishlist();

  const { data: product, isLoading, isError, error, refetch } = useProductQuery(productId);
  const isFavorite = product ? isInWishlist(product.id) : false;

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-6 w-32" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Skeleton className="aspect-square w-full rounded-2xl" />
          <div className="space-y-4">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-6 w-1/4" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div className="max-w-xl mx-auto">
        <ErrorMessage
          title="Product Not Found"
          message={error?.message || 'The requested product does not exist.'}
          onRetry={() => refetch()}
        />
        <div className="mt-4 text-center">
          <Link to="/">
            <Button variant="outline">Back to Products</Button>
          </Link>
        </div>
      </div>
    );
  }

  const isOutOfStock = product.stock <= 0;

  const handleAddToCart = () => {
    if (isOutOfStock) return;
    addItemToCart(product, quantity);
    setIsAdded(true);
    setTimeout(() => setIsAdded(false), 1500);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-blue-600 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        <span>Back to Products</span>
      </Link>

      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm grid grid-cols-1 md:grid-cols-2">
        {/* Product Image */}
        <div className="relative aspect-square bg-slate-100 flex items-center justify-center p-8">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="max-h-full max-w-full object-contain"
            />
          ) : (
            <div className="text-slate-400 font-medium">No Image Available</div>
          )}

          <div className="absolute top-4 left-4">
            {isOutOfStock ? (
              <Badge variant="danger">Out of Stock</Badge>
            ) : (
              <Badge variant="success">In Stock ({product.stock} available)</Badge>
            )}
          </div>
        </div>

        {/* Product Info */}
        <div className="p-8 flex flex-col justify-between">
          <div className="space-y-4">
            {product.category && (
              <Badge variant="info">{product.category.name}</Badge>
            )}

            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">
              {product.name}
            </h1>

            <div className="text-3xl font-extrabold text-blue-600">
              ${Number(product.price).toFixed(2)}
            </div>

            <p className="text-slate-600 text-sm leading-relaxed">
              {product.description || 'No description provided for this product.'}
            </p>
          </div>

          <div className="space-y-6 pt-6 border-t border-slate-100 mt-6">
            {/* Quantity Selector */}
            {!isOutOfStock && (
              <div className="flex items-center gap-4">
                <label htmlFor="quantity-select" className="text-sm font-medium text-slate-700">
                  Quantity:
                </label>
                <div className="flex items-center border border-slate-300 rounded-lg overflow-hidden">
                  <button
                    type="button"
                    onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                    disabled={quantity <= 1}
                    className="px-3 py-1.5 text-slate-600 hover:bg-slate-100 disabled:opacity-50"
                  >
                    -
                  </button>
                  <span className="px-4 py-1.5 text-sm font-semibold text-slate-800">
                    {quantity}
                  </span>
                  <button
                    type="button"
                    onClick={() => setQuantity((q) => Math.min(product.stock, q + 1))}
                    disabled={quantity >= product.stock}
                    className="px-3 py-1.5 text-slate-600 hover:bg-slate-100 disabled:opacity-50"
                  >
                    +
                  </button>
                </div>
              </div>
            )}

            {/* Add to Cart & Wishlist Actions */}
            <div className="flex items-center gap-3">
              <Button
                size="lg"
                variant={isAdded ? 'secondary' : 'primary'}
                disabled={isOutOfStock}
                onClick={handleAddToCart}
                className="flex-1"
                data-testid="detail-add-to-cart-btn"
                leftIcon={
                  isAdded ? (
                    <Check className="h-5 w-5 text-emerald-600" />
                  ) : (
                    <ShoppingCart className="h-5 w-5" />
                  )
                }
              >
                {isOutOfStock ? 'Currently Out of Stock' : isAdded ? 'Added to Cart!' : 'Add to Cart'}
              </Button>

              <button
                type="button"
                onClick={() => product && toggleWishlist(product)}
                data-testid="detail-wishlist-toggle-btn"
                className={`p-3.5 rounded-xl border transition-all duration-200 flex items-center justify-center ${
                  isFavorite
                    ? 'bg-rose-50 border-rose-300 text-rose-500 dark:bg-rose-950/30 dark:border-rose-800'
                    : 'border-slate-300 dark:border-slate-700 text-slate-500 hover:text-rose-500 hover:border-rose-300'
                }`}
                title={isFavorite ? 'Remove from Wishlist' : 'Add to Wishlist'}
                aria-label={isFavorite ? 'Remove from Wishlist' : 'Add to Wishlist'}
              >
                <Heart className={`h-5 w-5 ${isFavorite ? 'fill-rose-500 text-rose-500' : ''}`} />
              </button>
            </div>

            {/* Feature Callouts */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100 text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <Truck className="h-4 w-4 text-blue-500" />
                <span>Fast express delivery</span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                <span>30-day money-back guarantee</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;

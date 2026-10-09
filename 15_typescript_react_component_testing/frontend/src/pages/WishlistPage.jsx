import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Heart, ShoppingCart, Trash2, ArrowLeft, ArrowRight, Package, Sparkles } from 'lucide-react';
import { useWishlist } from '../hooks/useWishlist';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

export const WishlistPage = () => {
  const { wishlist, removeFromWishlist, moveToCart } = useWishlist();
  const { isAuthenticated, isAdmin } = useAuth();
  const navigate = useNavigate();

  if (isAdmin) {
    return (
      <Card className="max-w-md mx-auto my-12 text-center p-8 border-amber-500/50">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-amber-500/10 text-amber-500 mb-4">
          <Heart className="h-7 w-7" />
        </div>
        <CardTitle className="text-xl font-bold mb-2 text-amber-500">Admin Mode</CardTitle>
        <p className="text-xs text-muted-foreground mb-6">
          Wishlists are designated for retail customers. Administrators manage store inventory and orders in the Admin Hub.
        </p>
        <Link to="/admin">
          <Button className="w-full bg-amber-500 hover:bg-amber-600 text-black font-bold">
            Open Admin Hub
          </Button>
        </Link>
      </Card>
    );
  }

  if (!wishlist || wishlist.length === 0) {
    return (
      <div className="card max-w-md mx-auto my-14 text-center p-8 space-y-4">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-rose-500/10 text-rose-500 mb-2">
          <Heart className="h-8 w-8" />
        </div>
        <h2 className="text-xl font-bold">Your Wishlist is Empty</h2>
        <p className="text-xs text-muted-foreground max-w-xs mx-auto">
          Explore our product catalog and click the heart icon on any item to save it for later.
        </p>
        <Link to="/" className="inline-block pt-2">
          <Button className="gap-2">
            Explore Product Catalog <ArrowRight size={16} />
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-border/60">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">My Wishlist</h1>
            <Badge variant="outline" className="border-rose-500/40 text-rose-500 font-bold gap-1 text-xs">
              <Heart className="h-3 w-3 fill-rose-500" /> {wishlist.length} {wishlist.length === 1 ? 'Item' : 'Items'}
            </Badge>
          </div>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Items saved for later. Move them to your cart whenever you are ready to order.
          </p>
        </div>

        <Link to="/" className="text-xs text-muted-foreground hover:text-foreground inline-flex items-center gap-1">
          <ArrowLeft size={14} /> Continue Shopping
        </Link>
      </div>

      {/* Wishlist Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {wishlist.map((item) => {
          const isOutOfStock = item.stock <= 0;

          return (
            <div
              key={item.id}
              className="card flex flex-col justify-between p-4 relative group"
              style={{ borderRadius: '12px' }}
            >
              <div>
                {/* Image */}
                <div
                  style={{
                    width: '100%',
                    height: '180px',
                    borderRadius: '8px',
                    overflow: 'hidden',
                    backgroundColor: 'var(--bg-elevated)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '0.85rem',
                    position: 'relative',
                  }}
                >
                  {item.image_url ? (
                    <img
                      src={item.image_url}
                      alt={item.name}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <Package size={40} className="text-muted-foreground" />
                  )}

                  {/* Remove heart button */}
                  <button
                    onClick={() => removeFromWishlist(item.id)}
                    className="absolute top-2 right-2 p-1.5 rounded-full bg-background/80 hover:bg-destructive hover:text-white transition-colors text-muted-foreground shadow-sm"
                    title="Remove from wishlist"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>

                {/* Info */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                    <span>{item.category?.name || 'Exclusive Tech'}</span>
                    <span className={isOutOfStock ? 'text-rose-500 font-semibold' : 'text-emerald-500 font-semibold'}>
                      {isOutOfStock ? 'Out of Stock' : 'In Stock'}
                    </span>
                  </div>

                  <Link
                    to={`/products/${item.id}`}
                    className="font-bold text-sm hover:text-primary transition-colors line-clamp-2"
                  >
                    {item.name}
                  </Link>

                  <div className="pt-1">
                    <span className="text-lg font-extrabold text-foreground">
                      ${Number(item.price).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Move to Cart Action */}
              <div className="pt-4 mt-3 border-t border-border/50">
                <Button
                  onClick={() => moveToCart(item)}
                  disabled={isOutOfStock}
                  className="w-full gap-2 font-bold bg-amber-500 hover:bg-amber-600 text-black text-xs"
                >
                  <ShoppingCart size={15} />
                  <span>{isOutOfStock ? 'Unavailable' : 'Move to Cart'}</span>
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WishlistPage;

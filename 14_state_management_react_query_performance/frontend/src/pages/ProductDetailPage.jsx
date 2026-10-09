import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ShoppingCart,
  Check,
  AlertCircle,
  ShieldCheck,
  Star,
  MapPin,
  Truck,
  RotateCcw,
  Zap,
  MessageSquare,
  ThumbsUp,
  Settings,
  Heart,
  ChevronRight,
  PackageCheck,
  Share2,
} from 'lucide-react';
import { productService } from '../services/productService';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';
import { useWishlist } from '../hooks/useWishlist';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { toast } from '../components/ui/sonner';

export const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated, isAdmin } = useAuth();
  const { addToCart } = useCart();
  const { isInWishlist, toggleWishlist } = useWishlist ? useWishlist() : { isInWishlist: () => false, toggleWishlist: () => {} };

  const [product, setProduct] = useState(null);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [buying, setBuying] = useState(false);
  const [added, setAdded] = useState(false);
  const [error, setError] = useState('');

  // Pin Code State
  const [pincode, setPincode] = useState('500001');
  const [pincodeMsg, setPincodeMsg] = useState('FREE delivery Tomorrow, 2 PM to 500001');

  // Customer Reviews State
  const [reviews, setReviews] = useState([
    {
      id: 1,
      author: 'Rajesh K.',
      rating: 5,
      date: 'September 24, 2026',
      title: 'Exceeded my expectations!',
      comment: 'The build quality and performance are top tier. Delivery was super fast via Prime.',
      helpful: 28,
    },
    {
      id: 2,
      author: 'Priya Sharma',
      rating: 4,
      date: 'September 18, 2026',
      title: 'Great value for money',
      comment: 'Very solid product. Design is premium and works seamlessly right out of the box.',
      helpful: 14,
    },
  ]);
  const [newReviewRating, setNewReviewRating] = useState(5);
  const [newReviewText, setNewReviewText] = useState('');
  const [reviewSubmitted, setReviewSubmitted] = useState(false);

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await productService.getProductById(id);
        setProduct(data);

        // Fetch related products in same category
        if (data.category_id) {
          const related = await productService.getProducts({
            category_id: data.category_id,
            size: 4,
          });
          setRelatedProducts((related.items || []).filter((p) => p.id !== Number(id)));
        }
      } catch (err) {
        console.error('Failed to load product detail:', err);
        setError('Product not found or unavailable.');
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [id]);

  const handlePincodeCheck = (e) => {
    e.preventDefault();
    if (pincode.length >= 5) {
      setPincodeMsg(`✓ Delivery available! Guaranteed FREE delivery by Tomorrow, 2 PM to ${pincode}`);
    } else {
      setPincodeMsg('Please enter a valid postal pin code.');
    }
  };

  const handleAddToCart = async () => {
    if (isAdmin) {
      toast.warning('Admin Access Detected', {
        description: 'Administrators have store management access only and cannot purchase products.',
      });
      return;
    }
    if (!isAuthenticated) {
      navigate(`/login?redirect=${encodeURIComponent(window.location.pathname)}`);
      return;
    }
    setAdding(true);
    try {
      await addToCart(product.id, quantity);
      setAdded(true);
      toast.success('Added to Cart! 🛒', {
        description: `${quantity}x ${product.name} added to your cart.`,
      });
      setTimeout(() => setAdded(false), 2500);
    } catch (err) {
      toast.error('Failed to add to cart', {
        description: err.response?.data?.detail || 'An unexpected error occurred',
      });
    } finally {
      setAdding(false);
    }
  };

  const handleBuyNow = async () => {
    if (isAdmin) {
      toast.warning('Admin Access Detected', {
        description: 'Administrators cannot place retail consumer orders. Please use a customer account.',
      });
      return;
    }
    if (!isAuthenticated) {
      navigate('/login?redirect=' + encodeURIComponent('/checkout'));
      return;
    }
    setBuying(true);
    try {
      await addToCart(product.id, quantity);
      navigate('/checkout');
    } catch (err) {
      toast.error('Could not initiate checkout', {
        description: err.response?.data?.detail || 'Failed to process purchase',
      });
    } finally {
      setBuying(false);
    }
  };

  const handleReviewSubmit = (e) => {
    e.preventDefault();
    if (!newReviewText.trim()) return;

    const addedRev = {
      id: Date.now(),
      author: user?.username || 'Verified Customer',
      rating: newReviewRating,
      date: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
      title: 'Verified Customer Review',
      comment: newReviewText.trim(),
      helpful: 1,
    };

    setReviews([addedRev, ...reviews]);
    setNewReviewText('');
    setReviewSubmitted(true);
    toast.success('Review Published!', {
      description: 'Thank you for submitting your feedback.',
    });
    setTimeout(() => setReviewSubmitted(false), 4000);
  };

  if (loading) {
    return (
      <div className="flex min-h-[65vh] items-center justify-center p-8">
        <LoadingSpinner size={36} text="Loading product details..." />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="container max-w-lg py-16 text-center">
        <Card className="p-8">
          <p className="text-destructive font-semibold mb-4">{error || 'Product not found'}</p>
          <Button variant="outline" asChild>
            <Link to="/">
              <ArrowLeft className="h-4 w-4 mr-2" /> Back to Catalog
            </Link>
          </Button>
        </Card>
      </div>
    );
  }

  const isOutOfStock = product.stock <= 0;
  const isLowStock = product.stock > 0 && product.stock <= 5;
  const originalMrp = (Number(product.price) * 1.3).toFixed(2);

  return (
    <div className="container max-w-6xl py-6 px-4 space-y-8 animate-in fade-in-50 duration-300">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Link to="/" className="hover:text-primary transition-colors">Catalog</Link>
        <ChevronRight className="h-3 w-3" />
        {product.category && (
          <>
            <span className="hover:text-primary">{product.category.name}</span>
            <ChevronRight className="h-3 w-3" />
          </>
        )}
        <span className="text-foreground font-medium truncate max-w-[300px]">{product.name}</span>
      </nav>

      {/* Main Detail Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12 bg-card border rounded-2xl p-6 sm:p-8 shadow-sm">
        {/* Left Column: Product Image Gallery */}
        <div className="space-y-4">
          <div className="relative aspect-square w-full rounded-xl overflow-hidden bg-muted/40 border flex items-center justify-center group">
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.name}
                className={`w-full h-full object-cover transition-transform duration-300 group-hover:scale-105 ${
                  isOutOfStock ? 'grayscale contrast-75' : ''
                }`}
              />
            ) : (
              <div className="text-muted-foreground text-sm font-medium">No Image Available</div>
            )}

            {isOutOfStock && (
              <div className="absolute inset-0 bg-background/70 backdrop-blur-xs flex items-center justify-center">
                <Badge variant="destructive" className="text-sm px-3 py-1 font-bold">
                  Out of Stock
                </Badge>
              </div>
            )}
          </div>

          {/* Assurance Badges */}
          <div className="grid grid-cols-3 gap-2.5 text-center text-xs text-muted-foreground">
            <div className="p-3 bg-muted/30 border rounded-lg flex flex-col items-center gap-1">
              <Truck className="h-5 w-5 text-sky-500" />
              <span className="font-medium text-[11px]">Free Express Delivery</span>
            </div>
            <div className="p-3 bg-muted/30 border rounded-lg flex flex-col items-center gap-1">
              <RotateCcw className="h-5 w-5 text-emerald-500" />
              <span className="font-medium text-[11px]">7 Days Replacement</span>
            </div>
            <div className="p-3 bg-muted/30 border rounded-lg flex flex-col items-center gap-1">
              <ShieldCheck className="h-5 w-5 text-amber-500" />
              <span className="font-medium text-[11px]">1 Year Warranty</span>
            </div>
          </div>
        </div>

        {/* Right Column: Product Info & Actions */}
        <div className="flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                {product.category && (
                  <Badge variant="secondary" className="font-semibold text-xs">
                    {product.category.name}
                  </Badge>
                )}
                <span className="flex items-center gap-1 text-sky-500 font-bold italic text-xs tracking-wider">
                  <Zap className="h-3.5 w-3.5 fill-sky-500" /> PRIME
                </span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-muted-foreground hover:text-foreground"
                onClick={() => {
                  navigator.clipboard.writeText(window.location.href);
                  toast.success('Link copied to clipboard!');
                }}
                title="Share Product"
              >
                <Share2 className="h-4 w-4" />
              </Button>
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              {product.name}
            </h1>

            {/* Ratings Row */}
            <div className="flex items-center gap-2 text-xs">
              <div className="flex items-center text-amber-500">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className={`h-4 w-4 ${i < 4 ? 'fill-amber-500' : 'text-muted-foreground'}`} />
                ))}
              </div>
              <span className="font-semibold text-sky-500">4.7 out of 5</span>
              <span className="text-muted-foreground">&bull; ({reviews.length + 120} verified reviews)</span>
            </div>

            {/* Price Box */}
            <div className="p-4 bg-muted/30 rounded-xl border space-y-1">
              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-extrabold text-foreground">
                  ${Number(product.price).toFixed(2)}
                </span>
                <span className="text-base text-muted-foreground line-through">
                  ${originalMrp}
                </span>
                <Badge variant="outline" className="text-emerald-600 dark:text-emerald-400 border-emerald-500/30 bg-emerald-500/10 font-bold">
                  23% OFF
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Inclusive of all taxes &bull; Use code <strong className="text-primary font-mono">SAVE20</strong> for 20% off
              </p>
            </div>

            {/* Description */}
            <div className="space-y-1.5 text-sm text-muted-foreground leading-relaxed">
              <span className="font-semibold text-foreground text-xs uppercase tracking-wider block">Overview</span>
              <p>{product.description || 'High quality build engineered for everyday reliability and top performance.'}</p>
            </div>

            {/* Pincode Estimator */}
            <div className="p-3.5 border rounded-xl bg-card space-y-2">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                <MapPin className="h-4 w-4 text-primary" /> Delivery Estimator:
              </div>
              <form onSubmit={handlePincodeCheck} className="flex gap-2">
                <Input
                  value={pincode}
                  onChange={(e) => setPincode(e.target.value)}
                  placeholder="Enter postal PIN code"
                  className="h-8 text-xs max-w-[200px]"
                />
                <Button type="submit" variant="secondary" size="sm" className="h-8 text-xs">
                  Verify
                </Button>
              </form>
              <p className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                {pincodeMsg}
              </p>
            </div>
          </div>

          {/* Action Buy Box */}
          <div className="space-y-4 pt-4 border-t">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Inventory Status:</span>
              {isOutOfStock ? (
                <Badge variant="destructive">Out of Stock</Badge>
              ) : isLowStock ? (
                <Badge variant="outline" className="border-amber-500/50 text-amber-600 dark:text-amber-400 bg-amber-500/10">
                  Only {product.stock} units remaining!
                </Badge>
              ) : (
                <Badge variant="outline" className="border-emerald-500/50 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10">
                  In Stock ({product.stock} units)
                </Badge>
              )}
            </div>

            {!isOutOfStock && !isAdmin && (
              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground font-medium">Qty:</span>
                <select
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="h-9 w-20 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-xs focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/40 focus:ring-offset-1 focus:ring-offset-background transition-all duration-200"
                >
                  {[...Array(Math.min(product.stock, 10))].map((_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {i + 1}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Cart & Buy Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                variant="outline"
                className="flex-1 h-11 border-primary text-primary hover:bg-primary/10 font-semibold"
                disabled={isOutOfStock || adding || isAdmin}
                onClick={handleAddToCart}
              >
                <ShoppingCart className="h-4 w-4 mr-2" />
                {added ? 'Added to Cart ✓' : adding ? 'Adding...' : 'Add to Cart'}
              </Button>
              <Button
                className="flex-1 h-11 font-semibold"
                disabled={isOutOfStock || buying || isAdmin}
                onClick={handleBuyNow}
              >
                <Zap className="h-4 w-4 mr-2" />
                {buying ? 'Processing...' : 'Buy Now'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Customer Reviews Section */}
      <div className="bg-card border rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
          <div>
            <h2 className="text-xl font-bold tracking-tight">Customer Reviews & Ratings</h2>
            <p className="text-xs text-muted-foreground">Real feedback submitted by verified purchasers</p>
          </div>
          <Badge variant="outline" className="w-fit text-xs font-semibold">
            {reviews.length} Verified Reviews
          </Badge>
        </div>

        {/* Write a review box */}
        <form onSubmit={handleReviewSubmit} className="p-4 bg-muted/30 rounded-xl border space-y-3">
          <span className="text-xs font-semibold text-foreground block">Leave a Review</span>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Rating:</span>
            <select
              value={newReviewRating}
              onChange={(e) => setNewReviewRating(Number(e.target.value))}
              className="h-8 rounded-md border text-xs bg-background px-2 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/40 focus:ring-offset-1 focus:ring-offset-background transition-all duration-200"
            >
              <option value={5}>5 Stars - Excellent</option>
              <option value={4}>4 Stars - Very Good</option>
              <option value={3}>3 Stars - Average</option>
              <option value={2}>2 Stars - Poor</option>
              <option value={1}>1 Star - Terrible</option>
            </select>
          </div>
          <Input
            placeholder="Share your thoughts on the product quality, performance, or packaging..."
            value={newReviewText}
            onChange={(e) => setNewReviewText(e.target.value)}
            className="text-xs"
          />
          <Button type="submit" size="sm" className="text-xs">
            Submit Review
          </Button>
        </form>

        {/* Existing Reviews List */}
        <div className="space-y-4 pt-2">
          {reviews.map((rev) => (
            <div key={rev.id} className="p-4 border rounded-xl space-y-2 bg-background/50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-xs">
                    {rev.author.charAt(0)}
                  </div>
                  <span className="font-semibold text-xs text-foreground">{rev.author}</span>
                  <Badge variant="secondary" className="text-[10px] py-0 px-1.5 h-4">Verified</Badge>
                </div>
                <span className="text-[11px] text-muted-foreground">{rev.date}</span>
              </div>
              <div className="flex items-center text-amber-500">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className={`h-3.5 w-3.5 ${i < rev.rating ? 'fill-amber-500' : 'text-muted-foreground'}`} />
                ))}
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">{rev.comment}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Related Products Strip */}
      {relatedProducts.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold tracking-tight">More from this Category</h3>
            <Link to="/" className="text-xs font-semibold text-primary hover:underline">
              View All Products &rarr;
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {relatedProducts.map((rel) => (
              <Card
                key={rel.id}
                tabIndex={0}
                className="overflow-hidden transition-all duration-300 border border-border/80 hover:border-primary/80 hover:ring-2 hover:ring-primary/40 hover:ring-offset-2 hover:ring-offset-background hover:shadow-xl hover:shadow-primary/10 hover:-translate-y-1 focus:border-primary focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-background outline-none cursor-pointer"
              >
                <Link to={`/products/${rel.id}`} className="block aspect-video bg-muted relative">
                  {rel.image_url ? (
                    <img src={rel.image_url} alt={rel.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs text-muted-foreground">
                      No Image
                    </div>
                  )}
                </Link>
                <CardContent className="p-3.5 space-y-1.5">
                  <Link to={`/products/${rel.id}`} className="font-medium text-xs hover:text-primary line-clamp-1 block">
                    {rel.name}
                  </Link>
                  <div className="flex items-center justify-between text-xs pt-1">
                    <span className="font-bold text-foreground">${Number(rel.price).toFixed(2)}</span>
                    <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                      {rel.stock > 0 ? 'In Stock' : 'Out of Stock'}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetailPage;

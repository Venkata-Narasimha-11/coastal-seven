import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Sparkles, Truck, ShieldCheck, Zap, Layers, Flame, ArrowRight, Heart, Gift } from 'lucide-react';
import { useProductsQuery, useCategoriesQuery } from '../hooks/useProducts';
import { useDebounce } from '../hooks/useDebounce';
import useAuthStore from '../stores/useAuthStore';
import useCartStore from '../stores/useCartStore';
import ProductGrid from '../components/product/ProductGrid';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ErrorMessage from '../components/common/ErrorMessage';
import { AIErrorBoundary } from '../components/ai/AIErrorBoundary';
import { aiService } from '../services/aiService';
import { Product } from '../types/api';

// Nykaa Fashion Story Highlights (All Drops + 8 Categories)
const STORY_HIGHLIGHTS = [
  { id: 'all', title: 'All Drops', icon: '✨', slug: null },
  { id: 'ethnic-couture', title: 'Couture', icon: '👑', slug: 'ethnic-couture' },
  { id: 'western-luxe', title: 'Western Luxe', icon: '👗', slug: 'western-luxe' },
  { id: 'luxury-handbags', title: 'Handbags', icon: '👜', slug: 'luxury-handbags' },
  { id: 'fine-jewellery', title: 'Fine Jewels', icon: '💎', slug: 'fine-jewellery' },
  { id: 'footwear', title: 'Footwear', icon: '👠', slug: 'footwear' },
  { id: 'beauty-fragrances', title: 'Fragrances', icon: '🌸', slug: 'beauty-fragrances' },
  { id: 'boys-kids-wear', title: 'Boys Kids', icon: '👦', slug: 'boys-kids-wear' },
  { id: 'girls-kids-wear', title: 'Girls Kids', icon: '👧', slug: 'girls-kids-wear' },
];

// AI Quick Vibe / Mood Search Chips
const AI_VIBE_CHIPS = [
  { label: '👑 Royal Wedding Reception', query: 'bridal lehenga wedding royal' },
  { label: '💃 Midnight Velvet Gala Night', query: 'evening gown cocktail velvet' },
  { label: '👦 Boys Royal Sherwani & Tuxedo', query: 'boys kids sherwani tuxedo suit' },
  { label: '👧 Girls Princess Tulle Lehenga', query: 'girls kids lehenga princess gown' },
  { label: '💎 Rose Gold Heritage Minimalist', query: 'rose gold diamond minimal jewellery' },
];

export const ProductsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [semanticMode, setSemanticMode] = useState(false);
  const [semanticResults, setSemanticResults] = useState<Product[] | null>(null);
  const [semanticMeta, setSemanticMeta] = useState<{
    cached: boolean;
    latency_ms: number;
    provider: string;
    total: number;
  } | null>(null);
  const [isSemanticLoading, setIsSemanticLoading] = useState(false);
  const [copiedCoupon, setCopiedCoupon] = useState(false);

  const debouncedSearch = useDebounce<string>(searchTerm, 350);
  const addItemToCart = useCartStore((state) => state.addItem);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  // TanStack Query for Categories
  const { data: categories = [] } = useCategoriesQuery();
  const selectedCategoryName = categories.find((c) => c.id === selectedCategory)?.name;

  // Standard Product Query
  const {
    data: productsData,
    isLoading: isStandardLoading,
    isError,
    error,
    refetch,
  } = useProductsQuery({
    size: 150,
    search: !semanticMode && debouncedSearch ? debouncedSearch : undefined,
    category_id: selectedCategory || undefined,
  });

  // Semantic Vector Search Effect
  useEffect(() => {
    let isCancelled = false;

    if (semanticMode && debouncedSearch.trim()) {
      setIsSemanticLoading(true);
      aiService
        .semanticSearch({
          q: debouncedSearch.trim(),
          category: selectedCategoryName,
          limit: 30,
        })
        .then((res) => {
          if (!isCancelled) {
            setSemanticResults(res.results as unknown as Product[]);
            setSemanticMeta({
              cached: res.cached,
              latency_ms: res.latency_ms,
              provider: res.provider,
              total: res.total_results,
            });
            setIsSemanticLoading(false);
          }
        })
        .catch(() => {
          if (!isCancelled) {
            setSemanticResults([]);
            setIsSemanticLoading(false);
          }
        });
    } else if (!semanticMode) {
      setSemanticResults(null);
      setSemanticMeta(null);
    }

    return () => {
      isCancelled = true;
    };
  }, [semanticMode, debouncedSearch, selectedCategoryName, selectedCategory]);

  const handleAddToCart = (product: Product) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    addItemToCart(product, 1);
  };

  const handleCopyCoupon = () => {
    navigator.clipboard.writeText('SAVE10');
    setCopiedCoupon(true);
    setTimeout(() => setCopiedCoupon(false), 2000);
  };

  const handleApplyVibe = (queryText: string) => {
    setSelectedCategory(null);
    setSearchTerm(queryText);
    setSemanticMode(true);
  };

  const handleStoryClick = (story: typeof STORY_HIGHLIGHTS[0]) => {
    setSearchTerm('');
    setSemanticMode(false);
    if (!story.slug) {
      setSelectedCategory(null);
    } else {
      const cat = categories.find((c) => c.slug === story.slug);
      if (cat) {
        setSelectedCategory(cat.id);
      } else {
        setSelectedCategory(null);
      }
    }
  };

  const displayedProducts =
    semanticMode && semanticResults !== null ? semanticResults : productsData?.items || [];
  const isLoading = semanticMode ? isSemanticLoading : isStandardLoading;

  return (
    <div className="space-y-8">
      {/* 1. Nykaa Fashion Signature: Story Circles Highlights */}
      <div className="overflow-x-auto pb-2 scrollbar-none">
        <div className="flex items-center gap-4 sm:gap-6 min-w-max px-1">
          {STORY_HIGHLIGHTS.map((story) => (
            <button
              key={story.id}
              onClick={() => handleStoryClick(story)}
              className="flex flex-col items-center gap-1.5 group cursor-pointer"
            >
              <div className="h-16 w-16 sm:h-20 sm:w-20 rounded-full p-[2px] bg-gradient-to-tr from-pink-600 via-rose-500 to-amber-400 group-hover:scale-105 transition-transform duration-300 shadow-sm">
                <div className="h-full w-full rounded-full bg-white dark:bg-slate-900 flex items-center justify-center text-2xl sm:text-3xl border border-white dark:border-slate-800">
                  {story.icon}
                </div>
              </div>
              <span className="text-[11px] sm:text-xs font-bold tracking-tight text-slate-800 dark:text-slate-200 group-hover:text-pink-600 transition-colors">
                {story.title}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* 2. SIVORA Luxe Editorial Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-rose-950 via-pink-900 to-slate-950 text-white shadow-2xl p-8 sm:p-12 border border-pink-500/20">
        <div className="absolute top-0 right-0 w-96 h-96 bg-pink-500/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur-md text-amber-300 text-xs font-bold uppercase tracking-widest border border-white/20">
            <Sparkles className="h-3.5 w-3.5 text-amber-300 animate-spin" />
            <span>S I V O R A • THE LUXE EDIT</span>
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-tight">
            Curated Elegance, <br />
            <span className="bg-gradient-to-r from-pink-300 via-rose-200 to-amber-200 bg-clip-text text-transparent">
              Powered by AI.
            </span>
          </h1>

          <p className="text-pink-100/90 text-sm sm:text-base leading-relaxed max-w-xl">
            Discover the new season catalogue with embedding-based Semantic Search, real-time stock verification, and exclusive lifestyle collections.
          </p>

          {/* Coupon Pill with 1-Click Copy */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={handleCopyCoupon}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/15 hover:bg-white/20 backdrop-blur-md border border-amber-300/40 text-amber-200 text-xs font-bold transition-all"
              title="Click to copy coupon code"
            >
              <Gift className="h-4 w-4 text-amber-300" />
              <span>Use Code: <strong>SAVE10</strong></span>
              <span className="bg-amber-400 text-slate-950 px-2 py-0.5 rounded text-[10px] font-black uppercase">
                {copiedCoupon ? 'COPIED! 🎉' : '10% OFF'}
              </span>
            </button>
          </div>

          {/* Trust Highlights */}
          <div className="flex flex-wrap items-center gap-5 pt-3 text-xs font-semibold text-pink-200/90">
            <div className="flex items-center gap-1.5">
              <Truck className="h-4 w-4 text-emerald-400" /> Free Express Delivery Across India
            </div>
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-amber-300" /> 100% Verified Authentic Luxury
            </div>
          </div>
        </div>
      </div>

      {/* 3. AI Vibe & Mood Search Chips */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold tracking-wider uppercase text-pink-600 dark:text-pink-400">
          <Sparkles className="h-3.5 w-3.5" />
          <span>AI Vibe Search (Instant Mood Match)</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {AI_VIBE_CHIPS.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleApplyVibe(chip.query)}
              className="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-pink-500 hover:text-pink-600 dark:hover:text-pink-400 text-slate-700 dark:text-slate-300 transition-all shadow-sm hover:shadow"
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* 4. Search Bar & AI Semantic Search Toggle Pill */}
      <div className="bg-white dark:bg-slate-900 p-4 sm:p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
        <div className="flex flex-col md:flex-row gap-3 items-center justify-between">
          {/* Search Input */}
          <div className="w-full md:w-96 relative">
            <Input
              placeholder={
                semanticMode
                  ? "Describe what you need (e.g. 'headphones for quiet studying')..."
                  : "Search SIVORA catalogue by brand or keyword..."
              }
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-muted-foreground" />}
              data-testid="search-input"
              aria-label="Search products"
              className="rounded-xl border-slate-200 dark:border-slate-800 focus:border-pink-500"
            />
          </div>

          {/* AI Semantic Search Toggle Pill */}
          <button
            type="button"
            onClick={() => setSemanticMode(!semanticMode)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all border ${
              semanticMode
                ? 'bg-gradient-to-r from-pink-600 to-rose-600 text-white border-transparent shadow-md shadow-pink-500/30'
                : 'bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700'
            }`}
          >
            <Sparkles className={`h-3.5 w-3.5 ${semanticMode ? 'text-amber-200 animate-spin' : ''}`} />
            <span>AI Semantic Vector Search:</span>
            <span className={`px-2 py-0.5 rounded-md text-[10px] font-black tracking-wider uppercase ${semanticMode ? 'bg-white/20 text-white' : 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white'}`}>
              {semanticMode ? 'ON (Vector Mode)' : 'OFF (Keyword)'}
            </span>
          </button>
        </div>

        {/* Semantic Search Status Notification Banner */}
        {semanticMode && debouncedSearch && semanticMeta && (
          <div className="flex flex-wrap items-center justify-between gap-2 p-3 rounded-xl bg-pink-50 dark:bg-pink-950/30 border border-pink-200 dark:border-pink-800/40 text-xs text-pink-900 dark:text-pink-300">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-pink-600" />
              <span>
                Retrieved <strong>{semanticMeta.total}</strong> products matching intent &ldquo;<em>{debouncedSearch}</em>&rdquo; via ChromaDB Cosine Embeddings
              </span>
            </div>
            <div className="flex items-center gap-2 text-[11px] font-mono">
              <span className="rounded bg-pink-200/50 dark:bg-pink-900/50 px-2 py-0.5 font-bold">
                {semanticMeta.provider}
              </span>
              {semanticMeta.cached ? (
                <span className="rounded bg-emerald-500 text-white px-2 py-0.5 flex items-center gap-1 font-bold shadow-sm">
                  <Zap className="h-3 w-3" /> Redis Cache HIT ({semanticMeta.latency_ms}ms)
                </span>
              ) : (
                <span className="rounded bg-slate-200 dark:bg-slate-800 px-2 py-0.5">
                  Latency: {semanticMeta.latency_ms}ms
                </span>
              )}
            </div>
          </div>
        )}

        {/* Category Filter Pills (Nykaa Fashion style) */}
        <div className="flex flex-wrap gap-2 items-center pt-2 border-t border-slate-100 dark:border-slate-800">
          <Button
            size="sm"
            variant={selectedCategory === null ? 'primary' : 'outline'}
            onClick={() => {
              setSelectedCategory(null);
              setSearchTerm('');
            }}
            data-testid="category-filter-all"
            className={selectedCategory === null ? 'bg-gradient-to-r from-pink-600 to-rose-600 text-white font-bold' : ''}
          >
            All Collections
          </Button>

          {categories.map((category) => (
            <Button
              key={category.id}
              size="sm"
              variant={selectedCategory === category.id ? 'primary' : 'outline'}
              onClick={() => {
                setSelectedCategory(category.id);
                setSearchTerm('');
              }}
              data-testid={`category-filter-${category.id}`}
              className={selectedCategory === category.id ? 'bg-gradient-to-r from-pink-600 to-rose-600 text-white font-bold' : ''}
            >
              {category.name}
            </Button>
          ))}
        </div>
      </div>

      {/* 5. Product Grid Area */}
      <AIErrorBoundary
        fallbackTitle="Error Loading Products or Vector Search"
        fallbackMessage="We encountered an issue retrieving products. Click retry to refresh."
        onReset={() => refetch()}
      >
        {isError ? (
          <ErrorMessage
            title="Failed to load products"
            message={error?.message || 'Could not connect to product service.'}
            onRetry={() => refetch()}
            data-testid="products-error-state"
          />
        ) : (
          <ProductGrid
            products={displayedProducts}
            isLoading={isLoading}
            onAddToCart={handleAddToCart}
            emptyMessage={
              searchTerm
                ? semanticMode
                  ? `No products matching your contextual intent "${searchTerm}". Try another description.`
                  : `No products found matching "${searchTerm}". Try a different keyword.`
                : 'No products available in this collection.'
            }
          />
        )}
      </AIErrorBoundary>
    </div>
  );
};

export default ProductsPage;

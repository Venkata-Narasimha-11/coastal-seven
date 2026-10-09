import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  Search,
  Filter,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Zap,
  Tag,
  Copy,
  ArrowUpDown,
  SlidersHorizontal,
  DollarSign,
  X,
  LayoutGrid,
  List as ListIcon,
  Check,
  ShoppingBag,
  Package,
  History,
  Clock,
  Trash2,
  Cpu,
  Infinity as InfinityIcon,
  Layers,
  Sparkles,
} from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { useProducts, useCategories } from '../hooks/useProductsQuery';
import { useInfiniteProducts } from '../hooks/useInfiniteProducts';
import { useIntersectionObserver } from '../hooks/useIntersectionObserver';
import { useDebounce } from '../hooks/useDebounce';
import ProductCard from '../components/product/ProductCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Card, CardContent } from '../components/ui/card';
import { toast } from '../components/ui/sonner';

const PROMO_BANNERS = [
  {
    id: 1,
    title: 'Guntur Tech Mega Festival 2026',
    subtitle: 'Save up to 60% on Studio Headphones, Curved Displays & Mechanical Keyboards',
    badge: 'GUNTUR FESTIVAL SALE',
    coupon: 'SAVE20',
    color: 'from-blue-900/90 via-slate-900 to-indigo-950',
    accent: '#38bdf8',
  },
  {
    id: 2,
    title: '⚡ Guntur Super Saver Week',
    subtitle: 'Free Express Delivery Across AP + Flat $50 OFF with voucher GUNTUR50',
    badge: 'GRAND LAUNCH SPECIAL',
    coupon: 'GUNTUR50',
    color: 'from-purple-950 via-slate-900 to-pink-950',
    accent: '#f472b6',
  },
  {
    id: 3,
    title: 'High-Performance Workstation Gear',
    subtitle: 'Precision mice, multi-port fast chargers & ergonomic desktop peripherals',
    badge: 'PRO SERIES',
    coupon: 'FESTIVE10',
    color: 'from-emerald-950 via-slate-900 to-teal-950',
    accent: '#34d399',
  },
];

export const ProductsPage = () => {
  const queryClient = useQueryClient();

  // Mode: 'infinite' (useInfiniteQuery + IntersectionObserver) vs 'paged' (traditional pagination)
  const [browseMode, setBrowseMode] = useState('infinite'); // 'infinite' | 'paged'
  const [showRenderCounters, setShowRenderCounters] = useState(false);

  // Filter states
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedSearch = useDebounce(searchQuery, 400); // Topic 7: Debounced search
  const [inStockOnly, setInStockOnly] = useState(false);
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('newest');
  const [page, setPage] = useState(1);
  const [size] = useState(8);
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [appliedMinPrice, setAppliedMinPrice] = useState('');
  const [appliedMaxPrice, setAppliedMaxPrice] = useState('');
  const [activeBanner, setActiveBanner] = useState(0);

  // Search History
  const [searchHistory, setSearchHistory] = useState(() => {
    try {
      const saved = localStorage.getItem('guntur_store_recent_searches');
      return saved ? JSON.parse(saved) : ['Headphones', 'Apple Watch', 'Mechanical Keyboard'];
    } catch {
      return ['Headphones', 'Apple Watch', 'Mechanical Keyboard'];
    }
  });
  const [showHistory, setShowHistory] = useState(false);
  const searchContainerRef = useRef(null);

  // Categories via TanStack Query (cached for 10 minutes)
  const { data: categories = [] } = useCategories();

  // Filter params object for query keys
  const queryFilters = useMemo(
    () => ({
      category_id: selectedCategory,
      search: debouncedSearch,
      sort_by: sortBy,
      min_price: appliedMinPrice !== '' ? Number(appliedMinPrice) : null,
      max_price: appliedMaxPrice !== '' ? Number(appliedMaxPrice) : null,
    }),
    [selectedCategory, debouncedSearch, sortBy, appliedMinPrice, appliedMaxPrice]
  );

  // 1. Paged Query (Used when in 'paged' mode)
  const pagedQuery = useProducts({
    ...queryFilters,
    page,
    size,
  });

  // 2. Infinite Query (Used when in 'infinite' mode)
  const infiniteQuery = useInfiniteProducts(queryFilters, 8);

  // Handle infinite scroll bottom intersection
  const handleIntersect = useCallback(() => {
    if (
      browseMode === 'infinite' &&
      infiniteQuery.hasNextPage &&
      !infiniteQuery.isFetchingNextPage
    ) {
      infiniteQuery.fetchNextPage();
    }
  }, [browseMode, infiniteQuery]);

  // Sentinel ref for infinite scrolling
  const sentinelRef = useIntersectionObserver(handleIntersect, {
    enabled: browseMode === 'infinite' && infiniteQuery.hasNextPage,
    rootMargin: '200px',
  });

  // Flatten infinite pages items or take paged items
  const rawProducts = useMemo(() => {
    if (browseMode === 'infinite') {
      if (!infiniteQuery.data?.pages) return [];
      return infiniteQuery.data.pages.flatMap((pg) => pg.items || []);
    }
    return pagedQuery.data?.items || [];
  }, [browseMode, infiniteQuery.data, pagedQuery.data]);

  // Apply inStockOnly filter client-side if selected
  const displayedProducts = useMemo(() => {
    if (!inStockOnly) return rawProducts;
    return rawProducts.filter((p) => p.stock > 0);
  }, [rawProducts, inStockOnly]);

  const totalCount =
    browseMode === 'infinite'
      ? infiniteQuery.data?.pages?.[0]?.total || displayedProducts.length
      : pagedQuery.data?.total || 0;

  const totalPages =
    browseMode === 'infinite'
      ? infiniteQuery.data?.pages?.[0]?.pages || 1
      : pagedQuery.data?.pages || 1;

  const isLoading = browseMode === 'infinite' ? infiniteQuery.isLoading : pagedQuery.isLoading;
  const isFetching = browseMode === 'infinite' ? infiniteQuery.isFetching : pagedQuery.isFetching;

  // Auto-rotate hero promo banner
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveBanner((prev) => (prev + 1) % PROMO_BANNERS.length);
    }, 6000);
    return () => clearInterval(timer);
  }, []);

  // Close search history dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(e.target)) {
        setShowHistory(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const addToSearchHistory = (term) => {
    if (!term || !term.trim()) return;
    const cleaned = term.trim();
    setSearchHistory((prev) => {
      const filtered = prev.filter((item) => item.toLowerCase() !== cleaned.toLowerCase());
      const updated = [cleaned, ...filtered].slice(0, 8);
      try {
        localStorage.setItem('guntur_store_recent_searches', JSON.stringify(updated));
      } catch (err) {
        console.error('Failed to save search history:', err);
      }
      return updated;
    });
  };

  const removeFromSearchHistory = (termToRemove, e) => {
    if (e) e.stopPropagation();
    setSearchHistory((prev) => {
      const updated = prev.filter((item) => item !== termToRemove);
      try {
        localStorage.setItem('guntur_store_recent_searches', JSON.stringify(updated));
      } catch (err) {
        console.error('Failed to update search history:', err);
      }
      return updated;
    });
  };

  const clearAllSearchHistory = (e) => {
    if (e) e.stopPropagation();
    setSearchHistory([]);
    try {
      localStorage.removeItem('guntur_store_recent_searches');
      toast.info('Search history cleared');
    } catch (err) {
      console.error('Failed to clear search history:', err);
    }
  };

  const handleSelectHistoryItem = (term) => {
    setSearchQuery(term);
    addToSearchHistory(term);
    setShowHistory(false);
    setPage(1);
  };

  const handleSearchSubmit = (e) => {
    if (e) e.preventDefault();
    if (searchQuery.trim()) {
      addToSearchHistory(searchQuery.trim());
    }
    setShowHistory(false);
    setPage(1);
  };

  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId === selectedCategory ? null : categoryId);
    setPage(1);
  };

  const handleApplyPriceFilter = (e) => {
    if (e) e.preventDefault();
    setAppliedMinPrice(minPrice);
    setAppliedMaxPrice(maxPrice);
    setPage(1);
  };

  const handleClearPriceFilter = () => {
    setMinPrice('');
    setMaxPrice('');
    setAppliedMinPrice('');
    setAppliedMaxPrice('');
    setPage(1);
  };

  const handlePricePreset = (min, max) => {
    setMinPrice(min !== null ? String(min) : '');
    setMaxPrice(max !== null ? String(max) : '');
    setAppliedMinPrice(min !== null ? String(min) : '');
    setAppliedMaxPrice(max !== null ? String(max) : '');
    setPage(1);
  };

  const handleClearAllFilters = () => {
    setSelectedCategory(null);
    setSearchQuery('');
    setSortBy('newest');
    setMinPrice('');
    setMaxPrice('');
    setAppliedMinPrice('');
    setAppliedMaxPrice('');
    setInStockOnly(false);
    setPage(1);
  };

  const handleManualCacheRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['products'] });
    toast.success('Query Cache Refreshed', {
      description: 'TanStack Query revalidated server catalog state in background.',
    });
  };

  const hasActiveFilters = Boolean(
    selectedCategory ||
      searchQuery ||
      appliedMinPrice ||
      appliedMaxPrice ||
      inStockOnly ||
      sortBy !== 'newest'
  );

  return (
    <div className="space-y-6 pb-12">
      {/* 1. HERO PROMOTIONAL BANNER CAROUSEL */}
      <div className="relative overflow-hidden rounded-2xl border border-border shadow-md">
        <div
          className={`bg-gradient-to-r ${PROMO_BANNERS[activeBanner].color} p-6 sm:p-8 text-white transition-all duration-700`}
        >
          <div className="max-w-2xl space-y-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/10 backdrop-blur-md border border-white/20 text-white">
              <Zap className="h-3 w-3 fill-amber-400 text-amber-400" />
              {PROMO_BANNERS[activeBanner].badge}
            </span>
            <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
              {PROMO_BANNERS[activeBanner].title}
            </h2>
            <p className="text-white/80 text-sm sm:text-base leading-relaxed">
              {PROMO_BANNERS[activeBanner].subtitle}
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <Button
                size="sm"
                className="bg-white text-slate-950 hover:bg-white/90 font-bold"
                onClick={() => {
                  navigator.clipboard.writeText(PROMO_BANNERS[activeBanner].coupon);
                  toast.success(`Coupon ${PROMO_BANNERS[activeBanner].coupon} Copied!`);
                }}
              >
                <Copy className="h-3.5 w-3.5 mr-1.5" />
                Code: {PROMO_BANNERS[activeBanner].coupon}
              </Button>
              <span className="text-xs text-white/70">
                Auto-applies at checkout with 1-click
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. DAY 14 PERFORMANCE & CACHING CONTROL BAR */}
      <div className="p-3.5 rounded-xl border border-emerald-500/20 bg-emerald-950/10 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <Badge className="bg-emerald-600 text-white font-mono flex items-center gap-1">
            <Sparkles className="w-3 h-3" /> TanStack Query v5 Active
          </Badge>
          <span className="text-muted-foreground hidden sm:inline">
            Cached for 5 mins (Stale-While-Revalidate)
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Mode switch: Infinite scroll vs Pagination */}
          <div className="inline-flex rounded-lg border border-border bg-card p-0.5">
            <button
              onClick={() => setBrowseMode('infinite')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-colors ${
                browseMode === 'infinite'
                  ? 'bg-primary text-primary-foreground font-semibold'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <InfinityIcon className="w-3.5 h-3.5" /> Infinite Scroll
            </button>
            <button
              onClick={() => setBrowseMode('paged')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-colors ${
                browseMode === 'paged'
                  ? 'bg-primary text-primary-foreground font-semibold'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Layers className="w-3.5 h-3.5" /> Paged
            </button>
          </div>

          {/* Render Stats Toggle */}
          <Button
            size="sm"
            variant={showRenderCounters ? 'default' : 'outline'}
            className="h-7 text-xs gap-1"
            onClick={() => setShowRenderCounters(!showRenderCounters)}
          >
            <Cpu className="w-3.5 h-3.5" />
            {showRenderCounters ? 'Hide Memo Badges' : 'Show Memo Badges'}
          </Button>

          {/* Invalidate Cache Button */}
          <Button
            size="sm"
            variant="ghost"
            className="h-7 text-xs text-muted-foreground hover:text-foreground gap-1"
            onClick={handleManualCacheRefresh}
            title="Invalidate Query Cache"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* 3. SEARCH & CATEGORY CHIPS */}
      <div className="space-y-4">
        {/* Search Bar with Debounce & History */}
        <div ref={searchContainerRef} className="relative max-w-xl">
          <form onSubmit={handleSearchSubmit} className="relative flex items-center">
            <Search className="absolute left-3.5 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              type="text"
              placeholder="Search products (Auto-debounced in 400ms)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setShowHistory(true)}
              className="pl-10 pr-10 h-11 text-sm bg-card border-border/80 rounded-xl focus-visible:ring-primary"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-3 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </form>

          {/* Recent Searches Dropdown */}
          {showHistory && searchHistory.length > 0 && (
            <div className="absolute top-full left-0 right-0 z-30 mt-1.5 rounded-xl border border-border bg-card p-2 shadow-xl backdrop-blur-md">
              <div className="flex items-center justify-between px-2 py-1 text-xs text-muted-foreground border-b border-border/50 pb-1.5 mb-1">
                <span className="flex items-center gap-1 font-semibold">
                  <History className="h-3 w-3" /> Recent Searches
                </span>
                <button
                  type="button"
                  onClick={clearAllSearchHistory}
                  className="text-[11px] text-muted-foreground hover:text-destructive flex items-center gap-1"
                >
                  <Trash2 className="h-3 w-3" /> Clear All
                </button>
              </div>
              <div className="space-y-0.5">
                {searchHistory.map((item, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleSelectHistoryItem(item)}
                    className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs hover:bg-muted cursor-pointer group"
                  >
                    <span className="flex items-center gap-2 text-foreground group-hover:text-primary">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      {item}
                    </span>
                    <button
                      type="button"
                      onClick={(e) => removeFromSearchHistory(item, e)}
                      className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Horizontal Category Pill Bar */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          <Button
            size="sm"
            variant={selectedCategory === null ? 'default' : 'outline'}
            onClick={() => handleCategorySelect(null)}
            className="rounded-full text-xs shrink-0 font-medium h-8"
          >
            All Items
          </Button>
          {categories.map((cat) => (
            <Button
              key={cat.id}
              size="sm"
              variant={selectedCategory === cat.id ? 'default' : 'outline'}
              onClick={() => handleCategorySelect(cat.id)}
              className="rounded-full text-xs shrink-0 font-medium h-8"
            >
              {cat.name}
            </Button>
          ))}
        </div>
      </div>

      {/* 4. TOOLBAR: SORT, VIEW MODE, IN-STOCK TOGGLE */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-border/60">
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">
            Showing <strong className="text-foreground">{displayedProducts.length}</strong> of{' '}
            <strong className="text-foreground">{totalCount}</strong> products
          </span>
          {isFetching && (
            <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
              <RefreshCw className="w-3 h-3 animate-spin" /> Syncing...
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          {/* In stock toggle */}
          <label className="flex items-center gap-1.5 text-xs text-muted-foreground cursor-pointer select-none">
            <input
              type="checkbox"
              checked={inStockOnly}
              onChange={(e) => setInStockOnly(e.target.checked)}
              className="rounded border-border text-primary focus:ring-primary w-3.5 h-3.5"
            />
            In Stock Only
          </label>

          {/* Sort Dropdown */}
          <div className="flex items-center gap-1.5">
            <ArrowUpDown className="w-3.5 h-3.5 text-muted-foreground" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="h-8 rounded-lg border border-border bg-card px-2 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="newest">Newest Arrivals</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="name_asc">Name: A to Z</option>
            </select>
          </div>

          {/* Grid / List switch */}
          <div className="inline-flex rounded-lg border border-border bg-card p-0.5">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-md ${
                viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'
              }`}
              title="Grid View"
            >
              <LayoutGrid className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded-md ${
                viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'
              }`}
              title="List View"
            >
              <ListIcon className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* 5. PRODUCT CATALOG DISPLAY */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="h-80 rounded-2xl border border-border/60 bg-card p-4 animate-pulse space-y-3"
            >
              <div className="aspect-4/3 w-full rounded-xl bg-muted/60" />
              <div className="h-4 w-3/4 rounded bg-muted/60" />
              <div className="h-4 w-1/2 rounded bg-muted/60" />
              <div className="h-8 w-full rounded bg-muted/60 pt-4" />
            </div>
          ))}
        </div>
      ) : displayedProducts.length === 0 ? (
        <div className="p-12 text-center border rounded-2xl border-dashed border-border space-y-3">
          <Package className="w-12 h-12 mx-auto text-muted-foreground" />
          <h3 className="font-semibold text-lg">No products found</h3>
          <p className="text-xs text-muted-foreground max-w-sm mx-auto">
            Try adjusting your search query, clearing filters, or resetting category selection.
          </p>
          {hasActiveFilters && (
            <Button size="sm" variant="outline" onClick={handleClearAllFilters}>
              Clear All Filters
            </Button>
          )}
        </div>
      ) : (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6'
              : 'space-y-4'
          }
        >
          {displayedProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              showRenderStats={showRenderCounters}
            />
          ))}
        </div>
      )}

      {/* 6. INFINITE SCROLL SENTINEL & LOADING SPINNER */}
      {browseMode === 'infinite' && (
        <div ref={sentinelRef} className="py-6 text-center">
          {infiniteQuery.isFetchingNextPage ? (
            <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
              <RefreshCw className="w-4 h-4 animate-spin text-primary" /> Loading more products...
            </div>
          ) : infiniteQuery.hasNextPage ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => infiniteQuery.fetchNextPage()}
              className="text-xs"
            >
              Load More Products
            </Button>
          ) : (
            displayedProducts.length > 0 && (
              <p className="text-xs text-muted-foreground">
                🎉 You've reached the end of the catalog ({displayedProducts.length} items loaded).
              </p>
            )
          )}
        </div>
      )}

      {/* 7. TRADITIONAL PAGINATION BAR (When in 'paged' mode) */}
      {browseMode === 'paged' && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-6">
          <Button
            size="sm"
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            <ChevronLeft className="w-4 h-4 mr-1" /> Previous
          </Button>
          <span className="text-xs font-medium px-3 text-muted-foreground">
            Page <strong className="text-foreground">{page}</strong> of{' '}
            <strong className="text-foreground">{totalPages}</strong>
          </span>
          <Button
            size="sm"
            variant="outline"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            Next <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default ProductsPage;

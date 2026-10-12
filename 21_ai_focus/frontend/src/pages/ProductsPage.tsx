import React, { useState, useEffect } from 'react';
import { Search, Sparkles, Truck, ShieldCheck, Zap, Layers } from 'lucide-react';
import { useProductsQuery, useCategoriesQuery } from '../hooks/useProducts';
import { useDebounce } from '../hooks/useDebounce';
import useCartStore from '../stores/useCartStore';
import ProductGrid from '../components/product/ProductGrid';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ErrorMessage from '../components/common/ErrorMessage';
import { AIErrorBoundary } from '../components/ai/AIErrorBoundary';
import { aiService } from '../services/aiService';
import { Product } from '../types/api';

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

  const debouncedSearch = useDebounce<string>(searchTerm, 350);
  const addItemToCart = useCartStore((state) => state.addItem);

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
    size: 65,
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
            // Map semantic results to Product schema
            const mapped: Product[] = res.results.map((r) => ({
              id: r.id,
              name: r.name,
              slug: r.name.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
              description: r.description,
              price: r.price,
              stock: r.stock,
              category_id: selectedCategory || 1,
              category: { id: selectedCategory || 1, name: r.category, slug: r.category.toLowerCase(), created_at: new Date().toISOString() },
              image_url: r.image_url,
              thumbnail_url: r.image_url,
              is_active: true,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }));
            setSemanticResults(mapped);
            setSemanticMeta({
              cached: res.cached,
              latency_ms: res.latency_ms,
              provider: res.provider,
              total: res.total_results,
            });
            setIsSemanticLoading(false);
          }
        })
        .catch((err) => {
          console.error('Semantic search failed, falling back to standard search:', err);
          if (!isCancelled) {
            setIsSemanticLoading(false);
            setSemanticResults(null);
          }
        });
    } else {
      setSemanticResults(null);
      setSemanticMeta(null);
    }

    return () => {
      isCancelled = true;
    };
  }, [semanticMode, debouncedSearch, selectedCategoryName, selectedCategory]);

  const handleAddToCart = (product: Product) => {
    addItemToCart(product, 1);
  };

  const displayedProducts =
    semanticMode && semanticResults !== null ? semanticResults : productsData?.items || [];
  const isLoading = semanticMode ? isSemanticLoading : isStandardLoading;

  return (
    <div className="space-y-8">
      {/* Real E-Commerce Hero / Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-blue-700 via-indigo-700 to-sky-700 rounded-3xl p-8 sm:p-10 text-white shadow-xl">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/15 backdrop-blur-md text-sky-200 text-xs font-semibold uppercase tracking-wider border border-white/20">
            <Sparkles className="h-3.5 w-3.5 text-amber-300" />
            <span>Welcome to Gunturu Store • AI Powered</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
            Gunturu E-Commerce
          </h1>
          <p className="text-blue-100 text-sm sm:text-base leading-relaxed max-w-xl">
            Explore intelligent shopping with embedding-based Semantic Search, RAG recommendations, and instant delivery. Use coupon{' '}
            <span className="font-bold text-amber-300 bg-amber-400/20 px-2 py-0.5 rounded">SAVE10</span>{' '}
            for 10% instant discount at checkout!
          </p>
          <div className="flex flex-wrap items-center gap-4 pt-2 text-xs font-medium text-sky-200">
            <div className="flex items-center gap-1.5">
              <Truck className="h-4 w-4 text-emerald-400" /> Free Shipping above ₹100
            </div>
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-sky-300" /> 100% Genuine Verified Products
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar with Semantic Search Toggle */}
      <div className="bg-card p-4 rounded-2xl border border-border shadow-sm space-y-3">
        <div className="flex flex-col md:flex-row gap-3 items-center justify-between">
          {/* Search Input */}
          <div className="w-full md:w-96 relative">
            <Input
              placeholder={
                semanticMode
                  ? "Describe what you want (e.g. 'headphones for noisy flights')..."
                  : "Search products by keyword..."
              }
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-muted-foreground" />}
              data-testid="search-input"
              aria-label="Search products"
            />
          </div>

          {/* AI Semantic Search Toggle Pill */}
          <button
            type="button"
            onClick={() => setSemanticMode(!semanticMode)}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all border ${
              semanticMode
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-transparent shadow-md shadow-indigo-500/20'
                : 'bg-muted/60 hover:bg-muted text-muted-foreground border-border'
            }`}
          >
            <Sparkles className={`h-3.5 w-3.5 ${semanticMode ? 'text-amber-300 animate-spin' : ''}`} />
            <span>AI Semantic Search:</span>
            <span className={`px-1.5 py-0.5 rounded-md text-[10px] font-bold ${semanticMode ? 'bg-white/20 text-white' : 'bg-background text-foreground'}`}>
              {semanticMode ? 'ENABLED (Vector Mode)' : 'OFF (Exact Keyword)'}
            </span>
          </button>
        </div>

        {/* Semantic Search Status Banner */}
        {semanticMode && debouncedSearch && semanticMeta && (
          <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-700 dark:text-indigo-300">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-indigo-500" />
              <span>
                Found <strong>{semanticMeta.total}</strong> products matching intent &ldquo;<em>{debouncedSearch}</em>&rdquo; via vector similarity
              </span>
            </div>
            <div className="flex items-center gap-2 text-[11px] font-mono">
              <span className="rounded bg-indigo-500/20 px-2 py-0.5">
                Provider: {semanticMeta.provider}
              </span>
              {semanticMeta.cached ? (
                <span className="rounded bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 px-2 py-0.5 flex items-center gap-1 font-semibold">
                  <Zap className="h-3 w-3" /> Redis Cache HIT ({semanticMeta.latency_ms}ms)
                </span>
              ) : (
                <span className="rounded bg-muted px-2 py-0.5">
                  Latency: {semanticMeta.latency_ms}ms
                </span>
              )}
            </div>
          </div>
        )}

        {/* Category Filter Pills */}
        <div className="flex flex-wrap gap-2 items-center pt-1 border-t border-border">
          <Button
            size="sm"
            variant={selectedCategory === null ? 'primary' : 'outline'}
            onClick={() => setSelectedCategory(null)}
            data-testid="category-filter-all"
          >
            All Products
          </Button>

          {categories.map((category) => (
            <Button
              key={category.id}
              size="sm"
              variant={selectedCategory === category.id ? 'primary' : 'outline'}
              onClick={() => setSelectedCategory(category.id)}
              data-testid={`category-filter-${category.id}`}
            >
              {category.name}
            </Button>
          ))}
        </div>
      </div>

      {/* Content Area wrapped in AIErrorBoundary */}
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
                  ? `No products matching your contextual description "${searchTerm}". Try adjusting your query.`
                  : `No products found matching "${searchTerm}". Try a different keyword.`
                : 'No products available in this category.'
            }
          />
        )}
      </AIErrorBoundary>
    </div>
  );
};

export default ProductsPage;

import React, { useState } from 'react';
import { Search, Sparkles, Truck, ShieldCheck } from 'lucide-react';
import { useProductsQuery, useCategoriesQuery } from '../hooks/useProducts';
import { useDebounce } from '../hooks/useDebounce';
import useCartStore from '../stores/useCartStore';
import ProductGrid from '../components/product/ProductGrid';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import ErrorMessage from '../components/common/ErrorMessage';
import { Product } from '../types/api';

export const ProductsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const debouncedSearch = useDebounce<string>(searchTerm, 350);

  const addItemToCart = useCartStore((state) => state.addItem);

  // TanStack Query for Products
  const {
    data: productsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useProductsQuery({
    search: debouncedSearch || undefined,
    category_id: selectedCategory || undefined,
  });

  // TanStack Query for Categories
  const { data: categories = [] } = useCategoriesQuery();

  const handleAddToCart = (product: Product) => {
    addItemToCart(product, 1);
  };

  return (
    <div className="space-y-8">
      {/* Real E-Commerce Hero / Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-blue-700 via-indigo-700 to-sky-700 rounded-3xl p-8 sm:p-10 text-white shadow-xl">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/15 backdrop-blur-md text-sky-200 text-xs font-semibold uppercase tracking-wider border border-white/20">
            <Sparkles className="h-3.5 w-3.5 text-amber-300" />
            <span>Welcome to Gunturu Store</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
            Gunturu E-Commerce
          </h1>
          <p className="text-blue-100 text-sm sm:text-base leading-relaxed max-w-xl">
            Premium Electronics & Everyday Essentials delivered directly to your doorstep. Use coupon{' '}
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

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="w-full md:w-96">
          <Input
            placeholder="Search products by title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            leftIcon={<Search className="h-4 w-4" />}
            data-testid="search-input"
            aria-label="Search products"
          />
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap gap-2 items-center w-full md:w-auto">
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

      {/* Content Area */}
      {isError ? (
        <ErrorMessage
          title="Failed to load products"
          message={error?.message || 'Could not connect to product service.'}
          onRetry={() => refetch()}
          data-testid="products-error-state"
        />
      ) : (
        <ProductGrid
          products={productsData?.items || []}
          isLoading={isLoading}
          onAddToCart={handleAddToCart}
          emptyMessage={
            searchTerm
              ? `No products found matching "${searchTerm}". Try a different search.`
              : 'No products available in this category.'
          }
        />
      )}
    </div>
  );
};

export default ProductsPage;

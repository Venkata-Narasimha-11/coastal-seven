import React, { useState } from 'react';
import { Search } from 'lucide-react';
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
      {/* Hero / Header */}
      <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-800 rounded-2xl p-8 text-white shadow-md">
        <div className="max-w-2xl">
          <span className="inline-block px-3 py-1 rounded-full bg-blue-500/30 text-blue-100 text-xs font-semibold uppercase tracking-wider mb-3">
            Day 15 Project Showcase
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">
            Type-Safe React E-Commerce
          </h1>
          <p className="mt-2 text-blue-100 text-sm sm:text-base leading-relaxed">
            Engineered with strict TypeScript contracts, React Testing Library, Vitest,
            MSW API mocking, and Playwright end-to-end testing.
          </p>
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

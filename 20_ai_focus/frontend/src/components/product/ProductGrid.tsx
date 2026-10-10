import React from 'react';
import { Product } from '../../types/api';
import ProductCard from './ProductCard';
import Skeleton from '../ui/Skeleton';

interface ProductGridProps {
  products: Product[];
  isLoading?: boolean;
  onAddToCart?: (product: Product) => void;
  emptyMessage?: string;
}

export const ProductGrid: React.FC<ProductGridProps> = ({
  products,
  isLoading = false,
  onAddToCart,
  emptyMessage = 'No products found.',
}) => {
  if (isLoading) {
    return (
      <div
        data-testid="product-grid-loading"
        className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"
      >
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-xl border border-slate-200 overflow-hidden p-4 space-y-4"
          >
            <Skeleton className="aspect-square w-full rounded-lg" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
            <div className="flex justify-between items-center pt-2">
              <Skeleton className="h-6 w-16" />
              <Skeleton className="h-8 w-24 rounded-lg" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div
        data-testid="product-grid-empty"
        className="text-center py-16 px-4 bg-white rounded-xl border border-dashed border-slate-200"
      >
        <p className="text-slate-500 text-base">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div
      data-testid="product-grid"
      className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"
    >
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={onAddToCart}
        />
      ))}
    </div>
  );
};

export default ProductGrid;

import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from './test-utils';
import ProductCard from '../components/product/ProductCard';
import { mockProducts } from '../mocks/handlers';

describe('ProductCard Component', () => {
  const sampleProduct = mockProducts[0]; // Price: 199.99, Stock: 12

  it('renders product name, price, category, and image', () => {
    renderWithProviders(<ProductCard product={sampleProduct} />);

    expect(screen.getByText(sampleProduct.name)).toBeInTheDocument();
    expect(screen.getByTestId('product-price')).toHaveTextContent('$199.99');
    expect(screen.getByText(sampleProduct.category!.name)).toBeInTheDocument();
    expect(screen.getByRole('img', { name: sampleProduct.name })).toBeInTheDocument();
  });

  it('displays "In Stock" badge for items with healthy stock (> 5)', () => {
    renderWithProviders(<ProductCard product={sampleProduct} />);
    expect(screen.getByTestId('in-stock-badge')).toHaveTextContent(/in stock/i);
  });

  it('displays "Low Stock" badge for items with <= 5 stock', () => {
    const lowStockProduct = mockProducts[1]; // Stock: 5
    renderWithProviders(<ProductCard product={lowStockProduct} />);
    expect(screen.getByTestId('low-stock-badge')).toHaveTextContent(/only 5 left/i);
  });

  it('displays "Out of Stock" badge and disables "Add to Cart" button when stock is 0', async () => {
    const user = userEvent.setup();
    const handleAdd = vi.fn();
    const outOfStockProduct = mockProducts[2]; // Stock: 0

    renderWithProviders(
      <ProductCard product={outOfStockProduct} onAddToCart={handleAdd} />
    );

    expect(screen.getByTestId('out-of-stock-badge')).toHaveTextContent(/out of stock/i);

    const button = screen.getByRole('button', { name: /add ultra-fast usb-c/i });
    expect(button).toBeDisabled();
    expect(button).toHaveTextContent(/sold out/i);

    await user.click(button);
    expect(handleAdd).not.toHaveBeenCalled();
  });

  it('calls onAddToCart handler with the product payload when clicked', async () => {
    const user = userEvent.setup();
    const handleAdd = vi.fn();

    renderWithProviders(
      <ProductCard product={sampleProduct} onAddToCart={handleAdd} />
    );

    const button = screen.getByRole('button', { name: /add wireless noise-canceling/i });
    await user.click(button);

    expect(handleAdd).toHaveBeenCalledTimes(1);
    expect(handleAdd).toHaveBeenCalledWith(sampleProduct);
  });

  it('renders wishlist heart button and toggles wishlist state when clicked', async () => {
    const user = userEvent.setup();

    renderWithProviders(
      <ProductCard product={sampleProduct} />
    );

    const wishlistBtn = screen.getByTestId(`wishlist-toggle-btn-${sampleProduct.id}`);
    expect(wishlistBtn).toBeInTheDocument();

    await user.click(wishlistBtn);
    expect(wishlistBtn).toHaveAttribute('title', 'Remove from Wishlist');

    await user.click(wishlistBtn);
    expect(wishlistBtn).toHaveAttribute('title', 'Save to Wishlist');
  });
});

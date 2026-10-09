import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Trash2, Plus, Minus, ShoppingBag, ArrowRight } from 'lucide-react';
import useCartStore from '../stores/useCartStore';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';

export const CartPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    items,
    updateQuantity,
    removeItem,
    clearCart,
    getTotalPrice,
    getTotalItems,
    getSubtotal,
  } = useCartStore();

  const subtotal = getSubtotal();
  const totalPrice = getTotalPrice();
  const totalItems = getTotalItems();

  if (items.length === 0) {
    return (
      <div
        data-testid="empty-cart-state"
        className="max-w-md mx-auto text-center py-16 px-4 bg-white rounded-2xl border border-slate-200 shadow-sm"
      >
        <div className="h-16 w-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <ShoppingBag className="h-8 w-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Your Cart is Empty</h2>
        <p className="mt-2 text-sm text-slate-500">
          Looks like you haven't added any products to your shopping cart yet.
        </p>
        <div className="mt-6">
          <Link to="/">
            <Button variant="primary">Start Shopping</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
          Shopping Cart ({totalItems} items)
        </h1>
        <Button
          variant="outline"
          size="sm"
          onClick={clearCart}
          data-testid="clear-cart-btn"
          className="text-red-600 hover:bg-red-50 hover:border-red-200"
        >
          Clear Cart
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Items List */}
        <div className="lg:col-span-2 space-y-4">
          {items.map(({ product, quantity }) => (
            <Card
              key={product.id}
              data-testid={`cart-item-${product.id}`}
              className="p-4 flex flex-col sm:flex-row items-center gap-4 hover:border-slate-300"
            >
              {/* Product Thumbnail */}
              <div className="h-20 w-20 bg-slate-100 rounded-lg overflow-hidden shrink-0 flex items-center justify-center">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <ShoppingBag className="h-8 w-8 text-slate-400" />
                )}
              </div>

              {/* Title & Price */}
              <div className="flex-1 min-w-0 text-center sm:text-left">
                <Link
                  to={`/products/${product.id}`}
                  className="font-semibold text-slate-900 hover:text-blue-600 transition-colors line-clamp-1"
                >
                  {product.name}
                </Link>
                <div className="text-sm text-slate-500 mt-0.5">
                  ${Number(product.price).toFixed(2)} each
                </div>
              </div>

              {/* Quantity Controls */}
              <div className="flex items-center border border-slate-300 rounded-lg overflow-hidden">
                <button
                  type="button"
                  data-testid={`decrease-qty-${product.id}`}
                  onClick={() => updateQuantity(product.id, quantity - 1)}
                  className="p-1.5 text-slate-600 hover:bg-slate-100 transition-colors"
                  aria-label={`Decrease quantity of ${product.name}`}
                >
                  <Minus className="h-3.5 w-3.5" />
                </button>
                <span
                  data-testid={`item-qty-${product.id}`}
                  className="px-3 text-sm font-semibold text-slate-800"
                >
                  {quantity}
                </span>
                <button
                  type="button"
                  data-testid={`increase-qty-${product.id}`}
                  onClick={() => updateQuantity(product.id, quantity + 1)}
                  disabled={quantity >= product.stock}
                  className="p-1.5 text-slate-600 hover:bg-slate-100 transition-colors disabled:opacity-50"
                  aria-label={`Increase quantity of ${product.name}`}
                >
                  <Plus className="h-3.5 w-3.5" />
                </button>
              </div>

              {/* Line Total */}
              <div className="text-right min-w-[5rem]">
                <div className="text-base font-bold text-slate-900">
                  ${(Number(product.price) * quantity).toFixed(2)}
                </div>
              </div>

              {/* Remove Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeItem(product.id)}
                data-testid={`remove-item-${product.id}`}
                aria-label={`Remove ${product.name} from cart`}
                className="text-slate-400 hover:text-red-600"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </Card>
          ))}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <Card className="p-6 space-y-6">
            <h2 className="text-lg font-bold text-slate-900 border-b border-slate-100 pb-3">
              Order Summary
            </h2>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between text-slate-600">
                <span>Subtotal</span>
                <span data-testid="cart-subtotal">${subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Estimated Shipping</span>
                <span className="text-emerald-600 font-medium">Free</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Estimated Tax</span>
                <span>${(subtotal * 0.08).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-base font-bold text-slate-900 border-t border-slate-100 pt-3">
                <span>Estimated Total</span>
                <span data-testid="cart-total">
                  ${(totalPrice * 1.08).toFixed(2)}
                </span>
              </div>
            </div>

            <Button
              variant="primary"
              size="lg"
              className="w-full"
              data-testid="checkout-button"
              rightIcon={<ArrowRight className="h-4 w-4" />}
              onClick={() => navigate('/checkout')}
            >
              Proceed to Checkout
            </Button>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CartPage;

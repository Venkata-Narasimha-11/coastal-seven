import { describe, it, expect, beforeEach } from 'vitest';
import useCartStore from '../stores/useCartStore';
import { mockProducts } from '../mocks/handlers';

describe('useCartStore (Zustand State Management)', () => {
  beforeEach(() => {
    useCartStore.getState().clearCart();
  });

  it('initializes with an empty cart and zero totals', () => {
    const state = useCartStore.getState();
    expect(state.items).toEqual([]);
    expect(state.coupon).toBeNull();
    expect(state.discountPercent).toBe(0);
    expect(state.getTotalItems()).toBe(0);
    expect(state.getSubtotal()).toBe(0);
    expect(state.getTotalPrice()).toBe(0);
  });

  it('adds a new product to the cart with default quantity 1', () => {
    const product = mockProducts[0];
    useCartStore.getState().addItem(product);

    const state = useCartStore.getState();
    expect(state.items).toHaveLength(1);
    expect(state.items[0].product.id).toBe(product.id);
    expect(state.items[0].quantity).toBe(1);
    expect(state.getTotalItems()).toBe(1);
    expect(state.getSubtotal()).toBe(product.price);
  });

  it('increments quantity when the same product is added multiple times', () => {
    const product = mockProducts[0];
    useCartStore.getState().addItem(product, 1);
    useCartStore.getState().addItem(product, 2);

    const state = useCartStore.getState();
    expect(state.items).toHaveLength(1);
    expect(state.items[0].quantity).toBe(3);
    expect(state.getTotalItems()).toBe(3);
    expect(state.getSubtotal()).toBe(product.price * 3);
  });

  it('updates the quantity of an item', () => {
    const product = mockProducts[1];
    useCartStore.getState().addItem(product, 2);

    useCartStore.getState().updateQuantity(product.id, 5);

    const state = useCartStore.getState();
    expect(state.items[0].quantity).toBe(5);
    expect(state.getTotalItems()).toBe(5);
    expect(state.getSubtotal()).toBe(product.price * 5);
  });

  it('removes an item from the cart', () => {
    const product1 = mockProducts[0];
    const product2 = mockProducts[1];

    useCartStore.getState().addItem(product1);
    useCartStore.getState().addItem(product2);

    expect(useCartStore.getState().items).toHaveLength(2);

    useCartStore.getState().removeItem(product1.id);

    const state = useCartStore.getState();
    expect(state.items).toHaveLength(1);
    expect(state.items[0].product.id).toBe(product2.id);
  });

  it('clears all items and resets coupon state from the cart', () => {
    useCartStore.getState().addItem(mockProducts[0]);
    useCartStore.getState().applyCoupon('SAVE10');

    useCartStore.getState().clearCart();

    const state = useCartStore.getState();
    expect(state.items).toEqual([]);
    expect(state.coupon).toBeNull();
    expect(state.discountPercent).toBe(0);
    expect(state.getTotalItems()).toBe(0);
    expect(state.getTotalPrice()).toBe(0);
  });

  it('applies promotional coupon codes and calculates discount accurately', () => {
    const product = mockProducts[0]; // Price 199.99
    useCartStore.getState().addItem(product, 1);

    const resultValid = useCartStore.getState().applyCoupon('SAVE10');
    expect(resultValid.success).toBe(true);
    expect(useCartStore.getState().coupon).toBe('SAVE10');
    expect(useCartStore.getState().discountPercent).toBe(10);

    const subtotal = useCartStore.getState().getSubtotal();
    expect(subtotal).toBe(199.99);

    const discountAmount = useCartStore.getState().getDiscountAmount();
    expect(discountAmount).toBe(20.0); // 10% of 199.99 rounded to 20.00

    const resultInvalid = useCartStore.getState().applyCoupon('FAKECODE');
    expect(resultInvalid.success).toBe(false);

    useCartStore.getState().removeCoupon();
    expect(useCartStore.getState().coupon).toBeNull();
    expect(useCartStore.getState().getDiscountAmount()).toBe(0);
  });

  it('computes shipping and tax breakdown correctly', () => {
    // Add product below $100 threshold
    const cheapProduct = { ...mockProducts[2], price: 50.0, stock: 10 };
    useCartStore.getState().addItem(cheapProduct, 1);

    expect(useCartStore.getState().getSubtotal()).toBe(50.0);
    expect(useCartStore.getState().getShippingCost()).toBe(10.0); // Standard shipping
    expect(useCartStore.getState().getTaxAmount()).toBe(4.0); // 8% of 50 = 4.0
    expect(useCartStore.getState().getTotalPrice()).toBe(64.0); // 50 + 10 + 4 = 64.0
  });
});

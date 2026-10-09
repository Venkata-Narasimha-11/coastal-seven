import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  CreditCard,
  Truck,
  ShieldCheck,
  AlertCircle,
  ShoppingBag,
  Lock,
  Tag,
  Sparkles,
  ArrowLeft,
} from 'lucide-react';
import useCartStore from '../stores/useCartStore';
import { checkoutSchema, CheckoutFormData } from '../schemas/checkoutSchema';
import { useCheckoutMutation } from '../hooks/useOrders';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';

export const CheckoutPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    items,
    coupon,
    discountPercent,
    applyCoupon,
    removeCoupon,
    getSubtotal,
    getDiscountAmount,
    getShippingCost,
    getTaxAmount,
    getTotalPrice,
    clearCart,
  } = useCartStore();

  const checkoutMutation = useCheckoutMutation();
  const [couponInput, setCouponInput] = useState('');
  const [couponFeedback, setCouponFeedback] = useState<{ success: boolean; message: string } | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);

  const subtotal = getSubtotal();
  const discountAmount = getDiscountAmount();
  const shippingCost = getShippingCost();
  const taxAmount = getTaxAmount();
  const grandTotal = getTotalPrice();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CheckoutFormData>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      fullName: '',
      email: '',
      phone: '',
      streetAddress: '',
      city: '',
      state: '',
      postalCode: '',
      country: 'India',
      shippingSpeed: 'standard',
      paymentMethod: 'credit_card',
      cardNumber: '',
      cardHolder: '',
      cardExpiry: '',
      cardCvv: '',
      upiId: '',
      termsAccepted: false,
    },
  });

  const selectedPaymentMethod = watch('paymentMethod');

  const handleApplyCoupon = (e: React.FormEvent) => {
    e.preventDefault();
    if (!couponInput.trim()) return;
    const res = applyCoupon(couponInput);
    setCouponFeedback(res);
  };

  const handleFillDemoData = () => {
    setValue('fullName', 'John Doe', { shouldValidate: true });
    setValue('email', 'john.doe@example.com', { shouldValidate: true });
    setValue('phone', '9876543210', { shouldValidate: true });
    setValue('streetAddress', '42 MG Road, Koramangala', { shouldValidate: true });
    setValue('city', 'Bengaluru', { shouldValidate: true });
    setValue('state', 'Karnataka', { shouldValidate: true });
    setValue('postalCode', '560034', { shouldValidate: true });
    setValue('shippingSpeed', 'standard');
    setValue('paymentMethod', 'credit_card');
    setValue('cardNumber', '4532112233445566', { shouldValidate: true });
    setValue('cardHolder', 'JOHN DOE', { shouldValidate: true });
    setValue('cardExpiry', '12/28', { shouldValidate: true });
    setValue('cardCvv', '789', { shouldValidate: true });
    setValue('termsAccepted', true, { shouldValidate: true });
    setServerError(null);
  };

  const onSubmit = async (data: CheckoutFormData) => {
    setServerError(null);

    const formattedAddress = `${data.fullName}, ${data.streetAddress}, ${data.city}, ${data.state} - ${data.postalCode}, ${data.country}. Phone: ${data.phone}. [Delivery: ${data.shippingSpeed.toUpperCase()} | Payment: ${data.paymentMethod.toUpperCase()}]`;

    try {
      await checkoutMutation.mutateAsync(formattedAddress);
      clearCart();
      navigate('/orders');
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        'Failed to process checkout. Please check your network and try again.';
      setServerError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  };

  if (items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto py-16 px-4 text-center">
        <div className="h-20 w-20 bg-blue-50 dark:bg-blue-900/30 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
          <ShoppingBag className="h-10 w-10" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
          Your Shopping Cart is Empty
        </h2>
        <p className="text-slate-600 dark:text-slate-400 mb-8">
          Add items to your cart before proceeding to checkout.
        </p>
        <Link to="/">
          <Button variant="primary" size="lg">
            Browse Catalog
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <Link
            to="/cart"
            className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-blue-600 mb-2 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Cart
          </Link>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Checkout & Order Finalization
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Validated via React Hook Form & Zod schema, connected to FastAPI backend.
          </p>
        </div>

        {/* 1-Click Demo Fill */}
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleFillDemoData}
          className="border-dashed border-blue-400 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/40"
        >
          <Sparkles className="h-4 w-4 mr-1.5 text-blue-500" />
          Auto-fill Demo Details
        </Button>
      </div>

      {serverError && (
        <div
          role="alert"
          className="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 flex items-start gap-3 text-red-700 dark:text-red-300"
        >
          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0 text-red-500" />
          <div>
            <h4 className="font-semibold text-sm">Checkout Error</h4>
            <p className="text-xs mt-0.5">{serverError}</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Main Form Fields */}
          <div className="lg:col-span-8 space-y-6">
            {/* Section 1: Shipping Address */}
            <Card>
              <Card.Header>
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-blue-100 dark:bg-blue-900/40 text-blue-600 flex items-center justify-center font-bold text-sm">
                    1
                  </div>
                  <div>
                    <Card.Title>Shipping Destination</Card.Title>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Where should we deliver your order?
                    </p>
                  </div>
                </div>
              </Card.Header>

              <Card.Content className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="Full Name"
                    placeholder="e.g. John Doe"
                    error={errors.fullName?.message}
                    {...register('fullName')}
                  />
                  <Input
                    label="Email Address"
                    type="email"
                    placeholder="john@example.com"
                    error={errors.email?.message}
                    {...register('email')}
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="Phone Number (10 digits)"
                    placeholder="9876543210"
                    error={errors.phone?.message}
                    {...register('phone')}
                  />
                  <Input
                    label="Country"
                    placeholder="India"
                    error={errors.country?.message}
                    {...register('country')}
                  />
                </div>

                <Input
                  label="Street Address"
                  placeholder="Flat No, Building, Street, Landmark"
                  error={errors.streetAddress?.message}
                  {...register('streetAddress')}
                />

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <Input
                    label="City"
                    placeholder="Bengaluru"
                    error={errors.city?.message}
                    {...register('city')}
                  />
                  <Input
                    label="State"
                    placeholder="Karnataka"
                    error={errors.state?.message}
                    {...register('state')}
                  />
                  <Input
                    label="Postal Code (PIN)"
                    placeholder="560034"
                    error={errors.postalCode?.message}
                    {...register('postalCode')}
                  />
                </div>
              </Card.Content>
            </Card>

            {/* Section 2: Delivery Speed */}
            <Card>
              <Card.Header>
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-blue-100 dark:bg-blue-900/40 text-blue-600 flex items-center justify-center font-bold text-sm">
                    2
                  </div>
                  <div>
                    <Card.Title>Delivery Method</Card.Title>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Choose your preferred transit speed
                    </p>
                  </div>
                </div>
              </Card.Header>

              <Card.Content>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <label className="border rounded-xl p-3 flex flex-col cursor-pointer border-slate-200 dark:border-slate-800 hover:border-blue-400 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <input
                        type="radio"
                        value="standard"
                        {...register('shippingSpeed')}
                        className="text-blue-600 focus:ring-blue-500"
                      />
                      <Badge variant="default">Standard</Badge>
                    </div>
                    <span className="font-semibold text-sm text-slate-800 dark:text-slate-200">
                      Standard Ground
                    </span>
                    <span className="text-xs text-slate-500 mt-1">3-5 business days</span>
                  </label>

                  <label className="border rounded-xl p-3 flex flex-col cursor-pointer border-slate-200 dark:border-slate-800 hover:border-blue-400 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <input
                        type="radio"
                        value="express"
                        {...register('shippingSpeed')}
                        className="text-blue-600 focus:ring-blue-500"
                      />
                      <Badge variant="info">Express</Badge>
                    </div>
                    <span className="font-semibold text-sm text-slate-800 dark:text-slate-200">
                      Express Air
                    </span>
                    <span className="text-xs text-slate-500 mt-1">1-2 business days</span>
                  </label>

                  <label className="border rounded-xl p-3 flex flex-col cursor-pointer border-slate-200 dark:border-slate-800 hover:border-blue-400 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <input
                        type="radio"
                        value="overnight"
                        {...register('shippingSpeed')}
                        className="text-blue-600 focus:ring-blue-500"
                      />
                      <Badge variant="warning">Priority</Badge>
                    </div>
                    <span className="font-semibold text-sm text-slate-800 dark:text-slate-200">
                      Overnight Delivery
                    </span>
                    <span className="text-xs text-slate-500 mt-1">Next morning by 10 AM</span>
                  </label>
                </div>
              </Card.Content>
            </Card>

            {/* Section 3: Payment Method */}
            <Card>
              <Card.Header>
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-blue-100 dark:bg-blue-900/40 text-blue-600 flex items-center justify-center font-bold text-sm">
                    3
                  </div>
                  <div>
                    <Card.Title>Payment Method</Card.Title>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Transactions are 256-bit encrypted and secure
                    </p>
                  </div>
                </div>
              </Card.Header>

              <Card.Content className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <label className="border rounded-xl p-3 flex items-center gap-3 cursor-pointer border-slate-200 dark:border-slate-800 hover:border-blue-500 transition-colors">
                    <input
                      type="radio"
                      value="credit_card"
                      {...register('paymentMethod')}
                      className="text-blue-600 focus:ring-blue-500"
                    />
                    <CreditCard className="h-5 w-5 text-slate-600 dark:text-slate-300" />
                    <span className="text-sm font-medium text-slate-800 dark:text-slate-200">
                      Credit / Debit Card
                    </span>
                  </label>

                  <label className="border rounded-xl p-3 flex items-center gap-3 cursor-pointer border-slate-200 dark:border-slate-800 hover:border-blue-500 transition-colors">
                    <input
                      type="radio"
                      value="upi"
                      {...register('paymentMethod')}
                      className="text-blue-600 focus:ring-blue-500"
                    />
                    <Sparkles className="h-5 w-5 text-indigo-500" />
                    <span className="text-sm font-medium text-slate-800 dark:text-slate-200">
                      UPI / QR
                    </span>
                  </label>

                  <label className="border rounded-xl p-3 flex items-center gap-3 cursor-pointer border-slate-200 dark:border-slate-800 hover:border-blue-500 transition-colors">
                    <input
                      type="radio"
                      value="cod"
                      {...register('paymentMethod')}
                      className="text-blue-600 focus:ring-blue-500"
                    />
                    <Truck className="h-5 w-5 text-emerald-500" />
                    <span className="text-sm font-medium text-slate-800 dark:text-slate-200">
                      Cash on Delivery
                    </span>
                  </label>
                </div>

                {/* Conditional Card Form */}
                {selectedPaymentMethod === 'credit_card' && (
                  <div className="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-3">
                    <Input
                      label="Card Number (16 digits)"
                      placeholder="4532 1122 3344 5566"
                      error={errors.cardNumber?.message}
                      {...register('cardNumber')}
                    />

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <div className="sm:col-span-1">
                        <Input
                          label="Expiry (MM/YY)"
                          placeholder="12/28"
                          error={errors.cardExpiry?.message}
                          {...register('cardExpiry')}
                        />
                      </div>
                      <div className="sm:col-span-1">
                        <Input
                          label="CVV"
                          placeholder="123"
                          type="password"
                          maxLength={4}
                          error={errors.cardCvv?.message}
                          {...register('cardCvv')}
                        />
                      </div>
                      <div className="sm:col-span-1">
                        <Input
                          label="Cardholder Name"
                          placeholder="Name on card"
                          error={errors.cardHolder?.message}
                          {...register('cardHolder')}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Conditional UPI Form */}
                {selectedPaymentMethod === 'upi' && (
                  <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
                    <Input
                      label="UPI Virtual Payment Address"
                      placeholder="e.g. mobile@oksbi or username@upi"
                      error={errors.upiId?.message}
                      {...register('upiId')}
                    />
                  </div>
                )}

                {/* Terms and conditions checkbox */}
                <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      data-testid="terms-checkbox"
                      {...register('termsAccepted')}
                      className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-xs text-slate-600 dark:text-slate-400">
                      I agree to the Terms of Service, Return Policy, and authorize the charge for this purchase.
                    </span>
                  </label>
                  {errors.termsAccepted && (
                    <p className="text-xs text-red-600 mt-1 font-medium">
                      {errors.termsAccepted.message}
                    </p>
                  )}
                </div>
              </Card.Content>
            </Card>
          </div>

          {/* Sidebar: Order Summary & Placement */}
          <div className="lg:col-span-4 space-y-6">
            <Card>
              <Card.Header>
                <Card.Title>Order Summary</Card.Title>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {items.length} unique item{items.length !== 1 ? 's' : ''} in cart
                </p>
              </Card.Header>

              <Card.Content className="space-y-4">
                {/* Items List */}
                <div className="max-h-60 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800 pr-1">
                  {items.map((item) => (
                    <div key={item.product.id} className="py-2.5 flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2.5">
                        <img
                          src={item.product.thumbnail_url || item.product.image_url || 'https://via.placeholder.com/48'}
                          alt={item.product.name}
                          className="h-10 w-10 object-cover rounded-md bg-slate-100 dark:bg-slate-800"
                        />
                        <div>
                          <p className="font-medium text-slate-800 dark:text-slate-200 line-clamp-1 text-xs">
                            {item.product.name}
                          </p>
                          <p className="text-xs text-slate-500">Qty: {item.quantity}</p>
                        </div>
                      </div>
                      <span className="font-semibold text-xs text-slate-900 dark:text-white">
                        ₹{(Number(item.product.price) * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Promo Code Input */}
                <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Promo Code (SAVE10, WELCOME20)"
                      value={couponInput}
                      onChange={(e) => setCouponInput(e.target.value)}
                      className="flex-1 px-3 py-1.5 text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleApplyCoupon}
                      className="text-xs"
                    >
                      Apply
                    </Button>
                  </div>

                  {couponFeedback && (
                    <p
                      className={`text-xs mt-1.5 ${
                        couponFeedback.success ? 'text-emerald-600 font-medium' : 'text-red-500'
                      }`}
                    >
                      {couponFeedback.message}
                    </p>
                  )}

                  {coupon && (
                    <div className="mt-2 flex items-center justify-between bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 px-2.5 py-1 rounded-lg">
                      <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 flex items-center gap-1">
                        <Tag className="h-3 w-3" /> {coupon} ({discountPercent}% OFF)
                      </span>
                      <button
                        type="button"
                        onClick={removeCoupon}
                        className="text-xs text-red-600 hover:underline font-medium"
                      >
                        Remove
                      </button>
                    </div>
                  )}
                </div>

                {/* Pricing Breakdown */}
                <div className="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-2 text-xs">
                  <div className="flex justify-between text-slate-600 dark:text-slate-400">
                    <span>Subtotal</span>
                    <span>₹{subtotal.toFixed(2)}</span>
                  </div>

                  {discountAmount > 0 && (
                    <div className="flex justify-between text-emerald-600 dark:text-emerald-400 font-medium">
                      <span>Discount ({coupon})</span>
                      <span>-₹{discountAmount.toFixed(2)}</span>
                    </div>
                  )}

                  <div className="flex justify-between text-slate-600 dark:text-slate-400">
                    <span>Shipping</span>
                    <span>{shippingCost === 0 ? 'FREE' : `₹${shippingCost.toFixed(2)}`}</span>
                  </div>

                  <div className="flex justify-between text-slate-600 dark:text-slate-400">
                    <span>Estimated Tax (8%)</span>
                    <span>₹{taxAmount.toFixed(2)}</span>
                  </div>

                  <div className="pt-2 border-t border-slate-200 dark:border-slate-700 flex justify-between text-base font-bold text-slate-900 dark:text-white">
                    <span>Grand Total</span>
                    <span>₹{grandTotal.toFixed(2)}</span>
                  </div>
                </div>

                {/* Submit Order Button */}
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  fullWidth
                  loading={isSubmitting || checkoutMutation.isPending}
                  className="mt-4"
                  data-testid="place-order-button"
                >
                  <Lock className="h-4 w-4 mr-2" />
                  Place Order (₹{grandTotal.toFixed(2)})
                </Button>

                <div className="flex items-center justify-center gap-1.5 text-slate-400 text-xs text-center pt-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-500" />
                  <span>Safe & Secure 256-Bit SSL Encrypted Checkout</span>
                </div>
              </Card.Content>
            </Card>
          </div>
        </div>
      </form>
    </div>
  );
};

export default CheckoutPage;

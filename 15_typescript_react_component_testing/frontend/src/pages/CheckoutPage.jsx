import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  CreditCard,
  Truck,
  CheckCircle2,
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
  MapPin,
  FileCheck,
  Lock,
  Sparkles,
  ShoppingBag,
  Tag,
  Settings,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useCart } from "../hooks/useCart";
import { orderService } from "../services/orderService";
import {
  shippingStepSchema,
  deliveryStepSchema,
  paymentStepSchema,
  reviewStepSchema,
} from "../schemas/checkoutSchemas";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "../components/ui/card";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from "../components/ui/form";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { toast } from "../components/ui/sonner";

const STEPS = [
  { id: 1, name: "Shipping", icon: MapPin },
  { id: 2, name: "Delivery", icon: Truck },
  { id: 3, name: "Payment", icon: CreditCard },
  { id: 4, name: "Review", icon: FileCheck },
];

export const CheckoutPage = () => {
  const { cart, refreshCart, appliedCoupon, markCouponRedeemed } = useCart();
  const { isAdmin } = useAuth();
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(1);
  const [submittingOrder, setSubmittingOrder] = useState(false);
  const [checkoutError, setCheckoutError] = useState("");

  // Master multi-step form state
  const [formData, setFormData] = useState({
    // Step 1: Shipping
    fullName: "",
    email: "",
    phone: "",
    streetAddress: "",
    city: "",
    state: "",
    postalCode: "",
    country: "India",
    // Step 2: Delivery
    shippingSpeed: "standard",
    specialInstructions: "",
    giftPackaging: false,
    // Step 3: Payment
    paymentMethod: "card",
    cardNumber: "",
    cardHolder: "",
    cardExpiry: "",
    cardCvv: "",
    upiId: "",
    // Step 4: Terms
    termsAccepted: false,
  });

  // Step 1 Form
  const shippingForm = useForm({
    resolver: zodResolver(shippingStepSchema),
    defaultValues: {
      fullName: formData.fullName,
      email: formData.email,
      phone: formData.phone,
      streetAddress: formData.streetAddress,
      city: formData.city,
      state: formData.state,
      postalCode: formData.postalCode,
      country: formData.country,
    },
    mode: "onTouched",
  });

  // Step 2 Form
  const deliveryForm = useForm({
    resolver: zodResolver(deliveryStepSchema),
    defaultValues: {
      shippingSpeed: formData.shippingSpeed,
      specialInstructions: formData.specialInstructions,
      giftPackaging: formData.giftPackaging,
    },
    mode: "onTouched",
  });

  // Step 3 Form
  const paymentForm = useForm({
    resolver: zodResolver(paymentStepSchema),
    defaultValues: {
      paymentMethod: formData.paymentMethod,
      cardNumber: formData.cardNumber,
      cardHolder: formData.cardHolder,
      cardExpiry: formData.cardExpiry,
      cardCvv: formData.cardCvv,
      upiId: formData.upiId,
    },
    mode: "onTouched",
  });

  // Step 4 Form
  const reviewForm = useForm({
    resolver: zodResolver(reviewStepSchema),
    defaultValues: {
      termsAccepted: formData.termsAccepted,
    },
    mode: "onChange",
  });

  if (isAdmin) {
    return (
      <Card className="max-w-md mx-auto my-12 text-center p-8 border-amber-500/50">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-amber-500/10 text-amber-500 mb-4">
          <ShieldCheck className="h-7 w-7" />
        </div>
        <CardTitle className="text-xl font-bold mb-2 text-amber-500">Admin Mode: Checkout Restricted</CardTitle>
        <CardDescription className="mb-6 leading-relaxed">
          Store administrators cannot perform retail consumer checkouts or purchase products. Please use the Admin Hub to manage products, categories, and customer orders.
        </CardDescription>
        <Link to="/admin">
          <Button className="w-full bg-amber-500 hover:bg-amber-600 text-black font-bold gap-2">
            <Settings className="h-4 w-4" /> Open Admin Hub
          </Button>
        </Link>
      </Card>
    );
  }

  if (!cart.items || cart.items.length === 0) {
    return (
      <Card className="max-w-md mx-auto my-12 text-center p-8">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-muted mb-4">
          <ShoppingBag className="h-6 w-6 text-muted-foreground" />
        </div>
        <CardTitle className="text-xl font-bold mb-2">Your Cart is Empty</CardTitle>
        <CardDescription className="mb-6">
          Add items to your cart before proceeding to multi-step checkout.
        </CardDescription>
        <Link to="/">
          <Button className="w-full">Explore Product Catalog</Button>
        </Link>
      </Card>
    );
  }

  // Cost calculations with Amazon-Style Promotional Discount
  const subtotal = Number(cart.total_amount || 0);
  const promoDiscount = appliedCoupon ? Math.min(subtotal, appliedCoupon.discount) : 0;
  const discountedSubtotal = Math.max(0, subtotal - promoDiscount);
  const shippingCost =
    formData.shippingSpeed === "overnight"
      ? 19.99
      : formData.shippingSpeed === "express"
      ? 9.99
      : 0;
  const estimatedTax = Number((discountedSubtotal * 0.08).toFixed(2));
  const grandTotal = Number((discountedSubtotal + shippingCost + estimatedTax).toFixed(2));

  // Step 1 Submission
  const handleShippingSubmit = (values) => {
    setFormData((prev) => ({ ...prev, ...values }));
    setCurrentStep(2);
    toast.success("Shipping address verified");
  };

  // Step 2 Submission
  const handleDeliverySubmit = (values) => {
    setFormData((prev) => ({ ...prev, ...values }));
    setCurrentStep(3);
    toast.success("Delivery preferences saved");
  };

  // Step 3 Submission
  const handlePaymentSubmit = (values) => {
    setFormData((prev) => ({ ...prev, ...values }));
    setCurrentStep(4);
    toast.success("Payment details validated");
  };

  // Step 4 Final Order Placement
  const handleFinalOrderSubmit = async (values) => {
    setSubmittingOrder(true);
    setCheckoutError("");
    try {
      // Build formatted delivery string expected by backend
      const formattedAddress = `${formData.fullName}, ${formData.streetAddress}, ${formData.city}, ${formData.state} - ${formData.postalCode} (${formData.country}). Phone: ${formData.phone}. Method: ${formData.shippingSpeed.toUpperCase()} shipping. Payment: ${formData.paymentMethod.toUpperCase()}`;

      const order = await orderService.checkout(formattedAddress);
      
      // Permanently mark single-use promotional coupon as redeemed for this user (Amazon rule)
      if (appliedCoupon && markCouponRedeemed) {
        markCouponRedeemed(appliedCoupon.code);
      }

      await refreshCart();

      toast.success("Order Placed Successfully! 🎉", {
        description: `Order #${order.id} is confirmed. Tracking live updates...`,
      });

      navigate(`/orders/${order.id}`);
    } catch (err) {
      console.error("Order placement failed:", err);
      const msg =
        err.response?.data?.detail ||
        "Checkout failed. Insufficient stock or transaction error.";
      setCheckoutError(msg);
      toast.error("Checkout Failed", { description: msg });
    } finally {
      setSubmittingOrder(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header & Back Link */}
      <div className="flex items-center justify-between">
        <Link
          to="/cart"
          className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Cart
        </Link>
        <Badge variant="outline" className="gap-1 border-primary/30 text-primary text-xs">
          <Lock className="h-3 w-3" /> 256-Bit Encrypted Checkout
        </Badge>
      </div>

      <div className="space-y-1">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Checkout</h1>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Step-by-step validated checkout workflow with dynamic pricing & live inventory reservation
        </p>
      </div>

      {/* Multi-Step Stepper Progress Bar */}
      <nav aria-label="Checkout Steps" className="relative py-2">
        <div className="grid grid-cols-4 gap-2 sm:gap-4">
          {STEPS.map((step) => {
            const Icon = step.icon;
            const isCompleted = currentStep > step.id;
            const isCurrent = currentStep === step.id;

            return (
              <div
                key={step.id}
                className={`flex flex-col items-center sm:items-start p-2.5 sm:p-3 rounded-lg border transition-all ${
                  isCurrent
                    ? "border-primary bg-primary/5 text-primary shadow-sm"
                    : isCompleted
                    ? "border-emerald-500/40 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400"
                    : "border-border/60 bg-card text-muted-foreground opacity-60"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div
                    className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                      isCurrent
                        ? "bg-primary text-primary-foreground"
                        : isCompleted
                        ? "bg-emerald-500 text-white"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {isCompleted ? <CheckCircle2 className="h-4 w-4" /> : step.id}
                  </div>
                  <span className="hidden sm:inline text-xs font-semibold">{step.name}</span>
                </div>
                <span className="sm:hidden text-[10px] font-medium mt-1 truncate">{step.name}</span>
              </div>
            );
          })}
        </div>
      </nav>

      {/* Checkout Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Step Form Area (2 cols) */}
        <div className="lg:col-span-2">
          {checkoutError && (
            <div
              className="flex items-center gap-2 rounded-lg bg-destructive/10 p-3 text-xs font-medium text-destructive border border-destructive/20 mb-4"
              role="alert"
            >
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{checkoutError}</span>
            </div>
          )}

          {/* STEP 1: Shipping Address Form */}
          {currentStep === 1 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-primary" /> Step 1: Shipping Address
                </CardTitle>
                <CardDescription>
                  Enter the recipient and physical delivery address
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...shippingForm}>
                  <form
                    onSubmit={shippingForm.handleSubmit(handleShippingSubmit)}
                    className="space-y-4"
                    noValidate
                  >
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <FormField
                        control={shippingForm.control}
                        name="fullName"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>Full Name</FormLabel>
                            <FormControl>
                              <Input placeholder="John Doe" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={shippingForm.control}
                        name="email"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>Email for Tracking</FormLabel>
                            <FormControl>
                              <Input type="email" placeholder="john@domain.com" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <FormField
                        control={shippingForm.control}
                        name="phone"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>Phone Number</FormLabel>
                            <FormControl>
                              <Input placeholder="+91 9876543210" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={shippingForm.control}
                        name="country"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>Country</FormLabel>
                            <FormControl>
                              <Input {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <FormField
                      control={shippingForm.control}
                      name="streetAddress"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel required>Street Address</FormLabel>
                          <FormControl>
                            <Input placeholder="Flat 402, Green Avenue, Landmark Road" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid grid-cols-3 gap-3">
                      <FormField
                        control={shippingForm.control}
                        name="city"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>City</FormLabel>
                            <FormControl>
                              <Input placeholder="Hyderabad" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={shippingForm.control}
                        name="state"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>State</FormLabel>
                            <FormControl>
                              <Input placeholder="Telangana" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={shippingForm.control}
                        name="postalCode"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel required>PIN Code</FormLabel>
                            <FormControl>
                              <Input placeholder="500081" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <div className="flex justify-end pt-4">
                      <Button type="submit">
                        Continue to Delivery <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </div>
                  </form>
                </Form>
              </CardContent>
            </Card>
          )}

          {/* STEP 2: Delivery Method Form */}
          {currentStep === 2 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Truck className="h-5 w-5 text-primary" /> Step 2: Delivery Preferences
                </CardTitle>
                <CardDescription>
                  Choose fulfillment speed and special packaging instructions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...deliveryForm}>
                  <form
                    onSubmit={deliveryForm.handleSubmit(handleDeliverySubmit)}
                    className="space-y-6"
                    noValidate
                  >
                    <FormField
                      control={deliveryForm.control}
                      name="shippingSpeed"
                      render={({ field }) => (
                        <FormItem className="space-y-3">
                          <FormLabel required>Select Delivery Speed</FormLabel>
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            {[
                              { id: "standard", title: "Standard", time: "3-5 Business Days", fee: "Free" },
                              { id: "express", title: "Express", time: "1-2 Business Days", fee: "$9.99" },
                              { id: "overnight", title: "Priority", time: "Next Day Guaranteed", fee: "$19.99" },
                            ].map((opt) => (
                              <label
                                key={opt.id}
                                className={`flex flex-col justify-between p-3.5 rounded-lg border cursor-pointer transition-all ${
                                  field.value === opt.id
                                    ? "border-primary bg-primary/5 ring-1 ring-primary"
                                    : "border-border hover:bg-muted/30"
                                }`}
                              >
                                <div className="flex items-center justify-between mb-2">
                                  <input
                                    type="radio"
                                    name="shippingSpeed"
                                    value={opt.id}
                                    checked={field.value === opt.id}
                                    onChange={() => field.onChange(opt.id)}
                                    className="text-primary focus:ring-primary h-4 w-4"
                                  />
                                  <Badge variant={opt.fee === "Free" ? "success" : "secondary"}>
                                    {opt.fee}
                                  </Badge>
                                </div>
                                <span className="text-sm font-semibold text-foreground">
                                  {opt.title}
                                </span>
                                <span className="text-xs text-muted-foreground">{opt.time}</span>
                              </label>
                            ))}
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={deliveryForm.control}
                      name="specialInstructions"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Special Delivery Instructions</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="e.g. Leave with security at gate, ring second bell..."
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            Optional notes for the courier service
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="flex items-center justify-between pt-4">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setCurrentStep(1)}
                      >
                        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Shipping
                      </Button>
                      <Button type="submit">
                        Continue to Payment <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </div>
                  </form>
                </Form>
              </CardContent>
            </Card>
          )}

          {/* STEP 3: Payment Method Form */}
          {currentStep === 3 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <CreditCard className="h-5 w-5 text-primary" /> Step 3: Payment Method
                </CardTitle>
                <CardDescription>
                  Enter and validate payment details securely with Zod schema rules
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...paymentForm}>
                  <form
                    onSubmit={paymentForm.handleSubmit(handlePaymentSubmit)}
                    className="space-y-6"
                    noValidate
                  >
                    <FormField
                      control={paymentForm.control}
                      name="paymentMethod"
                      render={({ field }) => (
                        <FormItem className="space-y-3">
                          <FormLabel required>Payment Method</FormLabel>
                          <div className="grid grid-cols-3 gap-3">
                            {[
                              { id: "card", title: "Credit Card", desc: "Visa, Mastercard" },
                              { id: "upi", title: "UPI / QR", desc: "GPay, PhonePe, Paytm" },
                              { id: "cod", title: "Cash On Delivery", desc: "Pay on arrival" },
                            ].map((pm) => (
                              <label
                                key={pm.id}
                                className={`flex flex-col p-3 rounded-lg border cursor-pointer transition-all ${
                                  field.value === pm.id
                                    ? "border-primary bg-primary/5 ring-1 ring-primary"
                                    : "border-border hover:bg-muted/30"
                                }`}
                              >
                                <div className="flex items-center justify-between mb-1.5">
                                  <input
                                    type="radio"
                                    name="paymentMethod"
                                    value={pm.id}
                                    checked={field.value === pm.id}
                                    onChange={() => field.onChange(pm.id)}
                                    className="text-primary focus:ring-primary h-4 w-4"
                                  />
                                </div>
                                <span className="text-xs font-semibold text-foreground">
                                  {pm.title}
                                </span>
                                <span className="text-[11px] text-muted-foreground">{pm.desc}</span>
                              </label>
                            ))}
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Conditional Fields: Card Details */}
                    {paymentForm.watch("paymentMethod") === "card" && (
                      <div className="rounded-lg border border-border p-4 bg-muted/20 space-y-4">
                        <div className="flex items-center justify-between pb-2 border-b border-border/50 text-xs font-medium text-muted-foreground">
                          <span>Card Information</span>
                          <span className="flex items-center gap-1 text-[11px] text-emerald-500 font-semibold">
                            <ShieldCheck className="w-3.5 h-3.5" /> 100% Mock Safe
                          </span>
                        </div>

                        <FormField
                          control={paymentForm.control}
                          name="cardNumber"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel required>Card Number (16 Digits)</FormLabel>
                              <FormControl>
                                <Input placeholder="4532 8910 2345 6789" maxLength={16} {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <FormField
                          control={paymentForm.control}
                          name="cardHolder"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel required>Cardholder Name</FormLabel>
                              <FormControl>
                                <Input placeholder="ALEX MORGAN" {...field} />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <div className="grid grid-cols-2 gap-3">
                          <FormField
                            control={paymentForm.control}
                            name="cardExpiry"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel required>Expiry (MM/YY)</FormLabel>
                                <FormControl>
                                  <Input placeholder="12/28" maxLength={5} {...field} />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={paymentForm.control}
                            name="cardCvv"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel required>CVV / CVC</FormLabel>
                                <FormControl>
                                  <Input
                                    type="password"
                                    placeholder="•••"
                                    maxLength={4}
                                    {...field}
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </div>
                      </div>
                    )}

                    {/* Conditional Fields: UPI */}
                    {paymentForm.watch("paymentMethod") === "upi" && (
                      <div className="rounded-lg border border-border p-4 bg-muted/20 space-y-3">
                        <FormField
                          control={paymentForm.control}
                          name="upiId"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel required>Virtual Payment Address (VPA / UPI ID)</FormLabel>
                              <FormControl>
                                <Input placeholder="yourname@okaxis or mobile@paytm" {...field} />
                              </FormControl>
                              <FormDescription>
                                Instant UPI authorization request will be simulated
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                    )}

                    {/* Conditional Fields: COD */}
                    {paymentForm.watch("paymentMethod") === "cod" && (
                      <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-4 text-xs text-foreground space-y-1">
                        <p className="font-semibold flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                          <CheckCircle2 className="h-4 w-4" /> Cash on Delivery Selected
                        </p>
                        <p className="text-muted-foreground text-[11px]">
                          Please keep exact cash handy at delivery. No advance online transfer required.
                        </p>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setCurrentStep(2)}
                      >
                        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Delivery
                      </Button>
                      <Button type="submit">
                        Review Order <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </div>
                  </form>
                </Form>
              </CardContent>
            </Card>
          )}

          {/* STEP 4: Review & Final Confirmation */}
          {currentStep === 4 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <FileCheck className="h-5 w-5 text-primary" /> Step 4: Final Order Review
                </CardTitle>
                <CardDescription>
                  Review your order details before final submission to FastAPI backend
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Summary Snapshot Blocks */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="rounded-lg border border-border p-3 space-y-1">
                    <span className="text-[11px] font-semibold uppercase text-muted-foreground">
                      Recipient
                    </span>
                    <p className="text-xs font-bold text-foreground">{formData.fullName}</p>
                    <p className="text-[11px] text-muted-foreground truncate">{formData.email}</p>
                    <p className="text-[11px] text-muted-foreground">{formData.phone}</p>
                  </div>

                  <div className="rounded-lg border border-border p-3 space-y-1">
                    <span className="text-[11px] font-semibold uppercase text-muted-foreground">
                      Shipping To
                    </span>
                    <p className="text-xs text-foreground line-clamp-2">{formData.streetAddress}</p>
                    <p className="text-[11px] text-muted-foreground">
                      {formData.city}, {formData.postalCode}
                    </p>
                  </div>

                  <div className="rounded-lg border border-border p-3 space-y-1">
                    <span className="text-[11px] font-semibold uppercase text-muted-foreground">
                      Method & Speed
                    </span>
                    <p className="text-xs font-bold uppercase text-primary">
                      {formData.shippingSpeed}
                    </p>
                    <p className="text-[11px] text-muted-foreground capitalize">
                      Payment: {formData.paymentMethod}
                    </p>
                  </div>
                </div>

                {/* Items preview */}
                <div className="border rounded-lg divide-y">
                  <div className="bg-muted/40 px-3 py-2 text-xs font-semibold text-muted-foreground">
                    Items in Order ({cart.total_items})
                  </div>
                  <div className="max-h-48 overflow-y-auto divide-y">
                    {cart.items.map((item) => (
                      <div key={item.product_id} className="flex items-center justify-between p-3 text-xs">
                        <div className="space-y-0.5">
                          <span className="font-medium text-foreground">{item.name}</span>
                          <p className="text-[11px] text-muted-foreground">
                            Qty: {item.quantity} × ${Number(item.unit_price || 0).toFixed(2)}
                          </p>
                        </div>
                        <span className="font-semibold text-foreground">
                          ${Number(item.subtotal || 0).toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Terms Agreement Form */}
                <Form {...reviewForm}>
                  <form
                    onSubmit={reviewForm.handleSubmit(handleFinalOrderSubmit)}
                    className="space-y-4"
                  >
                    <FormField
                      control={reviewForm.control}
                      name="termsAccepted"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 bg-muted/20">
                          <FormControl>
                            <input
                              type="checkbox"
                              checked={field.value}
                              onChange={field.onChange}
                              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary mt-0.5"
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel className="text-xs font-medium cursor-pointer">
                              I agree to the Terms of Service and acknowledge the atomic order reservation
                            </FormLabel>
                            <FormDescription className="text-[11px]">
                              Stock is decremented atomically upon confirmation with Celery confirmation email dispatch
                            </FormDescription>
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="flex items-center justify-between pt-4">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setCurrentStep(3)}
                        disabled={submittingOrder}
                      >
                        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Payment
                      </Button>
                      <Button
                        type="submit"
                        className="bg-emerald-600 hover:bg-emerald-700 text-white min-w-[160px]"
                        isLoading={submittingOrder}
                        disabled={submittingOrder}
                      >
                        <CheckCircle2 className="mr-2 h-4 w-4" />
                        {submittingOrder ? "Confirming..." : `Pay $${grandTotal.toFixed(2)}`}
                      </Button>
                    </div>
                  </form>
                </Form>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Order Summary Sidebar (1 col) */}
        <div>
          <Card className="sticky top-20 border-border/80">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold flex items-center justify-between">
                <span>Order Summary</span>
                <Badge variant="secondary" className="text-xs font-normal">
                  {cart.total_items} items
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="flex justify-between text-muted-foreground">
                <span>Cart Subtotal</span>
                <span className="font-medium text-foreground">${Number(subtotal || 0).toFixed(2)}</span>
              </div>

              {appliedCoupon && (
                <div className="flex justify-between text-emerald-500 font-semibold animate-in fade-in-50">
                  <span className="flex items-center gap-1">
                    <Tag className="w-3 h-3" /> Promo ({appliedCoupon.code}):
                  </span>
                  <span>-${Number(promoDiscount || 0).toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between text-muted-foreground">
                <span>Shipping Fee</span>
                <span className="font-medium text-foreground">
                  {shippingCost === 0 ? "FREE" : `$${Number(shippingCost || 0).toFixed(2)}`}
                </span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>Estimated Tax (8%)</span>
                <span className="font-medium text-foreground">${Number(estimatedTax || 0).toFixed(2)}</span>
              </div>

              <div className="border-t border-border/60 pt-3 flex justify-between text-sm font-bold text-foreground">
                <span>Total Amount</span>
                <span className="text-primary text-base">${Number(grandTotal || 0).toFixed(2)}</span>
              </div>

              <div className="rounded-md bg-muted/40 p-2.5 text-[11px] text-muted-foreground space-y-1">
                <div className="flex items-center gap-1 font-semibold text-foreground">
                  <Sparkles className="w-3 h-3 text-primary" /> Multi-Step Features:
                </div>
                <p>• Form state retained across back & forth steps</p>
                <p>• Step-by-step Zod schemas prevention</p>
                <p>• Direct checkout into Day 10 FastAPI backend</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;

import { z } from "zod";

// Step 1: Shipping Address Schema
export const shippingStepSchema = z.object({
  fullName: z
    .string()
    .min(3, { message: "Full recipient name must be at least 3 characters" })
    .max(80, { message: "Recipient name cannot exceed 80 characters" }),
  email: z
    .string()
    .min(1, { message: "Email is required for order notifications" })
    .email({ message: "Invalid email address" }),
  phone: z
    .string()
    .min(10, { message: "Phone number must have at least 10 digits" })
    .regex(/^[0-9+\s()-]+$/, { message: "Invalid phone number format" }),
  streetAddress: z
    .string()
    .min(5, { message: "Street address must be at least 5 characters" })
    .max(150, { message: "Address line too long" }),
  city: z
    .string()
    .min(2, { message: "City is required" }),
  state: z
    .string()
    .min(2, { message: "State/Province is required" }),
  postalCode: z
    .string()
    .regex(/^\d{5,6}$/, { message: "Postal code must be 5 or 6 digits" }),
  country: z
    .string()
    .default("India"),
});

// Step 2: Delivery Method Schema
export const deliveryStepSchema = z.object({
  shippingSpeed: z.enum(["standard", "express", "overnight"], {
    errorMap: () => ({ message: "Please select a valid delivery speed" }),
  }),
  specialInstructions: z
    .string()
    .max(250, { message: "Special instructions cannot exceed 250 characters" })
    .optional()
    .or(z.literal("")),
  giftPackaging: z.boolean().default(false),
});

// Step 3: Payment Method Schema
export const paymentStepSchema = z
  .object({
    paymentMethod: z.enum(["card", "upi", "cod"], {
      errorMap: () => ({ message: "Please select a payment method" }),
    }),
    // Card fields
    cardNumber: z.string().optional().or(z.literal("")),
    cardHolder: z.string().optional().or(z.literal("")),
    cardExpiry: z.string().optional().or(z.literal("")),
    cardCvv: z.string().optional().or(z.literal("")),
    // UPI field
    upiId: z.string().optional().or(z.literal("")),
  })
  .superRefine((data, ctx) => {
    if (data.paymentMethod === "card") {
      const cleanNum = (data.cardNumber || "").replace(/\s+/g, "");
      if (!/^\d{16}$/.test(cleanNum)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Credit card number must be 16 numeric digits",
          path: ["cardNumber"],
        });
      }
      if (!data.cardHolder || data.cardHolder.trim().length < 3) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Name on card is required",
          path: ["cardHolder"],
        });
      }
      if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(data.cardExpiry || "")) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Expiration date must be in MM/YY format",
          path: ["cardExpiry"],
        });
      }
      if (!/^\d{3,4}$/.test(data.cardCvv || "")) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "CVV security code must be 3 or 4 digits",
          path: ["cardCvv"],
        });
      }
    } else if (data.paymentMethod === "upi") {
      if (!data.upiId || !/^[\w.-]+@[\w.-]+$/.test(data.upiId.trim())) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Please enter a valid UPI ID (e.g. username@okhdfcbank)",
          path: ["upiId"],
        });
      }
    }
  });

// Step 4: Final Confirmation Schema
export const reviewStepSchema = z.object({
  termsAccepted: z.literal(true, {
    errorMap: () => ({ message: "You must accept the terms & conditions to place your order" }),
  }),
});

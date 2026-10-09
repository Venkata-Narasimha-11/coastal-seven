import { z } from 'zod';

export const checkoutSchema = z
  .object({
    // Step 1: Shipping Address
    fullName: z
      .string()
      .min(2, 'Full name must be at least 2 characters')
      .max(60, 'Full name cannot exceed 60 characters'),
    email: z
      .string()
      .email('Please enter a valid email address'),
    phone: z
      .string()
      .regex(/^[0-9]{10}$/, 'Phone number must be exactly 10 digits'),
    streetAddress: z
      .string()
      .min(5, 'Street address must be at least 5 characters'),
    city: z
      .string()
      .min(2, 'City must be at least 2 characters'),
    state: z
      .string()
      .min(2, 'State must be at least 2 characters'),
    postalCode: z
      .string()
      .regex(/^[0-9]{5,6}$/, 'Postal code must be 5 or 6 digits'),
    country: z
      .string()
      .default('India'),

    // Step 2: Shipping Method
    shippingSpeed: z
      .enum(['standard', 'express', 'overnight'])
      .default('standard'),

    // Step 3: Payment Details
    paymentMethod: z
      .enum(['credit_card', 'upi', 'cod']),
    cardNumber: z.string().optional(),
    cardHolder: z.string().optional(),
    cardExpiry: z.string().optional(),
    cardCvv: z.string().optional(),
    upiId: z.string().optional(),

    // Step 4: Terms
    termsAccepted: z
      .boolean()
      .refine((val) => val === true, {
        message: 'You must accept the terms and conditions to complete checkout',
      }),
  })
  .superRefine((data, ctx) => {
    if (data.paymentMethod === 'credit_card') {
      if (!data.cardNumber || !/^[0-9]{16}$/.test(data.cardNumber.replace(/\s+/g, ''))) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['cardNumber'],
          message: 'Valid 16-digit card number is required',
        });
      }
      if (!data.cardHolder || data.cardHolder.trim().length < 3) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['cardHolder'],
          message: 'Cardholder name is required',
        });
      }
      if (!data.cardExpiry || !/^(0[1-9]|1[0-2])\/?([0-9]{2})$/.test(data.cardExpiry)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['cardExpiry'],
          message: 'Expiry date must be in MM/YY format',
        });
      }
      if (!data.cardCvv || !/^[0-9]{3,4}$/.test(data.cardCvv)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['cardCvv'],
          message: 'CVV must be 3 or 4 digits',
        });
      }
    } else if (data.paymentMethod === 'upi') {
      if (!data.upiId || !/^[\w.-]+@[\w.-]+$/.test(data.upiId)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['upiId'],
          message: 'Valid UPI ID required (e.g., username@bank)',
        });
      }
    }
  });

export type CheckoutFormData = z.infer<typeof checkoutSchema>;

import { z } from 'zod';

export const productFormSchema = z.object({
  name: z
    .string()
    .min(2, 'Product name must be at least 2 characters')
    .max(100, 'Product name cannot exceed 100 characters'),
  description: z
    .string()
    .min(5, 'Description must be at least 5 characters')
    .max(1000, 'Description cannot exceed 1000 characters')
    .optional()
    .or(z.literal('')),
  price: z
    .coerce
    .number()
    .positive('Price must be greater than 0'),
  stock: z
    .coerce
    .number()
    .int('Stock must be an integer')
    .min(0, 'Stock cannot be negative'),
  category_id: z
    .coerce
    .number()
    .int()
    .positive('Please select a valid category'),
  image_url: z
    .string()
    .url('Image URL must be a valid URL')
    .optional()
    .or(z.literal('')),
});

export type ProductFormData = z.infer<typeof productFormSchema>;

import { z } from "zod";

export const specificationSchema = z.object({
  key: z.string().min(1, { message: "Attribute name required (e.g. RAM)" }),
  value: z.string().min(1, { message: "Value required (e.g. 16GB)" }),
});

export const productFormSchema = z.object({
  name: z
    .string()
    .min(3, { message: "Product name must be at least 3 characters" })
    .max(120, { message: "Product name cannot exceed 120 characters" }),
  description: z
    .string()
    .min(10, { message: "Description must be at least 10 characters long" })
    .max(2000, { message: "Description cannot exceed 2000 characters" }),
  price: z.coerce
    .number({ invalid_type_error: "Price must be a valid number" })
    .positive({ message: "Price must be greater than $0.00" })
    .max(1000000, { message: "Price cannot exceed $1,000,000" }),
  stock: z.coerce
    .number({ invalid_type_error: "Stock must be an integer" })
    .int({ message: "Stock must be a whole number" })
    .min(0, { message: "Stock cannot be negative" })
    .max(100000, { message: "Stock cannot exceed 100,000 units" }),
  category_id: z.coerce
    .number({ invalid_type_error: "Please select a category" })
    .int()
    .positive({ message: "Please select a category" }),
  is_active: z.boolean().default(true),
  // Dynamic fields via useFieldArray
  specs: z.array(specificationSchema).default([]),
  // Dynamic tag array
  tags: z.string().optional().default(""),
});

export const categoryFormSchema = z.object({
  name: z
    .string()
    .min(2, { message: "Category name must be at least 2 characters" })
    .max(50, { message: "Category name cannot exceed 50 characters" }),
  description: z
    .string()
    .max(300, { message: "Description cannot exceed 300 characters" })
    .optional()
    .or(z.literal("")),
});

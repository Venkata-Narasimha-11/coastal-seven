/**
 * API Type Definitions matching FastAPI Pydantic Models.
 * Provides strict type-safety between the Python backend and React frontend.
 */

export type UserRole = 'customer' | 'admin';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  created_at: string;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  price: number;
  stock: number;
  category_id: number;
  image_url?: string | null;
  thumbnail_url?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  category?: Category | null;
}

export interface ProductListResponse {
  items: Product[];
  total: int_or_number;
  page: number;
  size: number;
}

type int_or_number = number;

export interface CartItem {
  product_id: number;
  product_name: string;
  unit_price: number;
  quantity: number;
  subtotal: number;
  thumbnail_url?: string | null;
  available_stock: number;
}

export interface CartResponse {
  items: CartItem[];
  total_items: number;
  total_amount: number;
}

export interface OrderItem {
  id: number;
  product_id: number;
  product_name: string;
  unit_price: number;
  quantity: number;
  subtotal: number;
}

export type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';

export interface Order {
  id: number;
  user_id: number;
  status: OrderStatus;
  total_amount: number;
  shipping_address: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface ProductCreate {
  name: string;
  description?: string;
  price: number;
  stock: number;
  category_id: number;
  image_url?: string;
  thumbnail_url?: string;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  price?: number;
  stock?: number;
  category_id?: number;
  image_url?: string;
  thumbnail_url?: string;
  is_active?: boolean;
}

export interface OrderCreate {
  shipping_address: string;
}

export interface OrderStatusUpdate {
  status: OrderStatus;
}

/**
 * Generic API Response wrapper.
 * Demonstrates TypeScript Generics for unified API contracts.
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

/**
 * Generic Paginated Response wrapper.
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Structured API Error details.
 */
export interface ApiError {
  detail: string | Array<{ loc: (string | number)[]; msg: string; type: string }>;
  status?: number;
}


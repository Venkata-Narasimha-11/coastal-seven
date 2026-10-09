import { User, Product } from './api';

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  setUser: (user: User) => void;
}

export interface CartStoreItem {
  product: Product;
  quantity: number;
}

export interface CartState {
  items: CartStoreItem[];
  coupon: string | null;
  discountPercent: number;
  addItem: (product: Product, quantity?: number) => void;
  removeItem: (productId: number) => void;
  updateQuantity: (productId: number, quantity: number) => void;
  clearCart: () => void;
  applyCoupon: (code: string) => { success: boolean; message: string };
  removeCoupon: () => void;
  getTotalItems: () => number;
  getSubtotal: () => number;
  getDiscountAmount: () => number;
  getShippingCost: () => number;
  getTaxAmount: () => number;
  getTotalPrice: () => number;
  getGrandTotal: () => number;
}


export interface UIState {
  isMockNetworkDown: boolean;
  mockLatencyMs: number;
  setMockNetworkDown: (down: boolean) => void;
  setMockLatencyMs: (ms: number) => void;
}

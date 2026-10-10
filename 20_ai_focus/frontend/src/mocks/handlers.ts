import { http, HttpResponse } from 'msw';
import { Product, Category, User, CartResponse, Order } from '../types/api';

export const mockCategories: Category[] = [
  { id: 1, name: 'Electronics', slug: 'electronics', created_at: '2026-01-01T00:00:00Z' },
  { id: 2, name: 'Audio', slug: 'audio', created_at: '2026-01-01T00:00:00Z' },
  { id: 3, name: 'Accessories', slug: 'accessories', created_at: '2026-01-01T00:00:00Z' },
];

export const mockProducts: Product[] = [
  {
    id: 1,
    name: 'Wireless Noise-Canceling Headphones',
    slug: 'wireless-noise-canceling-headphones',
    description: 'Premium over-ear headphones with active noise cancellation and 30-hour battery life.',
    price: 199.99,
    stock: 12,
    category_id: 2,
    image_url: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
    thumbnail_url: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=150',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    category: mockCategories[1],
  },
  {
    id: 2,
    name: 'Ergonomic Mechanical Keyboard',
    slug: 'ergonomic-mechanical-keyboard',
    description: 'Hot-swappable RGB mechanical keyboard with custom linear switches.',
    price: 129.5,
    stock: 5,
    category_id: 1,
    image_url: 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500',
    thumbnail_url: 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=150',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    category: mockCategories[0],
  },
  {
    id: 3,
    name: 'Ultra-Fast USB-C GaN Charger 65W',
    slug: 'usb-c-gan-charger-65w',
    description: 'Compact high-efficiency GaN charger supporting laptop and phone fast charging.',
    price: 39.99,
    stock: 0, // Out of stock for testing
    category_id: 3,
    image_url: 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500',
    thumbnail_url: 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=150',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    category: mockCategories[2],
  },
  {
    id: 4,
    name: '4K Ultra-Wide Curved Monitor 34"',
    slug: '4k-ultrawide-curved-monitor',
    description: 'Immersive curved gaming and productivity monitor with 144Hz refresh rate.',
    price: 499.0,
    stock: 7,
    category_id: 1,
    image_url: 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500',
    thumbnail_url: 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=150',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    category: mockCategories[0],
  },
];

export const mockUser: User = {
  id: 1,
  username: 'admin',
  email: 'admin@example.com',
  full_name: 'Administrator',
  role: 'admin',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

export const mockCustomerUser: User = {
  id: 2,
  username: 'customer1',
  email: 'customer1@example.com',
  full_name: 'John Customer',
  role: 'customer',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

let activeMockUser: User = mockUser;

export const mockOrders: Order[] = [
  {
    id: 101,
    user_id: 1,
    status: 'shipped',
    total_amount: 399.98,
    shipping_address: 'John Doe, 42 MG Road, Bengaluru, Karnataka - 560034, India. Phone: 9876543210.',
    created_at: '2026-03-15T10:30:00Z',
    updated_at: '2026-03-16T14:20:00Z',
    items: [
      {
        id: 1,
        product_id: 1,
        product_name: 'Wireless Noise-Canceling Headphones',
        unit_price: 199.99,
        quantity: 2,
        subtotal: 399.98,
      },
    ],
  },
  {
    id: 102,
    user_id: 1,
    status: 'pending',
    total_amount: 129.5,
    shipping_address: 'Jane Smith, 12 Park Avenue, Mumbai, Maharashtra - 400001, India. Phone: 9123456789.',
    created_at: '2026-03-20T08:15:00Z',
    updated_at: '2026-03-20T08:15:00Z',
    items: [
      {
        id: 2,
        product_id: 2,
        product_name: 'Ergonomic Mechanical Keyboard',
        unit_price: 129.5,
        quantity: 1,
        subtotal: 129.5,
      },
    ],
  },
];


export const handlers = [
  // GET /api/v1/products/
  http.get('*/api/v1/products/', ({ request }) => {
    const url = new URL(request.url);
    const search = url.searchParams.get('search')?.toLowerCase() || '';
    const categoryId = url.searchParams.get('category_id');

    let filtered = mockProducts;

    if (search) {
      filtered = filtered.filter(
        (p) =>
          p.name.toLowerCase().includes(search) ||
          p.description?.toLowerCase().includes(search)
      );
    }

    if (categoryId) {
      const catIdNum = Number(categoryId);
      filtered = filtered.filter((p) => p.category_id === catIdNum);
    }

    return HttpResponse.json({
      items: filtered,
      total: filtered.length,
      page: 1,
      size: 20,
    });
  }),

  // GET /api/v1/products/categories
  http.get('*/api/v1/products/categories', () => {
    return HttpResponse.json(mockCategories);
  }),

  // GET /api/v1/products/:id
  http.get('*/api/v1/products/:id', ({ params }) => {
    const id = Number(params.id);
    const product = mockProducts.find((p) => p.id === id);

    if (!product) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Product not found' }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(product);
  }),

  // POST /api/v1/auth/login
  http.post('*/api/v1/auth/login', async ({ request }) => {
    const body = (await request.json()) as any;

    if (
      body.username === 'admin' &&
      (body.password === 'secret123' || body.password === 'AdminPassword123!')
    ) {
      activeMockUser = mockUser;
      return HttpResponse.json({
        access_token: 'mock-jwt-token-xyz-12345',
        token_type: 'bearer',
      });
    }

    if (
      (body.username === 'customer1' || body.username === 'customer') &&
      (body.password === 'SecretPassword123!' || body.password === 'secret123')
    ) {
      activeMockUser = mockCustomerUser;
      return HttpResponse.json({
        access_token: 'mock-jwt-token-customer-999',
        token_type: 'bearer',
      });
    }

    return new HttpResponse(
      JSON.stringify({ detail: 'Incorrect username or password' }),
      { status: 401, headers: { 'Content-Type': 'application/json' } }
    );
  }),

  // GET /api/v1/auth/me
  http.get('*/api/v1/auth/me', ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new HttpResponse(
        JSON.stringify({ detail: 'Not authenticated' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return HttpResponse.json(activeMockUser);
  }),

  // POST /api/v1/auth/register
  http.post('*/api/v1/auth/register', async ({ request }) => {
    const body = (await request.json()) as any;
    return HttpResponse.json({
      id: 99,
      username: body.username,
      email: body.email,
      role: 'customer',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  }),

  // GET /api/v1/cart/
  http.get('*/api/v1/cart/', () => {
    const mockCart: CartResponse = {
      items: [
        {
          product_id: 1,
          product_name: mockProducts[0].name,
          unit_price: mockProducts[0].price,
          quantity: 2,
          subtotal: mockProducts[0].price * 2,
          available_stock: mockProducts[0].stock,
        },
      ],
      total_items: 2,
      total_amount: mockProducts[0].price * 2,
    };
    return HttpResponse.json(mockCart);
  }),

  // DELETE /api/v1/cart
  http.delete('*/api/v1/cart*', () => {
    return new HttpResponse(null, { status: 204 });
  }),

  // POST /api/v1/cart/items
  http.post('*/api/v1/cart/items', async () => {
    return HttpResponse.json({
      items: [],
      total_items: 1,
      total_amount: 100,
    });
  }),

  // GET /api/v1/orders
  http.get('*/api/v1/orders', () => {
    return HttpResponse.json(mockOrders);
  }),

  // GET /api/v1/orders/:id
  http.get('*/api/v1/orders/:id', ({ params }) => {
    const id = Number(params.id);
    const order = mockOrders.find((o) => o.id === id);
    if (!order) {
      return new HttpResponse(JSON.stringify({ detail: 'Order not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return HttpResponse.json(order);
  }),

  // POST /api/v1/orders/checkout
  http.post('*/api/v1/orders/checkout', async ({ request }) => {
    const body = (await request.json()) as any;
    const newOrder: Order = {
      id: Math.floor(Math.random() * 900) + 100,
      user_id: 1,
      status: 'pending',
      total_amount: 199.99,
      shipping_address: body.shipping_address || 'Default Address',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      items: [
        {
          id: 1,
          product_id: 1,
          product_name: 'Wireless Noise-Canceling Headphones',
          unit_price: 199.99,
          quantity: 1,
          subtotal: 199.99,
        },
      ],
    };
    mockOrders.unshift(newOrder);
    return HttpResponse.json(newOrder, { status: 201 });
  }),

  // PUT /api/v1/orders/:id/status
  http.put('*/api/v1/orders/:id/status', async ({ params, request }) => {
    const id = Number(params.id);
    const body = (await request.json()) as any;
    const order = mockOrders.find((o) => o.id === id);
    if (!order) {
      return new HttpResponse(JSON.stringify({ detail: 'Order not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    order.status = body.status;
    order.updated_at = new Date().toISOString();
    return HttpResponse.json(order);
  }),

  // POST /api/v1/products/
  http.post('*/api/v1/products/', async ({ request }) => {
    const body = (await request.json()) as any;
    const created: Product = {
      id: mockProducts.length + 1,
      name: body.name,
      slug: body.name.toLowerCase().replace(/\s+/g, '-'),
      description: body.description || '',
      price: Number(body.price),
      stock: Number(body.stock),
      category_id: Number(body.category_id),
      image_url: body.image_url || null,
      thumbnail_url: body.thumbnail_url || null,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      category: mockCategories.find((c) => c.id === Number(body.category_id)) || mockCategories[0],
    };
    mockProducts.push(created);
    return HttpResponse.json(created, { status: 201 });
  }),

  // PUT /api/v1/products/:id
  http.put('*/api/v1/products/:id', async ({ params, request }) => {
    const id = Number(params.id);
    const body = (await request.json()) as any;
    const index = mockProducts.findIndex((p) => p.id === id);
    if (index === -1) {
      return new HttpResponse(JSON.stringify({ detail: 'Product not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    mockProducts[index] = {
      ...mockProducts[index],
      ...body,
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(mockProducts[index]);
  }),

  // DELETE /api/v1/products/:id
  http.delete('*/api/v1/products/:id', ({ params }) => {
    const id = Number(params.id);
    const index = mockProducts.findIndex((p) => p.id === id);
    if (index !== -1) {
      mockProducts.splice(index, 1);
    }
    return new HttpResponse(null, { status: 204 });
  }),
];


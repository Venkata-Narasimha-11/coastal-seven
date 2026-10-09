import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Package,
  ShoppingCart,
  TrendingUp,
  AlertTriangle,
  Plus,
  Edit,
  Trash2,
  RotateCcw,
  Search,
  Filter,
  ShieldCheck,
  Cpu,
  Upload,
} from 'lucide-react';
import {
  useAdminProductsQuery,
  useCreateProductMutation,
  useUpdateProductMutation,
  useDeleteProductMutation,
  useAdminOrdersQuery,
  useAdminUpdateOrderStatusMutation,
} from '../hooks/useAdmin';
import { useCategoriesQuery } from '../hooks/useProducts';
import { productFormSchema, ProductFormData } from '../schemas/productFormSchema';
import { Product, OrderStatus } from '../types/api';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { BackgroundTasksPage } from './BackgroundTasksPage';

type AdminTab = 'products' | 'orders' | 'analytics' | 'tasks';

export const AdminPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get('tab') as AdminTab;
  const [activeTab, setActiveTab] = useState<AdminTab>(
    tabParam === 'tasks' || tabParam === 'orders' || tabParam === 'analytics' ? tabParam : 'products'
  );

  useEffect(() => {
    if (tabParam && ['products', 'orders', 'analytics', 'tasks'].includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);

  const handleTabChange = (tab: AdminTab) => {
    setActiveTab(tab);
    setSearchParams({ tab });
  };

  const [productSearch, setProductSearch] = useState('');
  const [orderStatusFilter, setOrderStatusFilter] = useState<string>('all');

  // Modals state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [deletingProductId, setDeletingProductId] = useState<number | null>(null);

  // Queries
  const {
    data: productsData,
    isLoading: isProductsLoading,
  } = useAdminProductsQuery();

  const {
    data: ordersData,
    isLoading: isOrdersLoading,
    refetch: refetchOrders,
  } = useAdminOrdersQuery();

  const { data: categories = [] } = useCategoriesQuery();

  // Mutations
  const createMutation = useCreateProductMutation();
  const updateMutation = useUpdateProductMutation();
  const deleteMutation = useDeleteProductMutation();
  const updateOrderStatusMutation = useAdminUpdateOrderStatusMutation();

  // Create Form
  const {
    register: registerCreate,
    handleSubmit: handleSubmitCreate,
    reset: resetCreate,
    formState: { errors: createErrors, isSubmitting: isCreating },
  } = useForm<ProductFormData>({
    resolver: zodResolver(productFormSchema),
    defaultValues: {
      name: '',
      description: '',
      price: 0,
      stock: 10,
      category_id: categories[0]?.id || 1,
      image_url: '',
    },
  });

  // Edit Form
  const {
    register: registerEdit,
    handleSubmit: handleSubmitEdit,
    reset: resetEdit,
    formState: { errors: editErrors, isSubmitting: isUpdating },
  } = useForm<ProductFormData>({
    resolver: zodResolver(productFormSchema),
  });

  const handleOpenEdit = (product: Product) => {
    setEditingProduct(product);
    resetEdit({
      name: product.name,
      description: product.description || '',
      price: product.price,
      stock: product.stock,
      category_id: product.category_id,
      image_url: product.image_url || '',
    });
  };

  const onSubmitCreate = async (data: ProductFormData) => {
    try {
      await createMutation.mutateAsync({
        name: data.name,
        description: data.description || undefined,
        price: data.price,
        stock: data.stock,
        category_id: data.category_id,
        image_url: data.image_url || undefined,
      });
      resetCreate();
      setIsCreateModalOpen(false);
    } catch (err) {
      console.error('Failed to create product:', err);
    }
  };

  const onSubmitEdit = async (data: ProductFormData) => {
    if (!editingProduct) return;
    try {
      await updateMutation.mutateAsync({
        id: editingProduct.id,
        data: {
          name: data.name,
          description: data.description || undefined,
          price: data.price,
          stock: data.stock,
          category_id: data.category_id,
          image_url: data.image_url || undefined,
        },
      });
      setEditingProduct(null);
    } catch (err) {
      console.error('Failed to update product:', err);
    }
  };

  const handleDeleteProduct = async (id: number) => {
    try {
      await deleteMutation.mutateAsync(id);
      setDeletingProductId(null);
    } catch (err) {
      console.error('Failed to delete product:', err);
    }
  };

  const handleStatusChange = async (orderId: number, status: OrderStatus) => {
    try {
      await updateOrderStatusMutation.mutateAsync({ orderId, status });
    } catch (err) {
      console.error('Failed to update order status:', err);
    }
  };

  // Filtered Products
  const productsList = productsData?.items || [];
  const filteredProducts = productsList.filter(
    (p) =>
      p.name.toLowerCase().includes(productSearch.toLowerCase()) ||
      p.category?.name?.toLowerCase().includes(productSearch.toLowerCase())
  );

  // Filtered Orders
  const ordersList = ordersData || [];
  const filteredOrders = ordersList.filter((o) => {
    if (orderStatusFilter === 'all') return true;
    return o.status === orderStatusFilter;
  });

  // Analytics Metrics
  const totalRevenue = ordersList.reduce((sum, o) => (o.status !== 'cancelled' ? sum + Number(o.total_amount || 0) : sum), 0);
  const totalOrdersCount = ordersList.length;
  const activeProductsCount = productsList.length;
  const lowStockProducts = productsList.filter((p) => p.stock < 5);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-purple-100 dark:bg-purple-900/40 text-purple-600">
              <ShieldCheck className="h-5 w-5" />
            </span>
            <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              Admin Control Hub
            </h1>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Centralized product catalog CRUD operations and real-time customer order management.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1.5 rounded-xl gap-1.5 shadow-inner">
          <button
            type="button"
            data-testid="admin-tab-products"
            onClick={() => handleTabChange('products')}
            className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'products'
                ? 'bg-blue-600 text-white shadow-md scale-[1.02]'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700/60'
            }`}
          >
            <Package className="h-4 w-4" />
            <span>Products ({productsList.length})</span>
          </button>
          <button
            type="button"
            data-testid="admin-tab-orders"
            onClick={() => handleTabChange('orders')}
            className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'orders'
                ? 'bg-blue-600 text-white shadow-md scale-[1.02]'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700/60'
            }`}
          >
            <ShoppingCart className="h-4 w-4" />
            <span>Orders ({ordersList.length})</span>
          </button>
          <button
            type="button"
            data-testid="admin-tab-analytics"
            onClick={() => handleTabChange('analytics')}
            className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'analytics'
                ? 'bg-blue-600 text-white shadow-md scale-[1.02]'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700/60'
            }`}
          >
            <TrendingUp className="h-4 w-4" />
            <span>Analytics & KPIs</span>
          </button>
          <button
            type="button"
            data-testid="admin-tab-tasks"
            onClick={() => handleTabChange('tasks')}
            className={`px-4 py-2.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'tasks'
                ? 'bg-purple-600 text-white shadow-md scale-[1.02]'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700/60'
            }`}
          >
            <Cpu className="h-4 w-4" />
            <span>Tasks & Bulk Import</span>
          </button>
        </div>
      </div>

      {/* TAB 1: PRODUCT MANAGEMENT */}
      {activeTab === 'products' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search products by name or category..."
                value={productSearch}
                onChange={(e) => setProductSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                data-testid="admin-bulk-import-btn"
                onClick={() => handleTabChange('tasks')}
                className="border-purple-300 dark:border-purple-700 text-purple-700 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-950/40"
              >
                <Upload className="h-4 w-4 mr-1.5" />
                Bulk Import CSV
              </Button>

              <Button
                variant="primary"
                size="sm"
                data-testid="add-product-btn"
                onClick={() => setIsCreateModalOpen(true)}
              >
                <Plus className="h-4 w-4 mr-1.5" />
                Add New Product
              </Button>
            </div>
          </div>

          {isProductsLoading ? (
            <div className="py-20 text-center">
              <LoadingSpinner size="lg" text="Loading product catalog..." />
            </div>
          ) : (
            <Card className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-600 dark:text-slate-300">
                  <thead className="bg-slate-50 dark:bg-slate-800/80 text-xs uppercase font-bold text-slate-400 border-b border-slate-100 dark:border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Product</th>
                      <th className="py-3 px-4">Category</th>
                      <th className="py-3 px-4">Price</th>
                      <th className="py-3 px-4">Stock</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {filteredProducts.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="py-12 text-center text-slate-400">
                          No products found matching "{productSearch}"
                        </td>
                      </tr>
                    ) : (
                      filteredProducts.map((product) => (
                        <tr
                          key={product.id}
                          className="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors"
                        >
                          <td className="py-3.5 px-4">
                            <div className="flex items-center gap-3">
                              <img
                                src={
                                  product.thumbnail_url ||
                                  product.image_url ||
                                  'https://via.placeholder.com/48'
                                }
                                alt={product.name}
                                className="h-10 w-10 rounded-lg object-cover bg-slate-100 dark:bg-slate-800 flex-shrink-0"
                              />
                              <div>
                                <p className="font-semibold text-slate-900 dark:text-white line-clamp-1">
                                  {product.name}
                                </p>
                                <p className="text-xs text-slate-400 font-mono">ID: #{product.id}</p>
                              </div>
                            </div>
                          </td>

                          <td className="py-3.5 px-4">
                            <span className="text-xs bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-md text-slate-700 dark:text-slate-300">
                              {product.category?.name || `Cat #${product.category_id}`}
                            </span>
                          </td>

                          <td className="py-3.5 px-4 font-bold text-slate-900 dark:text-white">
                            ₹{Number(product.price || 0).toFixed(2)}
                          </td>

                          <td className="py-3.5 px-4">
                            {product.stock === 0 ? (
                              <Badge variant="danger">Out of Stock</Badge>
                            ) : product.stock < 5 ? (
                              <Badge variant="warning">{product.stock} units left</Badge>
                            ) : (
                              <Badge variant="success">{product.stock} in stock</Badge>
                            )}
                          </td>

                          <td className="py-3.5 px-4 text-right">
                            <div className="flex items-center justify-end gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                data-testid={`edit-product-${product.id}`}
                                onClick={() => handleOpenEdit(product)}
                                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 dark:hover:bg-blue-950/40 text-xs px-2.5 py-1 gap-1 border-blue-200 dark:border-blue-800"
                              >
                                <Edit className="h-3.5 w-3.5" />
                                <span>Edit</span>
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                data-testid={`delete-product-${product.id}`}
                                onClick={() => setDeletingProductId(product.id)}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/40 text-xs px-2.5 py-1 gap-1 border-red-200 dark:border-red-800"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                                <span>Delete</span>
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* TAB 2: ORDER MANAGEMENT */}
      {activeTab === 'orders' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-slate-400" />
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Filter by Status:
              </span>
              <select
                value={orderStatusFilter}
                onChange={(e) => setOrderStatusFilter(e.target.value)}
                className="px-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Orders ({ordersList.length})</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="shipped">Shipped</option>
                <option value="delivered">Delivered</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <Button variant="outline" size="sm" onClick={() => refetchOrders()}>
              <RotateCcw className="h-4 w-4 mr-1.5" />
              Refresh Orders
            </Button>
          </div>

          {isOrdersLoading ? (
            <div className="py-20 text-center">
              <LoadingSpinner size="lg" text="Loading customer orders..." />
            </div>
          ) : (
            <Card className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-600 dark:text-slate-300">
                  <thead className="bg-slate-50 dark:bg-slate-800/80 text-xs uppercase font-bold text-slate-400 border-b border-slate-100 dark:border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Order ID</th>
                      <th className="py-3 px-4">Customer ID</th>
                      <th className="py-3 px-4">Date Placed</th>
                      <th className="py-3 px-4">Items</th>
                      <th className="py-3 px-4">Total</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4 text-right">Update Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {filteredOrders.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="py-12 text-center text-slate-400">
                          No orders found matching the selected filter.
                        </td>
                      </tr>
                    ) : (
                      filteredOrders.map((order) => (
                        <tr
                          key={order.id}
                          className="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors"
                        >
                          <td className="py-3.5 px-4 font-bold text-slate-900 dark:text-white font-mono">
                            #ORD-{order.id}
                          </td>
                          <td className="py-3.5 px-4 text-xs font-mono">
                            User #{order.user_id}
                          </td>
                          <td className="py-3.5 px-4 text-xs text-slate-500">
                            {new Date(order.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-3.5 px-4 text-xs">
                            {order.items?.length || 0} line item{order.items?.length !== 1 ? 's' : ''}
                          </td>
                          <td className="py-3.5 px-4 font-extrabold text-slate-900 dark:text-white">
                            ₹{Number(order.total_amount || 0).toFixed(2)}
                          </td>
                          <td className="py-3.5 px-4">
                            <Badge
                              variant={
                                order.status === 'delivered'
                                  ? 'success'
                                  : order.status === 'cancelled'
                                  ? 'danger'
                                  : order.status === 'pending'
                                  ? 'warning'
                                  : 'info'
                              }
                            >
                              {order.status.toUpperCase()}
                            </Badge>
                          </td>
                          <td className="py-3.5 px-4 text-right">
                            <select
                              value={order.status}
                              data-testid={`status-select-${order.id}`}
                              onChange={(e) =>
                                handleStatusChange(order.id, e.target.value as OrderStatus)
                              }
                              className="px-2.5 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 font-medium focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="pending">Pending</option>
                              <option value="processing">Processing</option>
                              <option value="shipped">Shipped</option>
                              <option value="delivered">Delivered</option>
                              <option value="cancelled">Cancelled</option>
                            </select>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* TAB 3: ANALYTICS & KPIS */}
      {activeTab === 'analytics' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="p-5 border-l-4 border-l-emerald-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Total Revenue
                  </p>
                  <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">
                    ₹{Number(totalRevenue || 0).toFixed(2)}
                  </h3>
                </div>
                <div className="h-10 w-10 rounded-xl bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 flex items-center justify-center">
                  <TrendingUp className="h-5 w-5" />
                </div>
              </div>
            </Card>

            <Card className="p-5 border-l-4 border-l-blue-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Total Orders
                  </p>
                  <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">
                    {totalOrdersCount}
                  </h3>
                </div>
                <div className="h-10 w-10 rounded-xl bg-blue-100 dark:bg-blue-950/40 text-blue-600 flex items-center justify-center">
                  <ShoppingCart className="h-5 w-5" />
                </div>
              </div>
            </Card>

            <Card className="p-5 border-l-4 border-l-purple-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Active Catalog
                  </p>
                  <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">
                    {activeProductsCount} Items
                  </h3>
                </div>
                <div className="h-10 w-10 rounded-xl bg-purple-100 dark:bg-purple-950/40 text-purple-600 flex items-center justify-center">
                  <Package className="h-5 w-5" />
                </div>
              </div>
            </Card>

            <Card className="p-5 border-l-4 border-l-amber-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Low Stock Alerts
                  </p>
                  <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-1">
                    {lowStockProducts.length}
                  </h3>
                </div>
                <div className="h-10 w-10 rounded-xl bg-amber-100 dark:bg-amber-950/40 text-amber-600 flex items-center justify-center">
                  <AlertTriangle className="h-5 w-5" />
                </div>
              </div>
            </Card>
          </div>

          {/* Low Stock Items Section */}
          <Card>
            <Card.Header>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                <Card.Title>Inventory Depletion Radar</Card.Title>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Products requiring immediate inventory replenishment.
              </p>
            </Card.Header>

            <Card.Content>
              {lowStockProducts.length === 0 ? (
                <div className="py-8 text-center text-slate-400 text-sm">
                  All items are well-stocked above inventory safety thresholds.
                </div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {lowStockProducts.map((p) => (
                    <div
                      key={p.id}
                      className="py-3 flex items-center justify-between gap-4 text-sm"
                    >
                      <div>
                        <p className="font-semibold text-slate-900 dark:text-white">{p.name}</p>
                        <p className="text-xs text-slate-400">Category: {p.category?.name || 'General'}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge variant={p.stock === 0 ? 'danger' : 'warning'}>
                          {p.stock === 0 ? 'Out of Stock' : `${p.stock} units left`}
                        </Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleOpenEdit(p)}
                          className="text-xs"
                        >
                          Restock
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card.Content>
          </Card>
        </div>
      )}

      {/* TAB 4: ASYNC TASKS & BULK OPERATIONS */}
      {activeTab === 'tasks' && (
        <div className="space-y-6">
          <BackgroundTasksPage isEmbedded={true} />
        </div>
      )}

      {/* CREATE PRODUCT MODAL */}
      {isCreateModalOpen && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto"
        >
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-1">
              Add New Product to Catalog
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-5">
              Validated using Zod productFormSchema and persisted via FastAPI.
            </p>

            <form onSubmit={handleSubmitCreate(onSubmitCreate)} className="space-y-4">
              <Input
                label="Product Title"
                placeholder="e.g. Ergonomic Keyboard"
                error={createErrors.name?.message}
                {...registerCreate('name')}
              />

              <Input
                label="Description"
                placeholder="Detailed specifications and key features..."
                error={createErrors.description?.message}
                {...registerCreate('description')}
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Price (₹)"
                  type="number"
                  step="0.01"
                  placeholder="99.99"
                  error={createErrors.price?.message}
                  {...registerCreate('price')}
                />
                <Input
                  label="Initial Stock Units"
                  type="number"
                  placeholder="15"
                  error={createErrors.stock?.message}
                  {...registerCreate('stock')}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Category
                </label>
                <select
                  {...registerCreate('category_id')}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
                {createErrors.category_id && (
                  <p className="text-xs text-red-500 mt-1">{createErrors.category_id.message}</p>
                )}
              </div>

              <Input
                label="Image URL"
                placeholder="https://images.unsplash.com/..."
                error={createErrors.image_url?.message}
                {...registerCreate('image_url')}
              />

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setIsCreateModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  loading={isCreating}
                  data-testid="save-new-product-btn"
                >
                  Save Product
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT PRODUCT MODAL */}
      {editingProduct && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto"
        >
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-1">
              Edit Product #{editingProduct.id}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-5">
              Update pricing, stock availability, or description.
            </p>

            <form onSubmit={handleSubmitEdit(onSubmitEdit)} className="space-y-4">
              <Input
                label="Product Title"
                placeholder="e.g. Ergonomic Keyboard"
                error={editErrors.name?.message}
                {...registerEdit('name')}
              />

              <Input
                label="Description"
                placeholder="Detailed specifications..."
                error={editErrors.description?.message}
                {...registerEdit('description')}
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Price (₹)"
                  type="number"
                  step="0.01"
                  placeholder="99.99"
                  error={editErrors.price?.message}
                  {...registerEdit('price')}
                />
                <Input
                  label="Stock Units"
                  type="number"
                  placeholder="15"
                  error={editErrors.stock?.message}
                  {...registerEdit('stock')}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Category
                </label>
                <select
                  {...registerEdit('category_id')}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
                {editErrors.category_id && (
                  <p className="text-xs text-red-500 mt-1">{editErrors.category_id.message}</p>
                )}
              </div>

              <Input
                label="Image URL"
                placeholder="https://..."
                error={editErrors.image_url?.message}
                {...registerEdit('image_url')}
              />

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setEditingProduct(null)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  loading={isUpdating}
                  data-testid="save-edit-product-btn"
                >
                  Update Product
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DELETE CONFIRMATION MODAL */}
      {deletingProductId && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4"
        >
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 text-center">
            <div className="h-12 w-12 rounded-full bg-red-100 dark:bg-red-950/50 text-red-600 flex items-center justify-center mx-auto mb-4">
              <Trash2 className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Confirm Delete Product
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-6">
              Are you sure you want to permanently remove product #{deletingProductId} from the catalog? This action cannot be undone.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setDeletingProductId(null)}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                size="sm"
                data-testid="confirm-delete-btn"
                onClick={() => handleDeleteProduct(deletingProductId)}
              >
                Delete Product
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPage;

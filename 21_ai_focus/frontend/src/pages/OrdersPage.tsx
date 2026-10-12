import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Package,
  Clock,
  MapPin,
  CheckCircle,
  RotateCcw,
  ShoppingBag,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Receipt,
  Eye,
} from 'lucide-react';
import { useOrdersQuery } from '../hooks/useOrders';
import { Order, OrderStatus } from '../types/api';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';

const getStatusBadgeVariant = (status: OrderStatus) => {
  switch (status) {
    case 'delivered':
      return 'success';
    case 'shipped':
    case 'processing':
      return 'info';
    case 'cancelled':
      return 'danger';
    case 'pending':
    default:
      return 'warning';
  }
};

const getStatusStepIndex = (status: OrderStatus) => {
  switch (status) {
    case 'pending':
      return 1;
    case 'processing':
      return 2;
    case 'shipped':
      return 3;
    case 'delivered':
      return 4;
    case 'cancelled':
      return 0;
    default:
      return 1;
  }
};

export const OrdersPage: React.FC = () => {
  const { data: orders, isLoading, isError, error, refetch } = useOrdersQuery();
  const [expandedOrderId, setExpandedOrderId] = useState<number | null>(null);

  const toggleExpand = (id: number) => {
    setExpandedOrderId((prev) => (prev === id ? null : id));
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto py-20 px-4 text-center">
        <LoadingSpinner size="lg" text="Retrieving your past orders..." />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-3xl mx-auto py-16 px-4">
        <div
          role="alert"
          className="p-6 rounded-2xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-center"
        >
          <AlertCircle className="h-10 w-10 text-red-500 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-red-900 dark:text-red-200 mb-1">
            Unable to Load Order History
          </h2>
          <p className="text-sm text-red-700 dark:text-red-300 mb-4">
            {error?.message || 'A network error occurred while fetching your orders.'}
          </p>
          <Button variant="primary" size="sm" onClick={() => refetch()}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (!orders || orders.length === 0) {
    return (
      <div className="max-w-2xl mx-auto py-16 px-4 text-center">
        <div className="h-20 w-20 bg-slate-100 dark:bg-slate-800 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-6">
          <Package className="h-10 w-10" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
          No Orders Placed Yet
        </h2>
        <p className="text-slate-600 dark:text-slate-400 mb-8 max-w-md mx-auto">
          You have not made any purchases yet. Explore our verified products catalog to place your first order.
        </p>
        <Link to="/">
          <Button variant="primary" size="lg">
            <ShoppingBag className="h-4 w-4 mr-2" />
            Explore Products
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Order History & Tracking
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Track real-time shipment statuses and review itemized invoice receipts.
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RotateCcw className="h-4 w-4 mr-1.5" />
          Refresh Orders
        </Button>
      </div>

      {/* Orders List */}
      <div className="space-y-6">
        {orders.map((order: Order) => {
          const isExpanded = expandedOrderId === order.id;
          const stepIndex = getStatusStepIndex(order.status);
          const orderDate = new Date(order.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          });

          return (
            <Card key={order.id} className="overflow-hidden shadow-sm hover:shadow-md transition-shadow">
              {/* Order Card Header */}
              <div className="p-5 sm:p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-blue-100 dark:bg-blue-900/40 text-blue-600 flex items-center justify-center font-bold">
                    <Receipt className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-base text-slate-900 dark:text-white">
                        Order #{order.id}
                      </span>
                      <Badge variant={getStatusBadgeVariant(order.status)}>
                        {order.status.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      <Clock className="h-3.5 w-3.5" />
                      <span>Placed on {orderDate}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-4">
                  <div className="text-right">
                    <p className="text-xs text-slate-500 dark:text-slate-400">Total Amount</p>
                    <p className="text-lg font-extrabold text-slate-900 dark:text-white">
                      ₹{Number(order.total_amount || 0).toFixed(2)}
                    </p>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleExpand(order.id)}
                    className="text-xs"
                    aria-label={`Toggle details for order ${order.id}`}
                  >
                    {isExpanded ? (
                      <>
                        <span>Hide Details</span>
                        <ChevronUp className="h-4 w-4 ml-1" />
                      </>
                    ) : (
                      <>
                        <span>View Details</span>
                        <ChevronDown className="h-4 w-4 ml-1" />
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {/* Status Stepper (if not cancelled) */}
              {order.status !== 'cancelled' ? (
                <div className="px-6 py-4 bg-white dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800">
                  <div className="flex items-center justify-between relative max-w-xl mx-auto">
                    {/* Connecting line */}
                    <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-slate-200 dark:bg-slate-800 -translate-y-1/2 z-0" />
                    <div
                      className="absolute top-1/2 left-0 h-0.5 bg-blue-600 -translate-y-1/2 z-0 transition-all duration-500"
                      style={{
                        width: `${((stepIndex - 1) / 3) * 100}%`,
                      }}
                    />

                    {[
                      { step: 1, label: 'Placed' },
                      { step: 2, label: 'Processing' },
                      { step: 3, label: 'Shipped' },
                      { step: 4, label: 'Delivered' },
                    ].map((s) => {
                      const isComplete = stepIndex >= s.step;
                      const isCurrent = stepIndex === s.step;

                      return (
                        <div key={s.step} className="relative z-10 flex flex-col items-center">
                          <div
                            className={`h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                              isComplete
                                ? 'bg-blue-600 text-white'
                                : 'bg-slate-200 dark:bg-slate-800 text-slate-500'
                            } ${isCurrent ? 'ring-4 ring-blue-100 dark:ring-blue-900/40' : ''}`}
                          >
                            {isComplete ? <CheckCircle className="h-4 w-4" /> : s.step}
                          </div>
                          <span
                            className={`text-xs mt-1 font-medium ${
                              isComplete
                                ? 'text-blue-600 dark:text-blue-400'
                                : 'text-slate-400 dark:text-slate-500'
                            }`}
                          >
                            {s.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="px-6 py-3 bg-red-50/50 dark:bg-red-950/20 border-b border-red-100 dark:border-red-900/30 text-xs text-red-600 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  <span>This order has been cancelled and refunded to original payment method.</span>
                </div>
              )}

              {/* Order Items & Shipping Breakdown */}
              <div className="p-5 sm:p-6 bg-white dark:bg-slate-900">
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Order Items ({order.items?.length || 0})
                  </h4>

                  <div className="divide-y divide-slate-100 dark:divide-slate-800">
                    {order.items?.map((item) => (
                      <div
                        key={item.id}
                        className="py-3 flex items-center justify-between gap-4 text-sm"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-500 font-medium text-xs">
                            <Package className="h-5 w-5 text-slate-400" />
                          </div>
                          <div>
                            <p className="font-semibold text-slate-900 dark:text-white text-sm">
                              {item.product_name}
                            </p>
                            <p className="text-xs text-slate-500">
                              Unit Price: ₹{Number(item.unit_price || 0).toFixed(2)} × Qty: {item.quantity}
                            </p>
                          </div>
                        </div>

                        <span className="font-bold text-sm text-slate-900 dark:text-white">
                          ₹{Number(item.subtotal || 0).toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Expanded Details Section */}
                {isExpanded && (
                  <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800 space-y-4">
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
                        <MapPin className="h-3.5 w-3.5" />
                        Shipping Address
                      </h4>
                      <p className="text-xs text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/60 p-3 rounded-lg border border-slate-100 dark:border-slate-800 font-mono">
                        {order.shipping_address}
                      </p>
                    </div>

                    <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
                      <span>Order Reference: ORD-{order.id}-{new Date(order.created_at).getTime()}</span>
                      <Link to={`/orders/${order.id}`}>
                        <Button variant="outline" size="sm" className="text-xs">
                          <Eye className="h-3.5 w-3.5 mr-1.5" />
                          Live Tracking View
                        </Button>
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default OrdersPage;

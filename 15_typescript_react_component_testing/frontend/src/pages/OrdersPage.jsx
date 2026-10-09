import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Package, ArrowRight, Clock } from 'lucide-react';
import { orderService } from '../services/orderService';
import LoadingSpinner from '../components/common/LoadingSpinner';

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'delivered':
      return 'badge-success';
    case 'shipped':
    case 'processing':
    case 'confirmed':
      return 'badge-primary';
    case 'cancelled':
      return 'badge-danger';
    default:
      return 'badge-warning';
  }
};

export const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const data = await orderService.getOrders();
        setOrders(data);
      } catch (err) {
        console.error('Failed to fetch orders:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '6rem 0', textAlign: 'center' }}>
        <LoadingSpinner size={36} text="Loading your order history..." />
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="card" style={{ maxWidth: '500px', margin: '4rem auto', textAlign: 'center', padding: '3.5rem 2rem' }}>
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: 'var(--bg-elevated)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem auto',
          }}
        >
          <Package size={28} color="var(--text-muted)" />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          No Orders Yet
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          You have not placed any orders. Start browsing products to place your first order.
        </p>
        <Link to="/" className="btn btn-primary">
          Explore Products
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.85rem', fontWeight: 800, marginBottom: '2rem' }}>Order History</h1>

      <div className="flex flex-col gap-4">
        {orders.map((order) => (
          <div
            key={order.id}
            className="card flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            style={{ padding: '1.5rem' }}
          >
            <div>
              <div className="flex items-center gap-3" style={{ marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>Order #{order.id}</span>
                <span className={`badge ${getStatusBadgeClass(order.status)}`}>
                  {order.status.toUpperCase()}
                </span>
              </div>
              <p className="flex items-center gap-1" style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <Clock size={14} /> {new Date(order.created_at).toLocaleDateString()} at{' '}
                {new Date(order.created_at).toLocaleTimeString()}
              </p>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                {order.items?.length || 0} line items • Delivery to: {order.shipping_address}
              </p>
            </div>

            <div className="flex items-center justify-between sm:justify-end gap-6">
              <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--primary)' }}>
                ${Number(order.total_amount).toFixed(2)}
              </span>
              <Link
                to={`/orders/${order.id}`}
                className="btn btn-secondary flex items-center gap-1"
                style={{ padding: '0.5rem 0.9rem', fontSize: '0.85rem' }}
              >
                <span>Track Live</span>
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrdersPage;

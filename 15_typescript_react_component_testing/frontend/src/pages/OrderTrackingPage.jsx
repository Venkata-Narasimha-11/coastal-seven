import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  PackageCheck,
  Radio,
  Clock,
  CheckCircle2,
  Truck,
  Box,
  MapPin,
  ArrowLeft,
} from 'lucide-react';
import { orderService } from '../services/orderService';
import { useOrderWebSocket } from '../hooks/useOrderWebSocket';
import LoadingSpinner from '../components/common/LoadingSpinner';

const STATUS_STEPS = [
  { key: 'pending', label: 'Order Placed', icon: Clock },
  { key: 'confirmed', label: 'Payment Confirmed', icon: CheckCircle2 },
  { key: 'processing', label: 'Packaging', icon: Box },
  { key: 'shipped', label: 'Out for Delivery', icon: Truck },
  { key: 'delivered', label: 'Delivered', icon: PackageCheck },
];

export const OrderTrackingPage = () => {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState('');

  // Initial order fetch from REST API
  useEffect(() => {
    const fetchOrder = async () => {
      setLoading(true);
      try {
        const data = await orderService.getOrderById(id);
        setOrder(data);
      } catch (err) {
        console.error('Failed to load order:', err);
        setFetchError('Order not found or permission denied.');
      } finally {
        setLoading(false);
      }
    };
    fetchOrder();
  }, [id]);

  // Connect to live WebSocket for real-time lifecycle broadcasts
  const { currentStatus, events, isConnected } = useOrderWebSocket(id, order?.status);

  // Active status is either latest WebSocket status or REST order status
  const effectiveStatus = currentStatus || order?.status || 'pending';

  const getStepIndex = (status) => {
    const idx = STATUS_STEPS.findIndex((s) => s.key === status);
    return idx >= 0 ? idx : 0;
  };

  const currentStepIdx = getStepIndex(effectiveStatus);

  if (loading) {
    return (
      <div style={{ padding: '6rem 0', textAlign: 'center' }}>
        <LoadingSpinner size={36} text="Connecting to Order Tracking..." />
      </div>
    );
  }

  if (fetchError || !order) {
    return (
      <div className="card" style={{ maxWidth: '500px', margin: '3rem auto', textAlign: 'center' }}>
        <p style={{ color: 'var(--danger)', marginBottom: '1.5rem', fontWeight: 600 }}>{fetchError}</p>
        <Link to="/" className="btn btn-secondary">
          <ArrowLeft size={16} /> Back to Catalog
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '850px', margin: '0 auto' }}>
      <Link to="/orders" className="flex items-center gap-1" style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', display: 'inline-flex' }}>
        <ArrowLeft size={16} /> View All Orders
      </Link>

      <div className="card" style={{ padding: '2.5rem', marginBottom: '2rem' }}>
        {/* Header with Live Indicator */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4" style={{ marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Order #{order.id}</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Placed on {new Date(order.created_at).toLocaleString()}
            </p>
          </div>

          {/* WebSocket Status Indicator */}
          <div
            className="flex items-center gap-2"
            style={{
              backgroundColor: isConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              color: isConnected ? 'var(--success)' : 'var(--danger)',
              padding: '0.4rem 0.85rem',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.8rem',
              fontWeight: 600,
              width: 'fit-content',
            }}
          >
            <Radio size={14} className={isConnected ? 'animate-pulse' : ''} />
            <span>{isConnected ? 'Live WebSocket Connected' : 'Connecting to live updates...'}</span>
          </div>
        </div>

        {/* Visual Progress Stepper */}
        <div style={{ margin: '3rem 0' }}>
          <div className="flex flex-col sm:flex-row justify-between gap-6" style={{ position: 'relative' }}>
            {STATUS_STEPS.map((step, idx) => {
              const Icon = step.icon;
              const isCompleted = idx <= currentStepIdx;
              const isCurrent = idx === currentStepIdx;

              return (
                <div key={step.key} className="flex sm:flex-col items-center gap-3 sm:gap-2" style={{ flex: 1, textAlign: 'center' }}>
                  <div
                    style={{
                      width: '44px',
                      height: '44px',
                      borderRadius: '50%',
                      backgroundColor: isCompleted ? 'var(--primary)' : 'var(--bg-elevated)',
                      color: isCompleted ? 'white' : 'var(--text-muted)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.3s ease',
                      boxShadow: isCurrent ? '0 0 15px rgba(99, 102, 241, 0.5)' : 'none',
                    }}
                  >
                    <Icon size={20} />
                  </div>
                  <div>
                    <p style={{ fontSize: '0.875rem', fontWeight: isCompleted ? 700 : 500, color: isCompleted ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                      {step.label}
                    </p>
                    {isCurrent && (
                      <span className="badge badge-primary" style={{ marginTop: '0.25rem', fontSize: '0.7rem' }}>
                        Current Status
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Order Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '2rem' }}>
          {/* Shipping Address */}
          <div>
            <h4 className="flex items-center gap-2" style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              <MapPin size={16} /> Delivery Address
            </h4>
            <p style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{order.shipping_address}</p>
          </div>

          {/* Amount Paid */}
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Total Amount
            </h4>
            <p style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--primary)' }}>
              ${Number(order.total_amount).toFixed(2)}
            </p>
          </div>
        </div>

        {/* Itemized Line Items */}
        <div style={{ marginTop: '2rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Purchased Items</h4>
          <div className="flex flex-col gap-2">
            {order.items?.map((item) => (
              <div
                key={item.product_id}
                className="flex justify-between items-center"
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: 'var(--bg-elevated)',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.9rem',
                }}
              >
                <span>
                  <strong>{item.quantity}x</strong> {item.product_name}
                </span>
                <span style={{ fontWeight: 600 }}>${Number(item.subtotal).toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Live WebSocket Event Stream Log */}
        {events.length > 0 && (
          <div style={{ marginTop: '2rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
              Real-time Event Stream (WebSocket)
            </h4>
            <div className="flex flex-col gap-1">
              {events.map((ev, i) => (
                <div key={i} style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  [{ev.receivedAt}] {ev.event}: {ev.message || `Status updated to ${ev.status}`}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderTrackingPage;

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Bell, CheckCheck, PackageCheck, AlertTriangle, X, Tag, Sparkles, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useAuth } from '../../hooks/useAuth';

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: 'order' | 'offer' | 'alert' | 'system';
  timestamp: string;
  read: boolean;
  link?: string;
}

const INITIAL_NOTIFICATIONS: NotificationItem[] = [
  {
    id: 'notif-offer-1',
    title: '🎉 SIVORA Luxe Fest: Extra 10% OFF',
    message: 'Apply coupon code SAVE10 at checkout on orders above $10,000.',
    type: 'offer',
    timestamp: 'Just now',
    read: false,
    link: '/',
  },
  {
    id: 'notif-order-1',
    title: '📦 White-Glove Luxury Delivery',
    message: 'Complimentary insured shipping active on all couture orders.',
    type: 'order',
    timestamp: '1h ago',
    read: false,
    link: '/orders',
  },
  {
    id: 'notif-vip-1',
    title: '💎 Fine Jewellery Restocked',
    message: 'Heritage Kundan sets & 18K Diamond Tennis Bracelets available.',
    type: 'system',
    timestamp: 'Today',
    read: true,
    link: '/wishlist',
  },
];

export const NotificationBell: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAdmin } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'orders' | 'offers'>('all');
  const [notifications, setNotifications] = useState<NotificationItem[]>(INITIAL_NOTIFICATIONS);

  const dropdownRef = useRef<HTMLDivElement>(null);
  const bellButtonRef = useRef<HTMLButtonElement>(null);

  // Close dropdown on route transition
  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname]);

  // Global document click listener (capture phase) to reliably close on outside click anywhere on the page
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      const target = event.target as Node;
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(target) &&
        bellButtonRef.current &&
        !bellButtonRef.current.contains(target)
      ) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    // Auto-close after 8 seconds of inactivity if user doesn't interact
    const autoCloseTimer = setTimeout(() => {
      setIsOpen(false);
    }, 8000);

    document.addEventListener('mousedown', handleClickOutside, true);
    document.addEventListener('touchstart', handleClickOutside, true);
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      clearTimeout(autoCloseTimer);
      document.removeEventListener('mousedown', handleClickOutside, true);
      document.removeEventListener('touchstart', handleClickOutside, true);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  // Connect to appropriate WebSocket channel based on user role
  const wsBase = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws';
  const wsUrl = isAdmin ? `${wsBase}/admin` : user ? `${wsBase}/orders/${user.id || 1}` : null;

  const { isConnected, lastMessage } = useWebSocket(wsUrl, {
    autoReconnect: true,
    maxRetries: 10,
    baseDelay: 1000,
  });

  // Handle incoming real-time notifications with auto-dismissing toasts (3.5s)
  useEffect(() => {
    if (!lastMessage) return;

    let newNotification: NotificationItem | null = null;
    const timeStr = 'Just now';

    if (lastMessage.event === 'NEW_ORDER') {
      newNotification = {
        id: `notif-${Date.now()}`,
        title: `New Order #${lastMessage.order_id}`,
        message: `Placed by ${lastMessage.customer || 'Customer'} • $${lastMessage.total || ''}`,
        type: 'order',
        timestamp: timeStr,
        read: false,
        link: '/orders',
      };
      toast.success(`🛒 New Order #${lastMessage.order_id} received!`, { duration: 3500 });
    } else if (lastMessage.event === 'STATUS_UPDATED') {
      newNotification = {
        id: `notif-${Date.now()}`,
        title: `Order #${lastMessage.order_id} Update`,
        message: `Status updated to: ${lastMessage.new_status || lastMessage.status}`,
        type: 'order',
        timestamp: timeStr,
        read: false,
        link: `/orders/${lastMessage.order_id}`,
      };
      toast.info(`📦 Order #${lastMessage.order_id} is now ${lastMessage.new_status}!`, { duration: 3500 });
    } else if (lastMessage.event === 'LOW_STOCK') {
      newNotification = {
        id: `notif-${Date.now()}`,
        title: 'Inventory Alert',
        message: `${lastMessage.product_name} is running low on stock!`,
        type: 'alert',
        timestamp: timeStr,
        read: false,
        link: '/',
      };
      toast.warning(`⚠️ Low stock: ${lastMessage.product_name}`, { duration: 3500 });
    }

    if (newNotification) {
      setNotifications((prev) => [newNotification!, ...prev]);
    }
  }, [lastMessage]);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAllAsRead = (e: React.MouseEvent) => {
    e.stopPropagation();
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const clearAllNotifications = (e: React.MouseEvent) => {
    e.stopPropagation();
    setNotifications([]);
  };

  const clearNotification = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const handleItemClick = (item: NotificationItem) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === item.id ? { ...n, read: true } : n))
    );
    // Instantly close the dropdown on click!
    setIsOpen(false);
    if (item.link) {
      navigate(item.link);
    }
  };

  const filteredNotifications = notifications.filter((item) => {
    if (activeTab === 'orders') return item.type === 'order';
    if (activeTab === 'offers') return item.type === 'offer';
    return true;
  });

  return (
    <div className="relative">
      {/* Bell Action Button */}
      <button
        ref={bellButtonRef}
        onClick={() => setIsOpen((prev) => !prev)}
        data-testid="notification-bell-btn"
        className="relative p-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus:outline-none"
        title={isConnected ? 'Live Notifications Connected' : 'Connecting to notifications...'}
        aria-label="Real-time notifications"
      >
        <Bell className="h-5 w-5 transition-transform hover:scale-105" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-4 min-w-[16px] px-1 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow-sm animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Modern E-Commerce Notifications Dropdown */}
      {isOpen && (
        <div
          ref={dropdownRef}
          data-testid="notification-dropdown"
          className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl border border-border bg-card shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-muted/40">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm text-foreground">Notifications</span>
              {unreadCount > 0 && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-rose-500 text-white">
                  {unreadCount} new
                </span>
              )}
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 font-medium border border-emerald-200 dark:border-emerald-800 flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                {isConnected ? 'Live' : 'Offline'}
              </span>
            </div>

            <div className="flex items-center gap-1">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  title="Mark all as read"
                  className="p-1.5 rounded-lg text-xs text-muted-foreground hover:text-foreground hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <CheckCheck className="h-4 w-4" />
                </button>
              )}
              {notifications.length > 0 && (
                <button
                  onClick={clearAllNotifications}
                  title="Clear all notifications"
                  className="p-1.5 rounded-lg text-xs text-muted-foreground hover:text-rose-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              )}
              {/* Prominent Header Close (X) button */}
              <button
                onClick={() => setIsOpen(false)}
                title="Close (Esc)"
                aria-label="Close notifications"
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ml-1"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Filter Tabs (All / Orders / Offers) */}
          <div className="flex items-center border-b border-border px-3 bg-muted/20 text-xs font-medium">
            <button
              onClick={() => setActiveTab('all')}
              className={`py-2 px-3 border-b-2 transition-colors ${
                activeTab === 'all'
                  ? 'border-pink-500 text-pink-600 dark:text-pink-400 font-semibold'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              All ({notifications.length})
            </button>
            <button
              onClick={() => setActiveTab('orders')}
              className={`py-2 px-3 border-b-2 transition-colors flex items-center gap-1 ${
                activeTab === 'orders'
                  ? 'border-pink-500 text-pink-600 dark:text-pink-400 font-semibold'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              Orders ({notifications.filter((n) => n.type === 'order').length})
            </button>
            <button
              onClick={() => setActiveTab('offers')}
              className={`py-2 px-3 border-b-2 transition-colors flex items-center gap-1 ${
                activeTab === 'offers'
                  ? 'border-pink-500 text-pink-600 dark:text-pink-400 font-semibold'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              Offers ({notifications.filter((n) => n.type === 'offer').length})
            </button>
          </div>

          {/* Notifications List */}
          <div className="max-h-80 overflow-y-auto divide-y divide-border">
            {filteredNotifications.length === 0 ? (
              <div className="p-8 text-center flex flex-col items-center justify-center space-y-2">
                <div className="h-10 w-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400">
                  <Bell className="h-5 w-5" />
                </div>
                <p className="text-xs font-semibold text-foreground">You're all caught up!</p>
                <p className="text-[11px] text-muted-foreground max-w-[220px]">
                  No {activeTab !== 'all' ? activeTab : 'new'} notifications right now.
                </p>
              </div>
            ) : (
              filteredNotifications.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleItemClick(item)}
                  className={`p-3.5 transition-colors flex items-start gap-3 cursor-pointer group ${
                    item.read
                      ? 'bg-transparent hover:bg-muted/40'
                      : 'bg-primary/5 hover:bg-primary/10'
                  }`}
                >
                  {/* Icon based on notification type */}
                  <div className="mt-0.5 shrink-0">
                    {item.type === 'order' ? (
                      <div className="h-8 w-8 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                        <PackageCheck className="h-4 w-4" />
                      </div>
                    ) : item.type === 'offer' ? (
                      <div className="h-8 w-8 rounded-full bg-pink-100 dark:bg-pink-950/60 text-pink-600 dark:text-pink-400 flex items-center justify-center">
                        <Tag className="h-4 w-4" />
                      </div>
                    ) : item.type === 'alert' ? (
                      <div className="h-8 w-8 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center">
                        <AlertTriangle className="h-4 w-4" />
                      </div>
                    ) : (
                      <div className="h-8 w-8 rounded-full bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center">
                        <Sparkles className="h-4 w-4" />
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1">
                      <p className="text-xs font-semibold text-foreground truncate group-hover:text-primary transition-colors">
                        {item.title}
                      </p>
                      <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                        {item.timestamp}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed line-clamp-2">
                      {item.message}
                    </p>
                  </div>

                  {/* Quick remove button */}
                  <button
                    onClick={(e) => clearNotification(item.id, e)}
                    title="Dismiss"
                    className="text-muted-foreground/60 hover:text-foreground p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2 bg-muted/30 border-t border-border flex items-center justify-between text-[11px] text-muted-foreground">
            <span>Auto-closes in 8s or on click</span>
            <button
              onClick={() => {
                setIsOpen(false);
                navigate('/orders');
              }}
              className="text-primary hover:underline font-medium"
            >
              View all orders →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;

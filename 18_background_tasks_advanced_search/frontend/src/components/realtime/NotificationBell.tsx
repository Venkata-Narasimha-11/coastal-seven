import React, { useState, useEffect } from 'react';
import { Bell, CheckCheck, Clock, PackageCheck, AlertTriangle, X } from 'lucide-react';
import { toast } from 'sonner';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useAuth } from '../../hooks/useAuth';

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: 'order' | 'alert' | 'system';
  timestamp: string;
  read: boolean;
}

export const NotificationBell: React.FC = () => {
  const { user, isAdmin } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    {
      id: 'init-1',
      title: 'Welcome to Gunturu Store',
      message: 'Real-time WebSocket event notifications are active.',
      type: 'system',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      read: true,
    },
  ]);

  // Connect to appropriate WebSocket channel based on user role
  const wsBase = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws';
  const wsUrl = isAdmin ? `${wsBase}/admin` : user ? `${wsBase}/orders/${user.id || 1}` : null;

  const { isConnected, lastMessage } = useWebSocket(wsUrl, {
    autoReconnect: true,
    maxRetries: 10,
    baseDelay: 1000,
  });

  // Handle incoming real-time notifications
  useEffect(() => {
    if (!lastMessage) return;

    let newNotification: NotificationItem | null = null;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (lastMessage.event === 'NEW_ORDER') {
      newNotification = {
        id: `notif-${Date.now()}`,
        title: `New Order #${lastMessage.order_id}`,
        message: `Placed by ${lastMessage.customer || 'Customer'} - $${lastMessage.total || ''}`,
        type: 'order',
        timestamp: timeStr,
        read: false,
      };
      toast.success(`🛒 New Order #${lastMessage.order_id} received!`);
    } else if (lastMessage.event === 'STATUS_UPDATED') {
      newNotification = {
        id: `notif-${Date.now()}`,
        title: `Order #${lastMessage.order_id} Update`,
        message: `Status is now: ${lastMessage.new_status || lastMessage.status}`,
        type: 'order',
        timestamp: timeStr,
        read: false,
      };
      toast.info(`📦 Order #${lastMessage.order_id} is now ${lastMessage.new_status}!`);
    } else if (lastMessage.event === 'LOW_STOCK') {
      newNotification = {
        id: `notif-${Date.now()}`,
        title: 'Inventory Alert',
        message: `${lastMessage.product_name} is running low on stock!`,
        type: 'alert',
        timestamp: timeStr,
        read: false,
      };
      toast.warning(`⚠️ Low stock: ${lastMessage.product_name}`);
    }

    if (newNotification) {
      setNotifications((prev) => [newNotification!, ...prev]);
    }
  }, [lastMessage]);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const clearNotification = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  return (
    <div className="relative">
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-full text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus:outline-none"
        title={isConnected ? 'Live WebSocket Connected' : 'Connecting to notifications...'}
        aria-label="Real-time notifications"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
        <span
          className={`absolute bottom-1 right-1 h-2 w-2 rounded-full ${
            isConnected ? 'bg-emerald-500' : 'bg-amber-500'
          }`}
        />
      </button>

      {/* Notifications Dropdown Panel */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl border border-border bg-card shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-muted/40">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">Notifications</span>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
                  {isConnected ? '🟢 Live' : '🟠 Offline'}
                </span>
              </div>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-primary hover:underline flex items-center gap-1 font-medium"
                >
                  <CheckCheck className="h-3.5 w-3.5" /> Mark all read
                </button>
              )}
            </div>

            {/* List */}
            <div className="max-h-80 overflow-y-auto divide-y divide-border">
              {notifications.length === 0 ? (
                <div className="p-6 text-center text-xs text-muted-foreground">
                  No notifications right now
                </div>
              ) : (
                notifications.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => {
                      setNotifications((prev) =>
                        prev.map((n) => (n.id === item.id ? { ...n, read: true } : n))
                      );
                    }}
                    className={`p-3 transition-colors flex items-start gap-3 cursor-pointer ${
                      item.read
                        ? 'bg-transparent hover:bg-muted/30'
                        : 'bg-primary/5 hover:bg-primary/10'
                    }`}
                  >
                    <div className="mt-0.5">
                      {item.type === 'order' ? (
                        <PackageCheck className="h-4 w-4 text-emerald-500" />
                      ) : item.type === 'alert' ? (
                        <AlertTriangle className="h-4 w-4 text-amber-500" />
                      ) : (
                        <Clock className="h-4 w-4 text-blue-500" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-xs font-semibold text-foreground truncate">
                          {item.title}
                        </p>
                        <span className="text-[10px] text-muted-foreground ml-2 whitespace-nowrap">
                          {item.timestamp}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                        {item.message}
                      </p>
                    </div>
                    <button
                      onClick={(e) => clearNotification(item.id, e)}
                      className="text-muted-foreground hover:text-foreground p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationBell;

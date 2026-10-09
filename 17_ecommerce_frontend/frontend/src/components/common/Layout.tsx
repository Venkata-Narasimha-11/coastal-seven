import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import Navbar from './Navbar';
import ErrorBoundary from './ErrorBoundary';
import { Toaster } from '../ui/sonner';
import Badge from '../ui/Badge';
import { Sparkles, Shield, Cpu, RefreshCw, Radio } from 'lucide-react';
import LiveChatWidget from '../realtime/LiveChatWidget';

interface LayoutProps {
  children?: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground transition-colors duration-200">
      <Navbar />

      <main className="flex-1 py-6 sm:py-8">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <ErrorBoundary>
            {children || <Outlet />}
          </ErrorBoundary>
        </div>
      </main>

      <footer className="border-t border-border/60 bg-muted/20 py-8 text-center text-xs text-muted-foreground transition-colors duration-200">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-4">
          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-4">
            <Badge variant="outline" className="gap-1 border-primary/30 text-primary">
              <Radio className="h-3 w-3 animate-pulse text-emerald-500" /> Day 17 Real-Time WebSockets
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Sparkles className="h-3 w-3" /> Live Order Tracking + Notifications
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Cpu className="h-3 w-3" /> Admin ↔ Customer Live Chat
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Shield className="h-3 w-3" /> JWT Auth + CORS Config
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <RefreshCw className="h-3 w-3" /> Exponential Backoff Reconnection
            </Badge>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 pt-2 border-t border-border/40 text-[11px]">
            <p>© 2026 Gunturu E-Commerce Fullstack Hub. All rights reserved.</p>
            <div className="flex items-center gap-4">
              <Link to="/" className="hover:text-primary transition-colors font-medium">
                Store Catalog
              </Link>
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="hover:text-primary transition-colors font-medium text-blue-500"
              >
                FastAPI Swagger Docs
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Real-time Floating Live Support Chat Widget */}
      <LiveChatWidget />

      {/* Global Toast Provider */}
      <Toaster richColors closeButton position="top-right" />
    </div>
  );
};

export default Layout;

import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import Navbar from './Navbar';
import ErrorBoundary from './ErrorBoundary';
import { Toaster } from '../ui/sonner';
import Badge from '../ui/Badge';
import { Sparkles, Shield, Cpu, RefreshCw, Radio } from 'lucide-react';
import LiveChatWidget from '../realtime/LiveChatWidget';
import AIChatWidget from '../ai/AIChatWidget';

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
          <div className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2">
            <Badge variant="outline" className="gap-1 border-primary/30 text-primary text-[10px]">
              <Radio className="h-3 w-3 animate-pulse text-emerald-500" /> Day 10-11 Core E-Commerce
            </Badge>
            <Badge variant="secondary" className="gap-1 text-[10px]">
              <Sparkles className="h-3 w-3 text-pink-500" /> Day 12 Tailwind & Zod
            </Badge>
            <Badge variant="secondary" className="gap-1 text-[10px]">
              <Cpu className="h-3 w-3 text-purple-500" /> Day 14 Zustand & React Query
            </Badge>
            <Badge variant="secondary" className="gap-1 text-[10px]">
              <Shield className="h-3 w-3 text-blue-500" /> Day 15 TypeScript & Vitest
            </Badge>
            <Badge variant="secondary" className="gap-1 text-[10px]">
              <RefreshCw className="h-3 w-3 text-amber-500" /> Day 16-17 WebSockets Real-Time
            </Badge>
            <Badge variant="secondary" className="gap-1 text-[10px]">
              <Cpu className="h-3 w-3 text-cyan-500" /> Day 18 Celery & CSV Import
            </Badge>
            <Badge variant="secondary" className="gap-1 text-[10px]">
              <Shield className="h-3 w-3 text-emerald-500" /> Day 19 Rate Limiting & OWASP
            </Badge>
            <Badge variant="secondary" className="gap-1 text-[10px]">
              <Sparkles className="h-3 w-3 text-rose-500" /> Day 20-21 AI RAG & ChromaDB Search
            </Badge>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-border/40 text-[11px]">
            <p className="font-serif tracking-wide text-slate-700 dark:text-slate-300">
              © 2026 <strong className="text-pink-600 dark:text-pink-400">SIVORA</strong> Luxury Fashion • Nykaa Fashion Flagship Hub (Day 10 - Day 21 Integrated).
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link to="/" className="hover:text-primary transition-colors font-medium">Store Catalog</Link>
              <Link to="/orders" className="hover:text-primary transition-colors font-medium">Order History</Link>
              <Link to="/state-comparison" className="hover:text-primary transition-colors font-medium text-pink-600 dark:text-pink-400">Day 14 State Lab</Link>
              <Link to="/performance-lab" className="hover:text-primary transition-colors font-medium text-purple-600 dark:text-purple-400">Day 14 Perf Lab</Link>
              <Link to="/testing-lab" className="hover:text-primary transition-colors font-medium text-blue-600 dark:text-blue-400">Day 15 Test Lab</Link>
              <Link to="/admin?tab=tasks" className="hover:text-primary transition-colors font-medium text-amber-600 dark:text-amber-400">Day 18 Tasks & CSV</Link>
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="hover:text-primary transition-colors font-medium text-emerald-500"
              >
                FastAPI Swagger
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Real-time Floating Live Support Chat Widget */}
      <LiveChatWidget />

      {/* Day 20 AI Shopping Assistant (RAG + SSE Streaming) */}
      <AIChatWidget />

      {/* Global Toast Provider (Auto-dismisses in 3.5 seconds) */}
      <Toaster richColors closeButton position="top-right" duration={3500} />
    </div>
  );
};

export default Layout;

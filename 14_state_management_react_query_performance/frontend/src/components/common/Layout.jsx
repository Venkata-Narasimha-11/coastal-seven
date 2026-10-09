import React from "react";
import { Outlet, Link } from "react-router-dom";
import Navbar from "./Navbar";
import ErrorBoundary from "./ErrorBoundary";
import { Toaster } from "../ui/sonner";
import { Badge } from "../ui/badge";
import { Sparkles, Shield, Cpu, RefreshCw } from "lucide-react";

export const Layout = () => {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground transition-colors duration-200">
      <Navbar />

      <main className="flex-1 py-6 sm:py-8">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </div>
      </main>

      <footer className="border-t border-border/60 bg-muted/20 py-8 text-center text-xs text-muted-foreground transition-colors duration-200">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-4">
          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-4">
            <Badge variant="outline" className="gap-1 border-primary/30 text-primary">
              <Sparkles className="h-3 w-3" /> Day 12 Architecture
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Cpu className="h-3 w-3" /> Tailwind CSS + Shadcn/ui
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Shield className="h-3 w-3" /> React Hook Form + Zod V4
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <RefreshCw className="h-3 w-3" /> Live FastAPI Backend
            </Badge>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 pt-2 border-t border-border/40 text-[11px]">
            <p>© 2026 Production E-Commerce Fullstack Hub. All rights reserved.</p>
            <div className="flex items-center gap-4">
              <Link to="/day12-lab" className="hover:text-primary transition-colors">
                Day 12 Interactive Lab
              </Link>
              <Link to="/" className="hover:text-primary transition-colors">
                Storefront Catalog
              </Link>
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="hover:text-primary transition-colors"
              >
                Swagger API Docs
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Global Shadcn / Sonner Toast Provider */}
      <Toaster richColors closeButton position="top-right" />
    </div>
  );
};

export default Layout;

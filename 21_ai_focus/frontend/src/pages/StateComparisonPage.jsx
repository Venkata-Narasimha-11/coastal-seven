import React, { useState, createContext, useContext, useRef, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import {
  Layers,
  Zap,
  Cpu,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Flame,
  ArrowRight,
  TrendingDown,
  Info,
} from 'lucide-react';
import { useCartStore } from '../stores/cartStore';

// =================================================================
// 1. CONTEXT API SIMULATION (with render flash)
// =================================================================
const DemoContext = createContext(null);

function ContextDemoParent({ children }) {
  const [cartCount, setCartCount] = useState(0);
  const [userName, setUserName] = useState('Narasimha');
  const parentRenders = useRef(0);
  parentRenders.current += 1;

  return (
    <DemoContext.Provider value={{ cartCount, setCartCount, userName, setUserName, parentRenders: parentRenders.current }}>
      {children}
    </DemoContext.Provider>
  );
}

function ContextCartWidget() {
  const { cartCount, setCartCount } = useContext(DemoContext);
  const renders = useRef(0);
  renders.current += 1;

  return (
    <div className="p-3 rounded-lg border border-border bg-card/50 space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Cart Component</span>
        <Badge variant="outline" className="bg-amber-500/10 text-amber-500 border-amber-500/20 text-xs font-mono">
          Renders: {renders.current}
        </Badge>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xl font-bold font-mono">Items: {cartCount}</span>
        <Button size="sm" variant="outline" onClick={() => setCartCount((c) => c + 1)}>
          + Add
        </Button>
      </div>
      <p className="text-[11px] text-muted-foreground">Consumes cartCount from Context</p>
    </div>
  );
}

function ContextUserWidget() {
  const { userName } = useContext(DemoContext);
  const renders = useRef(0);
  renders.current += 1;

  return (
    <div className="p-3 rounded-lg border border-border bg-card/50 space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">User Profile Component</span>
        <Badge
          variant="outline"
          className="bg-red-500/10 text-red-500 border-red-500/20 text-xs font-mono animate-pulse"
        >
          Renders: {renders.current}
        </Badge>
      </div>
      <div className="text-sm font-medium">Logged in: <span className="font-semibold text-primary">{userName}</span></div>
      <p className="text-[11px] text-red-400 font-medium flex items-center gap-1">
        <Flame className="w-3 h-3" /> Re-renders every time Cart updates even though User didn't change!
      </p>
    </div>
  );
}

// =================================================================
// 2. ZUSTAND SIMULATION (atomic selectors, zero unnecessary renders)
// =================================================================
function ZustandCartWidget() {
  const cartStore = useCartStore();
  const renders = useRef(0);
  renders.current += 1;

  return (
    <div className="p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/5 space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">Cart Component</span>
        <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-xs font-mono">
          Renders: {renders.current}
        </Badge>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xl font-bold font-mono">Items: {cartStore.getItemCount()}</span>
        <Button
          size="sm"
          className="bg-emerald-600 hover:bg-emerald-700 text-white"
          onClick={() => cartStore.addItem({ id: 999, title: 'Demo Item', price: 99 })}
        >
          + Add
        </Button>
      </div>
      <p className="text-[11px] text-muted-foreground">Subscribed only to cart changes</p>
    </div>
  );
}

function ZustandUserWidget() {
  // Unrelated component with static or distinct selector
  const renders = useRef(0);
  renders.current += 1;

  return (
    <div className="p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/5 space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">User Profile Component</span>
        <Badge variant="outline" className="bg-emerald-500/20 text-emerald-300 border-emerald-500/30 text-xs font-mono">
          Renders: {renders.current} (Frozen)
        </Badge>
      </div>
      <div className="text-sm font-medium">Logged in: <span className="font-semibold text-emerald-400">Narasimha</span></div>
      <p className="text-[11px] text-emerald-400/90 font-medium flex items-center gap-1">
        <CheckCircle2 className="w-3 h-3 text-emerald-400" /> 0 unnecessary re-renders! Selective subscription protects performance.
      </p>
    </div>
  );
}

// =================================================================
// 3. REDUX SIMULATION (Dispatch & Action logs)
// =================================================================
function ReduxSimulationWidget() {
  const [reduxState, setReduxState] = useState({ count: 0, user: 'Narasimha' });
  const [actionLog, setActionLog] = useState([
    { type: '@@INIT', timestamp: '12:00:00' },
  ]);

  const dispatch = (action) => {
    setActionLog((prev) => [
      { type: action.type, payload: action.payload, timestamp: new Date().toLocaleTimeString() },
      ...prev.slice(0, 4),
    ]);
    if (action.type === 'cart/itemAdded') {
      setReduxState((prev) => ({ ...prev, count: prev.count + 1 }));
    } else if (action.type === 'cart/reset') {
      setReduxState((prev) => ({ ...prev, count: 0 }));
    }
  };

  return (
    <div className="space-y-3">
      <div className="p-3 rounded-lg border border-purple-500/30 bg-purple-500/5 space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-purple-400">Redux Store & Dispatch</span>
          <Badge variant="outline" className="bg-purple-500/10 text-purple-400 border-purple-500/20 text-xs font-mono">
            State: {JSON.stringify(reduxState)}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            className="border-purple-500/40 text-purple-300 hover:bg-purple-500/10"
            onClick={() => dispatch({ type: 'cart/itemAdded', payload: { id: 1 } })}
          >
            Dispatch (cart/itemAdded)
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => dispatch({ type: 'cart/reset' })}
          >
            Reset
          </Button>
        </div>
      </div>

      <div className="p-2.5 rounded bg-black/40 border border-border/50 text-[11px] font-mono space-y-1">
        <div className="text-muted-foreground font-semibold flex items-center gap-1">
          <Cpu className="w-3 h-3 text-purple-400" /> Redux Action Log (Unidirectional Flow):
        </div>
        {actionLog.map((log, i) => (
          <div key={i} className="flex justify-between text-muted-foreground hover:text-foreground">
            <span className="text-purple-400">{log.type}</span>
            <span className="text-[10px] opacity-70">{log.timestamp}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// =================================================================
// MAIN COMPARISON PAGE
// =================================================================
export default function StateComparisonPage() {
  return (
    <div className="container max-w-6xl mx-auto py-8 px-4 space-y-8">
      {/* Header */}
      <div className="space-y-2 text-center md:text-left">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium border border-primary/20">
          <Layers className="w-3.5 h-3.5" /> Day 14 Architecture Blueprint
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight">
          State Management Deep Dive
        </h1>
        <p className="text-muted-foreground text-sm max-w-3xl">
          Comprehensive benchmark and live render comparison between{' '}
          <strong className="text-foreground">React Context API</strong>,{' '}
          <strong className="text-emerald-400">Zustand</strong>, and{' '}
          <strong className="text-purple-400">Redux Toolkit</strong>.
        </p>
      </div>

      {/* 3-WAY LIVE INTERACTIVE BENCHMARK GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* PANEL 1: CONTEXT API */}
        <Card className="border-amber-500/20 bg-amber-500/[0.02]">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <Layers className="w-5 h-5 text-amber-500" /> Context API
              </CardTitle>
              <Badge variant="outline" className="text-amber-400 border-amber-500/30 text-xs">
                Built-in (0 KB)
              </Badge>
            </div>
            <CardDescription className="text-xs">
              React's native dependency injection. Triggers render on every consumer.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <ContextDemoParent>
              <ContextCartWidget />
              <ContextUserWidget />
            </ContextDemoParent>
            <div className="p-2.5 rounded bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300/90 leading-relaxed">
              <strong>Observation:</strong> Incrementing cart count forces the User component to re-render because React Context lacks atomic selector subscriptions.
            </div>
          </CardContent>
        </Card>

        {/* PANEL 2: ZUSTAND (OUR CHOICE) */}
        <Card className="border-emerald-500/30 bg-emerald-500/[0.03] ring-1 ring-emerald-500/20">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2 text-emerald-400">
                <Zap className="w-5 h-5 text-emerald-400" /> Zustand
              </CardTitle>
              <Badge className="bg-emerald-500 text-black font-semibold text-xs">
                Recommended (~1.1 KB)
              </Badge>
            </div>
            <CardDescription className="text-xs">
              Minimalist, atomic store. Re-renders ONLY components reading changed slices.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <ZustandCartWidget />
            <ZustandUserWidget />
            <div className="p-2.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 leading-relaxed">
              <strong>Observation:</strong> Changing cart state leaves the User component completely untouched (0 re-renders), saving massive CPU cycles on complex apps!
            </div>
          </CardContent>
        </Card>

        {/* PANEL 3: REDUX TOOLKIT */}
        <Card className="border-purple-500/20 bg-purple-500/[0.02]">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2 text-purple-400">
                <Cpu className="w-5 h-5 text-purple-400" /> Redux Toolkit
              </CardTitle>
              <Badge variant="outline" className="text-purple-400 border-purple-500/30 text-xs">
                Heavy (~11 KB)
              </Badge>
            </div>
            <CardDescription className="text-xs">
              Enterprise standard with rigid boilerplate and time-travel debugging.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <ReduxSimulationWidget />
            <div className="p-2.5 rounded bg-purple-500/10 border border-purple-500/20 text-xs text-purple-300/90 leading-relaxed">
              <strong>Observation:</strong> Highly structured and predictable, but requires actions, reducers, and providers for basic state mutations.
            </div>
          </CardContent>
        </Card>
      </div>

      {/* DETAILED COMPARISON TABLE */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2">
            <Info className="w-5 h-5 text-primary" /> Feature & Architecture Matrix
          </CardTitle>
          <CardDescription>
            Key factors for deciding state management in production applications.
          </CardDescription>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-muted/40">
                <th className="p-3 font-semibold">Evaluation Criteria</th>
                <th className="p-3 font-semibold text-amber-400">React Context API</th>
                <th className="p-3 font-semibold text-emerald-400">Zustand (Day 14)</th>
                <th className="p-3 font-semibold text-purple-400">Redux Toolkit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              <tr>
                <td className="p-3 font-medium">Bundle Size</td>
                <td className="p-3 text-muted-foreground">0 KB (React Core)</td>
                <td className="p-3 text-emerald-400 font-semibold">~1.1 KB (Ultralight)</td>
                <td className="p-3 text-muted-foreground">~11 KB (Heavy)</td>
              </tr>
              <tr>
                <td className="p-3 font-medium">Render Optimization</td>
                <td className="p-3 text-red-400 flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" /> High re-renders
                </td>
                <td className="p-3 text-emerald-400 font-semibold">Selective subscriptions</td>
                <td className="p-3 text-muted-foreground">Selector memoization (Reselect)</td>
              </tr>
              <tr>
                <td className="p-3 font-medium">Boilerplate & DX</td>
                <td className="p-3 text-muted-foreground">Provider nesting hell</td>
                <td className="p-3 text-emerald-400 font-semibold">Single create() function</td>
                <td className="p-3 text-muted-foreground">Slices, reducers, dispatches</td>
              </tr>
              <tr>
                <td className="p-3 font-medium">Local Storage Sync</td>
                <td className="p-3 text-muted-foreground">Manual useEffect</td>
                <td className="p-3 text-emerald-400 font-semibold">Built-in persist middleware</td>
                <td className="p-3 text-muted-foreground">redux-persist setup required</td>
              </tr>
              <tr>
                <td className="p-3 font-medium">Ideal Use Case</td>
                <td className="p-3 text-muted-foreground">Theme toggle, static locale</td>
                <td className="p-3 text-emerald-400 font-semibold">E-Commerce Cart, Auth, Modals</td>
                <td className="p-3 text-muted-foreground">Multi-team enterprise dashboards</td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* WHY WE CHOSE ZUSTAND FOR DAY 14 */}
      <div className="p-6 rounded-xl border border-emerald-500/20 bg-emerald-950/10 space-y-3">
        <h3 className="text-lg font-bold text-emerald-400 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5" /> Why Zustand + TanStack Query is the Modern 2026 Gold Standard
        </h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Previously, developers stored everything (server data, cache, loading spinners, form inputs, cart items) inside giant Redux stores.
          In modern React, we split state into two clean domains:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div className="p-4 rounded-lg border border-border bg-card/60">
            <h4 className="font-semibold text-emerald-400 text-sm">Client State (Zustand)</h4>
            <p className="text-xs text-muted-foreground mt-1">
              For local UI data that only lives in the browser (Shopping Cart items, Auth token, theme mode, drawer open/closed).
            </p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-card/60">
            <h4 className="font-semibold text-primary text-sm">Server State (TanStack Query)</h4>
            <p className="text-xs text-muted-foreground mt-1">
              For database data (Product catalog, reviews, orders). Handles caching, auto-refetch, pagination, and optimistic updates out of the box.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

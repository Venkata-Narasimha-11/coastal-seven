import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, X, Send, Bot, ShoppingBag, Loader2, Wrench } from 'lucide-react';
import useAuthStore from '../../stores/useAuthStore';
import useCartStore from '../../stores/useCartStore';
import { toast } from 'sonner';
import { AIErrorBoundary } from './AIErrorBoundary';

interface ProductCitation {
  id: number;
  name: string;
  category: string;
  price: number;
  stock: number;
  image_url: string;
  slug: string;
  relevance_score?: number;
}

interface ToolExecution {
  tool: string;
  result: any;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: ProductCitation[];
  tools?: ToolExecution[];
  isStreaming?: boolean;
}

const QUICK_SUGGESTIONS = [
  'Is Sony headphones in stock?',
  'Calculate discount with coupon SAVE10 on ₹15,000',
  'Best wireless noise-canceling headphones under ₹30,000?',
  'Recommend laptops for programming',
];

export const AIChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hello! I am your SIVORA AI Stylist & Shopping Assistant ✨ Powered by autonomous tool calling, I can check live warehouse inventory, calculate coupon discounts (e.g. SAVE10), and recommend curated luxury fashion & lifestyle pieces. How may I assist you today?',
    },
  ]);
  const [isGenerating, setIsGenerating] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const addItemToCart = useCartStore((state) => state.addItem);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query || isGenerating) return;

    setInput('');
    const userMsgId = `user_${Date.now()}`;
    const assistantMsgId = `asst_${Date.now()}`;

    // Add User Message & empty Assistant placeholder
    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: 'user', content: query },
      { id: assistantMsgId, role: 'assistant', content: '', isStreaming: true, sources: [], tools: [] },
    ]);

    setIsGenerating(true);

    try {
      const historyForApi = messages
        .filter((m) => m.id !== 'welcome')
        .map((m) => ({ role: m.role, content: m.content }));

      const response = await fetch('http://127.0.0.1:8000/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          history: historyForApi,
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Failed to stream chat: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let accumulatedContent = '';
      let receivedSources: ProductCitation[] = [];
      const executedTools: ToolExecution[] = [];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.replace('data: ', ''));

              if (eventData.type === 'sources') {
                receivedSources = eventData.sources || [];
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId ? { ...msg, sources: receivedSources } : msg
                  )
                );
              } else if (eventData.type === 'tool_executed') {
                executedTools.push({ tool: eventData.tool, result: eventData.result });
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId ? { ...msg, tools: [...executedTools] } : msg
                  )
                );
              } else if (eventData.type === 'token') {
                accumulatedContent += eventData.content;
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId
                      ? { ...msg, content: accumulatedContent }
                      : msg
                  )
                );
              } else if (eventData.type === 'done') {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId
                      ? { ...msg, isStreaming: false }
                      : msg
                  )
                );
              }
            } catch (err) {
              // Ignore partial JSON chunks
            }
          }
        }
      }
    } catch (error) {
      console.error('Error streaming AI response:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                content:
                  'Sorry, I encountered an issue connecting to the AI service. Please make sure the backend server is running.',
                isStreaming: false,
              }
            : msg
        )
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAddCitationToCart = (p: ProductCitation) => {
    if (!isAuthenticated) {
      setIsOpen(false);
      navigate('/login');
      return;
    }
    addItemToCart(
      {
        id: p.id,
        name: p.name,
        slug: p.slug,
        description: '',
        price: p.price,
        stock: p.stock,
        category_id: 1,
        category: { id: 1, name: p.category, slug: p.category.toLowerCase(), created_at: new Date().toISOString() },
        image_url: p.image_url,
        thumbnail_url: p.image_url,
        is_active: true,
        created_at: '',
        updated_at: '',
      },
      1
    );
    toast.success(`Added ${p.name} to cart!`);
  };

  return (
    <AIErrorBoundary
      fallbackTitle="AI Shopping Assistant Offline"
      fallbackMessage="The assistant encountered an error. Click retry or continue shopping."
    >
      {/* Floating Action Button */}
      <div className="fixed bottom-24 right-4 sm:right-6 z-40">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="relative group p-4 rounded-full bg-gradient-to-tr from-pink-600 via-rose-600 to-amber-500 text-white shadow-xl shadow-pink-500/30 hover:shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300"
          aria-label="Toggle AI Shopping Assistant"
        >
          <div className="absolute inset-0 rounded-full bg-white/20 animate-ping opacity-20 pointer-events-none" />
          {isOpen ? <X className="h-6 w-6" /> : <Bot className="h-6 w-6" />}
        </button>
      </div>

      {/* Floating Chat Modal */}
      {isOpen && (
        <div className="fixed bottom-24 right-4 sm:right-6 w-[92vw] sm:w-[440px] h-[580px] max-h-[82vh] bg-card text-foreground rounded-2xl shadow-2xl border border-pink-200/50 dark:border-slate-800 flex flex-col z-50 overflow-hidden animate-scale-up">
          {/* Header */}
          <div className="bg-gradient-to-r from-rose-950 via-pink-900 to-slate-900 p-4 text-white flex items-center justify-between shadow-md border-b border-pink-500/20">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-white/15 backdrop-blur-md border border-white/20">
                <Sparkles className="h-5 w-5 text-amber-300" />
              </div>
              <div>
                <h3 className="font-bold text-sm leading-tight flex items-center gap-1.5">
                  SIVORA AI Stylist
                  <span className="text-[10px] bg-pink-500/30 text-pink-200 font-semibold px-2 py-0.5 rounded-full border border-pink-400/30">
                    Live Co-Pilot
                  </span>
                </h3>
                <p className="text-[11px] text-pink-200/80">Live Stock • Coupons • Curated Catalogue</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm bg-muted/20">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="h-7 w-7 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0 mt-0.5 border border-primary/20">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-tr-none'
                      : 'bg-card text-foreground border border-border rounded-tl-none'
                  }`}
                >
                  {/* Tool Execution Badges */}
                  {msg.tools && msg.tools.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-2.5 pb-2 border-b border-border/50">
                      {msg.tools.map((t, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-500/20"
                        >
                          <Wrench className="h-2.5 w-2.5 text-indigo-500" />
                          {t.tool === 'check_product_stock'
                            ? `Stock: ${t.result?.stock_quantity ?? 'Checked'}`
                            : t.tool === 'apply_coupon_calculator'
                            ? `Coupon ${t.result?.coupon_code}: -₹${t.result?.discount_amount}`
                            : t.tool === 'lookup_product_price'
                            ? `Price: ₹${t.result?.price}`
                            : t.tool === 'check_order_status'
                            ? `Order #${t.result?.order_id}: ${t.result?.status}`
                            : t.tool}
                        </span>
                      ))}
                    </div>
                  )}

                  <p className="whitespace-pre-wrap leading-relaxed text-[13px]">
                    {msg.content}
                    {msg.isStreaming && (
                      <span className="inline-block w-1.5 h-4 ml-1 bg-primary animate-pulse align-middle" />
                    )}
                  </p>

                  {/* Sources Citations / Product Cards */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-border/60 space-y-2">
                      <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                        <Sparkles className="h-3 w-3 text-amber-500" /> Recommended Products
                      </p>
                      <div className="grid grid-cols-1 gap-2">
                        {msg.sources.map((product) => (
                          <div
                            key={product.id}
                            className="flex items-center justify-between p-2 rounded-xl bg-muted/40 border border-border/70 hover:border-primary/50 transition-colors"
                          >
                            <div className="flex items-center gap-2.5 min-w-0">
                              {product.image_url ? (
                                <img
                                  src={product.image_url}
                                  alt={product.name}
                                  className="h-10 w-10 rounded-lg object-cover bg-muted shrink-0"
                                />
                              ) : (
                                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                                  <ShoppingBag className="h-4 w-4 text-primary" />
                                </div>
                              )}
                              <div className="min-w-0">
                                <h5 className="font-semibold text-xs text-foreground truncate">
                                  {product.name}
                                </h5>
                                <p className="text-[11px] text-muted-foreground">
                                  ₹{product.price.toLocaleString()} • {product.category}
                                </p>
                              </div>
                            </div>

                            <button
                              onClick={() => handleAddCitationToCart(product)}
                              className="ml-2 px-2.5 py-1.5 rounded-lg bg-primary/10 hover:bg-primary hover:text-primary-foreground text-primary text-[11px] font-medium transition-colors shrink-0 flex items-center gap-1"
                              title="Add to cart"
                            >
                              <ShoppingBag className="h-3 w-3" />
                              Add
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestion Pills */}
          <div className="p-2 bg-card border-t border-border flex items-center gap-1.5 overflow-x-auto text-[11px] no-scrollbar">
            {QUICK_SUGGESTIONS.map((pill, idx) => (
              <button
                key={idx}
                disabled={isGenerating}
                onClick={() => handleSend(pill)}
                className="whitespace-nowrap px-3 py-1 rounded-full bg-muted/60 hover:bg-primary/10 hover:text-primary border border-border text-muted-foreground transition-all duration-200 shrink-0"
              >
                {pill}
              </button>
            ))}
          </div>

          {/* Input Area */}
          <div className="p-3 bg-card border-t border-border flex items-center gap-2">
            <input
              type="text"
              value={input}
              disabled={isGenerating}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about products, stock, coupons..."
              className="flex-1 bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:bg-background transition-all"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isGenerating}
              className="p-2.5 rounded-xl bg-primary text-primary-foreground disabled:opacity-40 hover:opacity-90 active:scale-95 transition-all shrink-0"
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      )}
    </AIErrorBoundary>
  );
};

export default AIChatWidget;

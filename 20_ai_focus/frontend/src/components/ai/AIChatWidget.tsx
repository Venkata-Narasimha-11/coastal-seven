import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, X, Send, Bot, User, ShoppingBag, Loader2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import useCartStore from '../../stores/useCartStore';
import { toast } from 'sonner';

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

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: ProductCitation[];
  isStreaming?: boolean;
}

const QUICK_SUGGESTIONS = [
  'Best wireless headphones under ₹30,000?',
  'Recommend laptops for coding & multitasking',
  'What smartwatches and wearables are in stock?',
  'Show me gaming consoles and VR gear',
];

export const AIChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hello! I am your AI Shopping Assistant for Gunturu Store. I can help you discover products, compare prices, and check live stock based on our catalog. How can I help you today?',
    },
  ]);
  const [isGenerating, setIsGenerating] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const addItemToCart = useCartStore((state) => state.addItem);

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
      { id: assistantMsgId, role: 'assistant', content: '', isStreaming: true, sources: [] },
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
              // Ignore partial JSON parse chunks
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
                  'Sorry, I encountered an issue connecting to the AI service. Please make sure the backend is running.',
                isStreaming: false,
              }
            : msg
        )
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAddToCartFromCitation = (citation: ProductCitation) => {
    addItemToCart(
      {
        id: citation.id,
        name: citation.name,
        price: citation.price,
        image_url: citation.image_url,
        stock: citation.stock,
        slug: citation.slug,
        is_active: true,
      } as any,
      1
    );
    toast.success(`Added ${citation.name} to cart!`);
  };

  return (
    <>
      {/* Floating Launcher Button */}
      <div className="fixed bottom-24 right-6 z-40 flex items-center gap-2">
        {!isOpen && (
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900/90 text-white text-xs font-medium shadow-lg backdrop-blur-md border border-slate-700 animate-fade-in">
            <Sparkles className="h-3.5 w-3.5 text-amber-300 animate-pulse" />
            <span>Ask AI Assistant</span>
          </div>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="relative group p-4 rounded-full bg-gradient-to-tr from-blue-600 via-indigo-600 to-sky-500 text-white shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300"
          aria-label="Toggle AI Shopping Assistant"
        >
          <div className="absolute inset-0 rounded-full bg-white/20 animate-ping opacity-20 pointer-events-none" />
          {isOpen ? <X className="h-6 w-6" /> : <Bot className="h-6 w-6" />}
        </button>
      </div>

      {/* Floating Chat Modal */}
      {isOpen && (
        <div className="fixed bottom-24 right-4 sm:right-6 w-[92vw] sm:w-[440px] h-[580px] max-h-[82vh] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col z-50 overflow-hidden animate-scale-up">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-sky-700 p-4 text-white flex items-center justify-between shadow-md">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-white/15 backdrop-blur-md border border-white/20">
                <Bot className="h-5 w-5 text-amber-300" />
              </div>
              <div>
                <h3 className="font-bold text-sm leading-tight flex items-center gap-1.5">
                  Gunturu AI Assistant
                  <span className="text-[10px] bg-emerald-500/30 text-emerald-300 font-semibold px-2 py-0.5 rounded-full border border-emerald-400/30">
                    RAG Live
                  </span>
                </h3>
                <p className="text-[11px] text-blue-100">Grounded in 78 Catalog Products</p>
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
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm bg-slate-50/50 dark:bg-slate-950/40">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="h-7 w-7 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-300 flex items-center justify-center shrink-0 mt-0.5 border border-blue-200 dark:border-blue-800">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-slate-200/80 dark:border-slate-700/80 rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed text-[13px]">
                    {msg.content}
                    {msg.isStreaming && (
                      <span className="inline-block w-1.5 h-4 ml-1 bg-blue-500 animate-pulse align-middle" />
                    )}
                  </p>

                  {/* Embedded Product Source Citations */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 space-y-2">
                      <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1">
                        <Sparkles className="h-3 w-3 text-amber-500" />
                        <span>Recommended Products ({msg.sources.length})</span>
                      </div>
                      <div className="grid grid-cols-1 gap-2 pt-1">
                        {msg.sources.map((item) => (
                          <div
                            key={item.id}
                            className="flex items-center justify-between gap-2 p-2 rounded-xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200/70 dark:border-slate-700/60 hover:border-blue-400 dark:hover:border-blue-500 transition-colors"
                          >
                            <div className="flex items-center gap-2.5 min-w-0">
                              <img
                                src={item.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80'}
                                alt={item.name}
                                className="h-10 w-10 rounded-lg object-cover bg-slate-200 shrink-0"
                              />
                              <div className="min-w-0">
                                <Link
                                  to={`/products/${item.id}`}
                                  className="text-xs font-semibold text-slate-800 dark:text-slate-100 hover:text-blue-600 truncate block"
                                >
                                  {item.name}
                                </Link>
                                <div className="text-[11px] text-slate-500 flex items-center gap-2">
                                  <span className="font-bold text-blue-600 dark:text-blue-400">
                                    ₹{item.price.toLocaleString('en-IN')}
                                  </span>
                                  <span>•</span>
                                  <span className="text-[10px] text-emerald-600 dark:text-emerald-400">
                                    {item.stock} in stock
                                  </span>
                                </div>
                              </div>
                            </div>

                            <button
                              onClick={() => handleAddToCartFromCitation(item)}
                              className="p-1.5 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-600 hover:text-white transition-colors shrink-0"
                              title="Add to Cart"
                            >
                              <ShoppingBag className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="h-7 w-7 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}

            {/* Quick Suggestion Chips (Shown on welcome) */}
            {messages.length === 1 && (
              <div className="pt-2 space-y-2">
                <p className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Quick Questions
                </p>
                <div className="flex flex-col gap-1.5">
                  {QUICK_SUGGESTIONS.map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSend(suggestion)}
                      className="text-left text-xs p-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-blue-500 hover:bg-blue-50/50 dark:hover:bg-blue-900/20 text-slate-700 dark:text-slate-200 transition-all flex items-center justify-between group"
                    >
                      <span>{suggestion}</span>
                      <ArrowRight className="h-3 w-3 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about products, prices, or specs..."
              disabled={isGenerating}
              className="flex-1 bg-slate-100 dark:bg-slate-800 border-none rounded-xl px-3.5 py-2.5 text-xs focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 dark:text-slate-100 placeholder:text-slate-400"
            />
            <button
              type="submit"
              disabled={!input.trim() || isGenerating}
              className="p-2.5 rounded-xl bg-blue-600 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors shadow-md"
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default AIChatWidget;

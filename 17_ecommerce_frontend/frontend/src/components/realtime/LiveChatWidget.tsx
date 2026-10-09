import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, X, Send, Radio, User, ShieldCheck } from 'lucide-react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useAuth } from '../../hooks/useAuth';

export interface ChatMessage {
  id: string;
  sender: string;
  sender_role: 'admin' | 'customer';
  text: string;
  time: string;
}

export const LiveChatWidget: React.FC = () => {
  const { user, isAdmin } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      sender: 'System Support',
      sender_role: 'admin',
      text: 'Hello! Welcome to Live Support. How can we assist you today?',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use a shared support room for Customer <-> Admin live communication
  const wsBase = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws';
  const chatRoomId = 'general_support';
  const wsUrl = `${wsBase}/chat/${chatRoomId}`;

  const { isConnected, lastMessage, sendMessage, reconnectCount } = useWebSocket(wsUrl, {
    autoReconnect: true,
    maxRetries: 10,
    baseDelay: 1000,
  });

  // Listen for incoming live chat messages and database history
  useEffect(() => {
    if (!lastMessage) return;

    if (lastMessage.event === 'CHAT_JOINED' && Array.isArray(lastMessage.history)) {
      if (lastMessage.history.length > 0) {
        setMessages((prev) => {
          const welcome = prev.filter((m) => m.id === 'welcome-1');
          return [...welcome, ...lastMessage.history];
        });
      }
      return;
    }

    if (lastMessage.text && lastMessage.sender) {
      setMessages((prev) => [
        ...prev,
        {
          id: lastMessage.id || `msg-${Date.now()}-${Math.random()}`,
          sender: lastMessage.sender,
          sender_role: lastMessage.sender_role || 'customer',
          text: lastMessage.text,
          time: lastMessage.time || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    }
  }, [lastMessage]);

  // Scroll to bottom on new message
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const currentUserName = user?.username || (isAdmin ? 'Admin' : 'Customer');
    const role = isAdmin ? 'admin' : 'customer';
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const payload = {
      sender: currentUserName,
      sender_role: role,
      text: inputMessage.trim(),
      time: timeStr,
    };

    sendMessage(payload);
    setInputMessage('');
  };

  const currentRole = isAdmin ? 'admin' : 'customer';

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-2.5 px-4 py-3 rounded-full bg-primary text-primary-foreground shadow-2xl hover:bg-primary/90 transition-all transform hover:scale-105 focus:outline-none"
          aria-label="Open Live Chat"
        >
          <div className="relative">
            <MessageSquare className="h-5 w-5" />
            <span
              className={`absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full ring-2 ring-background ${
                isConnected ? 'bg-emerald-400' : 'bg-amber-400'
              }`}
            />
          </div>
          <span className="font-semibold text-sm">Live Support</span>
        </button>
      )}

      {/* Floating Chat Modal */}
      {isOpen && (
        <div className="w-80 sm:w-96 rounded-2xl border border-border bg-card shadow-2xl overflow-hidden flex flex-col h-[480px] animate-in fade-in slide-in-from-bottom-4 duration-200">
          {/* Header */}
          <div className="bg-primary text-primary-foreground px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="relative">
                <MessageSquare className="h-5 w-5" />
                <span
                  className={`absolute -bottom-0.5 -right-0.5 h-2 w-2 rounded-full ${
                    isConnected ? 'bg-emerald-300' : 'bg-amber-300'
                  }`}
                />
              </div>
              <div>
                <h3 className="font-bold text-sm leading-none">Admin ↔ Customer Live Chat</h3>
                <p className="text-[11px] text-primary-foreground/80 mt-1 flex items-center gap-1">
                  <Radio className="h-2.5 w-2.5 animate-pulse" />
                  {isConnected
                    ? 'Connected (Real-time)'
                    : reconnectCount > 0
                    ? `Reconnecting (${reconnectCount})...`
                    : 'Connecting...'}
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-full hover:bg-primary-foreground/10 text-primary-foreground/80 hover:text-primary-foreground transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages Body */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-muted/20">
            {messages.map((msg) => {
              const isMine =
                (currentRole === 'admin' && msg.sender_role === 'admin') ||
                (currentRole === 'customer' && msg.sender_role === 'customer' && msg.sender !== 'System Support');

              return (
                <div
                  key={msg.id}
                  className={`flex flex-col ${isMine ? 'items-end' : 'items-start'}`}
                >
                  <div className="flex items-center gap-1 mb-0.5 px-1">
                    {msg.sender_role === 'admin' ? (
                      <ShieldCheck className="h-3 w-3 text-blue-500" />
                    ) : (
                      <User className="h-3 w-3 text-slate-400" />
                    )}
                    <span className="text-[10px] font-semibold text-muted-foreground">
                      {msg.sender}
                    </span>
                    <span className="text-[9px] text-muted-foreground/70">{msg.time}</span>
                  </div>
                  <div
                    className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-xs leading-relaxed shadow-sm ${
                      isMine
                        ? 'bg-primary text-primary-foreground rounded-br-xs'
                        : 'bg-card border border-border text-foreground rounded-bl-xs'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input Footer */}
          <form onSubmit={handleSend} className="p-3 border-t border-border bg-card flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={
                isConnected ? 'Type a real-time message...' : 'Connecting to chat...'
              }
              disabled={!isConnected}
              className="flex-1 rounded-xl border border-input bg-background px-3 py-2 text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!isConnected || !inputMessage.trim()}
              className="px-3 py-2 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors focus:outline-none flex items-center justify-center"
            >
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default LiveChatWidget;

"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Toast } from "@/components/Toast";
import { getToken } from "@/lib/auth";
import { getErrorMessage } from "@/lib/errors";
import { useAuth } from "@/context/AuthContext";
import { TaskPilotLogo } from "@/components/brand/TaskPilotLogo";
import {
  startConversation,
  sendMessage,
  closeConversation,
  getConversation,
  type Conversation,
  type Message,
  type MessageRole,
} from "@/services/aiApi";

// Language types and translations
type Language = "en" | "ur";

interface Translations {
  title: string;
  subtitle: string;
  back: string;
  logout: string;
  welcome: string;
  status: {
    active: string;
    closed: string;
  };
  newChat: string;
  closeChat: string;
  startChat: string;
  noConversation: {
    title: string;
    subtitle: string;
    startButton: string;
  };
  emptyConversation: {
    title: string;
    subtitle: string;
  };
  inputPlaceholder: string;
  inputPlaceholderDisabled: string;
  send: string;
  sending: string;
  aiTyping: string;
  characterCount: string;
  enterHint: string;
  chatClosed: string;
  chatStarted: string;
  notSignedIn: {
    title: string;
    message: string;
    button: string;
  };
}

const translations: Record<Language, Translations> = {
  en: {
    title: "AI Chat",
    subtitle: "Your Smart Copilot for Tasks",
    back: "Back",
    logout: "Logout",
    welcome: "Welcome,",
    status: {
      active: "Active",
      closed: "Closed",
    },
    newChat: "New Chat",
    closeChat: "Close Chat",
    startChat: "Start Chat",
    noConversation: {
      title: "Start a conversation with AI",
      subtitle: 'Click "Start Chat" to begin',
      startButton: "Start Chat",
    },
    emptyConversation: {
      title: "Start the conversation",
      subtitle: "Ask me anything about your tasks!",
    },
    inputPlaceholder: "Type your message...",
    inputPlaceholderDisabled: "Start a chat first...",
    send: "Send",
    sending: "Sending...",
    aiTyping: "AI is typing...",
    characterCount: "characters",
    enterHint: "Press Enter to send, Shift+Enter for new line",
    chatClosed: "Conversation closed!",
    chatStarted: "New conversation started!",
    notSignedIn: {
      title: "Not signed in",
      message: "Please sign in to chat with AI.",
      button: "Go to login",
    },
  },
  ur: {
    title: "AI چیٹ",
    subtitle: "آپ کے ٹاسکس کے لیے ہمکار",
    back: "واپس",
    logout: "لاگ آؤٹ",
    welcome: "خوش آمدید،",
    status: {
      active: "فعال",
      closed: "بند",
    },
    newChat: "نئی چیٹ",
    closeChat: "چیٹ بند کریں",
    startChat: "چیٹ شروع کریں",
    noConversation: {
      title: "AI کے سے بات چیت شروع کریں",
      subtitle: "شروع کرنے کے لیے 'چیٹ شروع کریں' پر کلک کریں",
      startButton: "چیٹ شروع کریں",
    },
    emptyConversation: {
      title: "بات چیت شروع کریں",
      subtitle: "اپنے ٹاسکس کے بارے میں کچھ بھی پوچھیں!",
    },
    inputPlaceholder: "اپنا پیغام لکھیں...",
    inputPlaceholderDisabled: "پہلے چیٹ شروع کریں...",
    send: "بھیجیں",
    sending: "بھیجا جا رہا ہے...",
    aiTyping: "AI لکھ رہا ہے...",
    characterCount: "حروف",
    enterHint: "بھیجنے کے لیے Enter دبائیں، نئی لائن کے لیے Shift+Enter",
    chatClosed: "بات چیت بند کر دی گئی!",
    chatStarted: "نئی بات چیت شروع ہو گئی!",
    notSignedIn: {
      title: "سائن ان نہیں ہیں",
      message: "AI سے بات چیت کرنے کے لیے براہ کرم سائن ان کریں۔",
      button: "لاگ ان پر جائیں",
    },
  },
};

const messageVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring" as const,
      stiffness: 300,
      damping: 24,
    },
  },
};

export default function ChatPage() {
  const { userName, logout: authLogout } = useAuth();
  const [token, setToken] = useState<string | null>(null);
  const [toast, setToast] = useState<{ kind: "error" | "success"; message: string } | null>(null);
  const [language, setLanguage] = useState<Language>("en");

  // Chat state
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get current translations
  const t = translations[language];

  // Toggle language
  function toggleLanguage() {
    setLanguage((prev) => (prev === "en" ? "ur" : "en"));
  }

  useEffect(() => {
    // Load token and initialize conversation on mount
    const t = getToken();
    setToken(t);

    if (!t) return;

    async function initConversation() {
      try {
        const conv = await startConversation(t, { language: "en" });
        setConversation(conv);

        // Load conversation with messages
        const fullConv = await getConversation(t, conv.id);
        if (fullConv.messages) {
          setMessages(fullConv.messages);
        }
      } catch (err) {
        setToast({ kind: "error", message: getErrorMessage(err) });
      }
    }

    void initConversation();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!token || !conversation || isSending) return;
    if (!input.trim()) return;

    setIsSending(true);
    const userMessage = input.trim();
    setInput("");

    // Optimistically add user message
    const optimisticUserMsg: Message = {
      id: Date.now(),
      conversation_id: conversation.id,
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);

    try {
      const aiResponse = await sendMessage(token, conversation.id, { content: userMessage, language });
      setMessages((prev) => [...prev, aiResponse]);

      // Check if a task was created
      if ("created_task" in aiResponse && aiResponse.created_task) {
        const task = aiResponse.created_task as { id: string; title: string; priority: string };
        const successMsg = language === "ur"
          ? `ٹاسک "${task.title}" کامیابی سے بن گیا!`
          : `Task "${task.title}" created successfully!`;
        setToast({ kind: "success", message: successMsg });
      }

      // Check if a task was deleted
      if ("deleted_task" in aiResponse && aiResponse.deleted_task) {
        const task = aiResponse.deleted_task as { id: string; title: string };
        const successMsg = language === "ur"
          ? `ٹاسک "${task.title}" حذف کر دیا گیا!`
          : `Task "${task.title}" deleted successfully!`;
        setToast({ kind: "success", message: successMsg });
      }

      // Check if a task was completed
      if ("completed_task" in aiResponse && aiResponse.completed_task) {
        const task = aiResponse.completed_task as { id: string; title: string };
        const successMsg = language === "ur"
          ? `ٹاسک "${task.title}" مکمل ہو گیا! شاباش!`
          : `Task "${task.title}" completed! Great job!`;
        setToast({ kind: "success", message: successMsg });
      }
    } catch (err) {
      setToast({ kind: "error", message: getErrorMessage(err) });
      // Remove optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== optimisticUserMsg.id));
    } finally {
      setIsSending(false);
    }
  }

  async function handleStartNew() {
    if (!token) return;

    setIsLoading(true);
    try {
      const conv = await startConversation(token, { language });
      setConversation(conv);
      setMessages([]);
      setToast({ kind: "success", message: t.chatStarted });
    } catch (err) {
      setToast({ kind: "error", message: getErrorMessage(err) });
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCloseConversation() {
    if (!token || !conversation) return;

    setIsLoading(true);
    try {
      await closeConversation(token, conversation.id);
      setConversation(null);
      setMessages([]);
      setToast({ kind: "success", message: t.chatClosed });
    } catch (err) {
      setToast({ kind: "error", message: getErrorMessage(err) });
    } finally {
      setIsLoading(false);
    }
  }

  function logout() {
    authLogout();
    setToken(null);
    window.location.href = "/login";
  }

  function messageBubbleClasses(role: MessageRole): string {
    const base = "max-w-[80%] rounded-2xl px-4 py-3 ";
    if (role === "user") {
      return base + "bg-gradient-to-r from-purple-600 to-pink-600 text-white ml-auto";
    }
    return base + "bg-white/10 border border-white/20 text-white mr-auto";
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 px-6 py-16 text-white">
        <div className="mx-auto max-w-md">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card title={t.notSignedIn.title}>
              <div className="flex flex-col gap-3">
                <p className="text-white/70">{t.notSignedIn.message}</p>
                <Button onClick={() => (window.location.href = "/login")}>{t.notSignedIn.button}</Button>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    );
  }

  const isUrdu = language === "ur";
  const dir = isUrdu ? "rtl" : "ltr";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 px-6 py-12 text-white" dir={dir}>
      {toast ? <Toast kind={toast.kind} message={toast.message} /> : null}

      <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between"
        >
          <div className="flex items-center gap-4">
            <Link href="/tasks">
              <Button
                variant="ghost"
                className="rounded-xl border border-white/10 hover:bg-white/10 hover:border-white/20"
              >
                {isUrdu ? "→" : "←"} {t.back}
              </Button>
            </Link>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-violet-400 via-cyan-400 to-violet-400 bg-clip-text text-transparent">
                {t.title}
              </h1>
              <p className="mt-1 text-sm text-white/60">{t.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* Language Switcher */}
            <Button
              variant="ghost"
              onClick={toggleLanguage}
              className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-sm font-medium text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-500/50"
            >
              {isUrdu ? "🇺🇸 English" : "🇵🇰 اردو"}
            </Button>

            {conversation && (
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${conversation.status === "active" ? "bg-green-500" : "bg-gray-500"}`}></span>
                <span className="text-xs text-white/70 uppercase">{conversation.status === "active" ? t.status.active : t.status.closed}</span>
              </div>
            )}
            {userName && (
              <span className="text-sm text-white/70">
                {t.welcome} <span className="font-semibold text-cyan-400">{userName}</span>
              </span>
            )}
            <Button
              variant="ghost"
              onClick={logout}
              className="rounded-xl border border-white/10 hover:bg-white/10 hover:border-white/20"
            >
              {t.logout}
            </Button>
          </div>
        </motion.header>

        {/* Chat Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex gap-3"
        >
          {conversation ? (
            <>
              <Button
                onClick={handleStartNew}
                loading={isLoading}
                className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600"
              >
                {t.newChat}
              </Button>
              <Button
                onClick={handleCloseConversation}
                loading={isLoading}
                variant="secondary"
                className="border border-white/20 hover:bg-white/10"
              >
                {t.closeChat}
              </Button>
            </>
          ) : (
            <Button
              onClick={handleStartNew}
              loading={isLoading}
              className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600"
            >
              {t.startChat}
            </Button>
          )}
        </motion.div>

        {/* Chat Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl max-w-none">
            <div className="flex flex-col h-[600px]">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                <AnimatePresence>
                  {!conversation ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex flex-col items-center justify-center h-full text-white/60"
                    >
                      <svg className="mb-4 h-16 w-16 text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      <p className="text-lg font-medium">{t.noConversation.title}</p>
                      <p className="text-sm mt-2">{t.noConversation.subtitle}</p>
                    </motion.div>
                  ) : messages.length === 0 ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex flex-col items-center justify-center h-full text-white/60"
                    >
                      <svg className="mb-4 h-16 w-16 text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      <p className="text-lg font-medium">{t.emptyConversation.title}</p>
                      <p className="text-sm mt-2">{t.emptyConversation.subtitle}</p>
                    </motion.div>
                  ) : (
                    messages.map((msg, index) => (
                      <motion.div
                        key={msg.id}
                        variants={messageVariants}
                        initial="hidden"
                        animate="visible"
                        transition={{ delay: index * 0.05 }}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                      >
                        <div className={messageBubbleClasses(msg.role)}>
                          <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
                          <p className="text-xs opacity-60 mt-1">
                            {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </motion.div>
                    ))
                  )}
                  {isSending && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex justify-start"
                    >
                      <div className="bg-white/10 border border-white/20 text-white rounded-2xl px-4 py-3 mr-auto">
                        <div className="flex items-center gap-2">
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            className="h-4 w-4 rounded-full border-2 border-cyan-500 border-t-transparent"
                          />
                          <span className="text-sm text-white/60">{t.aiTyping}</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-white/10 p-4">
                <form onSubmit={handleSendMessage} className="flex gap-3">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={!conversation || isSending}
                    placeholder={conversation ? t.inputPlaceholder : t.inputPlaceholderDisabled}
                    className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-white/40 focus:border-cyan-500/50 focus:bg-white/10 focus:outline-none disabled:opacity-50"
                  />
                  <Button
                    type="submit"
                    loading={isSending}
                    disabled={!conversation || !input.trim()}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 px-6"
                  >
                    {isSending ? t.sending : t.send}
                  </Button>
                </form>
                <div className="flex items-center justify-between mt-2 text-xs text-white/40">
                  <span>{input.length} / 10,000 {t.characterCount}</span>
                  <span className="hidden sm:inline">{t.enterHint}</span>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}

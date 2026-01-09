/**
 * Local ChatGPT Simulator
 *
 * A development tool that simulates ChatGPT's widget rendering environment.
 * Uses OpenAI's API with MCP tools to display interactive widgets locally.
 */

import { useState, useRef, useEffect } from "react";
import { Send, Plus, Sun, Moon, Maximize2, X } from "lucide-react";
import WidgetRenderer from "./WidgetRenderer";

interface WidgetData {
  html: string;
  toolOutput: Record<string, unknown>;
  toolName: string;
}

interface Message {
  id: string;
  role: "user" | "assistant" | "error";
  content: string;
  widget?: WidgetData;
  timestamp: Date;
}

const EXAMPLE_PROMPTS = [
  "Show me a carousel of restaurants",
  "Display a dashboard with stats",
  "Show me a photo gallery",
  "Create a todo list",
  "Show me the solar system",
  "Display a shopping cart",
];

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [expandedWidget, setExpandedWidget] = useState<WidgetData | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = async (messageText?: string) => {
    const text = messageText || input;
    if (!text.trim() || loading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || "Request failed");
      }

      const widgetData: WidgetData | undefined = data.widget
        ? {
            html: data.widget.html,
            toolOutput: data.widget.tool_output,
            toolName: data.widget.tool_name,
          }
        : undefined;

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.message || "Here's what I found:",
        widget: widgetData,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "error",
        content:
          error instanceof Error ? error.message : "An error occurred",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const newConversation = async () => {
    try {
      await fetch("/chat/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    } catch {
      // Ignore reset errors
    }
    setMessages([]);
    setExpandedWidget(null);
    inputRef.current?.focus();
  };

  const handleWidgetMessage = (message: { type: string; [key: string]: unknown }) => {
    console.log("Widget message:", message);

    if (message.type === "sendFollowUp" && typeof message.prompt === "string") {
      sendMessage(message.prompt);
    }

    if (message.type === "requestDisplayMode" && message.mode === "fullscreen") {
      // Find the widget that requested fullscreen
      const lastWidgetMsg = [...messages].reverse().find(m => m.widget);
      if (lastWidgetMsg?.widget) {
        setExpandedWidget(lastWidgetMsg.widget);
      }
    }
  };

  const isDark = theme === "dark";

  return (
    <div className={`h-screen flex flex-col ${isDark ? "bg-gray-900" : "bg-gray-50"}`}>
      {/* Header */}
      <header
        className={`px-4 py-3 border-b flex items-center justify-between ${
          isDark ? "border-gray-700 bg-gray-900" : "border-gray-200 bg-white"
        }`}
      >
        <div className="flex items-center gap-3">
          <button
            onClick={newConversation}
            className={`p-2 rounded-lg transition-colors ${
              isDark
                ? "hover:bg-gray-800 text-gray-400 hover:text-white"
                : "hover:bg-gray-100 text-gray-600 hover:text-gray-900"
            }`}
            title="New conversation"
          >
            <Plus size={20} />
          </button>
          <div>
            <h1 className={`text-lg font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>
              ChatGPT Simulator
            </h1>
          </div>
        </div>
        <button
          onClick={() => setTheme(isDark ? "light" : "dark")}
          className={`p-2 rounded-lg transition-colors ${
            isDark
              ? "hover:bg-gray-800 text-gray-400"
              : "hover:bg-gray-100 text-gray-600"
          }`}
          title={`Switch to ${isDark ? "light" : "dark"} mode`}
        >
          {isDark ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <h2 className={`text-2xl font-semibold mb-2 ${isDark ? "text-white" : "text-gray-900"}`}>
                ChatGPT Widget Simulator
              </h2>
              <p className={`text-sm mb-6 ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                Test your widgets locally before deploying to ChatGPT
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {EXAMPLE_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => sendMessage(prompt)}
                    className={`px-4 py-2 text-sm rounded-full transition-colors ${
                      isDark
                        ? "bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700"
                        : "bg-white hover:bg-gray-50 text-gray-700 border border-gray-200"
                    }`}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className="space-y-3">
              {/* Message */}
              <div className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white"
                      : msg.role === "error"
                      ? isDark
                        ? "bg-red-900/50 text-red-300 border border-red-800"
                        : "bg-red-50 text-red-700 border border-red-200"
                      : isDark
                      ? "bg-gray-800 text-gray-100"
                      : "bg-white text-gray-900 border border-gray-200"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>

              {/* Inline Widget */}
              {msg.widget && (
                <div className={`rounded-2xl overflow-hidden border ${
                  isDark ? "border-gray-700 bg-gray-800" : "border-gray-200 bg-white"
                }`}>
                  {/* Widget Header */}
                  <div className={`px-4 py-2 flex items-center justify-between border-b ${
                    isDark ? "border-gray-700" : "border-gray-100"
                  }`}>
                    <span className={`text-sm font-medium ${isDark ? "text-gray-300" : "text-gray-600"}`}>
                      {msg.widget.toolName.replace("show_", "").replace(/_/g, " ")}
                    </span>
                    <button
                      onClick={() => setExpandedWidget(msg.widget!)}
                      className={`p-1.5 rounded-lg transition-colors ${
                        isDark
                          ? "hover:bg-gray-700 text-gray-400"
                          : "hover:bg-gray-100 text-gray-500"
                      }`}
                      title="Expand"
                    >
                      <Maximize2 size={16} />
                    </button>
                  </div>
                  {/* Widget Content */}
                  <div className="h-[400px]">
                    <WidgetRenderer
                      html={msg.widget.html}
                      toolOutput={msg.widget.toolOutput}
                      theme={theme}
                      onMessage={handleWidgetMessage}
                    />
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div
                className={`rounded-2xl px-4 py-3 ${
                  isDark ? "bg-gray-800" : "bg-white border border-gray-200"
                }`}
              >
                <div className="flex items-center gap-1">
                  <div
                    className={`w-2 h-2 rounded-full animate-bounce ${
                      isDark ? "bg-gray-500" : "bg-gray-400"
                    }`}
                    style={{ animationDelay: "0ms" }}
                  />
                  <div
                    className={`w-2 h-2 rounded-full animate-bounce ${
                      isDark ? "bg-gray-500" : "bg-gray-400"
                    }`}
                    style={{ animationDelay: "150ms" }}
                  />
                  <div
                    className={`w-2 h-2 rounded-full animate-bounce ${
                      isDark ? "bg-gray-500" : "bg-gray-400"
                    }`}
                    style={{ animationDelay: "300ms" }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className={`border-t ${isDark ? "border-gray-700 bg-gray-900" : "border-gray-200 bg-white"}`}>
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className={`flex items-center gap-3 rounded-2xl border px-4 py-2 ${
            isDark
              ? "bg-gray-800 border-gray-700"
              : "bg-white border-gray-200"
          }`}>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
              placeholder="Message ChatGPT..."
              disabled={loading}
              className={`flex-1 bg-transparent outline-none ${
                isDark
                  ? "text-white placeholder-gray-500"
                  : "text-gray-900 placeholder-gray-400"
              }`}
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className={`p-2 rounded-lg transition-colors ${
                input.trim()
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : isDark
                  ? "text-gray-600"
                  : "text-gray-300"
              }`}
            >
              <Send size={18} />
            </button>
          </div>
          <p className={`text-xs text-center mt-2 ${isDark ? "text-gray-500" : "text-gray-400"}`}>
            Local simulator for ChatGPT widget development
          </p>
        </div>
      </div>

      {/* Fullscreen Widget Modal */}
      {expandedWidget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className={`w-full h-full max-w-4xl max-h-[90vh] m-4 rounded-2xl overflow-hidden flex flex-col ${
            isDark ? "bg-gray-900" : "bg-white"
          }`}>
            {/* Modal Header */}
            <div className={`px-4 py-3 flex items-center justify-between border-b ${
              isDark ? "border-gray-700" : "border-gray-200"
            }`}>
              <span className={`font-medium ${isDark ? "text-white" : "text-gray-900"}`}>
                {expandedWidget.toolName.replace("show_", "").replace(/_/g, " ")}
              </span>
              <button
                onClick={() => setExpandedWidget(null)}
                className={`p-2 rounded-lg transition-colors ${
                  isDark
                    ? "hover:bg-gray-800 text-gray-400"
                    : "hover:bg-gray-100 text-gray-500"
                }`}
              >
                <X size={20} />
              </button>
            </div>
            {/* Modal Content */}
            <div className="flex-1 overflow-hidden">
              <WidgetRenderer
                html={expandedWidget.html}
                toolOutput={expandedWidget.toolOutput}
                theme={theme}
                displayMode="fullscreen"
                onMessage={handleWidgetMessage}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

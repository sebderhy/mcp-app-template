/**
 * Local ChatGPT Simulator
 *
 * A development tool that simulates ChatGPT's widget rendering environment.
 * Uses OpenAI's API with MCP tools to display interactive widgets locally.
 */

import { useState, useRef, useEffect } from "react";
import { Send, RotateCcw, Sun, Moon, Maximize2, Minimize2 } from "lucide-react";
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
  const [widgetFullscreen, setWidgetFullscreen] = useState(false);
  const [currentWidget, setCurrentWidget] = useState<WidgetData | null>(null);

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

      // Update current widget if present
      if (widgetData) {
        setCurrentWidget(widgetData);
      }

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

  const resetChat = async () => {
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
    setCurrentWidget(null);
    inputRef.current?.focus();
  };

  const handleWidgetMessage = (message: { type: string; [key: string]: unknown }) => {
    console.log("Widget message:", message);

    if (message.type === "sendFollowUp" && typeof message.prompt === "string") {
      sendMessage(message.prompt);
    }

    if (message.type === "requestDisplayMode") {
      if (message.mode === "fullscreen") {
        setWidgetFullscreen(true);
      } else {
        setWidgetFullscreen(false);
      }
    }
  };

  const isDark = theme === "dark";

  return (
    <div className={`h-screen flex ${isDark ? "bg-gray-900" : "bg-gray-50"}`}>
      {/* Chat Panel */}
      <div
        className={`${
          widgetFullscreen ? "hidden" : "w-1/2"
        } flex flex-col border-r ${
          isDark ? "border-gray-700 bg-gray-900" : "border-gray-200 bg-white"
        }`}
      >
        {/* Header */}
        <header
          className={`p-4 border-b flex items-center justify-between ${
            isDark ? "border-gray-700" : "border-gray-200"
          }`}
        >
          <div>
            <h1
              className={`text-lg font-semibold ${
                isDark ? "text-white" : "text-gray-900"
              }`}
            >
              ChatGPT Simulator
            </h1>
            <p className={`text-sm ${isDark ? "text-gray-400" : "text-gray-500"}`}>
              Local widget development environment
            </p>
          </div>
          <div className="flex items-center gap-2">
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
            <button
              onClick={resetChat}
              className={`p-2 rounded-lg transition-colors ${
                isDark
                  ? "hover:bg-gray-800 text-gray-400"
                  : "hover:bg-gray-100 text-gray-600"
              }`}
              title="Reset conversation"
            >
              <RotateCcw size={20} />
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <p
                className={`text-sm mb-4 ${
                  isDark ? "text-gray-400" : "text-gray-500"
                }`}
              >
                Try one of these prompts:
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {EXAMPLE_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => sendMessage(prompt)}
                    className={`px-3 py-2 text-sm rounded-lg transition-colors ${
                      isDark
                        ? "bg-gray-800 hover:bg-gray-700 text-gray-300"
                        : "bg-gray-100 hover:bg-gray-200 text-gray-700"
                    }`}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : msg.role === "error"
                    ? isDark
                      ? "bg-red-900/50 text-red-300 border border-red-800"
                      : "bg-red-50 text-red-700 border border-red-200"
                    : isDark
                    ? "bg-gray-800 text-gray-100"
                    : "bg-gray-100 text-gray-900"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.widget && (
                  <p
                    className={`text-xs mt-2 ${
                      msg.role === "user"
                        ? "text-blue-200"
                        : isDark
                        ? "text-gray-500"
                        : "text-gray-400"
                    }`}
                  >
                    Widget: {msg.widget.toolName}
                  </p>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div
                className={`rounded-2xl px-4 py-3 ${
                  isDark ? "bg-gray-800" : "bg-gray-100"
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

        {/* Input */}
        <div className={`p-4 border-t ${isDark ? "border-gray-700" : "border-gray-200"}`}>
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
              placeholder="Ask me to show a widget..."
              disabled={loading}
              className={`flex-1 px-4 py-3 rounded-xl border outline-none transition-colors ${
                isDark
                  ? "bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-blue-500"
                  : "bg-white border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500"
              }`}
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="px-4 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Widget Panel */}
      <div
        className={`${
          widgetFullscreen ? "w-full" : "w-1/2"
        } flex flex-col ${isDark ? "bg-gray-800" : "bg-gray-100"}`}
      >
        {/* Widget Header */}
        <header
          className={`p-4 border-b flex items-center justify-between ${
            isDark ? "border-gray-700" : "border-gray-200"
          }`}
        >
          <div>
            <h2
              className={`font-medium ${isDark ? "text-white" : "text-gray-900"}`}
            >
              Widget Preview
            </h2>
            {currentWidget && (
              <p className={`text-sm ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                {currentWidget.toolName}
              </p>
            )}
          </div>
          {currentWidget && (
            <button
              onClick={() => setWidgetFullscreen(!widgetFullscreen)}
              className={`p-2 rounded-lg transition-colors ${
                isDark
                  ? "hover:bg-gray-700 text-gray-400"
                  : "hover:bg-gray-200 text-gray-600"
              }`}
              title={widgetFullscreen ? "Exit fullscreen" : "Fullscreen"}
            >
              {widgetFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
            </button>
          )}
        </header>

        {/* Widget Content */}
        <div className="flex-1 p-4 overflow-hidden">
          {currentWidget ? (
            <div className="h-full rounded-xl overflow-hidden shadow-lg">
              <WidgetRenderer
                html={currentWidget.html}
                toolOutput={currentWidget.toolOutput}
                theme={theme}
                onMessage={handleWidgetMessage}
              />
            </div>
          ) : (
            <div
              className={`h-full flex items-center justify-center rounded-xl border-2 border-dashed ${
                isDark
                  ? "border-gray-700 text-gray-500"
                  : "border-gray-300 text-gray-400"
              }`}
            >
              <div className="text-center">
                <p className="text-lg mb-2">No widget loaded</p>
                <p className="text-sm">
                  Send a message to display a widget here
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

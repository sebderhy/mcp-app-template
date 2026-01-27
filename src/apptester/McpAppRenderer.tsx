/**
 * MCP App Renderer Component
 *
 * Renders MCP Apps in a sandboxed iframe and implements the host-side
 * of the MCP Apps protocol (JSON-RPC over postMessage).
 *
 * This is the "App Bridge" that connects the app to the host.
 */

import { useEffect, useRef, useCallback } from "react";

interface McpAppRendererProps {
  /** The widget HTML to render */
  html: string;
  /** Tool output/structured content to pass to the widget */
  toolOutput: Record<string, unknown>;
  /** Current theme */
  theme?: "light" | "dark";
  /** Display mode */
  displayMode?: "inline" | "fullscreen";
  /** Callback for messages from the app */
  onMessage?: (message: McpAppMessage) => void;
  /** Callback when app requests a tool call */
  onToolCall?: (name: string, args: Record<string, unknown>) => Promise<unknown>;
}

interface McpAppMessage {
  type: string;
  [key: string]: unknown;
}

interface JsonRpcRequest {
  jsonrpc: "2.0";
  id?: string | number;
  method: string;
  params?: Record<string, unknown>;
}

interface JsonRpcResponse {
  jsonrpc: "2.0";
  id: string | number;
  result?: unknown;
  error?: { code: number; message: string; data?: unknown };
}

interface JsonRpcNotification {
  jsonrpc: "2.0";
  method: string;
  params?: Record<string, unknown>;
}

let messageIdCounter = 0;

export default function McpAppRenderer({
  html,
  toolOutput,
  theme = "light",
  displayMode = "inline",
  onMessage,
  onToolCall,
}: McpAppRendererProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const initializedRef = useRef(false);

  // Send a JSON-RPC notification to the app
  const sendNotification = useCallback((method: string, params?: Record<string, unknown>) => {
    const iframe = iframeRef.current;
    if (!iframe?.contentWindow) return;

    const notification: JsonRpcNotification = {
      jsonrpc: "2.0",
      method,
      params,
    };

    iframe.contentWindow.postMessage(notification, "*");
  }, []);

  // Send a JSON-RPC response to the app
  const sendResponse = useCallback((id: string | number, result?: unknown, error?: { code: number; message: string }) => {
    const iframe = iframeRef.current;
    if (!iframe?.contentWindow) return;

    const response: JsonRpcResponse = {
      jsonrpc: "2.0",
      id,
    };

    if (error) {
      response.error = error;
    } else {
      response.result = result;
    }

    iframe.contentWindow.postMessage(response, "*");
  }, []);

  // Handle incoming JSON-RPC messages from the app
  const handleMessage = useCallback(
    async (event: MessageEvent) => {
      const iframe = iframeRef.current;
      if (!iframe || event.source !== iframe.contentWindow) return;

      const data = event.data;

      // Check if it's a JSON-RPC message
      if (data?.jsonrpc !== "2.0") {
        // Legacy message format - forward to onMessage
        if (onMessage && data?.type) {
          onMessage(data);
        }
        return;
      }

      const request = data as JsonRpcRequest;

      // Handle different methods
      switch (request.method) {
        case "ui/initialize": {
          // App is requesting initialization - send back capabilities and initial data
          sendResponse(request.id!, {
            protocolVersion: "2025-01-01",
            capabilities: {
              tools: true,
              context: true,
              theme: true,
            },
            theme,
          });

          // Send the tool result to the app
          setTimeout(() => {
            sendNotification("ui/toolResult", {
              content: [{ type: "text", text: JSON.stringify(toolOutput) }],
              structuredContent: toolOutput,
            });
          }, 50);

          initializedRef.current = true;
          break;
        }

        case "tools/call": {
          // App is requesting a tool call
          const params = request.params as { name: string; arguments?: Record<string, unknown> };
          const toolName = params?.name;
          const toolArgs = params?.arguments ?? {};

          if (onToolCall) {
            try {
              const result = await onToolCall(toolName, toolArgs);
              sendResponse(request.id!, {
                content: [{ type: "text", text: JSON.stringify(result) }],
              });
            } catch (err) {
              sendResponse(request.id!, undefined, {
                code: -32000,
                message: err instanceof Error ? err.message : "Tool call failed",
              });
            }
          } else {
            sendResponse(request.id!, undefined, {
              code: -32601,
              message: "Tool calls not supported",
            });
          }
          break;
        }

        case "ui/updateContext": {
          // App is updating the model context
          onMessage?.({ type: "updateContext", data: request.params });
          sendResponse(request.id!, { success: true });
          break;
        }

        case "ui/openLink": {
          // App wants to open an external link
          const url = (request.params as { url?: string })?.url;
          if (url) {
            window.open(url, "_blank", "noopener,noreferrer");
          }
          sendResponse(request.id!, { success: true });
          break;
        }

        case "ui/requestDisplayMode": {
          // App is requesting a display mode change
          const mode = (request.params as { mode?: string })?.mode;
          onMessage?.({ type: "requestDisplayMode", mode });
          sendResponse(request.id!, { mode });
          break;
        }

        case "ui/log": {
          // App is sending a log message
          const level = (request.params as { level?: string })?.level || "info";
          const message = (request.params as { message?: string })?.message;
          console[level as "log" | "info" | "warn" | "error"]?.("[MCP App]", message);
          break;
        }

        default:
          // Unknown method
          if (request.id) {
            sendResponse(request.id, undefined, {
              code: -32601,
              message: `Method not found: ${request.method}`,
            });
          }
      }
    },
    [onMessage, onToolCall, sendNotification, sendResponse, theme, toolOutput]
  );

  // Set up message listener
  useEffect(() => {
    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [handleMessage]);

  // Load the HTML into the iframe
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    initializedRef.current = false;

    // Inject a small bootstrap script that the MCP Apps SDK expects
    // This sets up the postMessage bridge before the app loads
    const bootstrapScript = `
      <script>
        // MCP Apps bridge bootstrap
        window.__MCP_APP_HOST__ = true;
        window.__MCP_APP_THEME__ = "${theme}";
        window.__MCP_APP_DISPLAY_MODE__ = "${displayMode}";

        // Also provide legacy window.openai for backward compatibility
        window.openai = {
          theme: "${theme}",
          displayMode: "${displayMode}",
          maxHeight: ${displayMode === "fullscreen" ? 900 : 400},
          toolOutput: ${JSON.stringify(toolOutput)},

          // Legacy API methods that use postMessage
          callTool: async (name, args) => {
            const id = Date.now();
            return new Promise((resolve, reject) => {
              const handler = (event) => {
                if (event.data?.jsonrpc === "2.0" && event.data?.id === id) {
                  window.removeEventListener("message", handler);
                  if (event.data.error) {
                    reject(new Error(event.data.error.message));
                  } else {
                    resolve(event.data.result);
                  }
                }
              };
              window.addEventListener("message", handler);
              window.parent.postMessage({
                jsonrpc: "2.0",
                id,
                method: "tools/call",
                params: { name, arguments: args }
              }, "*");
            });
          },

          openExternal: ({ href }) => {
            window.parent.postMessage({
              jsonrpc: "2.0",
              id: Date.now(),
              method: "ui/openLink",
              params: { url: href }
            }, "*");
          },

          requestDisplayMode: async ({ mode }) => {
            window.parent.postMessage({
              jsonrpc: "2.0",
              id: Date.now(),
              method: "ui/requestDisplayMode",
              params: { mode }
            }, "*");
            return { mode };
          },

          sendFollowUpMessage: async ({ prompt }) => {
            window.parent.postMessage({ type: "sendFollowUp", prompt }, "*");
          },

          setWidgetState: async (state) => {
            window.openai.widgetState = state;
          },
        };

        // Dispatch event for legacy widgets
        window.dispatchEvent(new CustomEvent("openai:set_globals", {
          detail: { globals: window.openai }
        }));
      </script>
    `;

    // Inject the bootstrap script into the HTML head
    const modifiedHtml = html.replace("<head>", `<head>${bootstrapScript}`);

    // Write to iframe
    iframe.srcdoc = modifiedHtml;
  }, [html, toolOutput, theme, displayMode]);

  // Notify app when theme changes
  useEffect(() => {
    if (initializedRef.current) {
      sendNotification("ui/themeChange", { theme });
    }
  }, [theme, sendNotification]);

  return (
    <iframe
      ref={iframeRef}
      className="w-full h-full border-0 rounded-lg bg-white"
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
      title="MCP App"
    />
  );
}

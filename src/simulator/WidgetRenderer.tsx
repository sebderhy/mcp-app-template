/**
 * Widget Renderer Component
 *
 * Renders widget HTML in an iframe and injects window.openai
 * with the tool output data, mimicking ChatGPT's behavior.
 */

import { useEffect, useRef } from "react";

interface WidgetRendererProps {
  html: string;
  toolOutput: Record<string, unknown>;
  theme?: "light" | "dark";
  displayMode?: "inline" | "fullscreen";
  onMessage?: (message: { type: string; [key: string]: unknown }) => void;
}

export default function WidgetRenderer({
  html,
  toolOutput,
  theme = "light",
  displayMode = "inline",
  onMessage,
}: WidgetRendererProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    // Script to inject window.openai before the widget loads
    const injectionScript = `
      <script>
        window.openai = {
          // Theme and layout
          theme: "${theme}",
          displayMode: "${displayMode}",
          maxHeight: ${displayMode === "fullscreen" ? 900 : 400},
          safeArea: { top: 0, bottom: 0, left: 0, right: 0 },
          locale: "en-US",
          userAgent: { platform: "simulator", version: "1.0.0" },

          // Data from tool call
          toolInput: {},
          toolOutput: ${JSON.stringify(toolOutput)},
          toolResponseMetadata: null,
          widgetState: null,

          // API Methods - communicate with parent via postMessage
          callTool: async (name, args) => {
            window.parent.postMessage({ type: 'callTool', name, args }, '*');
            return new Promise((resolve) => {
              const handler = (event) => {
                if (event.data.type === 'callToolResult' && event.data.name === name) {
                  window.removeEventListener('message', handler);
                  resolve({ result: event.data.result });
                }
              };
              window.addEventListener('message', handler);
            });
          },

          setWidgetState: async (state) => {
            window.openai.widgetState = state;
            window.parent.postMessage({ type: 'setWidgetState', state }, '*');
          },

          sendFollowUpMessage: async ({ prompt }) => {
            window.parent.postMessage({ type: 'sendFollowUp', prompt }, '*');
          },

          openExternal: ({ href }) => {
            window.parent.postMessage({ type: 'openExternal', href }, '*');
          },

          requestDisplayMode: async ({ mode }) => {
            window.parent.postMessage({ type: 'requestDisplayMode', mode }, '*');
            return { mode };
          },

          requestModal: async ({ title, params }) => {
            window.parent.postMessage({ type: 'requestModal', title, params }, '*');
            return {};
          },

          requestClose: async () => {
            window.parent.postMessage({ type: 'requestClose' }, '*');
          },
        };

        // Dispatch event to notify widget that openai is ready
        window.dispatchEvent(new CustomEvent('openai:set_globals'));
      </script>
    `;

    // Inject the script into the HTML head
    const modifiedHtml = html.replace("<head>", `<head>${injectionScript}`);

    // Write to iframe using srcdoc
    iframe.srcdoc = modifiedHtml;
  }, [html, toolOutput, theme, displayMode]);

  // Listen for messages from iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Only handle messages from our iframe
      if (event.source !== iframeRef.current?.contentWindow) return;

      const { type } = event.data;

      // Handle external link opening
      if (type === "openExternal" && event.data.href) {
        window.open(event.data.href, "_blank", "noopener,noreferrer");
        return;
      }

      // Forward other messages to parent component
      if (onMessage) {
        onMessage(event.data);
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [onMessage]);

  return (
    <iframe
      ref={iframeRef}
      className="w-full h-full border-0 rounded-lg bg-white"
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
      title="Widget Preview"
    />
  );
}

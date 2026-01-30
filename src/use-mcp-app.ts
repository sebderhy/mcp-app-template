/**
 * MCP Apps React Hook
 *
 * Provides React integration with the MCP Apps protocol.
 * This replaces the OpenAI-specific hooks with a cross-platform MCP Apps implementation.
 *
 * Usage:
 *   const { props, theme, callTool, ready } = useMcpApp<MyToolOutput>();
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { App } from "@modelcontextprotocol/ext-apps";

export type Theme = "light" | "dark";
export type DisplayMode = "inline" | "fullscreen" | "pip";

interface McpAppState<T> {
  /** Tool result data from the server */
  props: T | null;
  /** Current theme */
  theme: Theme;
  /** Current display mode */
  displayMode: DisplayMode;
  /** Whether the app is connected to the host */
  ready: boolean;
  /** Call a server tool */
  callTool: (name: string, args?: Record<string, unknown>) => Promise<unknown>;
  /** Update the model's context */
  updateContext: (data: Record<string, unknown>) => void;
  /** Open an external URL */
  openLink: (url: string) => void;
}

interface UseMcpAppOptions<T> {
  /** Default props to use while loading or in standalone mode */
  defaultProps?: T;
  /** App name for identification */
  name?: string;
  /** App version */
  version?: string;
}

/**
 * React hook for MCP Apps integration.
 * Handles connection to the host and provides tool results.
 */
export function useMcpApp<T extends Record<string, unknown>>(
  options: UseMcpAppOptions<T> = {}
): McpAppState<T> {
  const { defaultProps, name = "MCP App", version = "1.0.0" } = options;

  const [props, setProps] = useState<T | null>(defaultProps ?? null);
  const [theme, setTheme] = useState<Theme>("light");
  const [displayMode, setDisplayMode] = useState<DisplayMode>("inline");
  const [ready, setReady] = useState(false);

  const appRef = useRef<App | null>(null);

  useEffect(() => {
    // Check if we're in an MCP Apps host environment
    const inIframe = window !== window.parent;

    if (!inIframe) {
      // Standalone mode - use default props
      setReady(true);
      return;
    }

    // Create and connect the MCP App
    const app = new App({ name, version });
    appRef.current = app;

    // Handle tool results from the host
    app.ontoolresult = (result) => {
      // Extract the structured content from the tool result
      const textContent = result.content?.find((c) => c.type === "text");
      if (textContent && "text" in textContent) {
        try {
          // Try to parse as JSON (structured content)
          const parsed = JSON.parse(textContent.text);
          setProps(parsed as T);
        } catch {
          // Not JSON, might be plain text - wrap it
          setProps({ text: textContent.text } as unknown as T);
        }
      }

      // Also check for structured content passed directly
      if (result.structuredContent) {
        setProps(result.structuredContent as T);
      }
    };

    // Handle theme changes
    app.onthemechange = (newTheme) => {
      setTheme(newTheme as Theme);
    };

    // Connect to host
    app.connect();
    setReady(true);

    return () => {
      appRef.current = null;
    };
  }, [name, version]);

  const callTool = useCallback(
    async (toolName: string, args?: Record<string, unknown>) => {
      if (!appRef.current) {
        console.warn("MCP App not connected, cannot call tool");
        return null;
      }

      const result = await appRef.current.callServerTool({
        name: toolName,
        arguments: args ?? {},
      });

      return result;
    },
    []
  );

  const updateContext = useCallback((data: Record<string, unknown>) => {
    if (!appRef.current) {
      console.warn("MCP App not connected, cannot update context");
      return;
    }

    appRef.current.updateContext(data);
  }, []);

  const openLink = useCallback((url: string) => {
    if (appRef.current) {
      appRef.current.sendOpenLink(url);
    } else {
      // Fallback for standalone mode
      window.open(url, "_blank", "noopener,noreferrer");
    }
  }, []);

  return {
    props,
    theme,
    displayMode,
    ready,
    callTool,
    updateContext,
    openLink,
  };
}

/**
 * Standalone hook for just getting tool props.
 * Simpler API for widgets that only need to read data.
 */
export function useToolProps<T extends Record<string, unknown>>(
  defaultProps?: T
): T | null {
  const { props } = useMcpApp<T>({ defaultProps });
  return props ?? defaultProps ?? null;
}

/**
 * Standalone hook for getting the current theme.
 */
export function useMcpTheme(): Theme {
  const { theme } = useMcpApp();
  return theme;
}

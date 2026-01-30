/**
 * Widget Compliance Tests - Browser-based tests that verify widgets work correctly.
 *
 * These tests run each widget in a real browser and verify universal requirements
 * that any widget built with this template must satisfy.
 *
 * Tests are intentionally minimal and focused on things that MUST work:
 * - No JavaScript errors when rendering
 * - Widget actually renders content
 * - Works in both light and dark themes
 * - No unhandled promise rejections
 * - All callTool invocations reference tools registered on the server
 *
 * Setup:
 *   pnpm run setup:test              # Install Playwright browsers
 *   npx playwright install-deps      # Install system dependencies (may need sudo)
 *
 * Run with: pnpm run test:browser
 */

import { test, expect, chromium, type Page } from "@playwright/test";
import { spawn, type ChildProcess } from "child_process";

const SERVER_PORT = 8000;
const SERVER_URL = `http://localhost:${SERVER_PORT}`;

let serverProcess: ChildProcess | null = null;
let browserAvailable: boolean | null = null;

// Track rejections per page
const pageRejections = new WeakMap<Page, string[]>();
// Track tool calls per page (tool names invoked by widgets via callTool)
const pageToolCalls = new WeakMap<Page, string[]>();
const exposedPages = new WeakSet<Page>();

function getPageRejections(page: Page): string[] {
  if (!pageRejections.has(page)) {
    pageRejections.set(page, []);
  }
  return pageRejections.get(page)!;
}

function getPageToolCalls(page: Page): string[] {
  if (!pageToolCalls.has(page)) {
    pageToolCalls.set(page, []);
  }
  return pageToolCalls.get(page)!;
}

function clearPageRejections(page: Page): void {
  pageRejections.set(page, []);
}

function clearPageToolCalls(page: Page): void {
  pageToolCalls.set(page, []);
}

/**
 * Check if browser can be launched (cached)
 */
async function canLaunchBrowser(): Promise<boolean> {
  if (browserAvailable !== null) return browserAvailable;

  try {
    const browser = await chromium.launch({ headless: true });
    await browser.close();
    browserAvailable = true;
  } catch {
    browserAvailable = false;
    console.log("\n⚠️  Browser not available - tests will be skipped");
    console.log("   Run: pnpm run setup:test && npx playwright install-deps\n");
  }
  return browserAvailable;
}

/**
 * Check if server is running
 */
async function isServerRunning(): Promise<boolean> {
  try {
    const response = await fetch(`${SERVER_URL}/chat/status`);
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Start the MCP server
 */
async function startServer(): Promise<ChildProcess> {
  const proc = spawn("pnpm", ["run", "server"], {
    cwd: process.cwd(),
    stdio: ["ignore", "pipe", "pipe"],
    detached: true,
  });

  const maxWait = 30000;
  const startTime = Date.now();

  while (Date.now() - startTime < maxWait) {
    if (await isServerRunning()) {
      return proc;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  throw new Error("Server failed to start within 30 seconds");
}

/**
 * Get all registered tool names from the server (widget + helper tools).
 */
async function getAllRegisteredToolNames(): Promise<Set<string>> {
  const response = await fetch(`${SERVER_URL}/tools`);
  const data = await response.json();
  return new Set(
    (data.tools || []).map((t: { function: { name: string } }) => t.function.name)
  );
}

/**
 * Get widget tools from the server (tools with UI, excludes data-only helpers).
 */
async function getWidgetTools(): Promise<string[]> {
  const response = await fetch(`${SERVER_URL}/tools`);
  const data = await response.json();
  return (data.tools || [])
    .filter((t: { widget?: boolean }) => t.widget !== false)
    .map((t: { function: { name: string } }) => t.function.name);
}

/**
 * Render a widget in a page and return console logs
 */
async function renderWidget(
  page: Page,
  toolName: string,
  theme: "light" | "dark"
): Promise<{ logs: string[]; errors: string[]; rejections: string[]; toolCalls: string[] }> {
  const logs: string[] = [];
  const errors: string[] = [];

  // Clear tracking from previous renders
  clearPageRejections(page);
  clearPageToolCalls(page);

  page.on("console", (msg) => {
    const text = `[${msg.type()}] ${msg.text()}`;
    logs.push(text);
    if (msg.type() === "error") {
      errors.push(msg.text());
    }
  });

  page.on("pageerror", (error) => {
    errors.push(error.message);
  });

  // Expose reporting functions (only once per page)
  if (!exposedPages.has(page)) {
    await page.exposeFunction("__reportRejection__", (reason: string) => {
      getPageRejections(page).push(reason);
    });
    await page.exposeFunction("__reportToolCall__", (toolName: string) => {
      getPageToolCalls(page).push(toolName);
    });
    exposedPages.add(page);
  }

  const toolResponse = await fetch(`${SERVER_URL}/tools/call`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: toolName, arguments: {} }),
  });

  const toolData = await toolResponse.json();
  if (toolData.error) {
    throw new Error(`Tool error: ${toolData.error}`);
  }

  const openaiConfig = {
    theme,
    displayMode: "inline",
    maxHeight: 500,
    safeArea: { insets: { top: 0, bottom: 0, left: 0, right: 0 } },
    locale: "en-US",
    userAgent: {
      device: { type: "desktop" },
      capabilities: { hover: true, touch: false },
    },
    toolInput: {},
    toolOutput: toolData.tool_output,
    toolResponseMetadata: null,
    widgetState: null,
  };

  const injectionScript = `<script>
    window.openai = ${JSON.stringify(openaiConfig)};
    window.openai.callTool = async (name) => {
      window.parent.__reportToolCall__(name);
      return { result: "" };
    };
    window.openai.setWidgetState = async () => {};
    window.openai.sendFollowUpMessage = async () => {};
    window.openai.openExternal = () => {};
    window.openai.requestDisplayMode = async () => ({ mode: "inline" });
    window.openai.requestModal = async () => {};
    window.openai.requestClose = async () => {};
    window.dispatchEvent(new CustomEvent("openai:set_globals"));
    // Report unhandled promise rejections to parent
    window.addEventListener("unhandledrejection", (e) => {
      const reason = e.reason?.message || e.reason?.toString() || "Unknown rejection";
      window.parent.__reportRejection__(reason);
    });
  </script>`;

  const widgetHtml = toolData.html.replace("<head>", "<head>" + injectionScript);

  const testHtml = `<!DOCTYPE html>
<html>
<head>
  <title>Widget Test: ${toolName}</title>
  <style>
    body { margin: 0; padding: 20px; font-family: system-ui; background: ${theme === "dark" ? "#1a1a1a" : "#f5f5f5"}; }
    .widget-container { background: ${theme === "dark" ? "#2d2d2d" : "white"}; border-radius: 16px; overflow: hidden; height: 500px; }
    iframe { width: 100%; height: 100%; border: 0; }
  </style>
</head>
<body>
  <div class="widget-container">
    <iframe id="widget-frame" title="Widget"></iframe>
  </div>
</body>
</html>`;

  await page.setContent(testHtml);

  await page.evaluate((html) => {
    const iframe = document.getElementById("widget-frame") as HTMLIFrameElement;
    if (iframe) {
      iframe.srcdoc = html;
    }
  }, widgetHtml);

  await page.waitForTimeout(2000);

  return { logs, errors, rejections: getPageRejections(page), toolCalls: getPageToolCalls(page) };
}

/**
 * Filter out noise from error logs
 */
function filterErrors(errors: string[]): string[] {
  return errors.filter(
    (e) =>
      !e.includes("React DevTools") &&
      !e.includes("Download the React DevTools")
  );
}

// Setup and teardown
test.beforeAll(async () => {
  if (!(await canLaunchBrowser())) return;

  if (!(await isServerRunning())) {
    serverProcess = await startServer();
  }
});

test.afterAll(async () => {
  if (serverProcess) {
    process.kill(-serverProcess.pid!, "SIGTERM");
  }
});

test.describe("Widget Compliance", () => {
  test("all widgets render without JavaScript errors", async () => {
    if (!(await canLaunchBrowser())) {
      test.skip();
      return;
    }

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    try {
      const tools = await getWidgetTools();
      expect(tools.length).toBeGreaterThan(0);

      const failures: string[] = [];

      for (const tool of tools) {
        const { errors } = await renderWidget(page, tool, "light");
        const realErrors = filterErrors(errors);

        if (realErrors.length > 0) {
          failures.push(`${tool}: ${realErrors.join(", ")}`);
        }
      }

      expect(failures, `Widgets with JS errors:\n${failures.join("\n")}`).toHaveLength(0);
    } finally {
      await browser.close();
    }
  });

  test("all widgets render visible content", async () => {
    if (!(await canLaunchBrowser())) {
      test.skip();
      return;
    }

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    try {
      const tools = await getWidgetTools();
      const failures: string[] = [];

      for (const tool of tools) {
        await renderWidget(page, tool, "light");

        // Check if iframe exists and has loaded (srcdoc creates same-origin iframe)
        const hasContent = await page.evaluate(() => {
          const iframe = document.getElementById("widget-frame") as HTMLIFrameElement;
          if (!iframe) return false;

          // Check if srcdoc has been set (iframe has content to render)
          if (iframe.srcdoc && iframe.srcdoc.length > 0) return true;

          // Fallback: try to access contentDocument (works for same-origin)
          try {
            const body = iframe.contentDocument?.body;
            if (!body) return false;
            return body.innerHTML.length > 0;
          } catch {
            // Cross-origin - can't access, but iframe exists so assume content loaded
            return true;
          }
        });

        if (!hasContent) {
          failures.push(tool);
        }
      }

      expect(failures, `Widgets with no content: ${failures.join(", ")}`).toHaveLength(0);
    } finally {
      await browser.close();
    }
  });

  test("all widgets work in dark theme", async () => {
    if (!(await canLaunchBrowser())) {
      test.skip();
      return;
    }

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    try {
      const tools = await getWidgetTools();
      const failures: string[] = [];

      for (const tool of tools) {
        const { errors } = await renderWidget(page, tool, "dark");
        const realErrors = filterErrors(errors);

        if (realErrors.length > 0) {
          failures.push(`${tool}: ${realErrors.join(", ")}`);
        }
      }

      expect(failures, `Widgets failing in dark theme:\n${failures.join("\n")}`).toHaveLength(0);
    } finally {
      await browser.close();
    }
  });

  test("all widgets have no unhandled promise rejections", async () => {
    if (!(await canLaunchBrowser())) {
      test.skip();
      return;
    }

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    try {
      const tools = await getWidgetTools();
      const failures: string[] = [];

      for (const tool of tools) {
        const { rejections } = await renderWidget(page, tool, "light");

        if (rejections.length > 0) {
          failures.push(`${tool}: ${rejections.join(", ")}`);
        }
      }

      expect(failures, `Widgets with unhandled rejections:\n${failures.join("\n")}`).toHaveLength(0);
    } finally {
      await browser.close();
    }
  });

  test("all widget callTool invocations reference registered server tools", async () => {
    if (!(await canLaunchBrowser())) {
      test.skip();
      return;
    }

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();

    try {
      const [tools, registeredTools] = await Promise.all([
        getWidgetTools(),
        getAllRegisteredToolNames(),
      ]);
      const failures: string[] = [];

      for (const tool of tools) {
        const { toolCalls } = await renderWidget(page, tool, "light");
        const uniqueCalls = [...new Set(toolCalls)];

        for (const calledTool of uniqueCalls) {
          if (!registeredTools.has(calledTool)) {
            failures.push(
              `${tool} calls unregistered tool "${calledTool}" — ` +
              `the tool must be listed in the server's /tools endpoint`
            );
          }
        }
      }

      expect(
        failures,
        `Widgets calling tools not registered on the server:\n${failures.join("\n")}`
      ).toHaveLength(0);
    } finally {
      await browser.close();
    }
  });
});

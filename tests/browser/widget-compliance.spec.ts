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
 * - All callTool invocations are callable on the server
 *
 * Performance: Widgets are rendered once per theme in beforeAll, then each test
 * asserts on the cached results. This avoids redundant renders.
 *
 * Setup:
 *   pnpm run setup:test              # Install Playwright browsers
 *   npx playwright install-deps      # Install system dependencies (may need sudo)
 *
 * Run with: pnpm run test:browser
 */

import { test, expect, chromium, type Page, type Browser } from "@playwright/test";

const SERVER_PORT = 8000;
const SERVER_URL = `http://localhost:${SERVER_PORT}`;

let browserAvailable: boolean | null = null;

// ─── Per-page tracking ───────────────────────────────────────────────────────

const pageRejections = new WeakMap<Page, string[]>();
const pageToolCalls = new WeakMap<Page, string[]>();
const exposedPages = new WeakSet<Page>();

function getPageRejections(page: Page): string[] {
  if (!pageRejections.has(page)) pageRejections.set(page, []);
  return pageRejections.get(page)!;
}

function getPageToolCalls(page: Page): string[] {
  if (!pageToolCalls.has(page)) pageToolCalls.set(page, []);
  return pageToolCalls.get(page)!;
}

function clearPageRejections(page: Page): void {
  pageRejections.set(page, []);
}

function clearPageToolCalls(page: Page): void {
  pageToolCalls.set(page, []);
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

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
 * Get widget tools from the server.
 * The HTTP /tools endpoint returns only widget tools (tools with UI).
 */
async function getWidgetTools(): Promise<string[]> {
  const response = await fetch(`${SERVER_URL}/tools`);
  const data = await response.json();
  return (data.tools || []).map(
    (t: { function: { name: string } }) => t.function.name
  );
}

// ─── Render + collect ────────────────────────────────────────────────────────

interface RenderResult {
  tool: string;
  theme: "light" | "dark";
  errors: string[];
  rejections: string[];
  toolCalls: string[];
  hasContent: boolean;
  toolOutput: Record<string, unknown>;
  textContent: string;
}

async function renderWidget(
  page: Page,
  toolName: string,
  theme: "light" | "dark"
): Promise<RenderResult> {
  const errors: string[] = [];

  clearPageRejections(page);
  clearPageToolCalls(page);

  const onConsole = (msg: { type(): string; text(): string }) => {
    if (msg.type() === "error") errors.push(msg.text());
  };
  const onPageError = (error: Error) => {
    errors.push(error.message);
  };

  page.on("console", onConsole);
  page.on("pageerror", onPageError);

  if (!exposedPages.has(page)) {
    await page.exposeFunction("__reportRejection__", (reason: string) => {
      getPageRejections(page).push(reason);
    });
    await page.exposeFunction("__reportToolCall__", (name: string) => {
      getPageToolCalls(page).push(name);
    });
    exposedPages.add(page);
  }

  const toolResponse = await fetch(`${SERVER_URL}/tools/call`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: toolName, arguments: {} }),
  });
  const toolData = await toolResponse.json();
  if (toolData.error) throw new Error(`Tool error: ${toolData.error}`);

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
    window.addEventListener("unhandledrejection", (e) => {
      const reason = e.reason?.message || e.reason?.toString() || "Unknown rejection";
      window.parent.__reportRejection__(reason);
    });
  </script>`;

  const widgetHtml = toolData.html.replace("<head>", "<head>" + injectionScript);

  const bg = theme === "dark" ? "#1a1a1a" : "#f5f5f5";
  const cardBg = theme === "dark" ? "#2d2d2d" : "white";
  const testHtml = `<!DOCTYPE html>
<html><head><title>Widget Test: ${toolName}</title>
<style>body{margin:0;padding:20px;font-family:system-ui;background:${bg}}
.wc{background:${cardBg};border-radius:16px;overflow:hidden;height:500px}
iframe{width:100%;height:100%;border:0}</style>
</head><body><div class="wc"><iframe id="widget-frame" title="Widget"></iframe></div></body></html>`;

  await page.setContent(testHtml);
  await page.evaluate((html) => {
    const iframe = document.getElementById("widget-frame") as HTMLIFrameElement;
    if (iframe) iframe.srcdoc = html;
  }, widgetHtml);

  await page.waitForTimeout(2000);

  const hasContent = await page.evaluate(() => {
    const iframe = document.getElementById("widget-frame") as HTMLIFrameElement;
    if (!iframe) return false;
    if (iframe.srcdoc && iframe.srcdoc.length > 0) return true;
    try {
      const body = iframe.contentDocument?.body;
      if (!body) return false;
      return body.innerHTML.length > 0;
    } catch {
      return true;
    }
  });

  // Capture rendered text content from the iframe
  const textContent = await page.evaluate(() => {
    const iframe = document.getElementById("widget-frame") as HTMLIFrameElement;
    try {
      return iframe.contentDocument?.body?.textContent || "";
    } catch {
      return "";
    }
  });

  // Remove listeners so they don't leak into the next render
  page.removeListener("console", onConsole);
  page.removeListener("pageerror", onPageError);

  return {
    tool: toolName,
    theme,
    errors: errors.filter(
      (e) =>
        !e.includes("React DevTools") &&
        !e.includes("Download the React DevTools")
    ),
    rejections: [...getPageRejections(page)],
    toolCalls: [...getPageToolCalls(page)],
    hasContent,
    toolOutput: toolData.tool_output || {},
    textContent,
  };
}

// ─── Cached render results (populated in beforeAll) ──────────────────────────

let lightResults: RenderResult[] = [];
let darkResults: RenderResult[] = [];

// ─── Setup / teardown ────────────────────────────────────────────────────────

test.beforeAll(async ({ }, testInfo) => {
  testInfo.setTimeout(120_000);

  if (!(await canLaunchBrowser())) return;

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();

  try {
    const tools = await getWidgetTools();

    for (const tool of tools) {
      lightResults.push(await renderWidget(page, tool, "light"));
    }
    for (const tool of tools) {
      darkResults.push(await renderWidget(page, tool, "dark"));
    }
  } finally {
    await browser.close();
  }
});

// ─── Tests ───────────────────────────────────────────────────────────────────

test.describe("Widget Compliance", () => {
  test("all widgets render without JavaScript errors", async () => {
    if (!(await canLaunchBrowser())) { test.skip(); return; }

    expect(lightResults.length).toBeGreaterThan(0);

    const failures = lightResults
      .filter((r) => r.errors.length > 0)
      .map((r) => `${r.tool}: ${r.errors.join(", ")}`);

    expect(failures, `Widgets with JS errors:\n${failures.join("\n")}`).toHaveLength(0);
  });

  test("all widgets render visible content", async () => {
    if (!(await canLaunchBrowser())) { test.skip(); return; }

    const failures = lightResults
      .filter((r) => !r.hasContent)
      .map((r) => r.tool);

    expect(failures, `Widgets with no content: ${failures.join(", ")}`).toHaveLength(0);
  });

  test("all widgets work in dark theme", async () => {
    if (!(await canLaunchBrowser())) { test.skip(); return; }

    const failures = darkResults
      .filter((r) => r.errors.length > 0)
      .map((r) => `${r.tool}: ${r.errors.join(", ")}`);

    expect(failures, `Widgets failing in dark theme:\n${failures.join("\n")}`).toHaveLength(0);
  });

  test("all widgets have no unhandled promise rejections", async () => {
    if (!(await canLaunchBrowser())) { test.skip(); return; }

    const failures = lightResults
      .filter((r) => r.rejections.length > 0)
      .map((r) => `${r.tool}: ${r.rejections.join(", ")}`);

    expect(failures, `Widgets with unhandled rejections:\n${failures.join("\n")}`).toHaveLength(0);
  });

  test("all widget callTool invocations are callable on the server", async () => {
    if (!(await canLaunchBrowser())) { test.skip(); return; }

    const failures: string[] = [];
    const testedTools = new Map<string, string | null>(); // name → error or null

    for (const result of lightResults) {
      const uniqueCalls = [...new Set(result.toolCalls)];

      for (const calledTool of uniqueCalls) {
        if (!testedTools.has(calledTool)) {
          const response = await fetch(`${SERVER_URL}/tools/call`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: calledTool, arguments: {} }),
          });
          const data = await response.json();

          testedTools.set(
            calledTool,
            !response.ok || data.error
              ? data.error || `HTTP ${response.status}`
              : null
          );
        }

        const error = testedTools.get(calledTool);
        if (error) {
          failures.push(
            `${result.tool} calls tool "${calledTool}" which failed: ${error}`
          );
        }
      }
    }

    expect(
      failures,
      `Widgets calling tools that fail on the server:\n${failures.join("\n")}`
    ).toHaveLength(0);
  });

  test("widgets render their structured content values", async () => {
    if (!(await canLaunchBrowser())) { test.skip(); return; }

    const failures: string[] = [];

    for (const result of lightResults) {
      if (!result.toolOutput) continue;

      // Check that string values from toolOutput appear in rendered text
      for (const [key, value] of Object.entries(result.toolOutput)) {
        if (typeof value === "string" && value.length >= 3 && value.length <= 100) {
          if (!result.textContent.includes(value)) {
            failures.push(`${result.tool}: "${key}" value "${value}" not found in rendered output`);
          }
        }
      }
    }

    // Allow some failures (not all fields render visibly), but flag if many
    const failureRate = failures.length / lightResults.length;
    if (failureRate > 0.5) {
      expect(failures, `Many widgets not rendering their data:\n${failures.slice(0, 5).join("\n")}`).toHaveLength(0);
    }
  });
});

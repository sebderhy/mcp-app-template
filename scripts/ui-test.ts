#!/usr/bin/env tsx
/**
 * UI Test Tool for AI Agents
 *
 * Two modes:
 * 1. Direct Mode (no API key): pnpm run ui-test --tool show_carousel
 * 2. AI Mode (requires OPENAI_API_KEY): pnpm run ui-test "Show me the carousel"
 *
 * Output: /tmp/ui-test/{screenshot.png, dom.json, console.log}
 */

import { spawn, ChildProcess } from "child_process";
import * as fs from "fs";
import * as path from "path";

const OUTPUT_DIR = "/tmp/ui-test";
const SERVER_PORT = 8000;
const SIMULATOR_URL = `http://localhost:${SERVER_PORT}/assets/apptester.html`;

type Theme = "light" | "dark";

const THEME_STYLES = {
  light: { bg: "#f5f5f5", text: "#333", card: "white", shadow: "0.1" },
  dark: { bg: "#1a1a2e", text: "#e0e0e0", card: "#16213e", shadow: "0.4" },
};

const COLORS = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
} as const;

function log(message: string, color: keyof typeof COLORS = "reset") {
  console.log(`${COLORS[color]}${message}${COLORS.reset}`);
}

function logError(message: string) {
  console.error(`${COLORS.red}ERROR: ${message}${COLORS.reset}`);
}

function parseArg(args: string[], flag: string, shortFlag?: string): string | null {
  const longPattern = `--${flag}=`;
  const shortPattern = shortFlag ? `-${shortFlag}=` : null;

  const eqArg = args.find((a) => a.startsWith(longPattern) || (shortPattern && a.startsWith(shortPattern)));
  if (eqArg) return eqArg.split("=")[1];

  const flagIndex = args.findIndex((a) => a === `--${flag}` || (shortFlag && a === `-${shortFlag}`));
  if (flagIndex !== -1 && args[flagIndex + 1] && !args[flagIndex + 1].startsWith("-")) {
    return args[flagIndex + 1];
  }
  return null;
}

function hasFlag(args: string[], flag: string, shortFlag?: string): boolean {
  return args.includes(`--${flag}`) || (shortFlag ? args.includes(`-${shortFlag}`) : false);
}

async function checkPlaywright(): Promise<boolean> {
  try {
    await import("@playwright/test");
    return true;
  } catch {
    return false;
  }
}

async function checkBrowsers(): Promise<boolean> {
  try {
    const { chromium } = await import("@playwright/test");
    const browser = await chromium.launch({ headless: true });
    await browser.close();
    return true;
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : String(error);
    return !msg.includes("Executable doesn't exist") && !msg.includes("browserType.launch");
  }
}

async function isServerRunning(): Promise<boolean> {
  try {
    const response = await fetch(`http://localhost:${SERVER_PORT}/chat/status`);
    return response.ok;
  } catch {
    return false;
  }
}

async function hasApiKey(): Promise<boolean> {
  try {
    const response = await fetch(`http://localhost:${SERVER_PORT}/chat/status`);
    const data = await response.json();
    return data.has_api_key === true;
  } catch {
    return false;
  }
}

async function getAvailableTools(): Promise<string[]> {
  try {
    const response = await fetch(`http://localhost:${SERVER_PORT}/tools`);
    const data = await response.json();
    return (data.tools || []).map((t: { function: { name: string } }) => t.function.name);
  } catch {
    return [];
  }
}

async function startServer(): Promise<ChildProcess> {
  log("Starting server...", "yellow");
  const serverProcess = spawn("pnpm", ["run", "server"], {
    cwd: process.cwd(),
    stdio: ["ignore", "pipe", "pipe"],
    detached: true,
  });

  const startTime = Date.now();
  while (Date.now() - startTime < 30000) {
    if (await isServerRunning()) {
      log("Server is ready!", "green");
      return serverProcess;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error("Server failed to start within 30 seconds");
}

function ensureOutputDir() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
}

interface TestResult {
  success: boolean;
  hasWidget: boolean;
  isLoading: boolean;
  userMessages: string[];
  assistantMessages: string[];
  widgetCount: number;
  screenshotPath: string;
  domPath: string;
  logsPath: string;
}

function saveArtifacts(
  domData: object,
  consoleLogs: string[]
): { screenshotPath: string; domPath: string; logsPath: string } {
  const screenshotPath = path.join(OUTPUT_DIR, "screenshot.png");
  const domPath = path.join(OUTPUT_DIR, "dom.json");
  const logsPath = path.join(OUTPUT_DIR, "console.log");

  fs.writeFileSync(domPath, JSON.stringify(domData, null, 2));
  fs.writeFileSync(logsPath, consoleLogs.join("\n"));

  return { screenshotPath, domPath, logsPath };
}

async function runAITest(prompt: string, interactive: boolean): Promise<TestResult> {
  const { chromium } = await import("@playwright/test");

  log(`\nLaunching browser (headless: ${!interactive})...`, "blue");
  const browser = await chromium.launch({ headless: !interactive });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  const consoleLogs: string[] = [];
  page.on("console", (msg) => consoleLogs.push(`[${msg.type()}] ${msg.text()}`));
  page.on("pageerror", (error) => consoleLogs.push(`[error] ${error.message}`));

  try {
    log(`Navigating to ${SIMULATOR_URL}...`, "blue");
    await page.goto(SIMULATOR_URL);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);

    await page.screenshot({ path: path.join(OUTPUT_DIR, "initial.png"), fullPage: true });

    if (!interactive) {
      log(`\nSending message: "${prompt}"`, "blue");
      const inputSelector = 'input[type="text"], textarea';
      await page.waitForSelector(inputSelector, { timeout: 5000 });
      await page.fill(inputSelector, prompt);

      const sendButton = page.locator('button[type="submit"], button:has-text("Send")');
      if (await sendButton.isVisible()) {
        await sendButton.click();
      } else {
        await page.keyboard.press("Enter");
      }

      log("Waiting for response (~30s for AI)...", "yellow");
      try {
        await page.waitForFunction(
          () => {
            if (document.querySelectorAll("iframe").length > 0) return true;
            if (document.querySelectorAll(".animate-bounce").length > 0) return false;
            return document.querySelectorAll(".rounded-2xl.px-4.py-3").length >= 2;
          },
          { timeout: 90000 }
        );
      } catch {
        log("Response timeout - taking screenshot anyway", "yellow");
      }
      await page.waitForTimeout(2000);
    }

    const { screenshotPath, domPath, logsPath } = saveArtifacts({}, consoleLogs);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    log(`Screenshot saved: ${screenshotPath}`, "green");

    const domSnapshot = await page.evaluate(() => {
      const userMessages = Array.from(document.querySelectorAll('[class*="bg-blue-600"]'))
        .map((el) => el.textContent?.trim())
        .filter(Boolean) as string[];
      const assistantMessages = Array.from(
        document.querySelectorAll('.rounded-2xl.px-4.py-3:not([class*="bg-blue-600"])')
      )
        .map((el) => el.textContent?.trim())
        .filter(Boolean) as string[];
      const widgetCount = document.querySelectorAll("iframe").length;
      const isLoading = document.querySelectorAll(".animate-bounce").length > 0;
      return { userMessages, assistantMessages, widgetCount, hasWidget: widgetCount > 0, isLoading };
    });

    fs.writeFileSync(domPath, JSON.stringify({ ...domSnapshot, timestamp: new Date().toISOString() }, null, 2));

    if (interactive) {
      log("\n🖥️  Interactive mode - browser is open. Press Ctrl+C to exit.", "cyan");
      await new Promise(() => {});
    }

    await browser.close();
    return {
      success: !domSnapshot.isLoading && (domSnapshot.hasWidget || domSnapshot.assistantMessages.length > 0),
      ...domSnapshot,
      screenshotPath,
      domPath,
      logsPath,
    };
  } catch (error) {
    await browser.close();
    throw error;
  }
}

async function runDirectToolTest(toolName: string, theme: Theme): Promise<TestResult> {
  const { chromium } = await import("@playwright/test");

  log(`\nDirect tool test: ${toolName} (theme: ${theme})`, "blue");
  log("Calling tool endpoint...", "blue");

  const toolResponse = await fetch(`http://localhost:${SERVER_PORT}/tools/call`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: toolName, arguments: {} }),
  });

  const toolData = await toolResponse.json();
  if (toolData.error) throw new Error(`Tool error: ${toolData.error}`);

  log("Tool data received, launching browser...", "blue");

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  const consoleLogs: string[] = [];
  page.on("console", (msg) => consoleLogs.push(`[${msg.type()}] ${msg.text()}`));
  page.on("pageerror", (error) => consoleLogs.push(`[error] ${error.message}`));

  try {
    const openaiConfig = {
      theme,
      displayMode: "inline",
      maxHeight: 500,
      safeArea: { top: 0, bottom: 0, left: 0, right: 0 },
      locale: "en-US",
      toolInput: {},
      toolOutput: toolData.tool_output,
      toolResponseMetadata: null,
      widgetState: null,
    };

    const injectionScript = `<script>
      window.openai = ${JSON.stringify(openaiConfig)};
      window.openai.callTool = async () => ({});
      window.openai.setWidgetState = async () => {};
      window.openai.sendFollowUpMessage = async () => {};
      window.openai.openExternal = () => {};
      window.openai.requestDisplayMode = async () => ({});
      window.openai.requestModal = async () => ({});
      window.openai.requestClose = async () => {};
      window.dispatchEvent(new CustomEvent('openai:set_globals'));
    </script>`;

    const modifiedWidgetHtml = toolData.html.replace("<head>", "<head>" + injectionScript);
    const styles = THEME_STYLES[theme];

    const testHtml = `<!DOCTYPE html>
<html>
<head>
  <title>Tool Test: ${toolName}</title>
  <style>
    body { margin: 0; padding: 20px; font-family: system-ui, sans-serif; background: ${styles.bg}; }
    h1 { margin: 0 0 20px 0; font-size: 18px; color: ${styles.text}; }
    .widget-container { background: ${styles.card}; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,${styles.shadow}); height: 500px; }
    iframe { width: 100%; height: 100%; border: 0; }
  </style>
</head>
<body>
  <h1>Tool: ${toolName} (${theme} theme)</h1>
  <div class="widget-container">
    <iframe id="widget-frame" title="Widget"></iframe>
  </div>
</body>
</html>`;

    await page.setContent(testHtml);
    await page.evaluate((html) => {
      const iframe = document.getElementById("widget-frame") as HTMLIFrameElement;
      if (iframe) iframe.srcdoc = html;
    }, modifiedWidgetHtml);
    await page.waitForTimeout(2000);

    const { screenshotPath, domPath, logsPath } = saveArtifacts(
      { toolName, toolOutput: toolData.tool_output, timestamp: new Date().toISOString() },
      consoleLogs
    );
    await page.screenshot({ path: screenshotPath, fullPage: true });
    log(`Screenshot saved: ${screenshotPath}`, "green");

    const hasWidget = await page.evaluate(() => document.querySelector("iframe") !== null);

    fs.writeFileSync(
      domPath,
      JSON.stringify({ toolName, toolOutput: toolData.tool_output, hasWidget, timestamp: new Date().toISOString() }, null, 2)
    );

    await browser.close();
    return {
      success: hasWidget,
      hasWidget,
      isLoading: false,
      userMessages: [],
      assistantMessages: [`Direct tool test: ${toolName}`],
      widgetCount: hasWidget ? 1 : 0,
      screenshotPath,
      domPath,
      logsPath,
    };
  } catch (error) {
    await browser.close();
    throw error;
  }
}

function printResults(result: TestResult, mode: string, toolName: string) {
  log("\n📊 Test Summary:", "cyan");
  log(`   Mode: ${mode}`, "reset");
  log(`   Tool: "${toolName}"`, "reset");
  log(`   Widgets rendered: ${result.widgetCount}`, "reset");
  log(`   Has widget: ${result.hasWidget ? "Yes ✓" : "No"}`, result.hasWidget ? "green" : "yellow");
  log(`   Test result: ${result.success ? "PASSED ✓" : "NEEDS REVIEW"}`, result.success ? "green" : "yellow");
  log("\n📁 Artifacts:", "cyan");
  log(`   Screenshot: ${result.screenshotPath}`, "reset");
  log(`   DOM snapshot: ${result.domPath}`, "reset");
  log(`   Console logs: ${result.logsPath}`, "reset");
}

function printHelp(tools: string[]) {
  log("🧪 UI Test Tool for AI Agents", "cyan");
  log("\nUsage:", "reset");
  log('  pnpm run ui-test "Your prompt here"     # AI mode (needs API key)', "green");
  log("  pnpm run ui-test --tool show_carousel   # Direct tool test (no API key)", "green");
  log("  pnpm run ui-test --tool show_carousel --theme dark  # Dark mode test", "green");
  log("  pnpm run ui-test --interactive          # Open browser for manual testing", "green");
  log("\nExamples:", "reset");
  log("  pnpm run ui-test --tool show_dashboard", "reset");
  log("  pnpm run ui-test --tool show_list --theme dark", "reset");
  log("  pnpm run ui-test -t show_qr", "reset");
  log("\nAvailable tools:", "reset");
  if (tools.length > 0) {
    tools.forEach((t) => log(`  - ${t}`, "reset"));
  } else {
    log("  (start server to see available tools)", "yellow");
  }
  log("\nRequirements:", "reset");
  log("  1. Run `pnpm run setup:test` to install Playwright browsers", "reset");
  log("  2. Run `pnpm run build` to build widgets", "reset");
  log("  3. For AI mode: set OPENAI_API_KEY in .env", "reset");
}

async function main() {
  const args = process.argv.slice(2);

  const toolName = parseArg(args, "tool", "t");
  const themeArg = parseArg(args, "theme");
  const theme: Theme = themeArg === "dark" ? "dark" : "light";
  const interactive = hasFlag(args, "interactive", "i");

  const prompt = args
    .filter((arg) => !arg.startsWith("-") && arg !== toolName && arg !== themeArg)
    .join(" ");

  if (!prompt && !toolName && !interactive) {
    const tools = (await isServerRunning()) ? await getAvailableTools() : [];
    printHelp(tools);
    process.exit(0);
  }

  log("\n🧪 UI Test Tool for AI Agents\n", "cyan");

  if (!(await checkPlaywright())) {
    logError("Playwright is not installed. Run: pnpm install");
    process.exit(1);
  }
  if (!(await checkBrowsers())) {
    logError("Playwright browsers not installed. Run: pnpm run setup:test");
    process.exit(1);
  }

  let serverProcess: ChildProcess | null = null;
  if (!(await isServerRunning())) {
    serverProcess = await startServer();
  } else {
    log("Server already running", "green");
  }

  ensureOutputDir();

  try {
    let result: TestResult;

    if (toolName) {
      result = await runDirectToolTest(toolName, theme);
      printResults(result, `Direct (${theme})`, toolName);
    } else if (interactive) {
      result = await runAITest("", true);
      printResults(result, "Interactive", "manual");
    } else {
      if (!(await hasApiKey())) {
        log("⚠️  No OPENAI_API_KEY found. Trying to match tool from prompt...", "yellow");
        const tools = await getAvailableTools();
        const matchedTool = tools.find((t) => prompt.toLowerCase().includes(t.toLowerCase()));

        if (matchedTool) {
          result = await runDirectToolTest(matchedTool, theme);
          printResults(result, `Direct fallback (${theme})`, matchedTool);
        } else {
          logError(`Could not determine tool from prompt: "${prompt}"`);
          log("\nAvailable tools:", "yellow");
          tools.forEach((t) => log(`  - ${t}`, "reset"));
          log("\nUse: pnpm run ui-test --tool <name>", "yellow");
          process.exit(1);
        }
      } else {
        log("Using OpenAI API for AI-powered testing", "green");
        result = await runAITest(prompt, false);
        printResults(result, "AI (OpenAI)", prompt);
      }
    }
  } finally {
    if (serverProcess) {
      log("\nStopping server...", "yellow");
      process.kill(-serverProcess.pid!, "SIGTERM");
    }
  }
}

main().catch((error) => {
  logError(error.message);
  process.exit(1);
});

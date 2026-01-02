/**
 * Widget Structure Tests - Infrastructure tests for widget file organization.
 *
 * These tests verify that widgets follow the required structure patterns
 * without assuming anything about the widget's business logic.
 *
 * Key requirements verified:
 * 1. Each widget has an entry point (index.tsx)
 * 2. Each widget has a main component (App.tsx)
 * 3. Entry points use React 18+ createRoot pattern
 * 4. Entry points target the correct root element ID
 */

import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

// Read the targets array from build-all.mts to stay in sync
function getWidgetTargets(): string[] {
  const buildScript = fs.readFileSync(
    path.resolve("build-all.mts"),
    "utf-8"
  );
  // Extract targets array from the build script
  const match = buildScript.match(/const targets:\s*string\[\]\s*=\s*\[([\s\S]*?)\]/);
  if (!match) {
    throw new Error("Could not find targets array in build-all.mts");
  }
  // Parse the array contents
  return match[1]
    .split(",")
    .map((s) => s.trim().replace(/["']/g, ""))
    .filter((s) => s.length > 0);
}

const widgets = getWidgetTargets();
const srcDir = path.resolve("src");

describe("Widget File Structure", () => {
  describe("targets array discovery", () => {
    it("should find at least one widget target", () => {
      expect(widgets.length).toBeGreaterThan(0);
    });

    it("targets should be valid directory names", () => {
      for (const widget of widgets) {
        // Should be lowercase with optional hyphens
        expect(widget).toMatch(/^[a-z][a-z0-9-]*$/);
      }
    });
  });

  describe("required files", () => {
    it.each(widgets)("widget '%s' has index.tsx entry point", (widget) => {
      const entryPath = path.join(srcDir, widget, "index.tsx");
      expect(fs.existsSync(entryPath)).toBe(true);
    });

    it.each(widgets)("widget '%s' has App.tsx component", (widget) => {
      const appPath = path.join(srcDir, widget, "App.tsx");
      expect(fs.existsSync(appPath)).toBe(true);
    });
  });

  describe("entry point patterns", () => {
    it.each(widgets)(
      "widget '%s' entry point uses createRoot",
      (widget) => {
        const entryPath = path.join(srcDir, widget, "index.tsx");
        const content = fs.readFileSync(entryPath, "utf-8");

        // Should import createRoot from react-dom/client
        expect(content).toMatch(/import\s+{[^}]*createRoot[^}]*}\s+from\s+["']react-dom\/client["']/);

        // Should call createRoot
        expect(content).toMatch(/createRoot\(/);
      }
    );

    it.each(widgets)(
      "widget '%s' entry point imports App component",
      (widget) => {
        const entryPath = path.join(srcDir, widget, "index.tsx");
        const content = fs.readFileSync(entryPath, "utf-8");

        // Should import App from ./App
        expect(content).toMatch(/import\s+App\s+from\s+["']\.\/App["']/);
      }
    );

    it.each(widgets)(
      "widget '%s' entry point renders App component",
      (widget) => {
        const entryPath = path.join(srcDir, widget, "index.tsx");
        const content = fs.readFileSync(entryPath, "utf-8");

        // Should render <App /> or <App>
        expect(content).toMatch(/<App\s*\/?>|\.render\(\s*<App/);
      }
    );

    it.each(widgets)(
      "widget '%s' targets correct root element ID",
      (widget) => {
        const entryPath = path.join(srcDir, widget, "index.tsx");
        const content = fs.readFileSync(entryPath, "utf-8");

        // Should getElementById with widget-name-root
        const expectedId = `${widget}-root`;
        expect(content).toContain(`"${expectedId}"`);
      }
    );
  });

  describe("App component patterns", () => {
    it.each(widgets)(
      "widget '%s' App.tsx exports a component",
      (widget) => {
        const appPath = path.join(srcDir, widget, "App.tsx");
        const content = fs.readFileSync(appPath, "utf-8");

        // Should have a default export (function or const)
        expect(content).toMatch(/export\s+default\s+(function\s+App|App)/);
      }
    );

    it.each(widgets)(
      "widget '%s' App.tsx returns JSX",
      (widget) => {
        const appPath = path.join(srcDir, widget, "App.tsx");
        const content = fs.readFileSync(appPath, "utf-8");

        // Should have return statement with JSX (opening tag)
        expect(content).toMatch(/return\s*\(?[\s\S]*?</);
      }
    );
  });
});

describe("Widget Directory Organization", () => {
  it("src directory exists", () => {
    expect(fs.existsSync(srcDir)).toBe(true);
  });

  it("all target widgets have directories in src/", () => {
    for (const widget of widgets) {
      const widgetDir = path.join(srcDir, widget);
      expect(fs.existsSync(widgetDir)).toBe(true);
      expect(fs.statSync(widgetDir).isDirectory()).toBe(true);
    }
  });

  it("shared hooks exist in src/", () => {
    const requiredHooks = [
      "use-widget-props.ts",
      "use-widget-state.ts",
      "use-openai-global.ts",
    ];

    for (const hook of requiredHooks) {
      const hookPath = path.join(srcDir, hook);
      expect(fs.existsSync(hookPath)).toBe(true);
    }
  });

  it("types.ts exists in src/", () => {
    const typesPath = path.join(srcDir, "types.ts");
    expect(fs.existsSync(typesPath)).toBe(true);
  });

  it("global CSS exists in src/", () => {
    const cssPath = path.join(srcDir, "index.css");
    expect(fs.existsSync(cssPath)).toBe(true);
  });
});

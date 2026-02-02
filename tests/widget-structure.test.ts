/**
 * Widget Structure Tests - Infrastructure tests for widget file organization.
 *
 * These tests verify that widgets follow the REQUIRED structure patterns
 * enforced by the build system, without assuming anything about widget
 * business logic or implementation details.
 *
 * Key requirements verified:
 * 1. Each widget has an entry point (index.tsx) - required by build system
 * 2. Entry points target the correct root element ID - required by generated HTML
 * 3. Shared infrastructure files exist (hooks, types)
 *
 * NOT verified (developer choice):
 * - Component naming (App.tsx vs MyWidget.tsx)
 * - Rendering method (createRoot vs other)
 * - Component export patterns
 */

import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

// Auto-discover widget targets by scanning src/*/index.tsx (mirrors build-all.mts)
function getWidgetTargets(): string[] {
  const srcDir = path.resolve("src");
  return fs
    .readdirSync(srcDir)
    .filter((name) => {
      const entryTsx = path.join(srcDir, name, "index.tsx");
      const entryJsx = path.join(srcDir, name, "index.jsx");
      return (
        fs.statSync(path.join(srcDir, name)).isDirectory() &&
        (fs.existsSync(entryTsx) || fs.existsSync(entryJsx))
      );
    })
    .sort();
}

// Infrastructure targets that aren't normal widgets (no React root element)
const INFRASTRUCTURE_TARGETS = ["sandbox-proxy"];

const widgets = getWidgetTargets().filter(
  (w) => !INFRASTRUCTURE_TARGETS.includes(w)
);
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
  });

  describe("entry point requirements", () => {
    it.each(widgets)(
      "widget '%s' targets correct root element ID",
      (widget) => {
        const entryPath = path.join(srcDir, widget, "index.tsx");
        const content = fs.readFileSync(entryPath, "utf-8");

        // The build system generates HTML with <div id="${name}-root">
        // so entry points MUST target this ID
        const expectedId = `${widget}-root`;
        expect(content).toContain(`"${expectedId}"`);
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
      "use-host-global.ts",
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

import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/browser",
  timeout: 60000,
  retries: 0,
  use: {
    headless: true,
    viewport: { width: 1280, height: 720 },
  },
  // Don't run in parallel - we share a single server
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
});

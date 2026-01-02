import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    // Use happy-dom for fast DOM simulation
    environment: "happy-dom",

    // Test file patterns
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],

    // Global test setup
    setupFiles: ["tests/setup.ts"],

    // Coverage configuration
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: ["src/**/*.ts", "src/**/*.tsx"],
      exclude: [
        "src/**/index.tsx", // Entry points are tested structurally
        "**/*.d.ts",
      ],
    },

    // Timeout for async tests
    testTimeout: 10000,
  },

  // Resolve aliases matching the main config
  resolve: {
    alias: {
      "@": "/src",
    },
  },
});

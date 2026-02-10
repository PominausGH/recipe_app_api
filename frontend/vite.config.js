/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    allowedHosts: ["recipe.daintytrading.com"],
    proxy: {
      "/api": {
        target: "http://recipe-api.daintytrading.com",
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.js",
    css: true,
    exclude: ["**/node_modules/**", "**/e2e/**"],
  },
});

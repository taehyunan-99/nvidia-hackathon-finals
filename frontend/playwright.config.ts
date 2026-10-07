import { defineConfig } from "@playwright/test";
const live = !!process.env.AGENT_LIVE_BROWSER;
const url = live ? "http://127.0.0.1:5181" : "http://127.0.0.1:5173";
export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.ts",
  fullyParallel: true,
  use: {
    baseURL: url,
    viewport: { width: 1440, height: 1000 },
    headless: true,
  },
  webServer: {
    command: live ? "npm run dev -- --port 5181" : "npm run dev",
    env: { VITE_AGENT_MODE: live ? "live" : "mock" },
    url,
    reuseExistingServer: !live,
  },
});

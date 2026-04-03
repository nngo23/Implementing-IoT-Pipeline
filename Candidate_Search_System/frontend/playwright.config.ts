import { defineConfig } from "@playwright/test";

export default defineConfig({
  timeout: 10 * 60 * 1000, // 10 minutes per test
  use: {
    baseURL: "http://localhost:5173",
    actionTimeout: 5 * 60 * 1000, // 5 minutes per action like clicks
  },
});

import { defineConfig } from "@playwright/test";

const python =
  process.env.VCR_PYTHON ??
  (process.platform === "win32" ? "../.venv/Scripts/python.exe" : "python");
export default defineConfig({
  testDir: "tests",
  workers: 1,
  fullyParallel: false,
  timeout: 45_000,
  expect: { timeout: 10_000 },
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:18880",
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    viewport: { width: 1440, height: 1000 },
    reducedMotion: "reduce",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    launchOptions: {
      executablePath: process.env.CHROMIUM_EXECUTABLE,
      args: ["--disable-gpu"],
    },
  },
  webServer: {
    command: `"${python}" ../scripts/run_browser_stack.py`,
    url: "http://127.0.0.1:18880/api/v1/session",
    timeout: 90_000,
    reuseExistingServer: false,
  },
});

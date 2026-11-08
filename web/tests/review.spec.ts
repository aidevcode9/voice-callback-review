import fs from "node:fs";
import path from "node:path";
import AxeBuilder from "@axe-core/playwright";
import { type APIRequestContext, expect, test } from "@playwright/test";
import Ajv2020 from "ajv/dist/2020";
import schema from "../../docs/api/openapi.json";
import type { components } from "../lib/api.generated";

const controlURL = "http://127.0.0.1:18735/control";
const ajv = new Ajv2020({ strict: false, validateFormats: false });
ajv.addSchema(schema, "api");
const validSubmission = ajv.compile<components["schemas"]["SubmitJob"]>({
  $ref: "api#/components/schemas/SubmitJob",
});
const validSession = ajv.compile<components["schemas"]["Session"]>({
  $ref: "api#/components/schemas/Session",
});
const shots = path.resolve("../docs/evidence/F-006");
fs.mkdirSync(shots, { recursive: true });
async function control(request: APIRequestContext, body: object) {
  const response = await request.post(controlURL, { data: body });
  expect(response.ok()).toBeTruthy();
}
async function counts(request: APIRequestContext) {
  const response = await request.get(controlURL);
  const data: unknown = await response.json();
  if (
    !data ||
    typeof data !== "object" ||
    !("chats" in data) ||
    typeof data.chats !== "number" ||
    !("active" in data) ||
    typeof data.active !== "number"
  )
    throw new Error("Invalid controlled runtime response");
  return { chats: data.chats, active: data.active };
}

test("explicit review workflow, preserved history, real proxy, reconnect and failure states", async ({
  page,
  request,
  browser,
}) => {
  test.setTimeout(120_000);
  const errors: string[] = [];
  const apiOrigins = new Set<string>();
  const submissions: components["schemas"]["SubmitJob"][] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (req) => {
    if (req.url().includes("/api/")) apiOrigins.add(new URL(req.url()).origin);
    if (req.method() === "POST" && req.url().endsWith("/api/v1/jobs")) {
      const body: unknown = req.postDataJSON();
      if (!validSubmission(body)) throw new Error("UI sent an invalid submission");
      submissions.push(body);
    }
  });
  await page.goto("/");
  await expect(
    page.getByText("Controlled runtime · fictional browser-verification responses"),
  ).toBeVisible();
  await expect(page.getByRole("heading", { name: "Start with a conversation" })).toBeVisible();
  await page.screenshot({ path: path.join(shots, "empty-desktop.png"), fullPage: true });
  const baseline = (await counts(request)).chats;
  await page.getByRole("button", { name: "Paste transcript", exact: true }).click();
  const text =
    "Caller: Please call me back. Please call me back.\nRepresentative: Your request is recorded.";
  await page.getByLabel("Transcript text").fill(text);
  await expect(page.getByRole("button", { name: "Save new version" })).toBeEnabled();
  await page.getByRole("button", { name: "Save new version" }).click();
  await expect(page.getByTestId("transcript-text")).toHaveText(text);
  await page.getByLabel("Classification model", { exact: true }).selectOption("qwen35-4b");
  await page.getByRole("combobox", { name: "Outcome", exact: true }).selectOption("needs_review");
  await page.getByRole("combobox", { name: "Outcome", exact: true }).selectOption("");
  await page
    .getByRole("combobox", { name: "Fictional development case", exact: true })
    .selectOption("demo-101");
  expect((await counts(request)).chats).toBe(baseline);
  await page.getByRole("button", { name: /^Classify saved version/ }).click();
  await expect(page.locator(".result .outcome")).toHaveText("Callback required");
  await expect(page.locator(".conversation mark")).toHaveCount(2);
  await expect(page.locator(".conversation mark").first()).toHaveText("Please call me back.");
  expect((await counts(request)).chats).toBe(baseline + 1);
  const originalRun = await page.locator(".history .run").first().textContent();
  if (originalRun === null) throw new Error("Missing original history row");
  await page.getByLabel("Review decision", { exact: true }).selectOption("no_callback");
  await page
    .getByLabel("Review note", { exact: false })
    .fill("Human disagreement, retained separately.");
  await page.getByRole("button", { name: "Save human decision" }).click();
  await expect(page.getByText("Latest saved decision:")).toContainText("No callback");
  await expect(page.locator(".result .outcome")).toHaveText("Callback required");
  expect((await counts(request)).chats).toBe(baseline + 1);
  await page.screenshot({ path: path.join(shots, "review-desk-desktop.png"), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: path.join(shots, "review-desk-narrow.png"), fullPage: true });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
  const axeNarrow = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(axeNarrow.violations).toEqual([]);
  await page.setViewportSize({ width: 1440, height: 1000 });
  const axeDesktop = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(axeDesktop.violations).toEqual([]);

  await page.getByRole("button", { name: "Edit latest transcript" }).click();
  const edited =
    "Caller: Please call me back.\nRepresentative: I will pass on your revised message.";
  await page.getByLabel("Transcript text").fill(edited);
  await page.getByRole("button", { name: "Save new version" }).click();
  await expect(page.getByTestId("transcript-text")).toHaveText(edited);
  expect((await counts(request)).chats).toBe(baseline + 1);
  await control(request, { mode: "hold" });
  await page.getByRole("button", { name: /^Classify saved version/ }).click();
  await expect(page.getByText("Classification in progress", { exact: true })).toBeVisible();
  await page.locator(".history .run").first().click();
  await expect(page.getByTestId("transcript-text")).toHaveText(text);
  await expect(page.locator(".result .outcome")).toHaveText("Callback required");
  await page.screenshot({ path: path.join(shots, "loading-with-history.png"), fullPage: true });

  const submitted = submissions.at(-1);
  if (!submitted) throw new Error("Missing explicit submission");
  const second = await browser.newContext();
  const tab = await second.newPage();
  await tab.goto("http://127.0.0.1:18880/");
  await expect(tab.getByRole("button", { name: /^Classify saved version/ })).toBeDisabled();
  const sessionResponse = await request.get("/api/v1/session");
  const session: unknown = await sessionResponse.json();
  if (
    !session ||
    typeof session !== "object" ||
    !("nonce" in session) ||
    typeof session.nonce !== "string"
  )
    throw new Error("Invalid session");
  const rejected = await request.post("/api/v1/jobs", {
    data: submitted,
    headers: {
      Origin: "http://127.0.0.1:18880",
      "X-Workspace-Nonce": session.nonce,
      "Idempotency-Key": "second-tab",
    },
  });
  expect(rejected.status()).toBe(409);
  await second.close();
  await page.reload();
  await expect(page.getByText("Classification in progress", { exact: true })).toBeVisible();
  expect((await counts(request)).chats).toBe(baseline + 2);
  await control(request, { action: "release" });
  await expect(page.getByText("Classification in progress", { exact: true })).toBeHidden();
  expect((await counts(request)).chats).toBe(baseline + 2);
  await expect(page.locator(".history .run")).toHaveCount(2);
  await page.locator(".history .run").nth(1).click();
  await expect(page.getByTestId("transcript-text")).toHaveText(text);
  await expect(page.locator(".history .run").nth(1)).toHaveText(originalRun);

  await control(request, { mode: "malformed" });
  await page.getByRole("button", { name: /^Classify saved version/ }).click();
  await expect(page.locator(".result")).toContainText("Classification failed · invalid_output");
  await expect(page.getByText(/Classification submitted\./)).toBeHidden();
  await expect(page.locator(".result .outcome")).toHaveCount(0);
  await page.screenshot({ path: path.join(shots, "malformed-output.png"), fullPage: true });
  await page.locator(".history .run").last().click();
  await expect(page.locator(".result .outcome")).toHaveText("Callback required");
  await control(request, { mode: "unavailable" });
  await page.getByRole("button", { name: "Reconnect / check availability" }).click();
  await expect(page.getByText(/Local runtime unavailable/)).toBeVisible();
  await expect(page.getByRole("button", { name: /^Classify saved version/ })).toBeDisabled();
  await expect(page.locator(".result .outcome")).toHaveText("Callback required");
  await page.screenshot({ path: path.join(shots, "runtime-unavailable.png"), fullPage: true });

  await control(request, { mode: "timeout" });
  await page.getByRole("button", { name: "Reconnect / check availability" }).click();
  await expect(page.getByRole("button", { name: /^Classify saved version/ })).toBeEnabled();
  await page.getByRole("button", { name: /^Classify saved version/ }).click();
  await expect(page.locator(".result")).toContainText("Classification failed · timeout");
  await expect(page.getByText("Runtime recovery required", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: /^Classify saved version/ })).toBeDisabled();
  await page.screenshot({ path: path.join(shots, "timeout-recovery.png"), fullPage: true });
  await expect.poll(async () => (await counts(request)).active).toBe(0);
  await control(request, { action: "recover" });
  await control(request, { mode: "success" });
  await page.getByRole("button", { name: "Reconnect / check availability" }).click();

  let responseDropped = false;
  await page.route("**/api/v1/jobs", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    await route.fetch();
    await route.abort();
    responseDropped = true;
  });
  const beforeLoss = (await counts(request)).chats;
  await expect(page.getByRole("button", { name: /^Classify saved version/ })).toBeEnabled();
  await page.getByRole("button", { name: /^Classify saved version/ }).click();
  await expect.poll(() => responseDropped).toBe(true);
  await expect(
    page.getByText("Submission acceptance is unconfirmed", { exact: true }),
  ).toBeVisible();
  await page.unroute("**/api/v1/jobs");
  await page.reload();
  await expect(
    page.getByText("Submission acceptance is unconfirmed", { exact: true }),
  ).toBeHidden();
  await expect.poll(async () => (await counts(request)).chats).toBe(beforeLoss + 1);
  await expect(page.getByText("Classification in progress", { exact: true })).toBeHidden();
  await expect(page.locator(".history .run")).toHaveCount(5);

  await control(request, { action: "restart" });
  await expect
    .poll(async () => {
      try {
        const response = await request.get("/api/v1/session", { timeout: 1000 });
        const value: unknown = await response.json();
        return response.ok() && validSession(value) && value.nonce !== session.nonce;
      } catch {
        return false;
      }
    })
    .toBe(true);
  await page.reload();
  await expect(page.locator(".history .run")).toHaveCount(5);
  await page.locator(".history .run").last().click();
  await expect(page.getByTestId("transcript-text")).toHaveText(text);
  await expect(page.getByText("Latest saved decision:")).toContainText("No callback");
  await page.getByText("Inspect version and run provenance").click();
  await expect(page.getByText("controlled-browser-fixture", { exact: true })).toBeVisible();
  await page.screenshot({ path: path.join(shots, "preserved-provenance.png"), fullPage: true });
  expect(errors).toEqual([]);
  expect([...apiOrigins]).toEqual(["http://127.0.0.1:18880"]);
  fs.writeFileSync(
    path.join(shots, "browser-evidence.json"),
    `${JSON.stringify(
      {
        scope:
          "Production Next.js / Nginx / FastAPI with controlled Ollama HTTP fixture; no live inference",
        assertions: [
          "explicit submission",
          "no selector/edit/review/reload inference",
          "exact overlapping/repeated quote highlights",
          "version/run persistence",
          "separate review",
          "single-origin requests",
          "second-tab contention",
          "lost-response reconciliation",
          "runtime failure states",
          "server restart",
          "desktop/narrow accessibility",
        ],
        apiOrigins: [...apiOrigins],
        axeViolations: {
          desktop: axeDesktop.violations.length,
          narrow: axeNarrow.violations.length,
        },
        controlledRequests: (await counts(request)).chats,
      },
      null,
      2,
    )}\n`,
  );
});

test("keyboard, Unicode limits, recoverable save errors and interrupted work", async ({
  page,
  request,
}) => {
  await control(request, { mode: "success" });
  await page.goto("/");
  const before = (await counts(request)).chats;
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to review workspace" })).toBeFocused();
  await page.keyboard.press("Enter");
  const paste = page.getByRole("button", { name: "Paste transcript", exact: true });
  await paste.focus();
  await page.keyboard.press("Enter");
  const editor = page.getByLabel("Transcript text");
  await expect(editor).toBeFocused();
  const save = page.getByRole("button", { name: "Save new version" });
  await editor.fill("   ");
  await expect(save).toBeDisabled();
  await editor.fill("é".repeat(6001));
  await expect(save).toBeDisabled();
  await expect(page.locator("#text-limit")).toContainText("12,002 / 12,000");
  await page.screenshot({ path: path.join(shots, "input-limit.png"), fullPage: true });
  const unicode = `Caller: café 東京 👩🏽‍💻\n${"long".repeat(1600)}\nRepresentative: Please call me back.`;
  await editor.fill(unicode);
  await expect(save).toBeEnabled();
  await page.route("**/api/v1/cases", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: {
          code: "storage_unavailable",
          message: "Cannot save workspace records; check local storage before retrying.",
        },
      }),
    });
  });
  await page.keyboard.press("Tab");
  await expect(save).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("alert").filter({ hasText: "Action not confirmed" })).toBeVisible();
  await expect(editor).toHaveValue(unicode);
  await page.unroute("**/api/v1/cases");
  await save.click();
  await expect(page.getByTestId("transcript-text")).toHaveText(unicode);
  await expect(page.locator("#transcript-heading")).toBeFocused();
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
  await page.screenshot({ path: path.join(shots, "unicode-long-narrow.png"), fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.getByLabel("Classification model", { exact: true }).selectOption("qwen35-4b");
  await control(request, { mode: "worker_error" });
  await page.getByRole("button", { name: /^Classify saved version/ }).click();
  await expect(page.locator(".result")).toContainText("Processing interrupted");
  await expect(page.locator(".result .outcome")).toHaveCount(0);
  await expect(page.getByText("Runtime recovery required", { exact: true })).toBeVisible();
  await page.screenshot({ path: path.join(shots, "interrupted.png"), fullPage: true });
  expect((await counts(request)).chats).toBe(before);
  await control(request, { action: "recover" });
  await control(request, { mode: "success" });
  await page.getByRole("button", { name: "Reconnect / check availability" }).click();
  await page
    .getByRole("combobox", { name: "Fictional development case", exact: true })
    .selectOption("demo-101");
  await page.getByRole("button", { name: "Load fictional case" }).click();
  await expect(
    page.getByRole("heading", { level: 1, name: "Appointment confirmation" }),
  ).toBeVisible();
  expect((await counts(request)).chats).toBe(before);
  const model = page.getByLabel("Classification model", { exact: true });
  await expect(page.getByRole("button", { name: /^Classify saved version/ })).toBeEnabled();
  await expect(model).toBeEnabled();
  await model.focus();
  await expect(model).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: /^Classify saved version/ })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator(".result .outcome")).toHaveText("Callback required");
  const review = page.getByLabel("Review decision", { exact: true });
  for (
    let tabs = 0;
    tabs < 20 && !(await review.evaluate((element) => element === document.activeElement));
    tabs++
  )
    await page.keyboard.press("Tab");
  await expect(review).toBeFocused();
  await page.keyboard.press("Home");
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("Tab");
  await page.keyboard.type("Keyboard review");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Save human decision" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByText("Latest saved decision:")).toBeVisible();
  const provenance = page.getByText("Inspect version and run provenance", { exact: true });
  for (
    let tabs = 0;
    tabs < 20 && !(await provenance.evaluate((element) => element === document.activeElement));
    tabs++
  )
    await page.keyboard.press("Tab");
  await expect(provenance).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByText("controlled-browser-fixture", { exact: true })).toBeVisible();
  expect((await counts(request)).chats).toBe(before + 1);
  await page.route("**/api/v1/runtime", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "{}" }),
  );
  await page.getByRole("button", { name: "Reconnect / check availability" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "unexpected response" })).toBeVisible();
  await expect(page.locator(".result .outcome")).toHaveText("Callback required");
  await page.unroute("**/api/v1/runtime");
  await page.getByRole("button", { name: "Reconnect / check availability" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "unexpected response" })).toBeHidden();
  expect((await counts(request)).chats).toBe(before + 1);
});

import { expect, type Page, test } from "@playwright/test";
import type { components } from "../lib/api.generated";

type Schema = components["schemas"];
const created = "2026-11-07T00:00:00Z";
const hash = "a".repeat(64);
const model: Schema["ModelEntry"] = {
  id: "model",
  model_id: "synthetic-classifier",
  runtime: "ollama",
  stages: ["classification"],
  settings: {},
};
const record = (id: string): Schema["CaseRecord"] => ({
  id,
  title: `Case ${id}`,
  created_at: created,
  current_version_id: `version-${id}`,
});
const version = (id: string, text: string): Schema["VersionRecord"] => ({
  id: `version-${id}`,
  case_id: id,
  parent_version_id: null,
  text_sha256: hash,
  origin: "pasted",
  created_at: created,
  text,
});
const job = (
  id: string,
  caseId: string,
  status: "running" | "succeeded" = "running",
): Schema["JobRecord"] => ({
  id,
  case_id: caseId,
  transcript_version_id: `version-${caseId}`,
  model,
  source: { source_sha256: hash, git_revision: null, working_tree_clean: true },
  status,
  created_at: created,
  finished_at: status === "running" ? null : created,
  run_id: status === "running" ? null : `run-${id}`,
  error: null,
});
type State = { cases: string[]; texts: Record<string, string>; jobs: Schema["JobRecord"][] };

async function fixture(page: Page, state: State) {
  let runtimeReads = 0;
  let releaseSave = () => {};
  let savePending = false;
  await page.route("**/api/v1/**", async (route) => {
    const path = new URL(route.request().url()).pathname.replace("/api/v1", "");
    const reply = (body: unknown) =>
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
    if (path === "/runtime") {
      runtimeReads++;
      return reply({
        status: "available",
        server_version: "controlled",
        models: [],
        inference_verified: false,
        admission: state.jobs.some((j) => j.status === "running") ? "busy" : "ready",
        verification_mode: "controlled",
      });
    }
    if (path === "/session") return reply({ nonce: "fictional-session" });
    if (path === "/jobs") return reply(state.jobs);
    if (path === "/development-cases" || path.endsWith("/reviews")) return reply([]);
    if (path === "/cases" && route.request().method() === "GET")
      return reply(
        state.cases.map((id) => ({
          ...record(id),
          latest_job_id: state.jobs.find((j) => j.case_id === id)?.id ?? null,
          human_reviewed: false,
          outcome: null,
          processing_status: null,
        })),
      );
    if (path === "/cases" && route.request().method() === "POST") {
      const body: unknown = route.request().postDataJSON();
      if (!body || typeof body !== "object" || !("text" in body) || typeof body.text !== "string")
        throw new Error("Invalid fictional save");
      const text = body.text;
      state.texts.c = text;
      state.cases.push("c");
      await new Promise<void>((resolve) => {
        releaseSave = resolve;
        savePending = true;
      });
      return reply({ case: record("c"), version: version("c", text) });
    }
    const detail = path.match(/^\/cases\/([^/]+)$/)?.[1];
    if (detail) {
      const { text, ...summary } = version(detail, state.texts[detail] ?? "Fictional text");
      return reply({
        case: record(detail),
        versions: [summary],
        jobs: state.jobs.filter((j) => j.case_id === detail),
      });
    }
    const versionCase = path.match(/^\/cases\/([^/]+)\/versions\/[^/]+$/)?.[1];
    if (versionCase)
      return reply(version(versionCase, state.texts[versionCase] ?? "Fictional text"));
    const runId = path.match(/^\/runs\/([^/]+)$/)?.[1];
    if (runId) {
      const selected = state.jobs.find((j) => j.run_id === runId);
      if (!selected) throw new Error("Unknown fictional run");
      const result: Schema["RunSuccessRecord"] = {
        status: "success",
        run: {
          provenance: {
            run_id: runId,
            case_id: selected.case_id,
            stage: "classification",
            model,
            model_digest: "controlled",
            runtime_version: "controlled",
            runtime_url: null,
            transcript_version_id: selected.transcript_version_id,
            transcript_sha256: hash,
            prompt_version: "callback-text-v2",
            prompt_sha256: hash,
            policy_version: "1.0",
            policy_sha256: hash,
            request_sha256: hash,
            model_metadata_sha256: null,
            started_at: created,
            elapsed_seconds: 0,
          },
          output: {
            label: "callback_required",
            rule_ids: ["CB-002"],
            reason: "Controlled response.",
            evidence: [state.texts[selected.case_id] ?? "Fictional text"],
          },
        },
      };
      return reply(result);
    }
    throw new Error(`Unhandled fictional request ${path}`);
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Case a", exact: true })).toBeVisible();
  return {
    runtimeReads: () => runtimeReads,
    savePending: () => savePending,
    releaseSave: () => releaseSave(),
  };
}

test("pending saves prevent loss of subsequent typing", async ({ page }) => {
  const pending = await fixture(page, {
    cases: ["a"],
    texts: { a: "Saved original text" },
    jobs: [],
  });
  await page.getByRole("button", { name: "Paste transcript", exact: true }).click();
  const editor = page.getByLabel("Transcript text");
  await editor.fill("Text submitted for save");
  await page.getByRole("button", { name: "Save new version" }).click();
  await expect.poll(pending.savePending).toBe(true);
  try {
    await expect(editor).toBeDisabled();
    await page.keyboard.type(" extra typing while pending");
    await expect(editor).toHaveValue("Text submitted for save");
  } finally {
    pending.releaseSave();
  }
  await expect(page.getByTestId("transcript-text")).toHaveText("Text submitted for save");
});

test("reconnect preserves an existing case edit over an abandoned new draft", async ({ page }) => {
  const view = await fixture(page, { cases: ["a"], texts: { a: "Saved original text" }, jobs: [] });
  await page.getByRole("button", { name: "Paste transcript", exact: true }).click();
  await page.getByLabel("Transcript text").fill("Abandoned new-case draft");
  await page.locator(".case-link").click();
  await page.getByRole("button", { name: "Edit latest transcript" }).click();
  await page.getByLabel("Transcript text").fill("Current edit of case a");
  const reads = view.runtimeReads();
  await page.getByRole("button", { name: "Reconnect / check availability" }).click();
  await expect.poll(view.runtimeReads).toBeGreaterThan(reads + 1);
  await expect(page.getByRole("heading", { name: "Case a", exact: true })).toBeVisible();
  await expect(page.getByLabel("Transcript text")).toHaveValue("Current edit of case a");
});

test("a completed job is reconciled while another case job is running", async ({ page }) => {
  const state: State = {
    cases: ["a", "b"],
    texts: { a: "First saved text", b: "Second saved text" },
    jobs: [job("job-a", "a")],
  };
  await fixture(page, state);
  await expect(page.getByText("This run is processing", { exact: true })).toBeVisible();
  state.jobs = [job("job-b", "b"), job("job-a", "a", "succeeded")];
  await expect(page.locator(".processing")).toContainText("job-b");
  await expect(page.locator(".result .outcome")).toHaveText("Callback required");
  await expect(page.locator(".history .run").first()).toContainText("succeeded");
  state.jobs = [job("job-b", "b", "succeeded"), job("job-a", "a", "succeeded")];
  await expect(page.getByText("Classification in progress", { exact: true })).toBeHidden();
  await expect(page.locator(".result .outcome")).toHaveText("Callback required");
});

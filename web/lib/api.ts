import Ajv2020, { type ValidateFunction } from "ajv/dist/2020";
import schema from "../../docs/api/openapi.json";
import type { components } from "./api.generated";

type Schemas = components["schemas"];
export type CaseSummary = Schemas["CaseSummary"];
export type CaseDetail = Schemas["CaseDetail"];
export type Version = Schemas["VersionRecord"];
export type Job = Schemas["JobRecord"];
export type Review = Schemas["ReviewRecord"];
export type Outcome = Schemas["CreateReview"]["decision"];
export type Run = Schemas["RunSuccessRecord"] | Schemas["RunFailureRecord"];
export type Runtime = Schemas["RuntimeReport"];
export type Submission = { key: string; payload: Schemas["SubmitJob"] };
export type Filters = { outcome: string; review: string; status: string };

const ajv = new Ajv2020({ strict: false, validateFormats: false });
ajv.addSchema(schema, "workspace");
function model<T>(name: string): ValidateFunction<T> {
  return ajv.compile<T>({ $ref: `workspace#/components/schemas/${name}` });
}
function array<T>(name: string): ValidateFunction<T[]> {
  return ajv.compile<T[]>({
    type: "array",
    items: { $ref: `workspace#/components/schemas/${name}` },
  });
}
const parseSession = model<Schemas["Session"]>("Session");
const parseCreated = model<Schemas["CreatedCase"]>("CreatedCase");
const parseCase = model<CaseDetail>("CaseDetail");
const parseVersion = model<Version>("VersionRecord");
const parseJob = model<Job>("JobRecord");
const parseReview = model<Review>("ReviewRecord");
const parseRuntime = model<Runtime>("RuntimeReport");
const parseCases = array<CaseSummary>("CaseSummary");
const parseJobs = array<Job>("JobRecord");
const parseReviews = array<Review>("ReviewRecord");
const parseExamples = array<Schemas["DevelopmentSummary"]>("DevelopmentSummary");
const parseRun = ajv.compile<Run>({
  oneOf: [
    { $ref: "workspace#/components/schemas/RunSuccessRecord" },
    { $ref: "workspace#/components/schemas/RunFailureRecord" },
  ],
});
const parseSubmission = ajv.compile<Submission>({
  type: "object",
  required: ["key", "payload"],
  additionalProperties: false,
  properties: {
    key: { type: "string", pattern: "^[a-z0-9-]{1,120}$" },
    payload: { $ref: "workspace#/components/schemas/SubmitJob" },
  },
});
const parseError = ajv.compile<{ error: { code: string; message: string } }>({
  type: "object",
  required: ["error"],
  properties: {
    error: {
      type: "object",
      required: ["code", "message"],
      properties: { code: { type: "string" }, message: { type: "string" } },
    },
  },
});

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
  }
}
export function message(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return "The local connection was interrupted. Reconnect to check saved work before retrying.";
}
async function read<T>(
  path: string,
  validate: ValidateFunction<T>,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    cache: "no-store",
    signal: AbortSignal.timeout(15_000),
    ...init,
  });
  const value: unknown = await response.json();
  if (!response.ok) {
    if (parseError(value))
      throw new ApiError(response.status, value.error.code, value.error.message);
    throw new ApiError(
      response.status,
      "request_failed",
      "The local API could not complete this request.",
    );
  }
  if (!validate(value))
    throw new ApiError(
      502,
      "invalid_api_response",
      "The local API returned an unexpected response. Reconnect before continuing.",
    );
  return value;
}
let nonce: string | null = null;
async function write<T>(
  path: string,
  body: unknown,
  validate: ValidateFunction<T>,
  key?: string,
): Promise<T> {
  if (!nonce) nonce = (await read("/session", parseSession)).nonce;
  return read(path, validate, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Workspace-Nonce": nonce,
      ...(key ? { "Idempotency-Key": key } : {}),
    },
    body: JSON.stringify(body),
  });
}
export const api = {
  reconnect() {
    nonce = null;
  },
  cases(filters: Filters, offset = 0) {
    const query = new URLSearchParams({ offset: String(offset), limit: "50" });
    for (const [key, value] of Object.entries(filters)) if (value) query.set(key, value);
    return read(`/cases?${query}`, parseCases);
  },
  detail: (id: string) => read(`/cases/${encodeURIComponent(id)}`, parseCase),
  version: (caseId: string, id: string) =>
    read(`/cases/${encodeURIComponent(caseId)}/versions/${encodeURIComponent(id)}`, parseVersion),
  jobs: () => read("/jobs", parseJobs),
  job: (id: string) => read(`/jobs/${encodeURIComponent(id)}`, parseJob),
  runReviews: (id: string, offset = 0) =>
    read(`/runs/${encodeURIComponent(id)}/reviews?offset=${offset}&limit=50`, parseReviews),
  history: (id: string, offset = 0) =>
    read(`/cases/${encodeURIComponent(id)}/runs?offset=${offset}&limit=50`, parseJobs),
  reviews: (id: string, offset = 0) =>
    read(`/cases/${encodeURIComponent(id)}/reviews?offset=${offset}&limit=50`, parseReviews),
  run: (id: string) => read(`/runs/${encodeURIComponent(id)}`, parseRun),
  runtime: () => read("/runtime", parseRuntime),
  examples: () => read("/development-cases", parseExamples),
  create: (text: string) => write("/cases", { text }, parseCreated),
  load: (id: string) =>
    write(`/development-cases/${encodeURIComponent(id)}/load`, {}, parseCreated),
  save: (caseId: string, parent: string, text: string) =>
    write(
      `/cases/${encodeURIComponent(caseId)}/versions`,
      { parent_version_id: parent, text },
      parseVersion,
    ),
  submit: (submission: Submission) => write("/jobs", submission.payload, parseJob, submission.key),
  submission: (key: string) => read(`/submissions/${encodeURIComponent(key)}`, parseJob),
  review: (runId: string, decision: Outcome, note: string, key: string) =>
    write(`/runs/${encodeURIComponent(runId)}/reviews`, { decision, note }, parseReview, key),
};

export function remember(key: string, value: unknown): void {
  try {
    if (value === null) localStorage.removeItem(`vcr:${key}`);
    else localStorage.setItem(`vcr:${key}`, JSON.stringify(value));
  } catch {
    /* Server history remains authoritative when browser storage is unavailable. */
  }
}
export function recallSubmission(): Submission | null {
  try {
    const value: unknown = JSON.parse(localStorage.getItem("vcr:submission") ?? "null");
    return parseSubmission(value) ? value : null;
  } catch {
    return null;
  }
}
export function recallText(key: string): string {
  try {
    const value: unknown = JSON.parse(localStorage.getItem(`vcr:${key}`) ?? "null");
    return typeof value === "string" ? value : "";
  } catch {
    return "";
  }
}

"use client";

import { useState } from "react";
import type { Job, Outcome, Review, Run, Version } from "../lib/api";

export const outcomes: Record<Outcome, string> = {
  callback_required: "Callback required",
  no_callback: "No callback",
  needs_review: "Needs review",
};
export function short(id: string) {
  return id.slice(0, 8);
}
export function date(value: string) {
  return new Date(value).toLocaleString();
}
export function Badge({ outcome, label }: { outcome?: Outcome | null; label?: string }) {
  return (
    <span className={`badge ${outcome ?? "neutral"}`}>{outcome ? outcomes[outcome] : label}</span>
  );
}

export function Evidence({ text, quotes }: { text: string; quotes: string[] }) {
  const spans: { start: number; end: number }[] = [];
  for (const quote of quotes) {
    let start = text.indexOf(quote);
    while (quote && start !== -1) {
      spans.push({ start, end: start + quote.length });
      start = text.indexOf(quote, start + quote.length);
    }
  }
  spans.sort((a, b) => a.start - b.start);
  const merged: typeof spans = [];
  for (const span of spans) {
    const last = merged.at(-1);
    if (last && span.start <= last.end) last.end = Math.max(last.end, span.end);
    else merged.push({ ...span });
  }
  const pieces: { start: number; text: string; highlighted: boolean }[] = [];
  let cursor = 0;
  for (const span of merged) {
    if (span.start > cursor)
      pieces.push({
        start: cursor,
        text: text.slice(cursor, span.start),
        highlighted: false,
      });
    pieces.push({
      start: span.start,
      text: text.slice(span.start, span.end),
      highlighted: true,
    });
    cursor = span.end;
  }
  if (cursor < text.length)
    pieces.push({
      start: cursor,
      text: text.slice(cursor),
      highlighted: false,
    });
  return (
    <div className="conversation" data-testid="transcript-text">
      {pieces.map((piece) =>
        piece.highlighted ? (
          <mark key={piece.start}>{piece.text}</mark>
        ) : (
          <span key={piece.start}>{piece.text}</span>
        ),
      )}
    </div>
  );
}

export function Recommendation({ run, job }: { run: Run | null; job: Job | null }) {
  if (job?.status === "interrupted")
    return (
      <div className="notice error">
        <strong>Processing interrupted</strong>No callback outcome was produced. Earlier runs remain
        available. Restore the local runtime and recover admission before explicitly submitting
        again.
      </div>
    );
  if (run?.status === "processing_error")
    return (
      <div className="notice error">
        <strong>Classification failed · {run.run.failure.code}</strong>
        <p>{run.run.failure.message}</p>
        <p>
          No callback outcome was produced. Earlier successful runs remain in history.{" "}
          {job?.error === "recovery_required"
            ? "Stop/restart Ollama, then recover local inference admission before another submission."
            : "You can explicitly submit again after resolving the problem."}
        </p>
      </div>
    );
  if (run?.status !== "success" || !("label" in run.run.output))
    return (
      <div className="notice">
        <strong>
          {job?.status === "running" ? "This run is processing" : "No classification for this view"}
        </strong>
        <p>
          Save text, select an available model and explicitly classify. Earlier recommendations stay
          in run history.
        </p>
      </div>
    );
  const output = run.run.output;
  return (
    <>
      <Badge outcome={output.label} />
      <h3 className={`outcome ${output.label}`}>{outcomes[output.label]}</h3>
      <p>{output.reason}</p>
      <p className="rule">
        Policy {run.run.provenance.policy_version} · {output.rule_ids.join(", ")}
      </p>
      <p className="help">
        Run {short(run.run.provenance.run_id)} · version{" "}
        {short(run.run.provenance.transcript_version_id)}
      </p>
      <details className="quotes">
        <summary>Supporting quotes ({output.evidence.length})</summary>
        {output.evidence.map((quote) => (
          <blockquote key={quote}>{quote}</blockquote>
        ))}
      </details>
    </>
  );
}

export function HumanReview({
  run,
  job,
  events,
  busy,
  save,
  more,
}: {
  run: Run | null;
  job: Job | null;
  events: Review[];
  busy: boolean;
  save: (decision: Outcome, note: string) => void;
  more: () => void;
}) {
  const [decision, setDecision] = useState<Outcome | "">("");
  const [note, setNote] = useState("");
  const enabled = run?.status === "success" && "label" in run.run.output;
  const current = events.filter((event) => event.run_id === job?.run_id);
  const noteBytes = new TextEncoder().encode(note).length;
  return (
    <form
      className="review-form"
      onSubmit={(event) => {
        event.preventDefault();
        if (decision && enabled) save(decision, note);
      }}
    >
      <h2>Human review</h2>
      <p className="help">
        Your decision is a separate record. It does not replace model output or update gold.
      </p>
      {current[0] && (
        <p className="help">
          Latest saved decision: <strong>{outcomes[current[0].decision]}</strong>
        </p>
      )}
      <label htmlFor="review-choice">Review decision</label>
      <select
        id="review-choice"
        disabled={!enabled || busy}
        value={decision}
        onChange={(event) => {
          const value = event.target.value;
          if (
            value === "callback_required" ||
            value === "no_callback" ||
            value === "needs_review" ||
            value === ""
          )
            setDecision(value);
        }}
      >
        <option value="">Choose a decision…</option>
        {Object.entries(outcomes).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
      <label htmlFor="review-note">
        Review note <span className="muted">(optional)</span>
      </label>
      <textarea
        id="review-note"
        disabled={!enabled || busy}
        value={note}
        placeholder="What did you find?"
        onChange={(event) => setNote(event.target.value)}
      />
      {noteBytes > 2000 && (
        <p className="field-error" role="alert">
          Keep the note within 2,000 UTF-8 bytes.
        </p>
      )}
      <button type="submit" disabled={!enabled || !decision || busy || noteBytes > 2000}>
        Save human decision
      </button>
      {current.length > 0 && (
        <details>
          <summary>Review history ({current.length})</summary>
          {current.map((event) => (
            <div className="review-event" key={event.id}>
              <strong>{outcomes[event.decision]}</strong>
              <p>{event.note || "No note"}</p>
              <small>
                {date(event.created_at)} · {event.reviewer}
              </small>
            </div>
          ))}
        </details>
      )}
      {events.length > 0 && events.length % 50 === 0 && (
        <button type="button" onClick={more}>
          Load earlier review events
        </button>
      )}
    </form>
  );
}

export function Provenance({
  job,
  version,
  run,
}: {
  job: Job | null;
  version: Version;
  run: Run | null;
}) {
  return (
    <details className="provenance">
      <summary>Inspect version and run provenance</summary>
      <dl>
        <dt>Transcript version</dt>
        <dd>{version.id}</dd>
        <dt>Transcript SHA-256</dt>
        <dd>{version.text_sha256}</dd>
        <dt>Origin</dt>
        <dd>
          {version.origin}
          {version.development_case_id ? ` / ${version.development_case_id}` : ""}
        </dd>
        <dt>Parent version</dt>
        <dd>{version.parent_version_id ?? "Original input"}</dd>
      </dl>
      {job && (
        <>
          <h3>Submitted configuration</h3>
          <dl>
            <dt>Job / status</dt>
            <dd>
              {job.id} / {job.status}
            </dd>
            <dt>Model configuration</dt>
            <dd>
              {job.model.id} / {job.model.model_id}
            </dd>
            <dt>Submitted</dt>
            <dd>{date(job.created_at)}</dd>
            <dt>Source revision</dt>
            <dd>
              {job.source.git_revision ?? "Unknown"} ·{" "}
              {job.source.working_tree_clean ? "clean tree" : "uncommitted source"}
            </dd>
            <dt>Source SHA-256</dt>
            <dd>{job.source.source_sha256}</dd>
          </dl>
          <pre>{JSON.stringify(job.model.settings, null, 2)}</pre>
        </>
      )}
      {run && (
        <>
          <h3>Recorded run</h3>
          <dl>
            <dt>Run ID</dt>
            <dd>{run.run.provenance.run_id}</dd>
            <dt>Model digest</dt>
            <dd>{run.run.provenance.model_digest ?? "Unknown"}</dd>
            <dt>Runtime</dt>
            <dd>
              {run.run.provenance.runtime_version} / {run.run.provenance.runtime_url ?? "Unknown"}
            </dd>
            <dt>Prompt / policy</dt>
            <dd>
              {run.run.provenance.prompt_version ?? "Unknown"} /{" "}
              {run.run.provenance.policy_version ?? "Unknown"}
            </dd>
            <dt>Elapsed time</dt>
            <dd>{run.run.provenance.elapsed_seconds.toFixed(3)} seconds · this run only</dd>
          </dl>
          <details>
            <summary>Prompt, policy and request hashes</summary>
            <pre>
              {JSON.stringify(
                {
                  prompt: run.run.provenance.prompt_sha256,
                  policy: run.run.provenance.policy_sha256,
                  request: run.run.provenance.request_sha256,
                  model_metadata: run.run.provenance.model_metadata_sha256,
                },
                null,
                2,
              )}
            </pre>
          </details>
        </>
      )}
    </details>
  );
}

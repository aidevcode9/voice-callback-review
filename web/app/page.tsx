"use client";

import { useState } from "react";
import { useWorkspace } from "../lib/use-workspace";
import {
  Badge,
  date,
  Evidence,
  HumanReview,
  outcomes,
  Provenance,
  Recommendation,
  short,
} from "./components";

export default function ReviewDesk() {
  const desk = useWorkspace();
  const { actions, view, draft, runtime, active, busy } = desk;
  const [example, setExample] = useState("");
  const loaded = view.kind === "loaded" ? view : null;
  const selected = runtime?.models.find(
    (model) =>
      model.id === desk.model && model.selectable && model.stages.includes("classification"),
  );
  const bytes = new TextEncoder().encode(draft?.text ?? "").length;
  const validDraft = !!draft?.text.trim() && bytes <= 12000;
  const canSubmit =
    !!loaded &&
    !!selected &&
    !draft &&
    !busy &&
    !active &&
    !desk.pending &&
    desk.connected &&
    runtime?.admission === "ready";
  const output =
    loaded?.run?.status === "success" && "label" in loaded.run.run.output
      ? loaded.run.run.output
      : null;
  const displayedMatches = loaded?.job?.transcript_version_id === loaded?.version.id;
  const errorId = desk.error ? "connection-error" : undefined;
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to review workspace
      </a>
      {runtime?.verification_mode === "controlled" && (
        <div className="verification">
          Controlled runtime · fictional browser-verification responses · no model inference
        </div>
      )}
      <header className="brand">
        <strong>Voice Callback Review</strong>
        <span>Review desk · local workspace</span>
      </header>
      <div className="shell">
        <nav aria-label="Workspace cases">
          <h2>Cases</h2>
          <div className="filters">
            <label>
              Outcome
              <select
                value={desk.filters.outcome}
                onChange={(e) =>
                  actions.setFilters({
                    ...desk.filters,
                    outcome: e.target.value,
                  })
                }
              >
                <option value="">All outcomes</option>
                {Object.entries(outcomes).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Human review
              <select
                value={desk.filters.review}
                onChange={(e) =>
                  actions.setFilters({
                    ...desk.filters,
                    review: e.target.value,
                  })
                }
              >
                <option value="">All reviews</option>
                <option value="pending">Not reviewed</option>
                <option value="reviewed">Reviewed</option>
              </select>
            </label>
            <label>
              Processing
              <select
                value={desk.filters.status}
                onChange={(e) =>
                  actions.setFilters({
                    ...desk.filters,
                    status: e.target.value,
                  })
                }
              >
                <option value="">All statuses</option>
                <option value="running">Running</option>
                <option value="succeeded">Succeeded</option>
                <option value="failed">Failed</option>
                <option value="interrupted">Interrupted</option>
              </select>
            </label>
          </div>
          <div className="case-list">
            {desk.cases.map((item) => (
              <button
                key={item.id}
                type="button"
                className="case-link"
                aria-current={loaded?.detail.case.id === item.id ? "true" : undefined}
                disabled={busy}
                onClick={() => actions.select(item.id, item.latest_job_id ?? undefined)}
              >
                <small>{short(item.id)}</small>
                <strong>{item.title}</strong>
                <Badge outcome={item.outcome} label={item.processing_status ?? "Not classified"} />
              </button>
            ))}
            {!desk.cases.length && (
              <p className="help">
                {desk.connected
                  ? "No matching cases. Paste text, load a fictional case, or clear the filters."
                  : "Connecting to the local workspace…"}
              </p>
            )}
          </div>
          {desk.cases.length > 0 && desk.cases.length % 50 === 0 && (
            <button type="button" onClick={actions.moreCases}>
              Load more cases
            </button>
          )}
          <div className="nav-actions">
            <button type="button" disabled={busy} onClick={actions.newDraft}>
              Paste transcript
            </button>
            <label>
              Fictional development case
              <select value={example} onChange={(e) => setExample(e.target.value)}>
                <option value="">Choose an example…</option>
                {desk.examples.map((item) => (
                  <option value={item.id} key={item.id}>
                    {item.title}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              disabled={!example || busy}
              onClick={() => actions.loadExample(example)}
            >
              Load fictional case
            </button>
          </div>
          <p className="nav-footer">
            Local review workspace.
            <br />
            Held-out cases and expected answers are excluded.
            <br />
            <br />
            Audio integration is the final stage.
          </p>
        </nav>
        <main className="content" id="main">
          <div className="case-header">
            <div>
              <h1>
                {draft?.kind === "new"
                  ? "New transcript"
                  : (loaded?.detail.case.title ?? "Your review desk")}
              </h1>
              <p className="help">
                {draft?.kind === "new"
                  ? "Save this draft to create a separate case."
                  : loaded
                    ? `Case ${short(loaded.detail.case.id)} · saved version ${short(loaded.detail.case.current_version_id)}`
                    : "Start with text or a fictional development case."}
              </p>
            </div>
            <Badge
              label={
                draft?.kind === "new"
                  ? "No run to review"
                  : loaded?.job?.status === "failed"
                    ? "Processing failed"
                    : loaded?.reviews.some((review) => review.run_id === loaded.job?.run_id)
                      ? "Human reviewed"
                      : loaded?.run
                        ? "Awaiting human review"
                        : "No run to review"
              }
            />
          </div>
          <div className="status-row">
            <span className="help">
              {!runtime
                ? "Checking local runtime"
                : runtime.status === "available"
                  ? "Local runtime reachable"
                  : "Local runtime unavailable"}{" "}
              · {runtime?.admission ?? "checking admission"}
            </span>
            <button type="button" disabled={busy} onClick={() => void actions.reconnect()}>
              Reconnect / check availability
            </button>
          </div>
          {runtime?.status !== "available" && runtime && (
            <p className="notice" role="status">
              Start Ollama and check that the selected model is installed, then reconnect. Saved
              transcripts and results remain available.
            </p>
          )}
          {runtime?.admission === "busy" && !active && (
            <p className="notice" role="status">
              Another local process is using inference. Wait for it to finish, then reconnect.
            </p>
          )}
          {desk.error && (
            <div id="connection-error" role="alert" className="notice error">
              <strong>Action not confirmed</strong>
              <p>{desk.error}</p>
              <p>Reconnect to inspect saved work. No retry starts automatically.</p>
            </div>
          )}
          {desk.notice && (
            <p role="status" className="notice">
              {desk.notice}
            </p>
          )}
          {desk.pending && (
            <div className="notice">
              <strong>Submission acceptance is unconfirmed</strong>
              <p>
                The original submission key is retained. Check its status before creating another
                run.
              </p>
              <button type="button" disabled={busy} onClick={actions.checkSubmission}>
                Check original submission
              </button>
              <button
                type="button"
                disabled={busy || !!active || runtime?.admission !== "ready"}
                onClick={actions.submit}
              >
                Retry original submission
              </button>
            </div>
          )}
          {runtime?.admission === "recovery_required" && (
            <div className="notice error" role="status">
              <strong>Runtime recovery required</strong>
              <p>
                Prior work may still be running. Stop/restart Ollama, then run{" "}
                <code>voice-callback recover-inference --runtime-stopped</code> from this project.
                Reconnect afterward. Saved history remains available.
              </p>
            </div>
          )}
          {active && (
            <div className="notice processing" role="status">
              <strong>Classification in progress</strong>
              <p>
                Job {short(active.id)} · case {short(active.case_id)} · submitted version{" "}
                {short(active.transcript_version_id)}. You can inspect saved results while it
                finishes. Closing this page does not cancel the job.
              </p>
              <div className="loading-bar" />
              <button type="button" onClick={() => actions.select(active.case_id, active.id)}>
                Inspect active job
              </button>
            </div>
          )}
          <div className="workspace">
            <section className="transcript" aria-labelledby="transcript-heading">
              <div className="section-head">
                <h2 id="transcript-heading" tabIndex={-1}>
                  Transcript
                </h2>
                {loaded && !draft && (
                  <div className="actions">
                    <button type="button" disabled={busy} onClick={actions.edit}>
                      Edit latest transcript
                    </button>
                    {loaded.version.id !== loaded.detail.case.current_version_id && (
                      <button type="button" onClick={() => actions.select(loaded.detail.case.id)}>
                        View latest saved text
                      </button>
                    )}
                  </div>
                )}
              </div>
              {draft ? (
                <div className="editor">
                  <p className="help">
                    {draft.kind === "new"
                      ? "Paste a fictional conversation."
                      : `Editing from saved version ${short(draft.parent)}. Saving creates a new version.`}
                  </p>
                  <label htmlFor="transcript-input">Transcript text</label>
                  <textarea
                    id="transcript-input"
                    disabled={busy}
                    value={draft.text}
                    onChange={(e) => actions.text(e.target.value)}
                    placeholder="Caller: …"
                    aria-describedby="text-limit"
                  />
                  <p id="text-limit" className={bytes > 12000 ? "field-error" : "help"}>
                    {bytes.toLocaleString()} / 12,000 UTF-8 bytes. Text is never truncated.
                  </p>
                  <div className="actions">
                    <button
                      className="primary"
                      type="button"
                      disabled={!validDraft || busy}
                      onClick={actions.save}
                    >
                      Save new version
                    </button>
                    <button type="button" disabled={busy} onClick={actions.discard}>
                      Discard draft
                    </button>
                  </div>
                </div>
              ) : loaded ? (
                <>
                  <div className="transcript-meta">
                    Viewing{" "}
                    {loaded.job
                      ? `run ${short(loaded.job.run_id ?? loaded.job.id)}`
                      : "saved text without a selected run"}{" "}
                    · version {short(loaded.version.id)} · {date(loaded.version.created_at)}
                  </div>
                  <Evidence
                    text={loaded.version.text}
                    quotes={displayedMatches && output ? output.evidence : []}
                  />
                  <p className="evidence-note">
                    {displayedMatches && output
                      ? "Highlights show every exact occurrence of the supporting quotes in this run’s transcript. Overlapping quotes share a highlight."
                      : "No successful evidence for this view. Earlier results remain in history."}
                  </p>
                </>
              ) : (
                <div className="empty">
                  <h2>
                    {view.kind === "loading" ? "Loading saved case…" : "Start with a conversation"}
                  </h2>
                  <p>
                    Paste a transcript or choose a fictional development case. Then explicitly
                    classify a saved version.
                  </p>
                  <button type="button" onClick={actions.newDraft}>
                    Paste a transcript
                  </button>
                </div>
              )}
              <div className="classification">
                <label htmlFor="model">Classification model</label>
                <select
                  id="model"
                  value={desk.model}
                  onChange={(e) => actions.model(e.target.value)}
                >
                  <option value="">Choose an available classifier…</option>
                  {runtime?.models
                    .filter((item) => item.stages.includes("classification"))
                    .map((item) => (
                      <option key={item.id} value={item.id} disabled={!item.selectable}>
                        {item.model_id}
                        {!item.selectable ? ` · ${item.availability}` : ""}
                      </option>
                    ))}
                </select>
                <button
                  type="button"
                  className="primary"
                  disabled={!canSubmit}
                  aria-describedby={errorId ?? "submit-help"}
                  onClick={actions.submit}
                >
                  {busy
                    ? "Saving request…"
                    : loaded
                      ? `Classify saved version ${short(loaded.detail.case.current_version_id)}`
                      : "Save a transcript first"}
                </button>
                <p className="help" id="submit-help">
                  {draft
                    ? "Save or discard the draft before submitting."
                    : active
                      ? "One local inference job is active."
                      : !selected
                        ? "Select an installed compatible classifier. No model downloads automatically."
                        : "Explicit submission only. Editing, selectors and navigation do not run inference."}
                </p>
              </div>
            </section>
            <aside className="decision-column" aria-label="Recommendation and human review">
              <section className="result" aria-live="polite">
                <h2>Model recommendation</h2>
                <Recommendation
                  run={draft?.kind === "new" ? null : (loaded?.run ?? null)}
                  job={draft?.kind === "new" ? null : (loaded?.job ?? null)}
                />
              </section>
              <HumanReview
                key={loaded?.job?.run_id ?? "no-run"}
                run={draft?.kind === "new" ? null : (loaded?.run ?? null)}
                job={loaded?.job ?? null}
                events={loaded?.reviews ?? []}
                busy={busy}
                save={actions.review}
                more={actions.moreReviews}
              />
            </aside>
          </div>
          {loaded && draft?.kind !== "new" && (
            <section className="history">
              <div className="history-head">
                <h2>Run history</h2>
                <span className="help">
                  Earlier results retain their submitted transcript and model.
                </span>
              </div>
              <div className="runs">
                {loaded.history.map((job) => (
                  <button
                    key={job.id}
                    type="button"
                    className="run"
                    aria-pressed={loaded.job?.id === job.id}
                    disabled={busy}
                    onClick={() => actions.select(loaded.detail.case.id, job.id)}
                  >
                    <strong>
                      {short(job.run_id ?? job.id)} · version {short(job.transcript_version_id)}
                    </strong>
                    {job.status} · {job.model.id}
                    <br />
                    <span>{date(job.created_at)}</span>
                  </button>
                ))}
                {!loaded.history.length && (
                  <p className="help">No runs yet. An explicit classification will appear here.</p>
                )}
              </div>
              {loaded.history.length > 0 && loaded.history.length % 50 === 0 && (
                <button type="button" onClick={actions.moreHistory}>
                  Load earlier runs
                </button>
              )}
              <Provenance job={loaded.job} version={loaded.version} run={loaded.run} />
            </section>
          )}
          <footer>
            <p className="help">
              Local fictional-call review · Policy v1.0 · Human decisions never change frozen gold.
              Audio comes later.
            </p>
          </footer>
        </main>
      </div>
    </>
  );
}

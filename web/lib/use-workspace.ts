"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiError,
  api,
  type CaseDetail,
  type CaseSummary,
  type Filters,
  type Job,
  message,
  type Outcome,
  type Review,
  type Run,
  type Runtime,
  recallSubmission,
  recallText,
  remember,
  type Submission,
  type Version,
} from "./api";

export type View =
  | { kind: "empty" }
  | { kind: "loading"; id: string }
  | {
      kind: "loaded";
      detail: CaseDetail;
      version: Version;
      job: Job | null;
      run: Run | null;
      history: Job[];
      reviews: Review[];
    };
export type Draft =
  | { kind: "new"; text: string }
  | { kind: "edit"; text: string; caseId: string; parent: string };
const blankFilters: Filters = { outcome: "", review: "", status: "" };
const submissionNotice =
  "Classification submitted. You can inspect earlier runs while it processes.";
function finishedNotice(previous: string): string {
  return previous === submissionNotice
    ? "Classification finished. Inspect the result or choose an earlier run."
    : previous;
}

export function useWorkspace() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [filters, setFilters] = useState(blankFilters);
  const [view, setView] = useState<View>({ kind: "empty" });
  const [draft, setDraft] = useState<Draft | null>(null);
  const [runtime, setRuntime] = useState<Runtime | null>(null);
  const [examples, setExamples] = useState<Awaited<ReturnType<typeof api.examples>>>([]);
  const [model, setModel] = useState("");
  const [active, setActive] = useState<Job | null>(null);
  const [pending, setPending] = useState<Submission | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [connected, setConnected] = useState(false);
  const current = useRef({ id: "", jobId: "" });
  const requestVersion = useRef(0);
  const writeBusy = useRef(false);
  const activeId = useRef("");
  const follow = useRef("");
  const currentFilters = useRef(filters);
  currentFilters.current = filters;

  const refreshCases = useCallback(
    async (append = false) => {
      const selectedFilters = currentFilters.current;
      const items = await api.cases(selectedFilters, append ? cases.length : 0);
      if (selectedFilters !== currentFilters.current) return;
      setCases((old) =>
        append ? [...old, ...items.filter((item) => !old.some((c) => c.id === item.id))] : items,
      );
      return items;
    },
    [cases.length],
  );

  const load = useCallback(async (id: string, jobId?: string, loading = true) => {
    const serial = ++requestVersion.current;
    if (loading) setView({ kind: "loading", id });
    current.current = { id, jobId: jobId ?? "" };
    remember("case", id);
    remember("job", jobId ?? "");
    try {
      const detail = await api.detail(id);
      const job = jobId
        ? (detail.jobs.find((j) => j.id === jobId) ?? (await api.job(jobId)))
        : null;
      if (job && job.case_id !== id)
        throw new ApiError(404, "not_found", "Choose a run belonging to this case.");
      const reviews = job?.run_id ? await api.runReviews(job.run_id) : [];
      const [version, run] = await Promise.all([
        api.version(id, job?.transcript_version_id ?? detail.case.current_version_id),
        job?.run_id ? api.run(job.run_id) : Promise.resolve(null),
      ]);
      if (serial !== requestVersion.current) return;
      setView({
        kind: "loaded",
        detail,
        version,
        job,
        run,
        history: detail.jobs,
        reviews,
      });
      setConnected(true);
    } catch (e) {
      if (serial === requestVersion.current) {
        setError(message(e));
        setConnected(false);
      }
    }
  }, []);

  const reconnect = useCallback(async () => {
    api.reconnect();
    setError("");
    try {
      const [health, items, samples, jobs] = await Promise.all([
        api.runtime(),
        api.cases(currentFilters.current),
        api.examples(),
        api.jobs(),
      ]);
      setRuntime(health);
      setCases(items);
      setExamples(samples);
      setConnected(true);
      setModel((previous) => previous || recallText("model"));
      const running = jobs.find((j) => j.status === "running") ?? null;
      setActive(running);
      if (!running) setNotice(finishedNotice);
      activeId.current = running?.id ?? "";
      const saved = recallSubmission();
      setPending(saved);
      if (saved) {
        try {
          const accepted = await api.submission(saved.key);
          remember("submission", null);
          setPending(null);
          if (accepted.status === "running") {
            setActive(accepted);
            activeId.current = accepted.id;
          }
          await load(accepted.case_id, accepted.id);
        } catch (e) {
          if (!(e instanceof ApiError && e.status === 404)) throw e;
          setNotice(
            "Submission acceptance is unconfirmed. Inspect history, or explicitly retry the same submission.",
          );
        }
      } else {
        const id = current.current.id || recallText("case") || items[0]?.id;
        if (id) {
          const detail = await api.detail(id);
          const savedJob = current.current.jobId || recallText("job") || detail.jobs[0]?.id;
          await load(id, savedJob);
        }
      }
    } catch (e) {
      setError(message(e));
      setConnected(false);
    }
  }, [load]);

  useEffect(() => {
    const newDraft = recallText("new-draft");
    if (newDraft) setDraft({ kind: "new", text: newDraft });
    void reconnect();
  }, [reconnect]);
  useEffect(() => {
    if (draft?.kind) document.getElementById("transcript-input")?.focus();
  }, [draft?.kind]);
  useEffect(() => {
    let cancelled = false;
    void api
      .cases(filters)
      .then((items) => {
        if (!cancelled) setCases(items);
      })
      .catch((e) => {
        if (!cancelled) setError(message(e));
      });
    return () => {
      cancelled = true;
    };
  }, [filters]);
  useEffect(() => {
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    const tick = async () => {
      if (!document.hidden) {
        try {
          const [health, jobs] = await Promise.all([api.runtime(), api.jobs()]);
          if (stopped) return;
          setRuntime(health);
          setConnected(true);
          const running = jobs.find((j) => j.status === "running") ?? null;
          const finished = activeId.current
            ? (jobs.find((j) => j.id === activeId.current) ?? (await api.job(activeId.current)))
            : null;
          if (finished && finished.status !== "running") {
            setNotice(finishedNotice);
            const selectedId = current.current.id;
            if (selectedId === finished.case_id)
              await load(
                selectedId,
                follow.current === finished.id ? finished.id : current.current.jobId || undefined,
                false,
              );
            const items = await api.cases(currentFilters.current);
            if (!stopped) setCases(items);
            if (follow.current === finished.id) follow.current = "";
          }
          activeId.current = running?.id ?? "";
          setActive(running);
        } catch (e) {
          if (!stopped) {
            setError(message(e));
            setConnected(false);
          }
        }
      }
      if (!stopped) timer = setTimeout(tick, 1500);
    };
    timer = setTimeout(tick, 1500);
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  }, [load]);

  async function mutate(action: () => Promise<void>) {
    if (writeBusy.current) return;
    writeBusy.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
    } catch (e) {
      setError(message(e));
    } finally {
      writeBusy.current = false;
      setBusy(false);
    }
  }
  const actions = {
    reconnect,
    setFilters,
    model(value: string) {
      setModel(value);
      remember("model", value);
    },
    select(id: string, jobId?: string) {
      follow.current = "";
      setDraft(null);
      setError("");
      void load(id, jobId);
    },
    newDraft() {
      setDraft({ kind: "new", text: recallText("new-draft") });
      setNotice("");
    },
    edit() {
      if (view.kind === "loaded")
        void api
          .version(view.detail.case.id, view.detail.case.current_version_id)
          .then((version) => {
            if (current.current.id !== version.case_id) return;
            setDraft({
              kind: "edit",
              text: recallText(`draft:${version.case_id}`) || version.text,
              caseId: version.case_id,
              parent: version.id,
            });
          })
          .catch((e) => setError(message(e)));
    },
    text(text: string) {
      setDraft((old) => {
        if (!old) return null;
        remember(old.kind === "new" ? "new-draft" : `draft:${old.caseId}`, text);
        return { ...old, text };
      });
    },
    discard() {
      if (draft) remember(draft.kind === "new" ? "new-draft" : `draft:${draft.caseId}`, null);
      setDraft(null);
    },
    save() {
      void mutate(async () => {
        if (!draft) return;
        let id: string;
        if (draft.kind === "new") id = (await api.create(draft.text)).case.id;
        else {
          await api.save(draft.caseId, draft.parent, draft.text);
          id = draft.caseId;
        }
        remember(draft.kind === "new" ? "new-draft" : `draft:${draft.caseId}`, null);
        setDraft(null);
        await load(id);
        await refreshCases();
        setNotice(
          "Saved a transcript version. Earlier runs retain their original text. Classify explicitly to use this saved version.",
        );
        requestAnimationFrame(() => document.getElementById("transcript-heading")?.focus());
      });
    },
    loadExample(id: string) {
      void mutate(async () => {
        const created = await api.load(id);
        setDraft(null);
        await load(created.case.id);
        await refreshCases();
      });
    },
    submit() {
      void mutate(async () => {
        if (view.kind !== "loaded" || !model || draft || active) return;
        const submission = pending ?? {
          key: crypto.randomUUID(),
          payload: {
            case_id: view.detail.case.id,
            transcript_version_id: view.detail.case.current_version_id,
            model_config_id: model,
          },
        };
        remember("submission", submission);
        setPending(submission);
        let job: Job;
        try {
          job = await api.submit(submission);
        } catch (e) {
          if (e instanceof ApiError && (e.status === 400 || e.status === 422)) {
            remember("submission", null);
            setPending(null);
          }
          throw e;
        }
        remember("submission", null);
        setPending(null);
        setActive(job);
        activeId.current = job.id;
        follow.current = job.id;
        await refreshCases();
        setNotice(submissionNotice);
      });
    },
    checkSubmission() {
      void reconnect();
    },
    review(decision: Outcome, note: string) {
      void mutate(async () => {
        if (view.kind !== "loaded" || !view.job?.run_id || view.run?.status !== "success") return;
        const signature = JSON.stringify({
          run: view.job.run_id,
          decision,
          note,
        });
        const stored = recallText("review-signature") === signature ? recallText("review-key") : "";
        const key = stored || crypto.randomUUID();
        remember("review-signature", signature);
        remember("review-key", key);
        await api.review(view.job.run_id, decision, note, key);
        await load(view.detail.case.id, view.job.id, false);
        await refreshCases();
        setNotice(
          "Human decision saved separately. The model output and golden set are unchanged.",
        );
      });
    },
    moreCases() {
      void refreshCases(true).catch((e) => setError(message(e)));
    },
    moreHistory() {
      if (view.kind === "loaded")
        void api
          .history(view.detail.case.id, view.history.length)
          .then((items) =>
            setView((old) =>
              old.kind === "loaded" && old.detail.case.id === view.detail.case.id
                ? { ...old, history: [...old.history, ...items] }
                : old,
            ),
          )
          .catch((e) => setError(message(e)));
    },
    moreReviews() {
      if (view.kind === "loaded")
        void api
          .runReviews(view.job?.run_id ?? "", view.reviews.length)
          .then((items) =>
            setView((old) =>
              old.kind === "loaded" && old.detail.case.id === view.detail.case.id
                ? { ...old, reviews: [...old.reviews, ...items] }
                : old,
            ),
          )
          .catch((e) => setError(message(e)));
    },
  };
  return {
    cases,
    filters,
    view,
    draft,
    runtime,
    examples,
    model,
    active,
    pending,
    error,
    notice,
    busy,
    connected,
    actions,
  };
}

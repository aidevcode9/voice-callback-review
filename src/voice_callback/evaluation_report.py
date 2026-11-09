"""Self-contained human review projection of validated development artifacts."""

from html import escape
from typing import TYPE_CHECKING

from .domain import CallbackDecision, Failure, Outcome
from .evaluation_review import METRIC_LABELS, format_ratio

if TYPE_CHECKING:
    from .evaluation_review import Comparison, ReviewedCase, SavedEvaluation


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def _outcome(case: "ReviewedCase") -> str:
    result = case.prediction.result
    return result.label.value if isinstance(result, CallbackDecision) else "processing failure"


def _case_html(case: "ReviewedCase") -> str:
    result = case.prediction.result
    status = "Match" if case.correct else "Disagreement"
    tone = "good" if case.correct else "attention"
    if isinstance(result, Failure):
        status = "Processing failure"
    elif case.unsafe_miss:
        status = "Unsafe miss"
    if isinstance(result, CallbackDecision):
        evidence = "".join(f"<li><q>{_text(quote)}</q></li>" for quote in result.evidence)
        decision = (
            f"<p>{_text(result.reason)}</p>"
            f"<p class='muted'>Rules: {_text(', '.join(result.rule_ids))}</p>"
            f"<ul class='evidence'>{evidence}</ul>"
        )
    else:
        decision = (
            f"<p><strong>{_text(result.code.value)}</strong></p><p>{_text(result.message)}</p>"
        )
    case_id = _text(case.transcript.case_id)
    return (
        f"<details class='case' id='case-{case_id}'>"
        f"<summary><strong>{case_id}</strong><span>{_text(_outcome(case))}</span>"
        f"<span class='pill {tone}'>{status}</span></summary>"
        "<div class='case-body'><div class='case-grid'><section><h3>Approved reference</h3>"
        f"<p><strong>{_text(case.answer.label.value)}</strong></p>"
        f"<p>{_text(case.answer.rationale)}</p></section>"
        f"<section><h3>Model prediction</h3><p><strong>{_text(_outcome(case))}</strong></p>"
        f"{decision}</section></div><h3>Transcript used for this prediction</h3>"
        f"<pre>{_text(case.transcript.text)}</pre>"
        f"<p class='muted small'>Run {_text(case.prediction.run_id)}<br>"
        f"Transcript SHA-256: {_text(case.prediction.transcript_sha256)}</p></div></details>"
    )


def _comparison_html(current: "SavedEvaluation", comparison: "Comparison") -> str:
    metric_rows = "".join(
        "<tr>"
        f"<th>{_text(METRIC_LABELS[row.name])}</th>"
        f"<td>{_text(format_ratio(row.baseline))}</td>"
        f"<td>{_text(format_ratio(row.current))}</td>"
        f"<td>{'undefined' if row.percentage_points is None else f'{row.percentage_points:+.1f} pp'}</td>"
        "</tr>"
        for row in comparison.metrics
    )
    case_rows = "".join(
        f"<tr><th><a href='#case-{_text(change.case_id)}'>{_text(change.case_id)}</a></th>"
        f"<td>{_text(_outcome(change.baseline))}</td>"
        f"<td>{_text(_outcome(change.current))}</td><td>{_text(change.kind)}</td></tr>"
        for change in comparison.cases
    )
    if not case_rows:
        case_rows = (
            "<tr><td colspan='4'>No prediction, reason, evidence or failure changes.</td></tr>"
        )
    return (
        "<section class='panel' id='comparison'><div class='section-heading'><div>"
        "<h2>What changed?</h2></div>"
        f"<span class='pill'>{len(comparison.cases)} changed cases</span></div>"
        f"<p class='muted'>Baseline {_text(comparison.baseline_id)} → "
        f"{_text(current.report.evaluation_id)}</p>"
        f"<p><strong>{len(comparison.fixes)} fixes</strong> · "
        f"<strong>{len(comparison.regressions)} regressions</strong> · "
        f"{len(comparison.new_unsafe_misses)} new unsafe misses · "
        f"{len(comparison.removed_unsafe_misses)} removed unsafe misses</p>"
        f"<p class='muted'>Configuration fields changed: "
        f"{_text(', '.join(comparison.configuration_changes) or 'none')}.</p>"
        "<div class='table-scroll'><table><thead><tr><th>Metric</th><th>Baseline</th>"
        f"<th>Current</th><th>Change</th></tr></thead><tbody>{metric_rows}</tbody></table></div>"
        "<p class='small muted'>Changes are percentage points. Undefined values have no numeric delta. "
        "A higher needs-review rate alone does not establish improvement.</p>"
        "<h3>Changed cases</h3><div class='table-scroll'><table><thead><tr><th>Case</th>"
        f"<th>Baseline</th><th>Current</th><th>Result</th></tr></thead><tbody>{case_rows}</tbody>"
        "</table></div></section>"
    )


def render_review_html(
    current: "SavedEvaluation",
    baseline: "SavedEvaluation | None",
    comparison: "Comparison | None",
) -> str:
    report = current.report
    scored = report.score
    system = current.system
    metric_cards = "".join(
        f"<article class='metric'><h3>{_text(label)}</h3>"
        f"<p>{_text(format_ratio(getattr(scored.metrics, name)))}</p></article>"
        for name, label in METRIC_LABELS.items()
    )
    labels = list(Outcome)
    matrix_header = "".join(f"<th>{_text(label.value)}</th>" for label in labels)
    matrix_rows = "".join(
        f"<tr><th>{_text(label.value)}</th>"
        + "".join(f"<td>{scored.confusion_matrix[label][other]}</td>" for other in labels)
        + f"<td>{scored.processing_failures_by_expected[label]}</td></tr>"
        for label in labels
    )
    failures = scored.total - scored.valid_outputs
    unsafe = ", ".join(scored.unsafe_misses) or "None"
    disagreement_ids = [row.transcript.case_id for row in current.cases if not row.correct]
    disagreements = (
        "".join(
            f"<a class='case-link' href='#case-{_text(case_id)}'>{_text(case_id)}</a>"
            for case_id in disagreement_ids
        )
        or "<span class='muted'>No disagreements in this saved run.</span>"
    )
    cases_html = "".join(_case_html(case) for case in current.cases)
    comparison_html = (
        _comparison_html(current, comparison)
        if comparison is not None
        else (
            "<section class='panel' id='comparison'><h2>Baseline comparison</h2>"
            "<p class='muted'>No baseline selected. Select a saved development run using the same dataset "
            "and scoring definitions to inspect paired changes.</p></section>"
        )
    )
    provenance = (
        ("Dataset", f"{report.dataset_version} / {report.split}"),
        ("Model", system.model.model_id),
        ("Model digest", system.model_digest),
        ("Prompt", f"{system.prompt_version} / {system.prompt_sha256}"),
        ("Policy", f"{system.policy_version} / {system.policy_sha256}"),
        ("Code revision", system.code.git_revision or "unavailable"),
        ("Source fingerprint", system.code.source_sha256),
        ("Original clean checkout", str(system.code.working_tree_clean)),
        ("Runtime", f"{system.runtime_version} / {system.runtime_url}"),
        ("Scorer", report.score_version),
        ("Report SHA-256", current.report_sha256),
        ("Dataset manifest SHA-256", report.dataset_manifest_sha256),
    )
    provenance_rows = "".join(
        f"<div><dt>{_text(label)}</dt><dd>{_text(value)}</dd></div>" for label, value in provenance
    )
    baseline_note = (
        f"<p class='muted small'>Compared with saved report SHA-256 "
        f"{_text(baseline.report_sha256)}.</p>"
        if baseline is not None
        else ""
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Development evaluation · {_text(report.evaluation_id)}</title>
<style>
:root{{color-scheme:light dark;--bg:#f4f6f3;--panel:#fff;--ink:#203431;--muted:#52645f;--line:#cbd5cf;--accent:#245e4b;--attention:#833b17;--soft:#e1ebe4}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,sans-serif}}
a{{color:var(--accent)}}header,main,footer{{max-width:1220px;margin:auto;padding:30px 28px}}header{{padding-top:45px;padding-bottom:5px}}
h1{{font-size:clamp(27px,4vw,40px);line-height:1.15;margin:8px 0 18px}}h2{{font-size:24px;margin:0 0 12px}}h3{{font-size:15px;margin:8px 0}}
p{{margin:10px 0}}.metric,table{{font-variant-numeric:tabular-nums}}:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}::selection{{background:var(--accent);color:var(--panel)}}.table-scroll{{scrollbar-color:var(--line) var(--bg)}}nav a:hover{{text-decoration:underline;text-underline-offset:4px}}
.muted{{color:var(--muted)}}.small{{font-size:12px;overflow-wrap:anywhere}}nav{{display:flex;gap:20px;flex-wrap:wrap;margin:22px 0}}nav a{{text-decoration:none;font-weight:650}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:25px;margin-bottom:22px;overflow-wrap:anywhere}}
.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:20px 0}}.metric{{padding:18px;background:var(--panel);border:1px solid var(--line);border-radius:10px}}
.metric h3{{color:var(--muted);font-size:13px;font-weight:500}}.metric p{{font-size:20px;font-weight:700;margin:6px 0}}
.section-heading{{display:flex;justify-content:space-between;gap:15px;align-items:center;flex-wrap:wrap}}.pill{{font-size:12px;font-weight:650;border-radius:20px;padding:4px 10px;border:1px solid var(--line);white-space:nowrap}}
.good{{color:var(--accent);background:var(--soft)}}.attention{{color:var(--attention)}}.table-scroll{{overflow-x:auto}}table{{width:100%;min-width:600px;border-collapse:collapse;font-size:13px}}th,td{{text-align:left;padding:12px;border-bottom:1px solid var(--line);overflow-wrap:normal}}thead th{{color:var(--muted);font-weight:600}}
.case-link{{display:inline-block;margin:5px 10px 5px 0}}.case{{border:1px solid var(--line);border-radius:8px;margin:12px 0;overflow:hidden}}summary{{cursor:pointer;padding:16px;display:flex;gap:20px;align-items:center;flex-wrap:wrap}}summary strong{{margin-right:auto}}.case-body{{padding:0 20px 20px}}
.case-grid{{display:grid;grid-template-columns:1fr 1fr;gap:28px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.65 ui-monospace,monospace;background:var(--bg);padding:18px;border-radius:6px}}.evidence{{padding-left:20px}}dl{{margin:0}}dl div{{display:grid;grid-template-columns:190px minmax(0,1fr);gap:18px;padding:9px 0;border-bottom:1px solid var(--line)}}dt{{color:var(--muted)}}dd{{margin:0;font-size:13px;overflow-wrap:anywhere}}footer{{color:var(--muted);font-size:12px;padding-top:0}}
@media(prefers-color-scheme:dark){{:root{{--bg:#111b17;--panel:#1c2a23;--ink:#e5eee8;--muted:#abbbb1;--line:#3a4c40;--accent:#91cfab;--attention:#ffc195;--soft:#183c2a}}}}
@media(max-width:800px){{.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}.case-grid{{grid-template-columns:1fr}}header,main,footer{{padding-left:18px;padding-right:18px}}.panel{{padding:18px}}dl div{{grid-template-columns:1fr;gap:3px}}}}
@media(max-width:420px){{.metrics{{grid-template-columns:1fr}}}}
</style></head><body><header>
<h1>Development evaluation</h1><p class="muted small">Run {_text(report.evaluation_id)}</p>
<nav aria-label="Report sections"><a href="#results">Results</a><a href="#comparison">Comparison</a><a href="#cases">Cases</a><a href="#provenance">Provenance</a><a href="report.json">Saved JSON</a></nav>
</header><main><section id="results"><div class="section-heading"><h2>{scored.correct_outputs} of {scored.total} labels match</h2><span class="pill">One development trial</span></div>
<p class="muted">A completed run is evidence to inspect. Quality acceptance and deployment approval are not established here.</p><div class="metrics">{metric_cards}</div>
<section class="panel"><h2>Exceptions first</h2><p><strong>{len(scored.unsafe_misses)} unsafe misses</strong> · <strong>{failures} processing failures</strong> · {len(disagreement_ids)} total disagreements</p>
<p class="muted">Unsafe misses: {_text(unsafe)}. Processing failures remain in coverage and strict callback recall denominators.</p><div>{disagreements}</div></section>
<section class="panel"><h2>Confusion matrix</h2><p class="muted small">Rows: expected outcome. Columns: valid model prediction. Failures are shown separately.</p>
<div class="table-scroll"><table><thead><tr><th>Expected ↓ / predicted →</th>{matrix_header}<th>Failure</th></tr></thead><tbody>{matrix_rows}</tbody></table></div></section></section>
{comparison_html}{baseline_note}<section class="panel" id="cases"><h2>All cases</h2><p class="muted">Expand a case to inspect the approved answer, model evidence and exact transcript.</p>{cases_html}</section>
<section class="panel" id="provenance"><h2>Run provenance</h2><p class="muted">{_text(current.verification)}</p><dl>{provenance_rows}</dl></section>
</main><footer>Read-only projection of preserved local artifacts. Expected answers appear in this development report; they were not classifier inputs. No acceptance threshold is inferred.</footer></body></html>
"""

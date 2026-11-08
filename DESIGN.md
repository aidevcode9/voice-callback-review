---
name: Voice Callback Review
description: Approved A Review desk extended into the production frontend; B Casebook retained as historical comparison evidence.
colors:
  desk-ink: "#203431"
  desk-muted: "#52645f"
  desk-line: "#cbd5cf"
  desk-ground: "#f4f6f3"
  desk-accent: "#245e4b"
  desk-accent-hover: "#183f34"
  desk-tint: "#e1ebe4"
  desk-rail: "#e8eee7"
  casebook-ink: "#273248"
  casebook-muted: "#56617a"
  casebook-line: "#cbd1df"
  casebook-ground: "#eef0f6"
  casebook-accent: "#354d85"
  casebook-tint: "#e2e8f6"
  casebook-header: "#263651"
  casebook-rail: "#e2e7f1"
  paper: "#fff"
  focus: "#176b94"
  required-bg: "#f8e9df"
  required: "#833b17"
  clear-bg: "#e0eee8"
  clear: "#245842"
  review-bg: "#eae8f7"
  review: "#514578"
  evidence-bg: "#faedbd"
  evidence-ink: "#593b08"
  field-border: "#9facaa"
  transcript-meta: "#f6f8f5"
  notice-bg: "#edf1f4"
  error-bg: "#f9e9e5"
  error-ink: "#813723"
typography:
  title:
    fontFamily: "'Segoe UI', Arial, sans-serif"
    fontSize: "26px"
    fontWeight: 650
    lineHeight: 1.25
    letterSpacing: "-.025em"
  section:
    fontFamily: "'Segoe UI', Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 650
    lineHeight: 1.4
  body:
    fontFamily: "'Segoe UI', Arial, sans-serif"
    fontSize: "15px"
    lineHeight: 1.6
  transcript:
    fontFamily: "'Segoe UI', Arial, sans-serif"
    fontSize: "16px"
    lineHeight: 1.7
  label:
    fontFamily: "'Segoe UI', Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 600
  help:
    fontFamily: "'Segoe UI', Arial, sans-serif"
    fontSize: "13px"
    lineHeight: 1.55
rounded:
  evidence: "2px"
  badge: "4px"
  field: "5px"
  control: "6px"
  panel: "10px"
spacing:
  compact-gap: "9px"
  control-y: "9px"
  control-x: "13px"
  panel-y: "20px"
  panel-x: "22px"
  desk-column-gap: "30px"
  casebook-column-gap: "24px"
components:
  button-desk-primary:
    backgroundColor: "{colors.desk-accent}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "9px 13px"
  button-desk-primary-hover:
    backgroundColor: "{colors.desk-accent-hover}"
  button-casebook-primary:
    backgroundColor: "{colors.casebook-accent}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "9px 13px"
  button-casebook-primary-hover:
    backgroundColor: "{colors.casebook-header}"
  button-secondary:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "9px 13px"
  field:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.field}"
    padding: "9px"
    width: "100%"
  badge-required:
    backgroundColor: "{colors.required-bg}"
    textColor: "{colors.required}"
    rounded: "{rounded.badge}"
    padding: "5px 9px"
  transcript-panel:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.panel}"
---

# Design System: Voice Callback Review

## Overview

**Creative North Star: "A Review desk"**

A Review desk is the owner-selected visual world (SRC-021), extended into the production Next.js frontend under SRC-022. Its sage case rail, forest actions, white reading surface, system sans, and amber evidence marks remain the incumbent system. B Casebook remains historical prototype comparison evidence, not a second production theme. The frontmatter preserves the existing extracted token baseline; production differences are recorded below and in the surface record rather than silently redefining tokens.

The restrained hierarchy keeps readable transcript text and separate recommendation and human-review areas adjacent. Production uses the actual local API through Nginx; the original static prototypes remain simulations. Controlled browser-verification output is explicitly labeled and establishes interface behavior, not live-model quality.

**Key Characteristics:**
- Approved Review desk world extended into the production frontend; Casebook retained as historical comparison.
- Exact evidence tied to the selected run's original transcript version.
- Explicit submission, separate human judgment, and visible runtime state.

Sources: [product context](PRODUCT.md), [production direction contract](docs/REVIEW_DESK_SURFACE.md), [production surface record](.impeccable/surfaces/web-app-page-tsx.md), [production styles](web/app/globals.css), [page](web/app/page.tsx), and [components](web/app/components.tsx). Desktop and narrow production captures in [F-006 evidence](docs/evidence/F-006/browser-evidence.json) were inspected. Finish review passed after the stale processing notice was fixed; this is frontend implementation and controlled verification status, not deployment or live-model acceptance.

## Colors

### Primary

Review desk uses forest action color and a sage case rail. Casebook overrides the structural tokens with indigo actions, a dark blue header, and cool blue-gray ground. The frontmatter prefixes variant colors to prevent one alternative being mistaken for the shared default.

### Neutral

White transcript and control surfaces sit on each variant's pale ground, separated by fine borders. Muted text uses the corresponding variant token. Shared field borders, transcript metadata strips, and notice backgrounds are retained exactly as implemented.

Outcome pairs are shared: brown on peach for callback required, green on pale green for no callback, and purple on pale lavender for needs review. Amber marks identify exact supporting quotes; blue outlines identify keyboard focus. Runtime failures use a separate error notice, never an outcome badge.

## Typography

Every role uses the installed system stack from the frontmatter; no external font is loaded. Case titles, section headings, transcript text, compact labels, and help text form the hierarchy. Numeric text uses tabular figures. The historical prototype uses smaller muted speaker labels; production preserves the saved transcript as pre-wrapped text with inline speaker names.

The production reading surface uses (16px) transcript text with a (1.9) line height, while the retained transcript token and prototype use (1.7). This observed drift is recorded, not repaired in this documentation pass.

Case titles reduce to (24px) at the narrow breakpoint. Recommendation titles use (24px) in Review desk and (25px) in Casebook; these are local component sizes, not a separate display font.

## Layout

Review desk has a (235px) case rail and a workspace split between flexible transcript and a (330px) decision column, separated by the desk-column-gap token. At widths of at least (1650px), the decision column becomes (365px) with a (40px) gap. At widths up to (1120px), the rail becomes (210px), the transcript takes a full row, and recommendation/review share a two-column row.

Casebook uses horizontal case navigation and a centered content region capped at (1180px), including (30px) padding. A two-column decision band (1.1fr / 1fr, with a 34px gap) precedes a full-width transcript in both visual and DOM order. The reading field caps at (83ch); Review desk uses (74ch).

At widths up to (700px), both become sequential, case navigation scrolls horizontally, history buttons fill the available width, and review areas stack. Historical prototype speaker labels move above utterances; production retains inline saved text. The primary classification action has a minimum height of (44px). Production retains these breakpoints; the desktop and (390px) narrow captures verify the implemented responsive surface. Production makes the classification action full width, wraps long identifiers, and stacks the narrow navigation actions.

## Elevation & Depth

Both variants are flat: borders, background tones, spacing, and selected-state fills establish hierarchy. There are no elevation shadows. Evidence highlights use cloned decoration across line breaks. Controls change background over (.16s ease-out); the job indicator animates over (1.6s ease-in-out). The preserved sidecar describes the prototype segment (40% width, translation to 350%); production uses (35% width, translation to 400%). This motion drift is recorded without changing the shared token record. Reduced-motion preference disables animation and transition.

## Shapes

Panels use the panel radius; controls use the control radius; inputs and textareas use the field radius. Compact outcome badges and evidence marks use their smaller dedicated radii. Thin borders separate panels, metadata, review areas, and history without decorative framing.

## Components

- **Buttons:** variant-colored primary submission; white bordered secondary controls; tint hover; reduced opacity when disabled. Keyboard focus is a (3px) outline with a (3px) offset. Primary hover colors remain variant-specific.
- **Fields:** native selects, inputs, and resizable textareas retain explicit labels. Production model options come from runtime availability and disable unavailable classifiers; selecting an option never submits work. The historical prototype shows one Qwen3.5 4B Q4_K_M choice and disabled future Whisper. Production inputs/selects have a minimum height of (40px), compared with (39px) in the retained sidecar preview; narrow buttons use (44px).
- **Case navigation:** a vertical rail in Review desk and horizontal row in Casebook. A bordered white selected case and `aria-current` expose active selection. Empty filtered results explain how to restore the sample list.
- **Transcript and evidence:** each utterance pairs a speaker with readable text. Marks apply only to exact quotes in the viewed run's snapshot. Editing saves a new version and preserves prior results; controlled verification responses are explicitly labeled. Production displays exact repeated occurrences and merges overlapping evidence marks without replacing the saved text.
- **Recommendation and human review:** shared outcome colors accompany text labels. Human decisions remain separate records. Active-job and runtime notices appear separately from saved recommendations; failed runs state that no callback outcome was produced.
- **History and provenance:** pressed-state run buttons select preserved snapshots; production disclosures expose recorded version, request, model, and run provenance; the historical prototype uses explicitly illustrative provenance. Focus returns to surviving controls after rerender. Empty history, unsaved transcript, and no-run states have distinct labels.

## Do's and Don'ts

### Do

- Do implement the selected Review desk palette and layout; preserve Casebook as historical prototype evidence.
- Do keep controlled-verification status, selected transcript version, exact evidence, and human judgment visible and distinguishable.
- Do retain keyboard focus, reduced-motion handling, text outcome labels, and narrow sequential layouts.

### Don't

- Don't present historical Casebook or static simulated output as the production Review desk or live-model quality evidence.
- Don't turn runtime failures into policy outcomes or replace historical evidence with newer transcript text.
- Don't imply multiple installed classifiers, automatic downloads, fabricated hashes, or measured model performance.

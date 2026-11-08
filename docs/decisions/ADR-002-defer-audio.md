# ADR-002: Defer audio and voice-to-text

Date: 2026-11-07.
Status: accepted by the owner under SRC-024.

## Context

SRC-004 and SRC-016 included prerecorded audio and transcription. SRC-020 sequenced audio after the text workspace. The owner now wants to focus the current work on hardening the text review flow and presenting the implemented technology honestly to leadership.

## Decision

Move audio upload, voice-to-text, independent transcription model selection, and paired-audio evaluation to the [future roadmap](../ROADMAP.md). No date or implementation approach is committed. This supersedes the audio delivery scope and sequencing in SRC-004, SRC-016, SRC-020, and ADR-001 while preserving those records as history.

F-004 retains local text inference, development evaluation, candidate-freeze preparation, and its remaining quality decisions. F-004-AC08, F-004-AC10, and the transcription-selection portion of F-004-AC02 are deferred, not accepted. Text transcript inputs remain in scope. Existing transcription registry metadata remains unchanged and does not establish a working transcription feature.

## Consequences

The leadership demonstration can use the implemented text workspace and controlled evidence. The historical text-v1 baseline is not a current quality acceptance. Fresh text-v2 development evaluation, candidate freeze, numeric quality decisions, and separately authorized held-out evaluation remain open. Audio quality and hardware fit are not claimed.

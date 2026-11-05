"""Validate callback candidate data without changing it or promoting labels."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys


LABELS = {"callback_required", "no_callback", "needs_review"}
RULE_IDS = {"UR-001", "CB-002", "CB-003", "NC-001", "NC-002", "NC-003", "NR-001"}


def validate_record(record):
    if not isinstance(record, dict):
        return ["record must be an object"]
    errors = []
    for field in ("case_id", "family_id", "suggested_split", "source", "transcript",
                  "proposed_label", "rationale", "review_status"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f"{field} must be a nonempty string")
    for field in ("rule_ids", "evidence"):
        value = record.get(field)
        if not isinstance(value, list) or not value or any(
            not isinstance(item, str) or not item.strip() for item in value
        ):
            errors.append(f"{field} must be a nonempty list of nonempty strings")
    for field in ("reviewer", "reviewed_label"):
        if field not in record:
            errors.append(f"{field} is required")
    if errors:
        return errors
    if not re.fullmatch(r"VC-\d{3}", record["case_id"]):
        errors.append("case_id must use VC- followed by three digits")
    if not re.fullmatch(r"FAM-\d{3}", record["family_id"]):
        errors.append("family_id must use FAM- followed by three digits")
    if record["source"] != "synthetic":
        errors.append("source must be synthetic for this candidate set")
    if record["suggested_split"] not in {"development", "evaluation"}:
        errors.append("suggested_split must be development or evaluation")
    if record["proposed_label"] not in LABELS:
        errors.append("proposed_label is invalid")
    if any(rule not in RULE_IDS for rule in record["rule_ids"]):
        errors.append("rule_ids contains an unknown v1.0 policy rule")
    if any(quote not in record["transcript"] for quote in record["evidence"]):
        errors.append("evidence quote is not present in the transcript")
    status = record["review_status"]
    if status not in {"pending", "approved", "rejected"}:
        errors.append("review_status is invalid")
    if status == "pending" and (record["reviewer"] is not None or record["reviewed_label"] is not None):
        errors.append("pending records must have null reviewer and reviewed_label")
    if status in {"approved", "rejected"} and (
        not isinstance(record["reviewer"], str) or not record["reviewer"].strip()
    ):
        errors.append("reviewer is required for approved or rejected records")
    if status == "approved" and (
        not isinstance(record["reviewed_label"], str) or record["reviewed_label"] not in LABELS
    ):
        errors.append("approved records require a valid reviewed_label")
    if status == "rejected" and record["reviewed_label"] is not None:
        errors.append("rejected records must have null reviewed_label")
    return errors


def load_candidates(path):
    records, errors = [], []
    ids, transcripts, families = set(), set(), {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"line {line_number}: invalid JSON")
            continue
        issues = validate_record(record)
        if issues:
            errors.extend(f"line {line_number}: {issue}" for issue in issues)
            continue
        if record["case_id"] in ids:
            errors.append(f"line {line_number}: duplicate case_id")
        normalized = " ".join(record["transcript"].casefold().split())
        if normalized in transcripts:
            errors.append(f"line {line_number}: duplicate transcript")
        previous_split = families.setdefault(record["family_id"], record["suggested_split"])
        if previous_split != record["suggested_split"]:
            errors.append(f"line {line_number}: family occurs in more than one split")
        ids.add(record["case_id"])
        transcripts.add(normalized)
        records.append(record)
    if not records and not errors:
        errors.append("dataset contains no cases")
    return records, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=(
        Path(__file__).resolve().parents[1] / "data/candidates/v0.1/cases.jsonl"
    ))
    args = parser.parse_args()
    try:
        records, errors = load_candidates(args.path)
    except (OSError, UnicodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    summary = {
        "cases": len(records),
        "families": len({row["family_id"] for row in records}),
        "labels": dict(Counter(row["proposed_label"] for row in records)),
        "splits": dict(Counter(row["suggested_split"] for row in records)),
        "review_statuses": dict(Counter(row["review_status"] for row in records)),
        "labels_by_split": {
            split: dict(Counter(row["proposed_label"] for row in records if row["suggested_split"] == split))
            for split in sorted({row["suggested_split"] for row in records})
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

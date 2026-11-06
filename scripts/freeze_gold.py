"""Freeze explicitly approved candidate labels or verify an existing gold release."""

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys

from check_candidates import load_candidates


ROOT = Path(__file__).resolve().parents[1]


def digest(content):
    return hashlib.sha256(content).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def json_lines(rows):
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode("utf-8")


def load_approval(path, source_bytes, records, policy_bytes):
    review = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(review, dict):
        raise ValueError("Approval must be an object")
    for field in ("review_id", "reviewer", "reviewer_kind", "reviewed_on",
                  "approval_source", "decision", "source_sha256", "policy_version",
                  "policy_sha256", "policy_approval_source"):
        if not isinstance(review.get(field), str) or not review[field].strip():
            raise ValueError(f"Approval requires {field}")
    if review["reviewer_kind"] != "human" or review["decision"] != "approved_as_is":
        raise ValueError("Explicit human approval as-is is required")
    if review["policy_version"] != "1.0":
        raise ValueError("Approved policy version 1.0 is required by this exporter")
    if review["policy_sha256"] != digest(policy_bytes):
        raise ValueError("Approval does not match the policy hash")
    date.fromisoformat(review["reviewed_on"])
    ids = review.get("approved_case_ids")
    if not isinstance(ids, list) or not ids or any(not isinstance(item, str) for item in ids):
        raise ValueError("Approval requires a nonempty case ID list")
    if len(set(ids)) != len(ids) or set(ids) != {row["case_id"] for row in records}:
        raise ValueError("Approval must cover every source case exactly once")
    if review["source_sha256"] != digest(source_bytes):
        raise ValueError("Approval does not match the current candidate source hash")
    if review.get("corrections") != []:
        raise ValueError("This exporter requires unchanged labels; record corrections in a new reviewed source")
    return review


def build_release(source, review_path, policy, version):
    records, errors = load_candidates(source)
    if errors:
        raise ValueError("; ".join(errors))
    if any(row["review_status"] != "pending" for row in records):
        raise ValueError("Use the original pending-candidate snapshot with a separate approval ledger")
    source_bytes = source.read_bytes()
    policy_bytes = policy.read_bytes()
    review = load_approval(review_path, source_bytes, records, policy_bytes)
    records = sorted(records, key=lambda row: row["case_id"])
    gold = [{
        "case_id": row["case_id"], "family_id": row["family_id"],
        "split": row["suggested_split"], "source": row["source"],
        "transcript": row["transcript"], "expected_label": row["proposed_label"],
        "rule_ids": row["rule_ids"], "rationale": row["rationale"], "evidence": row["evidence"],
        "review_status": "approved", "reviewer": review["reviewer"],
        "reviewed_on": review["reviewed_on"], "approval_source": review["approval_source"],
    } for row in records]
    files = {
        "cases.jsonl": json_lines(gold),
        "source-candidates.jsonl": source_bytes,
        "approval.json": review_path.read_bytes(),
        f"policy-v{review['policy_version']}.txt": policy_bytes,
    }
    splits = {}
    for split in ("development", "evaluation"):
        selected = [row for row in gold if row["split"] == split]
        splits[split] = [row["case_id"] for row in selected]
        files[f"inputs/{split}.jsonl"] = json_lines([
            {"case_id": row["case_id"], "transcript": row["transcript"]} for row in selected
        ])
        files[f"answers/{split}.jsonl"] = json_lines([
            {key: row[key] for key in ("case_id", "expected_label", "rule_ids", "rationale", "evidence")}
            for row in selected
        ])
    files["README.md"] = (
        f"# Golden set v{version}\n\n"
        f"Status: frozen. {len(gold)} fictional cases, approved by {review['reviewer']} "
        f"on {review['reviewed_on']}, under {review['approval_source']}.\n\n"
        "Use [manifest.json](manifest.json) for versions, case IDs, frozen splits, and hashes. "
        "The [approval record](approval.json) preserves the explicit human acceptance.\n\n"
        "Only inputs/development.jsonl and inputs/evaluation.jsonl are classifier inputs. "
        "Each record contains exactly case_id and transcript. Expected labels and review metadata "
        "are in separate answer and audit artifacts. Never send the whole release folder to the classifier.\n\n"
        "Use development cases for prompt development. Keep evaluation cases out of prompt demonstrations. "
        "The source candidate snapshot remains unchanged and pending as historical provenance; "
        "the separate approval record and approved gold records establish subsequent acceptance.\n\n"
        "This small synthetic set does not establish operational accuracy. No model evaluation has run. "
        "Create a new release version for corrections; preserve this release.\n"
    ).encode("utf-8")
    manifest = {
        "dataset_version": version, "policy_version": review["policy_version"], "status": "frozen",
        "policy_sha256": review["policy_sha256"], "policy_approval_source": review["policy_approval_source"],
        "frozen_on": review["reviewed_on"], "reviewer": review["reviewer"],
        "approval_source": review["approval_source"], "review_id": review["review_id"],
        "candidate_source_sha256": digest(source_bytes), "case_ids": [row["case_id"] for row in gold],
        "case_count": len(gold), "family_count": len({row["family_id"] for row in gold}),
        "label_counts": dict(Counter(row["expected_label"] for row in gold)),
        "splits": splits, "classifier_input_fields": ["case_id", "transcript"],
        "split_rule": "Frozen prepared assignments; each scenario family stays in one split",
        "provenance": "Agent-authored fictional English transcripts; owner-approved labels as-is",
        "files": {name: {"sha256": digest(content), "bytes": len(content)}
                  for name, content in sorted(files.items())},
    }
    files["manifest.json"] = json_bytes(manifest)
    return files, manifest


def write_or_check(output, files, check):
    if output.exists() and not output.is_dir():
        raise ValueError("Release output must be a directory")
    existing = {path.relative_to(output).as_posix()
                for path in output.rglob("*") if path.is_file()} if output.exists() else set()
    if existing - set(files):
        raise ValueError("Release contains unexpected files; preserve it and use a new version")
    for name, content in files.items():
        path = output / name
        if path.exists() and (not path.is_file() or path.read_bytes() != content):
            raise ValueError(f"Frozen content differs: {name}; existing release was not overwritten")
        if check and not path.is_file():
            raise ValueError(f"Missing release artifact: {name}")
    if check:
        return
    for name, content in files.items():
        path = output / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "data/candidates/v0.1/cases.jsonl")
    parser.add_argument("--review", type=Path, default=ROOT / "data/reviews/v1.0.json")
    parser.add_argument("--policy", type=Path, default=ROOT / "docs/CALLBACK_POLICY.md")
    parser.add_argument("--version", default="1.0")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if not re.fullmatch(r"\d+\.\d+", args.version):
            raise ValueError("Version must contain two numeric parts")
        output = args.output or ROOT / "data/gold" / f"v{args.version}"
        files, manifest = build_release(args.source, args.review, args.policy, args.version)
        write_or_check(output, files, args.check)
        print(json.dumps({"mode": "verified" if args.check else "frozen",
                          "version": args.version, "cases": manifest["case_count"]}))
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

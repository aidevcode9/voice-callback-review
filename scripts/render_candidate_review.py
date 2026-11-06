"""Render a human review packet from validated candidate data."""

import argparse
from pathlib import Path
import sys

from check_candidates import load_candidates


def render(records):
    parts = [
        "# Candidate review packet",
        "",
        "Generated candidate snapshot from cases.jsonl. Consult the version README for subsequent approval and gold-release records; snapshot review fields retain their original state.",
        "",
    ]
    for row in records:
        parts.extend([
            f"## {row['case_id']}",
            "",
            f"Family: {row['family_id']}. Suggested split: {row['suggested_split']}.",
            f"Proposed label: {row['proposed_label']}. Rules: {', '.join(row['rule_ids'])}.",
            f"Review status: {row['review_status']}. Human label: {row['reviewed_label'] or 'not reviewed'}.",
            f"Reviewer: {row['reviewer'] or 'not recorded'}.",
            "",
            *["> " + line for line in row["transcript"].splitlines()],
            "",
            "Proposed rationale: " + row["rationale"],
            "",
            "Evidence: " + " | ".join(row["evidence"]),
            "",
        ])
    return "\n".join(parts).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output or args.path.parent / "REVIEW.md"
    try:
        if output.resolve() == args.path.resolve():
            raise ValueError("Review output must differ from the candidate input")
        records, errors = load_candidates(args.path)
        if errors:
            raise ValueError("; ".join(errors))
        text = render(records)
        if args.check:
            if not output.is_file() or output.read_text(encoding="utf-8") != text:
                raise ValueError("Review packet differs from the candidate data; regenerate it")
            print("Review packet matches the candidate data.")
        else:
            output.write_text(text, encoding="utf-8", newline="\n")
            print(f"Wrote {output}")
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

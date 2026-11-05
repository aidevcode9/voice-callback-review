"""Copy the bundled repository skeleton without replacing existing files."""

import argparse
import os
from pathlib import Path
import stat
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKELETON = SKILL_ROOT / "assets" / "repository"


def is_link(path):
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def source_files(root):
    for path in sorted(root.rglob("*")):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if is_link(path):
            raise ValueError(f"Source contains a link or junction: {path}")
        if path.is_file():
            yield path


def project_files(destination, name):
    for required in (
        SKELETON / "README.md",
        SKILL_ROOT / "SKILL.md",
        SKELETON / ".agents/skills/project-workflow/SKILL.md",
    ):
        if not required.is_file():
            raise ValueError(f"Required template resource is missing: {required}")
    files = {}
    for source in source_files(SKELETON):
        content = source.read_bytes().replace(b"{{PROJECT_NAME}}", name.encode("utf-8"))
        files[destination / source.relative_to(SKELETON)] = content
    for source in source_files(SKILL_ROOT):
        target = destination / ".agents" / "skills" / "project-intake" / source.relative_to(SKILL_ROOT)
        files[target] = source.read_bytes()
    return files


def check_destination(destination, files):
    if destination == SKILL_ROOT or SKILL_ROOT in destination.parents or destination in SKILL_ROOT.parents:
        raise ValueError("Destination must not overlap the source skill.")
    for path in (destination, *destination.parents):
        if is_link(path):
            raise ValueError(f"Destination contains a link or junction: {path}")
        if path.exists() and not path.is_dir():
            raise ValueError(f"Destination ancestor is not a directory: {path}")

    conflicts = []
    for target, content in files.items():
        for path in (target, *target.parents):
            if path == destination:
                break
            if is_link(path):
                raise ValueError(f"Destination contains a link or junction: {path}")
            if path != target and path.exists() and not path.is_dir():
                conflicts.append(str(path))
                break
        else:
            raise ValueError(f"Target escaped the destination: {target}")
        if target.exists() and (not target.is_file() or target.read_bytes() != content):
            conflicts.append(str(target))
    if conflicts:
        raise ValueError("Existing content conflicts; no files written:\n" + "\n".join(sorted(set(conflicts))))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if not args.name.strip() or any(ord(character) < 32 for character in args.name):
        parser.error("Project name must be nonempty and contain no control characters.")

    destination = Path(os.path.abspath(args.destination))
    try:
        files = project_files(destination, args.name.strip())
        check_destination(destination, files)
        created = 0
        skipped = 0
        for target, content in files.items():
            if target.exists():
                skipped += 1
                continue
            if not args.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as output:
                    output.write(content)
            created += 1
            print(f"{'WOULD CREATE' if args.dry_run else 'CREATED'} {target.relative_to(destination)}")
        print(f"{'Preview' if args.dry_run else 'Result'}: {created} new files, {skipped} identical files preserved.")
        return 0
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

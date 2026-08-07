from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "release-docs"
TARGET = ROOT / "docs"


def generate(check: bool) -> int:
    if not SOURCE.is_dir():
        raise SystemExit("release-docs source directory is missing")

    expected = sorted(path for path in SOURCE.glob("*.md") if path.is_file())
    if not expected:
        raise SystemExit("release-docs contains no markdown files")

    if check:
        missing = [path.name for path in expected if not (TARGET / path.name).is_file()]
        changed = [
            path.name
            for path in expected
            if (TARGET / path.name).is_file()
            and not filecmp.cmp(path, TARGET / path.name, shallow=False)
        ]
        extra = sorted(
            path.name
            for path in TARGET.glob("*.md")
            if path.is_file() and not (SOURCE / path.name).is_file()
        ) if TARGET.exists() else []
        if missing or changed or extra:
            print(
                {
                    "changed": changed,
                    "extra": extra,
                    "missing": missing,
                    "status": "stale",
                }
            )
            return 1
        print({"count": len(expected), "status": "fresh"})
        return 0

    TARGET.mkdir(parents=True, exist_ok=True)
    for current in TARGET.glob("*.md"):
        current.unlink()
    for path in expected:
        shutil.copyfile(path, TARGET / path.name)
    print({"count": len(expected), "status": "generated"})
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return generate(args.check)


if __name__ == "__main__":
    raise SystemExit(main())

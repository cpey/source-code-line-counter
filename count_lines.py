#!/usr/bin/env python3
"""
Count non-blank, non-comment lines in *.c, *.h, and *.cpp files.

- If a directory is given: recursively scan all *.c, *.h, and *.cpp files.
- If a single file is given: count only that file (must be .c, .h, or .cpp).
- Exclude paths containing any of the --exclude strings.
- Optionally specify a depth to show hierarchical counts.
"""

import argparse
from pathlib import Path
from typing import Iterator, List

DEFAULT_EXTS = {".c", ".h", ".cpp"}

def iter_source_files(root: Path, excludes: List[str], exts: set[str]) -> Iterator[tuple[Path, list[str]]]:
    """Yield *.c or *.h files from a directory, skipping excluded paths."""
    if root.is_file():
        if root.suffix in exts and not any(exc in root.parts for exc in excludes):
            rel_parts = list(root.relative_to(root.parent).parts)
            yield root, rel_parts
        return

    if root.is_dir():
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in exts:
                if not any(exc in path.parts for exc in excludes):
                    rel_parts = list(path.relative_to(root).parts)
                    yield path, rel_parts

def look_for_code_in_line(line: str) -> bool:
    idx = 0
    in_comment = True
    while idx < len(line):
        if in_comment:
            # inside the block comment: look for the closing
            close_pos = line.find("*/", idx) 
            if close_pos == -1: # never closes
                return (False, in_comment)
            idx = close_pos + 2
            in_comment = False
            continue

        # outside comment: look for the next block comment or real code
        open_pos = line.find("/*", idx) 
        if open_pos >= 0:
            if line[idx:open_pos].strip():
                return (True, in_comment)
            else:
                idx = open_pos + 2
                in_comment = True
                continue

        after = line[idx:].strip()
        if after and after not in ["\\", "//"]:
            return (True, in_comment)

        idx += 1
    return (False, in_comment)

def count_real_lines(file_path: Path) -> int:
    """Count lines that contain actual code (not blank, not pure comments)."""
    in_block_comment = False
    real = 0

    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                line = raw.rstrip("\n")
                if not line.strip():
                    continue

                stripped = line.lstrip()
                if stripped.startswith("//"):
                    continue

                # Start of block comment
                if stripped.startswith("/*"):
                    found, in_block_comment = look_for_code_in_line(stripped)
                    if found:
                        real += 1
                    continue

                # Inside block comment
                if in_block_comment:
                    found, in_block_comment = look_for_code_in_line(stripped)
                    if found:
                        real += 1
                    continue

                # Regular code line
                real += 1
    except Exception:
        pass

    return real

def main(path: str, excludes: List[str], exts: set[str], depth: int) -> None:
    root = Path(path).expanduser().resolve()
    total = 0

    counts: Dict[tuple[str, ...], int] = {}

    for src_file, rel_parts in iter_source_files(root, excludes, exts):
        file_count = count_real_lines(src_file)
        total += file_count

        # Build hierarchy up to depth
        key: tuple[str, ...] = tuple()
        for i in range(min(depth, len(rel_parts) - 1)):
            key = tuple(rel_parts[: i + 1])
            counts[key] = counts.get(key, 0) + file_count

    # Sort by path for consistent output
    for key in sorted(counts.keys(), key=lambda x: " ".join(x)):
        indent = "  " * (len(key) - 1)
        print(f"{indent}{key[-1]}/: {counts[key]}")
    print(f"TOTAL: {total}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Count non-comment source lines in *.c/*.h/*.cpp files."
    )
    parser.add_argument(
        "path",
        help="Path to a directory (scan recursively) or a single .c/.h/.cpp file",
    )
    parser.add_argument(
        "-e", "--exclude",
        action="append",
        help="Path component to exclude (repeatable)",
    )
    parser.add_argument(
        "--ext",
        action="append",
        choices=[".c", ".h", ".cpp"],
        help="File extension to count (default: .c, .h, and .cpp; repeat to specify multiple extensions)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=0,
        help="Show counts per subdirectory up to this depth (0 = total only)",
    )
    args = parser.parse_args()
    if not args.ext:
        exts = set(DEFAULT_EXTS)
    else:
        exts = set(args.ext)

    if not args.ext:
        excs = []
    else:
        excs = args.exclude
    main(args.path, excs, exts, args.depth)

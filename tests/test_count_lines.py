#!/usr/bin/env python3
"""
Unit tests for count_lines.py
Run with: python3 -m unittest discover -s tests
"""

import unittest
from pathlib import Path
import tempfile
import sys

# Add project root to path so we can import count_lines
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from count_lines import iter_source_files, count_real_lines, DEFAULT_EXTS


class TestLineCounter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # main.c
        (self.root / "main.c").write_text("""
            #include <stdio.h>
            
            int main() {
                printf("Hello");  /* inline comment */
                /* inline comment */ printf("Hello");
                return 0; // trailing comment
            }
            /* Line comment */
            /* block comment 

            */
            /* block comment 

            */ printf("Hello");
            /* block comment 

            */ /* block comment 

            */
            // full line comment
               \t  
        """)

        # utils.h
        (self.root / "utils.h").write_text("""
            #ifndef UTILS_H
            #define UTILS_H
            
            void helper(); /* declaration */
            
            #endif
        """)

        # excluded file
        gen_dir = self.root / "auto_gen"
        gen_dir.mkdir(parents=True, exist_ok=True)
        (gen_dir / "generated.c").write_text("int x = 1;")

        # empty file
        (self.root / "empty.c").write_text("\n\n   \n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_basic_count(self):
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root, [], DEFAULT_EXTS))
        self.assertEqual(total, 12)  # 7 from main.c + 4 from utils.h + 1 from generated.c

    def test_exclude_auto_gen(self):
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root, ["auto_gen"], DEFAULT_EXTS))
        self.assertEqual(total, 11)  # 7 from main.c + 4 from utils.h

    def test_single_file(self):
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root / "main.c", [], DEFAULT_EXTS))
        self.assertEqual(total, 7)

    def test_empty_file(self):
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root / "empty.c", [], DEFAULT_EXTS))
        self.assertEqual(total, 0)

    def test_inline_and_block_comments(self):
        self.assertEqual(count_real_lines(self.root / "main.c"), 7)
        self.assertEqual(count_real_lines(self.root / "utils.h"), 4)

    def test_extensions(self):
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root, [], DEFAULT_EXTS))
        self.assertEqual(total, 12)  # 7 from main.c + 4 from utils.h + 1 from generated.c
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root, [], {".c"}))
        self.assertEqual(total, 8)  # 7 from main.c + 4 from utils.h + 1 from generated.c
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root, [], {".h"}))
        self.assertEqual(total, 4)  # 4 from utils.h
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root / "main.c", [], DEFAULT_EXTS))
        self.assertEqual(total, 7)
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root / "main.c", [], {".c"}))
        self.assertEqual(total, 7)
        total = sum(count_real_lines(p) for p, _ in iter_source_files(self.root / "main.c", [], {".h"}))
        self.assertEqual(total, 0)

    def test_depth_argument(self):
            """
            Verify that --depth splits counts correctly:
            - depth=0: total only
            - depth=1: one level of subdirectories
            """
            from count_lines import main
            import io
            from contextlib import redirect_stdout

            def run_with_depth(depth: int):
                output = io.StringIO()
                with redirect_stdout(output):
                    main(
                        path=str(self.root),
                        excludes=[],
                        exts=DEFAULT_EXTS,
                        depth=depth,
                    )
                return output.getvalue().strip().splitlines()

            # depth=0: total only
            lines = run_with_depth(0)
            self.assertEqual(len(lines), 1)
            total = lines[0].split(":")[1].strip()
            self.assertTrue(total.isdigit())
            self.assertEqual(int(total), 12) # 7 from main.c + 4 from utils.h + 1 from generated.c

            # depth=1: subdirectories
            lines = run_with_depth(1)
            expected_dirs = {"auto_gen"}
            dir_lines = [l for l in lines if "/:" in l]
            self.assertEqual(len(dir_lines), len(expected_dirs))
            self.assertTrue(any("TOTAL:" in l for l in lines))

if __name__ == "__main__":
    unittest.main()

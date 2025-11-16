#!/usr/bin/env python3
import unittest
from pathlib import Path
import sys

# Add project root to path so we can import count_lines
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from count_lines import look_for_code_in_line

class TestLookForCodeInLine(unittest.TestCase):

    def _run(self, line: str) -> bool:
        result, _ = look_for_code_in_line(line)
        return result

    def test_printed_cases(self):
        # (line,   (has_code,  coment_left_open))
        cases = [
            ("*/ test",                    (True,  False)),
            ("*/ ",                        (False, False)),
            ("*/ test /* */",              (True,  False)),
            ("*/ /* */",                   (False, False)),
            ("*/ test /* */ /* */",        (True,  False)),
            ("*//* test *//* */ /* */",    (False, False)),
            ("test",                       (False, True)),
            ("test */ /* ",                (False, True)),
            ("test */ \\",                 (False, False)),
        ]
        for line, expected in cases:
            self.assertEqual(look_for_code_in_line(line), expected)

if __name__ == "__main__":
    unittest.main()

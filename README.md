# Source Code Line Counter

Counts non-comment, non-blank lines in `.c`, `.cpp`, and `.h` source files.

## Usage

```python
$ python3 count_lines.py -h
usage: count_lines.py [-h] [-e EXCLUDE] [--ext {.c,.h,.cpp}] [--depth DEPTH] path

Count non-comment source lines in *.c/*.h/*.cpp files.

positional arguments:
  path                  Path to a directory (scan recursively) or a single .c/.h/.cpp file

options:
  -h, --help            show this help message and exit
  -e, --exclude EXCLUDE
                        Path component to exclude (repeatable)
  --ext {.c,.h,.cpp}    File extension to count (default: .c, .h, and .cpp; repeat to specify multiple
                        extensions)
  --depth DEPTH         Show counts per subdirectory up to this depth (0 = total only)
```

## Output Format

```sh
$ python3 count_lines.py --depth 3 --exclude auto_gen_1_5  .
include/: 1182
src/: 38517
  common/: 18090
    accessors/: 880
    crypto/: 397
    data_structures/: 1634
    debug/: 736
    exception_handling/: 197
    helpers/: 5543
    memory_handlers/: 1921
    metadata_handlers/: 4066
    x86_defs/: 2716
  td_dispatcher/: 4147
    vm_exits/: 2771
    vm_exits_l2/: 283
  td_transitions/: 1676
  vmm_dispatcher/: 14604
    api_calls/: 7981
    migration_api_calls/: 5990
TOTAL: 39699
```

## Examples

Default: count *.c and *.h:

```sh
$ python3 count_lines.py .
```

Only C files:

```sh
$ python3 count_lines.py . --ext .c
```

Only header files:

```sh
$ python3 count_lines.py . --ext .h
```

Single file (extension is validated):

```sh
$ python3 count_lines.py src/main.c
$ python3 count_lines.py src/utils.h --ext .c # skipped (not .c)
```

Total only (default):

```sh
$ python3 count_lines.py .
```

One level of subdirs:

```sh
$ python3 count_lines.py . --depth 1
```

## Running the Tests

```sh
$ make test
python3 -m unittest discover -s tests -v
test_basic_count (test_count_lines.TestLineCounter.test_basic_count) ... ok
test_depth_argument (test_count_lines.TestLineCounter.test_depth_argument)
Verify that --depth splits counts correctly: ... ok
test_empty_file (test_count_lines.TestLineCounter.test_empty_file) ... ok
test_exclude_auto_gen (test_count_lines.TestLineCounter.test_exclude_auto_gen) ... ok
test_extensions (test_count_lines.TestLineCounter.test_extensions) ... ok
test_inline_and_block_comments (test_count_lines.TestLineCounter.test_inline_and_block_comments) ... ok
test_single_file (test_count_lines.TestLineCounter.test_single_file) ... ok
test_printed_cases (test_look_for_code_in_line.TestLookForCodeInLine.test_printed_cases) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.013s

OK
```

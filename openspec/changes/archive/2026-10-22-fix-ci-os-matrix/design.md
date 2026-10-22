# Design

## Context

- `.github/workflows/python-pdm.yml` has one job, `lint`, with a matrix of 6 Python versions × 3 operating systems.
  It runs format, lint and tests. `continue-on-error: true` is still set: the run for commit `752ee05` had 6 failing
  Windows jobs and still concluded `success`.
- On Windows, Python translates `\n` to `\r\n` when writing to text-mode stdout and files. Joining lines with
  `os.linesep` (`\r\n`) therefore produced `\r\r\n`. `json.dump()` writes `\n`, so JSON and jCal output already had
  single platform line endings.
- pytest's `capsys` does not translate newlines, so the stdout tests never saw `\r\r\n`. Only the file output tests
  failed, after the `shlex` quoting fix let them reach the file.
- `os.EX_OK` exists on Windows only from Python 3.11. On 3.10, `return os.EX_OK` raised `AttributeError` after the
  result was written. The catch-all handler in `cli()` printed its error message after the result and returned 1, so
  the JSON tests on stdout failed with "Extra data".
- With `d1f194c`, the Windows jobs pass.

## Goals / Non-Goals

**Goals:**

- Run every matrix entry on its operating system and fail the run when any entry fails.
- Single platform line endings in all output.

**Non-Goals:**

- Renaming the job or splitting lint and tests. Check names such as `lint (3.12, windows-latest)` may be required
  status checks.
- Other Windows issues (stdout encoding) have their own change, `fix-windows-stdout-encoding`.
- Dropping Python 3.10. See the decision on `os.EX_OK` below.

## Decisions

- **Write `\n` and let the stream translate it.** The Python documentation advises against `os.linesep` for text-mode
  writes. Writing `\n` gives CR LF on Windows and LF elsewhere, as JSON output already does.
  - *Alternative:* open files and reconfigure stdout with `newline=""` and keep `os.linesep`. Rejected, because it
    changes every write path, and `print()` adds its own `\n`.
- **Own exit code constants instead of dropping Python 3.10.** With Python 3.11 as minimum, `os.EX_OK` would work on
  every platform, and Python 3.10 reaches end of life in October 2026. Rejected for this change: dropping a Python
  version needs its own change (`requires-python`, CI matrix, CHANGELOG), not a patch-level fix.
- **Collect the constants in `constants.py`, grouped in namespace classes.** `Os` holds `EX_OK`, `EX_ERROR` and
  `linesep`, named like their `os` counterparts, so `Os.linesep` reads like `os.linesep` and stays visibly distinct.
  `StringEncoding` holds `UTF_8` and `BYTE_ORDER_MARK`. Each class documents its constants in a Google-style
  `Attributes:` section, including why the `os` values are not used, which keeps them from creeping back in. Tests
  keep their `"utf-8"` literals, so they check the output encoding independently of the constant.
  - *Alternative:* module-level constants `EX_OK`, `EX_ERROR` and `LINESEP` in `os_constants.py` (the first
    version). Replaced by the classes for `os`-like usage, and renamed to `constants` to also hold the encoding
    constants.
  - *Alternative:* name the class `os`, or import the module as `os`. Rejected: it is indistinguishable from the
    standard `os` module in the code. A file with the standard `import os` would still run `os.linesep`, silently
    with `\r\n` again, and the standard `os` could not be used in the same module.
- **Remove `continue-on-error` entirely.** No matrix entry is meant to be allowed to fail. If Python 3.15 is
  unavailable on a runner, scope it with `continue-on-error: ${{ matrix.python-version == '3.15' }}` instead.
- **No separate line ending tests.** The Windows jobs run the existing human-readable output-file tests, which
  failed on the doubled line breaks before the fix.
  - *Alternative:* two dedicated tests: the output file read as bytes, and stdout with `os.linesep` patched to
    `"\r\n"`, which would catch a reintroduced `os.linesep` on stdout on every platform. Rejected: running the
    regular test suite on each operating system in CI is considered sufficient.

## Risks / Trade-offs

- [Unknown macOS or Windows failures after `continue-on-error` is removed] → With `d1f194c`, the Windows jobs pass.
  Any further failure blocks the merge and is triaged: test-only fixes here, product bugs in their own change.
- [`TZ: Europe/Berlin` on Windows] → Tests compute expected dates with tzlocal, as the tool does, and no test relies on
  the current time, so expected and actual values agree.
- [Callers that strip `\r\r\n` on Windows] → They now get `\r\n`, which they handle anyway.
- [A reintroduced `os.linesep` on stdout goes unnoticed] → The tests capture stdout without newline translation and
  split it with `splitlines()`, so they cannot see `\r\r\n` on stdout, not even on Windows. The `Os.linesep`
  docstring explains why `os.linesep` must not be used.
- [Namespace classes without methods] → pylint reports `too-few-public-methods`. Each class disables it with a
  reason, as the code base does for other pylint exceptions.

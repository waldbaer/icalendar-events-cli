# Proposal

## Why

The CI workflow claimed to test Linux, macOS and Windows, but every job ran on Ubuntu: `runs-on` was hard-coded to
`ubuntu-latest`. The job-level `continue-on-error: true` also lets a failing job pass the workflow run. When pull
request #82 switched to the real operating systems, all 6 Windows jobs failed, yet the run still reported success.

The Windows jobs exposed these bugs:

- The human-readable output joined lines with `os.linesep`. Text-mode stdout and files translate `\n` again, so
  Windows got `\r\r\n` line breaks, which read back as an empty line after every line. The unexpected-error message
  had the same problem.
- The tool returned `os.EX_OK`, which is missing on Windows with Python 3.10. Every run there crashed after writing
  its result: the catch-all handler appended an error message to the output and the tool exited with code 1. The
  tests compared against `os.EX_OK` too.
- The tests passed output paths through `shlex.split()` unquoted, which dropped the backslashes of Windows paths.

## What Changes

All in #82:

- The CI job runs on the operating system named by `matrix.os` (`752ee05`), and a failing job fails the workflow
  run: `continue-on-error: true` is removed.
- Tests quote output paths for `shlex.split()` (`57edf67`).
- Human-readable output and the unexpected-error message join lines with `\n`, which stdout and files translate to
  the platform line ending. The test helper that reads output files joins their lines with `""` instead of
  `os.linesep` (`6c98b70`).
- A new module `constants` holds platform-independent constants in namespace classes (`d1f194c`):
  - `Os.EX_OK` (0), `Os.EX_ERROR` (1) and `Os.linesep` (`"\n"`) replace `os.EX_OK`, `os.linesep` and the literal
    exit code 1 in code and tests. The exit codes do not change.
  - `StringEncoding.UTF_8` (`"utf-8"`) replaces the encoding literals of the output files and the downloader's
    `DEFAULT_CHARSET`, which is removed. `StringEncoding.BYTE_ORDER_MARK` replaces the downloader's own constant.
- No separate line ending tests: the existing human-readable output-file tests catch doubled line breaks on the
  Windows jobs.
- `CHANGELOG.md` has the fix entry "Fixes for Windows OS" (`d7003c6`) and an "Infrastructure" entry for the CI
  change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `event-output`: new requirement "Line endings": each line break in the result is the platform's line separator,
  written once.

The exit code fix restores behavior that `cli-configuration` already requires (exit code 0 after writing the
output), so it needs no spec change.

## Impact

- CI: `.github/workflows/python-pdm.yml`.
- Code: new `src/icalendar_events_cli/constants.py`; `output.py`, `__main__.py`, `argparse.py` and `downloader.py`
  use it.
- Tests: `tests/test_query.py`, `tests/test_general.py`, `tests/util_runner.py`.
- Docs: `CHANGELOG.md` (fix and "Infrastructure" entries). No README change.
- Compatibility: on Windows, human-readable output changes from `\r\r\n` to `\r\n` line breaks, on stdout and in
  files. On Windows with Python 3.10, a successful run now writes only its result and exits with code 0. Nothing
  changes on Linux and macOS. Patch release.

# Tasks

## 1. Windows fixes (pull request #82)

- [x] 1.1 Human-readable output and the unexpected-error message join lines with `\n` instead of `os.linesep`, and
  `tests/util_runner.py` joins file lines with `""` (`6c98b70`, `d1f194c`). Verify that
  `grep -rn "os\.linesep" src tests` finds only the docstring in `constants.py`.
- [x] 1.2 Add `src/icalendar_events_cli/constants.py` with the classes `Os` (`EX_OK`, `EX_ERROR`, `linesep`) and
  `StringEncoding` (`UTF_8`, `BYTE_ORDER_MARK`), documented in `Attributes:` sections. Code and tests use them instead
  of `os.EX_OK`, `os.linesep` and literal exit codes, and `downloader.py` drops `DEFAULT_CHARSET` and its own
  `BYTE_ORDER_MARK` (`d1f194c`). Verify that `grep -rn "os\.EX_" src tests` finds only the docstring in
  `constants.py`, that `src` has no `"utf-8"` literal outside `constants.py`, and that `pdm run tests` passes.
- [x] 1.3 `build_output_file_cli_arg()` quotes the output path with `shlex.quote()` (`57edf67`). Verify that the
  output-file tests pass on the Windows jobs.
- [x] 1.4 No separate line ending tests (see design.md). Verify that the human-readable output-file tests in
  `tests/test_query.py` pass on the Windows jobs. Before `6c98b70` they failed there on the doubled line breaks.

## 2. CI

- [x] 2.1 `runs-on: ${{ matrix.os }}` (`752ee05`). Verify that the jobs run on their operating system: the Windows
  job logs show `platform win32`, and macOS uses the same `matrix.os` expression.
- [x] 2.2 Remove `continue-on-error: true` from `.github/workflows/python-pdm.yml`. If Python 3.15 cannot be installed
  on a runner, scope it to `matrix.python-version == '3.15'` instead and say so in the pull request. Verify that all
  18 jobs pass and the run concludes `success`.

## 3. Documentation and final checks

- [x] 3.1 In `CHANGELOG.md` under the unreleased version, add an `### Infrastructure` entry: CI now runs the test
  matrix on Linux, macOS and Windows and fails on errors. The fix entry "Fixes for Windows OS" exists (`d7003c6`).
  Verify that both link #82.
- [x] 3.2 Run `pdm run format`, `pdm run lint` and `pdm run tests`. Verify that all pass and coverage stays at 100%.

## Workflow follow-up

- Archive the change with `/opsx:archive` in pull request #82, before merging.

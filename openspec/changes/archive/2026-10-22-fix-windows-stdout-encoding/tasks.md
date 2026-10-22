# Tasks

## 1. UTF-8 output streams

- [x] 1.1 Add tests in `tests/test_query.py` that replace `sys.stdout` (and `sys.stderr` where needed) with
  `io.TextIOWrapper(io.BytesIO(), encoding="cp1252")` via `monkeypatch`, run `cli()` and read the bytes. Cover:
  JSON output of a calendar served by the test HTTP server whose summary contains `jährlich` and 🎉 (expect the
  UTF-8 bytes, a complete JSON document and exit code 0), human-readable output of the same calendar, and
  `--filter.summary "[🎉"` (expect the UTF-8 message on stderr and exit code 2). Verify that they fail before 1.2.
- [x] 1.2 At the start of `cli()` (`src/icalendar_events_cli/__main__.py`), call `reconfigure(encoding="utf-8")` on
  `sys.stdout` and `sys.stderr` when the stream has that method, and document this in the docstring. Verify that
  the tests from 1.1 pass.
- [x] 1.3 Add a test that runs `cli()` with `sys.stdout` replaced by an `io.StringIO`, which has no `reconfigure()`.
  Verify that the query succeeds and that coverage stays at 100%.

## 2. Documentation and final checks

- [x] 2.1 In `README.md`, state in the automation section that stdout and output files are always UTF-8. Add a
  `CHANGELOG.md` entry under the unreleased version, section `### Fixes`, linking the pull request: output and
  messages are written in UTF-8 on Windows pipes too, instead of the ANSI code page, which garbled non-ASCII text and
  aborted output on characters such as emoji. Verify both texts.
- [x] 2.2 Run `pdm run format`, `pdm run lint` and `pdm run tests`. Verify that all pass and coverage stays at 100%.

## Workflow follow-up

- Run the CI matrix (Linux, macOS, Windows; Python 3.10 to 3.15) through the pull request. On Windows, also check
  `icalendar-events-cli ... --output.format json | python -c "import sys; sys.stdin.buffer.read().decode('utf-8')"`
  by hand, since the tests simulate the code page.
- Archive the change with `/opsx:archive` after the pull request is merged.

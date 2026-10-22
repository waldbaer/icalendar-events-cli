# Tasks

## 1. Decode calendars as UTF-8 by default

- [x] 1.1 In `tests/test_query.py`, add a helper that serves given bytes through pytest-httpserver with an explicit
  `content_type`, and a parametrized JSON-output test that queries Ostermontag 2025 from `GermanHolidays.ics` and checks
  the description for these cases:
  - UTF-8 served as `text/calendar` (no charset): expect `jährlich`.
  - UTF-8 with a byte order mark prefix, served as `text/calendar`: expect exit code 0 and `jährlich`.
  - ISO-8859-1 encoded, served as `text/calendar; charset=ISO-8859-1`: expect `jährlich`.
  - ISO-8859-1 encoded, served as `text/calendar`: expect exit code 0 and `j�hrlich`.
  - `GermanHolidays.json` (jCal, UTF-8) served as `application/calendar+json` (no charset): expect `jährlich`.

  Generate the byte order mark and ISO-8859-1 variants from the UTF-8 fixture inside the test. Verify that the first,
  second and fourth cases fail on the current code.
- [x] 1.2 Add a test that queries `tests/calendar_examples/GermanHolidays.ics` through a `file://` URL built with
  `pathlib.Path(...).absolute().as_uri()` and expects `jährlich` in the output. Verify that it passes.
- [x] 1.3 In `download_calendar` (`src/icalendar_events_cli/downloader.py`), read the declared charset with
  `email.message.Message.get_content_charset()`. When there is none, set `response.encoding = "utf-8"`. Remove one
  leading U+FEFF from the decoded text. Verify that all tests from 1.1 and 1.2 pass.
- [x] 1.4 In `README.md`, replace `jÃ¤hrlich` with `jährlich` in the outputs of examples 1 and 3. Verify that
  `grep -n "Ã" README.md` finds nothing.
- [x] 1.5 Add a `CHANGELOG.md` entry under `[2.0.3] - Unreleased` → `### Fixes`, linking the PR. It should say that
  calendars without a declared charset are now decoded as UTF-8 (previously ISO-8859-1 over HTTP) and that a leading
  byte order mark is ignored. Verify that the entry sits with the other 2.0.3 fixes.

## 2. Final checks

- [x] 2.1 Run `pdm run format`, `pdm run lint` and `pdm run tests`. Verify that all pass and coverage stays at 100%.
- [x] 2.2 Run README example 1 against the live Thunderbird calendar URL. Verify that the Ostermontag description shows
  `jährlich`.

## Workflow follow-up

- Run the CI matrix (Linux, macOS, Windows; Python 3.10 to 3.15) through the pull request.
- Archive the change with `/opsx:archive` after the pull request is merged.

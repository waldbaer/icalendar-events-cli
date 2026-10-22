# Tasks

## 1. Floating times in output and sorting

- [x] 1.1 Add `tests/calendar_examples/floating_events.ics` with three events: `floating_winter` (floating
  `DTSTART:20250105T100000`, `DTEND:20250105T110000`), `utc_event` (`DTSTART:20250105T093000Z`,
  `DTEND:20250105T103000Z`) and `floating_summer` (floating `DTSTART:20250705T100000`, `DTEND:20250705T110000`).
  Verify that `icalendar-events-cli --calendar.url file://$(pwd)/tests/calendar_examples/floating_events.ics
  -s 2025-07-01 -e 2025-07-31 --output.format jcal` lists `floating_summer`.
- [x] 1.2 Add JSON output tests in `tests/test_query.py` that compute expected values with `localized_date_time`, so
  they pass in any local timezone: `floating_summer` starts at local 2025-07-05T10:00 and ends at local 11:00, both
  with UTC offset. A window over 2025-01-05 selects `floating_winter` and `utc_event`, succeeds and lists them in order
  of their start instants. Verify that these tests fail before 1.3 (offset missing, or the `TypeError` abort).
- [x] 1.3 In `get_event_dtstart()` and `get_event_dtend()` (`src/icalendar_events_cli/icalendar.py`), localize a
  datetime without tzinfo with the local timezone. Verify that the tests from 1.2 pass, and that the human-readable
  output of the 2025-01-05 query shows both events with UTC offsets.
- [x] 1.4 Add a jCal test asserting that the `vevent` of `floating_summer` has `dtstart` `2025-07-05T10:00:00` without a
  `tzid` parameter. Verify that it passes.

## 2. Time window in local time

- [x] 2.1 Add selection tests: the window local 2025-01-05T10:30 to 10:45, given in UTC (`.astimezone(timezone.utc)`),
  selects `floating_winter`. The window local 11:30 to 11:45, given in UTC, does not. On `GermanHolidays.ics`, the
  window local 2025-10-03T00:30 to 00:45, given in UTC, selects "Tag der Deutschen Einheit". The window local
  2025-10-04T01:30 to 01:45, given in UTC, does not. Verify that, with `TZ=Europe/Berlin`, the floating and
  all-day cases fail before 2.2.
- [x] 2.2 In `recurring_calendar()`, pass the window bounds converted with `.astimezone()` to the local timezone to
  `between()`, leaving the configuration unchanged. Verify that the tests from 2.1 pass and that all existing tests
  pass unchanged, including the JSON `filter` object and `x-filter-date-range` assertions.

## 3. Documentation and final checks

- [x] 3.1 Add two `CHANGELOG.md` entries under the unreleased version, section `### Fixes`, linking the pull request:
  floating times are read as local time in selection and output, and no longer abort queries that also select
  timezone-aware events. All-day events are selected in local time also for windows given in another UTC offset.
  Verify that the entries sit under the unreleased version.
- [x] 3.2 Run `pdm run format`, `pdm run lint` and `pdm run tests`. Verify that all pass and coverage stays at 100%.

## Workflow follow-up

- Run the CI matrix (Linux, macOS, Windows; Python 3.10 to 3.15) through the pull request.
- Archive the change with `/opsx:archive` after the pull request is merged.

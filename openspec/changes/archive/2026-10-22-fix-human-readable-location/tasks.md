# Tasks

## 1. Fix the location in human-readable output

- [x] 1.1 In `test_ct_valid_query_outputformat_humanreadable` (`tests/test_query.py`), replace the
  `re.match(f".*| ... |.*", line)` assertions with `re.search` patterns whose separators are escaped (`\|`) and that
  check ` | <summary>`, ` | Description: <description>` and ` | Location: <location>`. Keep the expected summary and
  description values as regex patterns, since they are written that way (for example `Ostersonntag.*`). When the
  expected event has no description or location, assert that the line contains no `Description:` or `Location:`
  segment. Verify that `pdm run tests` now fails for the `recurring_events.ics` cases that have a location.
- [x] 1.2 In `output_human_readable` (`src/icalendar_events_cli/output.py`), build the ` | Location: ` segment from the
  event's location instead of its description. Verify that the tests from 1.1 pass, and that
  `icalendar-events-cli --calendar.url file://$(pwd)/tests/calendar_examples/recurring_events.ics -s 2025-07-01
  -e 2025-09-30 --filter.location "location_recurring_event_monthly.*"` prints lines ending in
  `| Location: location_recurring_event_monthly_3months` instead of `| Location: None`.
- [x] 1.3 Add a `CHANGELOG.md` entry under `[2.0.3] - Unreleased` → `### Fixes` stating that the human-readable output
  now shows the event location instead of the description, linking the PR. Verify the entry sits next to the
  existing 2.0.3 fix.

## 2. Final checks

- [x] 2.1 Run `pdm run format`, `pdm run lint` and `pdm run tests`. Verify that all pass and coverage stays at 100%.

## Workflow follow-up

- Run the CI matrix (Linux, macOS, Windows; Python 3.10 to 3.15) through the pull request.
- Archive the change with `/opsx:archive` after the pull request is merged.

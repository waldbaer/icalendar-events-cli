# Proposal

## Why

The human-readable output prints an event's description in its `Location:` field. An event with a location but no
description shows `| Location: None`, and an event with both shows its description twice. The `event-output` spec
already requires ` | Location: <location>`. The existing test misses the bug because its regex assertions contain an
unescaped `|`, which turns each pattern into an alternation that matches any line.

## What Changes

- Human-readable event lines show the event's `LOCATION` value after ` | Location: `.
- The human-readable test checks the summary, description and location segments for real, and checks that a
  segment is absent when the event lacks that attribute.
- `CHANGELOG.md` gets a fix entry for the unreleased 2.0.3.
- JSON and jCal output, options and exit codes do not change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `event-output`: the requirement "Human-readable event lines" keeps its text and gains a scenario for an event with
  both a description and a location, which is where the bug shows the description twice.

## Impact

- Code: `src/icalendar_events_cli/output.py` (`output_human_readable`).
- Tests: `tests/test_query.py` (`test_ct_valid_query_outputformat_humanreadable`).
- Docs: `CHANGELOG.md`. The README examples contain no event with a location, so they stay as they are.
- Compatibility: only human-readable lines of events with a location change, from the wrong value to the documented
  one. This restores specified behavior and fits a patch release.

# Proposal

## Why

Events with a "floating" time, a date-time without `TZID` or `Z` such as `DTSTART:20250105T100000`, break the tool.
If a query selects a floating event and a timezone-aware event, it aborts with
`can't compare offset-naive and offset-aware datetimes`. If it selects only floating events, their start and end are
written without a UTC offset, although the `event-output` spec requires one.

All-day events have a related inconsistency. When the window is given with a UTC offset other than the local one, the
selection reads the all-day dates in the window's offset, while the output writes them in local time. For example, the
window 2025-10-03T23:30Z to 23:45Z (01:30 to 01:45 on Oct 4 in Berlin) reports the holiday on Oct 3, whose output
ends at 21:59:59Z, before the window starts. The window 2025-10-02T22:30Z to 22:45Z (00:30 on Oct 3 in Berlin)
misses it.

## What Changes

- Floating date-times are read as the system's local time, like all-day dates already are in the output. RFC 5545
  defines floating times as local time.
- The time window selection reads floating times and all-day dates in local time, so it matches the output. Window
  bounds keep their instants; only floating and all-day events can change whether they are selected.
- JSON and human-readable output write floating times with the local UTC offset.
- A query that selects floating and timezone-aware events succeeds and sorts all events by start instant.
- jCal output keeps floating times floating, as given in the source calendar.
- `CHANGELOG.md` gets fix entries for the unreleased version.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `event-query`: "Time window selection" states that floating times and all-day dates are read in local time.
  "Chronological order" gains a scenario that mixes floating and timezone-aware events.
- `event-output`: "Event start and end values" states that floating times are written in local time. "jCal event
  components" gains a scenario stating that floating times stay floating.

## Impact

- Code: `src/icalendar_events_cli/icalendar.py` (time window query, `get_event_dtstart`, `get_event_dtend`).
- Tests: new `tests/calendar_examples/floating_events.ics` and tests in `tests/test_query.py`.
- Docs: `CHANGELOG.md`. The README examples contain no floating events and no windows outside the local offset.
- Compatibility: output for floating events changes from a crash or a value without offset to the documented form.
  An all-day or floating event can change whether it is selected only for windows given in a non-local UTC offset.
  Both restore specified behavior and fit a patch release.

# Spec Delta

## MODIFIED Requirements

### Requirement: Time window selection

The tool SHALL select every event occurrence that overlaps the time window from `filter.start-date` to
`filter.end-date`, including occurrences that started before the window and are still ongoing within it. Floating
date-times (without timezone) and all-day dates SHALL be read in the system's local timezone when compared with the
window, whatever UTC offset the window bounds are given in.

#### Scenario: Event inside the window

- **WHEN** the window is 2025-10-03 00:00 to 2025-10-04 23:59:59 local time and the calendar has an all-day event on
  2025-10-03
- **THEN** the event is reported

#### Scenario: Event spanning the whole window

- **WHEN** an event runs from 2025-07-01 00:00 to 2025-07-03 23:59:59 and the window is 2025-07-02 12:00 to 13:00
- **THEN** the event is reported

#### Scenario: Event outside the window

- **WHEN** an event ends before the window starts or starts after the window ends
- **THEN** the event is not reported

#### Scenario: Zero-length window

- **WHEN** start-date and end-date are both 2025-01-01T00:00:00 local time and an all-day event covers 2025-01-01
- **THEN** that event is reported

#### Scenario: Floating event inside a window given in UTC

- **WHEN** the system timezone is Europe/Berlin, an event has `DTSTART:20250105T100000` and `DTEND:20250105T110000`,
  and the window is `2025-01-05T09:30:00+00:00` to `2025-01-05T09:45:00+00:00` (10:30 to 10:45 in Berlin)
- **THEN** the event is reported

#### Scenario: Floating event outside a window given in UTC

- **WHEN** the system timezone is Europe/Berlin, an event has `DTSTART:20250105T100000` and `DTEND:20250105T110000`,
  and the window is `2025-01-05T10:30:00+00:00` to `2025-01-05T10:45:00+00:00` (11:30 to 11:45 in Berlin)
- **THEN** the event is not reported

#### Scenario: All-day event and a window given in UTC

- **WHEN** the system timezone is Europe/Berlin and an all-day event covers 2025-10-03
- **THEN** it is reported for the window `2025-10-02T22:30:00+00:00` to `2025-10-02T22:45:00+00:00` (00:30 to 00:45
  on Oct 3 in Berlin)
- **AND** it is not reported for the window `2025-10-03T23:30:00+00:00` to `2025-10-03T23:45:00+00:00` (01:30 to
  01:45 on Oct 4 in Berlin)

### Requirement: Chronological order

The tool SHALL report the selected event occurrences sorted by start date and time in ascending order, in every
output format. Floating date-times and all-day dates SHALL be compared as local time.

#### Scenario: Events from several recurring series

- **WHEN** the selected occurrences come from different events and recurring series
- **THEN** they are output ordered by their start, earliest first

#### Scenario: Floating and timezone-aware events

- **WHEN** the system timezone is Europe/Berlin and the window selects an event with `DTSTART:20250105T100000`
  (09:00 UTC) and an event with `DTSTART:20250105T093000Z`
- **THEN** the query succeeds and reports the floating event first, then the UTC event

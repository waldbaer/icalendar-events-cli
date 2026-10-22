# event-query Specification

## Purpose

Selects the calendar events to report: event occurrences within the configured time window, with recurring events
expanded into individual occurrences, narrowed down by optional regular-expression filters on summary, description
and location, and ordered chronologically.

## Requirements

### Requirement: Events only

The tool SHALL consider only `VEVENT` components. Other components, such as `VTODO` and `VJOURNAL`, SHALL be ignored.

#### Scenario: Calendar with a to-do

- **WHEN** a calendar contains a `VTODO` and a `VEVENT`, both inside the time window
- **THEN** only the `VEVENT` is reported

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

### Requirement: Recurring event expansion

The tool SHALL expand recurring events into their individual occurrences and report each occurrence that falls in
the time window as a separate event. This SHALL honour the recurrence rules' frequency (daily, weekly, monthly,
yearly), `INTERVAL`, `COUNT`, `UNTIL` and `BY…` parts. An event with a `RECURRENCE-ID` SHALL be reported even when the
calendar does not contain the recurring event it modifies.

#### Scenario: Daily recurrence with an end date

- **WHEN** an event recurs daily at 19:00–20:00 from 2025-01-01 until 2025-01-03 and the window covers January and
  February 2025
- **THEN** three occurrences are reported, on 2025-01-01, 2025-01-02 and 2025-01-03

#### Scenario: Recurrence with interval and count

- **WHEN** an event recurs every second day with `COUNT=2` starting 2025-01-01
- **THEN** occurrences on 2025-01-01 and 2025-01-03 are reported

#### Scenario: Window covers only part of the recurrence

- **WHEN** an event recurs weekly with `COUNT=2` starting 2025-01-01 and the window ends on 2025-01-07
- **THEN** only the occurrence on 2025-01-01 is reported

#### Scenario: Yearly all-day recurrence

- **WHEN** an all-day event recurs yearly on May 1 with `COUNT=2` starting 2025 and the window covers 2025 to 2035
- **THEN** occurrences on 2025-05-01 and 2026-05-01 are reported

#### Scenario: Modified instance without its recurring event

- **WHEN** the calendar contains only a single event carrying a `RECURRENCE-ID` (github issue #6) and it lies in the
  window
- **THEN** that event is reported

### Requirement: Text filter matching

The tool SHALL match the regular expressions configured in `filter.summary`, `filter.description` and
`filter.location` against the event's `SUMMARY`, `DESCRIPTION` and `LOCATION` respectively, using Python
regular-expression syntax. Each expression SHALL be matched case-sensitively from the beginning of the attribute value
and need not match the whole value.

#### Scenario: Match at the beginning of the summary

- **WHEN** the summary filter is `Oster.*`
- **THEN** events with the summaries `Ostersonntag  (Brandenburg)` and `Ostermontag ` are reported

#### Scenario: Match in the middle of the summary

- **WHEN** the summary filter is `montag`
- **THEN** an event with the summary `Ostermontag ` is not reported
- **AND** the summary filter `.*montag` would report it

#### Scenario: Prefix match is sufficient

- **WHEN** the summary filter is `Sommer`
- **THEN** an event with the summary `Sommerferien Baden-Württemberg 2025` is reported

### Requirement: Combining text filters

The tool SHALL report an event only if it matches every configured text filter. An event that lacks an attribute
SHALL be excluded when a filter for that attribute is configured. Without any text filter, all events in the time
window SHALL be reported.

#### Scenario: Attribute missing

- **WHEN** the location filter is set and an event has no `LOCATION`
- **THEN** that event is not reported

#### Scenario: Combined filters

- **WHEN** summary, description and location filters are all set
- **THEN** only events matching all three are reported

#### Scenario: No text filter

- **WHEN** no text filter is configured
- **THEN** all events in the time window are reported

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

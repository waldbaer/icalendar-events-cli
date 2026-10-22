# Spec Delta

## MODIFIED Requirements

### Requirement: Event start and end values

In the JSON and human-readable formats, the start and end of each event SHALL be written as ISO 8601 date-times with
a UTC offset. Timed events SHALL keep the timezone the calendar gives them. Timed events with floating date-times
(without timezone) SHALL be written in the system's local timezone. All-day events SHALL start at 00:00:00 local
time on their first day and end at 23:59:59 local time on their last day, the last day being the day before the
event's exclusive `DTEND`.

#### Scenario: All-day event

- **WHEN** an all-day event has `DTSTART;VALUE=DATE:20251003` and `DTEND;VALUE=DATE:20251004` and the system
  timezone is Europe/Berlin
- **THEN** its start is `2025-10-03T00:00:00+02:00` and its end is `2025-10-03T23:59:59+02:00`

#### Scenario: Multi-day all-day event

- **WHEN** an all-day event has `DTSTART;VALUE=DATE:20250731` and `DTEND;VALUE=DATE:20250914`
- **THEN** its start is 2025-07-31 00:00:00 and its end is 2025-09-13 23:59:59, both in local time

#### Scenario: Event in UTC

- **WHEN** an event has `DTSTART:20250105T100000Z` and `DTEND:20250105T110000Z`
- **THEN** its start is `2025-01-05T10:00:00+00:00` and its end is `2025-01-05T11:00:00+00:00`

#### Scenario: Event with a TZID

- **WHEN** an event has `DTSTART;TZID=Europe/Berlin:20250101T190000`
- **THEN** its start is `2025-01-01T19:00:00+01:00`

#### Scenario: Floating event

- **WHEN** an event has `DTSTART:20250705T100000` and `DTEND:20250705T110000` and the system timezone is
  Europe/Berlin
- **THEN** its start is `2025-07-05T10:00:00+02:00` and its end is `2025-07-05T11:00:00+02:00`

### Requirement: jCal event components

The jCal components SHALL contain exactly one `vevent` per selected event occurrence, in chronological order, with the
event's properties as given in the source calendar. Each occurrence of a recurring event SHALL carry its own start and
a `recurrence-id` identifying that occurrence.

#### Scenario: Recurring event occurrences

- **WHEN** a weekly event starting 2025-01-01 09:00 Europe/Berlin has occurrences on 2025-01-01 and 2025-01-08 in the
  window
- **THEN** the components contain two `vevent` entries whose `dtstart` and `recurrence-id` are `2025-01-01T09:00:00`
  and `2025-01-08T09:00:00` with the `tzid` parameter `Europe/Berlin`

#### Scenario: Floating event

- **WHEN** a selected event has `DTSTART:20250705T100000`
- **THEN** its `vevent` has the `dtstart` `2025-07-05T10:00:00` without a `tzid` parameter, as in the source calendar

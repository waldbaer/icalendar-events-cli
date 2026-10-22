# Design

## Context

- `recurring_calendar()` passes the configured window bounds to `recurring_ical_events.of(...).between()`. The
  library reads floating date-times and dates in the timezone of those bounds. A bound given with a UTC offset, such
  as `2025-01-05T09:30:00+00:00`, carries a fixed-offset timezone. A bound without offset, and the default window,
  carry the local pytz timezone.
- `get_event_dtstart()` and `get_event_dtend()` give dates the local timezone, but return floating date-times
  unchanged, without tzinfo.
- `_sort_events()` sorts by `get_event_dtstart()`. Comparing a datetime without tzinfo to one with tzinfo raises
  `TypeError`, which `cli()` reports as an unexpected error.
- jCal output uses `event.to_jcal()` on the occurrences and does not call the two getters.

## Goals / Non-Goals

**Goals:**

- Selection, output and sorting read floating times and all-day dates in the same timezone: the system's local one.

**Non-Goals:**

- Changing jCal output. Floating times stay floating there, as RFC 5545 intends.
- Merging the two module-level local timezone objects in `argparse.py` and `icalendar.py`.
- Following RFC 5545's rule for DST edges (see Risks).

## Decisions

- **Query with the window converted to local time.** `recurring_calendar()` passes
  `start_date.astimezone(local_tz)` and `end_date.astimezone(local_tz)`. The instants do not change, so timed events
  with a timezone are selected exactly as before. The library then reads floating times and dates in local time.
  The configuration is not changed, so the header, the JSON `filter` object and `x-filter-date-range` still show the
  bounds as given.
  - *Alternative:* localize floating times only in the output. Rejected, because the selection would still use the
    window's offset and could report events outside the window, as all-day events already do.
- **Localize floating date-times in the getters.** `get_event_dtstart()` and `get_event_dtend()` call
  `local_tz.localize()` on a datetime without tzinfo, as they already do for dates. pytz's `localize()` is also what
  recurring-ical-events uses for a pytz window, so selection and output resolve DST edges the same way.
  - *Alternative:* `zoneinfo` with `fold=0`, which follows RFC 5545 at DST edges. Rejected for this fix, because
    the selection, the all-day handling and the default window all use pytz. Mixing the two would let selection and
    output disagree at DST edges.
- **Leave `_sort_events()` unchanged.** Once every start carries a timezone, the existing sort key works.

## Risks / Trade-offs

- [Floating time in the repeated or skipped hour at a DST change] → pytz `localize()` with its default
  `is_dst=False` picks standard time: the second occurrence of a repeated hour, and the offset before the gap for a
  skipped hour. RFC 5545 asks for the first occurrence of a repeated hour. Such events are rare, and selection and
  output agree, so this is accepted.
- [Windows given in a non-local offset now select different all-day and floating events] → That is the fix. It gets
  a changelog entry and tests.
- [Local timezone detection on Windows and macOS] → Unchanged. tzlocal already determines the timezone for all-day
  events on every platform. Tests compute expected values with tzlocal, so they pass in any local timezone.

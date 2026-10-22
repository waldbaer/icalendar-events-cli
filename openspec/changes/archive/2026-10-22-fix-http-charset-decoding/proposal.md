# Proposal

## Why

When an HTTP server returns a calendar as `text/calendar` without a charset, as Thunderbird's holiday calendars do,
the tool decodes it as ISO-8859-1 instead of UTF-8 and garbles every non-ASCII character (`jährlich` becomes
`jÃ¤hrlich`, visible in the README examples). RFC 5545 makes UTF-8 the default, the `calendar-source` spec requires
it, and the 2.0.0 changelog promises it. The tests do not notice, because their mock server always declares
`charset=utf-8`.

## What Changes

- Calendars without a declared charset are decoded as UTF-8, for `http(s)://` and `file://` URLs alike. For `file://`,
  this replaces the current guess based on the content.
- A declared charset is still honored.
- A leading UTF-8 byte order mark is ignored instead of breaking the parser.
- Bytes that are invalid in the charset are replaced with U+FFFD, as they are today, so a single bad byte does not
  abort the query.
- Tests serve calendars with and without a declared charset, with a byte order mark, and through `file://`.
- The README example outputs show `jährlich` instead of `jÃ¤hrlich`, and `CHANGELOG.md` gets a fix entry for the
  unreleased 2.0.3.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `calendar-source`: the requirement "Text decoding" now also covers the byte order mark and invalid bytes, and gains
  scenarios for a declared charset, a byte order mark and invalid UTF-8.

## Impact

- Code: `src/icalendar_events_cli/downloader.py` (`download_calendar`).
- Tests: `tests/test_query.py`, plus test calendar data with non-ASCII text, a byte order mark and a non-UTF-8
  encoding.
- Docs: `README.md` (outputs of examples 1 and 3), `CHANGELOG.md`.
- Compatibility: output changes only for calendars served as `text/*` without a charset. UTF-8 calendars, which is
  what RFC 5545 requires, are now shown correctly. A server that sends ISO-8859-1 content without declaring it
  previously worked by accident and will now show U+FFFD for its non-ASCII characters. This restores specified
  behavior and fits a patch release.

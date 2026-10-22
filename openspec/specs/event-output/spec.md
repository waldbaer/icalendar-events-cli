# event-output Specification

## Purpose

Writes the query result in one of three formats: a human-readable listing for people at the shell, a compact JSON
document for automation platforms such as Node-RED, and a jCal (RFC 7265) calendar that can be read back as input.
The result goes to stdout or to a file. The JSON and jCal structures are a contract that calling automation relies on.

## Requirements

### Requirement: Output target

The tool SHALL write the result to stdout in UTF-8 when `output.file` is not set, independent of the system locale
and console code page. When `output.file` is set, the tool SHALL write the result to that file in UTF-8, replacing
any existing content, and SHALL NOT write the result to stdout.

#### Scenario: Output to stdout

- **WHEN** no `--output.file` is given
- **THEN** the result is printed on stdout

#### Scenario: Output to a file

- **WHEN** `--output.file ./GermanHolidays.json` is given
- **THEN** the result is written to `./GermanHolidays.json`
- **AND** nothing is printed on stdout

#### Scenario: Non-ASCII text on a stdout with another code page

- **WHEN** stdout uses the cp1252 code page, as a pipe does on Windows with Python 3.10 to 3.14, and the result
  contains `jährlich`
- **THEN** stdout receives the UTF-8 bytes of `jährlich`

#### Scenario: Character outside the code page

- **WHEN** stdout uses the cp1252 code page and an event summary contains the character 🎉
- **THEN** the complete result is written to stdout in UTF-8
- **AND** the tool exits with code 0

### Requirement: Output format selection

The tool SHALL produce the format selected by `output.format`: `human_readable` (the default), `json` or `jcal`.

#### Scenario: Default format

- **WHEN** no `--output.format` is given
- **THEN** the result is written in the human-readable format

### Requirement: Event start and end values

In the JSON and human-readable formats, the start and end of each event SHALL be written as ISO 8601 date-times with
a UTC offset. Timed events SHALL keep the timezone the calendar gives them. All-day events SHALL start at 00:00:00 local
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

### Requirement: JSON output format

In the `json` format, the tool SHALL write a JSON object with exactly two keys, `filter` and `events`, indented by
2 spaces and with non-ASCII characters written unescaped.

#### Scenario: JSON result

- **WHEN** the tool is run with `--output.format json --filter.summary "Sommer.*"` and two summer vacations match
- **THEN** the output has the form

  ```json
  {
    "filter": {
      "start-date": "2025-01-25T11:09:20+01:00",
      "end-date": "2026-12-31T23:59:59+01:00",
      "summary": "Sommer.*"
    },
    "events": [
      {
        "start-date": "2025-07-31T00:00:00+02:00",
        "end-date": "2025-09-13T23:59:59+02:00",
        "summary": "Sommerferien Baden-Württemberg 2025",
        "description": "Schulferien 2025: https://www.feiertage-deutschland.de/schulferien/2025/",
        "location": "BW"
      },
      {
        "start-date": "2026-07-30T00:00:00+02:00",
        "end-date": "2026-09-12T23:59:59+02:00",
        "summary": "Sommerferien Baden-Württemberg 2026",
        "description": "Schulferien 2026: https://www.feiertage-deutschland.de/schulferien/2026/",
        "location": "BW"
      }
    ]
  }
  ```

### Requirement: JSON filter object

The JSON `filter` object SHALL contain `start-date` and `end-date` of the time window as ISO 8601 date-times with UTC
offset, plus `summary`, `description` and `location` only when the corresponding text filter is set.

#### Scenario: Only a summary filter set

- **WHEN** the summary filter `Sommer.*` is set and the description and location filters are not
- **THEN** the `filter` object has the keys `start-date`, `end-date` and `summary` only

### Requirement: JSON events array

The JSON `events` array SHALL contain one object per selected event occurrence, in chronological order. Each object
SHALL have `start-date`, `end-date` and `summary`, plus `description` and `location` only when the event has that
attribute.

#### Scenario: Event without description or location

- **WHEN** a selected event has no `DESCRIPTION` and no `LOCATION`
- **THEN** its JSON object has no `description` and no `location` key

#### Scenario: No matching events

- **WHEN** no event matches
- **THEN** the output contains the `filter` object and an empty `events` array

### Requirement: jCal output format

In the `jcal` format, the tool SHALL write an RFC 7265 jCal calendar as a JSON array of the form
`["vcalendar", <properties>, <components>]`, indented by 2 spaces.

#### Scenario: jCal result

- **WHEN** the tool is run with `--output.format jcal`
- **THEN** the output is a JSON array whose first element is `"vcalendar"`, whose second element is the list of
  calendar properties and whose third element is the list of event components

### Requirement: jCal calendar properties

The jCal calendar properties SHALL contain all properties of the source calendar (for example `version`, `prodid`,
`calscale`), followed by `["x-filter-date-range", {}, "period", [<start>, <end>]]` with the time window written in
UTC (`YYYY-MM-DDTHH:MM:SSZ`), and by an `x-filter-summary`, `x-filter-description` or `x-filter-location` entry of
type `text` for each text filter that is set.

#### Scenario: Filter metadata in UTC

- **WHEN** the tool is run with `--output.format jcal --filter.start-date 1900-01-01T02:00:00+02:00
  --filter.end-date 2500-12-31T02:00:00+01:00`
- **THEN** the properties contain `["x-filter-date-range", {}, "period", ["1900-01-01T00:00:00Z", "2500-12-31T01:00:00Z"]]`

#### Scenario: Text filter metadata

- **WHEN** the summary filter `.*(Weihnacht|Oster).*` is set and the description and location filters are not
- **THEN** the properties contain `["x-filter-summary", {}, "text", ".*(Weihnacht|Oster).*"]`
- **AND** contain no `x-filter-description` or `x-filter-location` entry

### Requirement: jCal event components

The jCal components SHALL contain exactly one `vevent` per selected event occurrence, in chronological order, with the
event's properties as given in the source calendar. Each occurrence of a recurring event SHALL carry its own start and
a `recurrence-id` identifying that occurrence.

#### Scenario: Recurring event occurrences

- **WHEN** a weekly event starting 2025-01-01 09:00 Europe/Berlin has occurrences on 2025-01-01 and 2025-01-08 in the
  window
- **THEN** the components contain two `vevent` entries whose `dtstart` and `recurrence-id` are `2025-01-01T09:00:00`
  and `2025-01-08T09:00:00` with the `tzid` parameter `Europe/Berlin`

### Requirement: jCal output can be read back

The jCal output SHALL be valid input for the tool itself and for RFC 7265 parsers. Querying the jCal output with the
same time window and filters SHALL report the same events as the original query, and its `x-filter-date-range` SHALL
parse to the configured start and end instants.

#### Scenario: Convert and query again

- **WHEN** a calendar is converted with `--output.format jcal --output.file ./GermanHolidays.json` over a window from
  1900 to 2500, and the tool is then run with `--calendar.url file://$(pwd)/GermanHolidays.json` and the same filters
  as a query on the original calendar
- **THEN** both queries report the same events

### Requirement: Human-readable output format

In the `human_readable` format, the tool SHALL write a header, an empty line, and then one line per selected event
occurrence in chronological order.

#### Scenario: Holiday query

- **WHEN** the tool is run with `--filter.summary ".*(Weihnacht|Oster).*"` for 2026 on the German holiday calendar
- **THEN** the output has the form

  ```text
  Start Date:         2026-01-01T02:00:00+02:00
  End Date:           2026-12-31T02:00:00+01:00
  Summary Filter:     .*(Weihnacht|Oster).*
  Number of Events:   3

  2026-04-05T00:00:00+02:00 -> 2026-04-05T23:59:59+02:00 [86399 sec]     | Ostersonntag  (Brandenburg) | Description: Common local holiday - ...
  2026-04-06T00:00:00+02:00 -> 2026-04-06T23:59:59+02:00 [86399 sec]     | Ostermontag  | Description: Christian - ...
  2026-12-25T00:00:00+01:00 -> 2026-12-25T23:59:59+01:00 [86399 sec]     | Weihnachten  | Description: Christian - ...
  ```

### Requirement: Human-readable header

The human-readable header SHALL consist of the lines `Start Date:         <start>` and `End Date:           <end>`,
then `Summary Filter:     <regex>`, `Description Filter: <regex>` and `Location Filter:    <regex>` for each text
filter that is set, then `Number of Events:   <count>`.

#### Scenario: Header without text filters

- **WHEN** no text filter is set and 20 events match
- **THEN** the header consists of the `Start Date`, `End Date` and `Number of Events:   20` lines only

### Requirement: Human-readable event lines

Each human-readable event line SHALL start with `<start> -> <end> [<duration> sec]`, left-aligned and padded to 70
characters, where the duration is the number of whole seconds between start and end. It SHALL continue with
` | <summary>`, then ` | Description: <description>` when the event has a description, then
` | Location: <location>` when the event has a location.

#### Scenario: Event with a location

- **WHEN** a selected event has the location `BW` and no description
- **THEN** its line ends with ` | <summary> | Location: BW`

#### Scenario: Event without description or location

- **WHEN** a selected event has neither a description nor a location
- **THEN** its line ends with ` | <summary>`

#### Scenario: Event with description and location

- **WHEN** a selected event has the description `Schulferien 2025` and the location `BW`
- **THEN** its line ends with ` | <summary> | Description: Schulferien 2025 | Location: BW`

### Requirement: Line endings

In every output format, on stdout and in output files, each line break SHALL be written as the platform's line
separator, exactly once: CR LF on Windows, LF on Linux and macOS.

#### Scenario: Human-readable output to a file on Windows

- **WHEN** the tool runs on Windows with `--output.format human_readable --output.file out.txt` and two events match
- **THEN** every line break in `out.txt` is CR LF
- **AND** `out.txt` contains no CR CR LF sequence

#### Scenario: Human-readable output on Linux

- **WHEN** the tool runs on Linux with `--output.format human_readable`
- **THEN** every line on stdout ends with LF and stdout contains no CR

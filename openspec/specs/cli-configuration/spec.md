# cli-configuration Specification

## Purpose

Defines how users invoke `icalendar-events-cli`: the available options, the JSON configuration file and how it
combines with command-line arguments, defaults, parameter validation, built-in help and version output, and the
process exit codes that calling automation (for example Node-RED) relies on.

## Requirements

### Requirement: Calendar options

The tool SHALL accept the required option `--calendar.url` (calendar URL) and the optional options
`--calendar.verify-url` (`true` or `false`, default `true`), `--calendar.user` and `--calendar.password` (HTTP basic
authentication credentials, default none).

#### Scenario: Calendar URL is missing

- **WHEN** the tool is run without `--calendar.url` and no configuration file provides `calendar.url`
- **THEN** it prints an error stating that `calendar.url` is required to stderr
- **AND** exits with code 2

### Requirement: Filter options

The tool SHALL accept the optional options `--filter.start-date` / `-s` and `--filter.end-date` / `-e` (ISO 8601 date
or date-time, default now and end of today) and `--filter.summary` / `-f`, `--filter.description` and
`--filter.location` (regular expressions, default none).

#### Scenario: Short aliases

- **WHEN** the tool is run with `-s 2025-01-01 -e 2025-12-31 -f "Oster.*"`
- **THEN** the values are used as filter start-date, filter end-date and summary filter respectively

### Requirement: Output options

The tool SHALL accept the optional options `--output.format` (`human_readable`, `json` or `jcal`, default
`human_readable`) and `--output.file` / `-o` (path of the output file, default none, meaning stdout).

#### Scenario: Short alias for the output file

- **WHEN** the tool is run with `-o out.txt`
- **THEN** the result is written to `out.txt`

#### Scenario: Unknown output format

- **WHEN** `--output.format` is given a value other than `human_readable`, `json` or `jcal`
- **THEN** the tool prints an error to stderr and exits with code 2

### Requirement: JSON configuration file

The tool SHALL read option values from a JSON configuration file passed with `--config` / `-c`. The file SHALL mirror
the option namespaces as nested objects, for example
`{"calendar": {"url": "...", "verify_url": true}, "filter": {"summary": "Sommer.*"}, "output": {"format": "json"}}`.
The tool SHALL also load `./config.json` from the current working directory automatically when that file exists.

#### Scenario: All parameters from a configuration file

- **WHEN** the tool is run with only `--config school-vacation.json` and the file defines the calendar URL, filters
  and output format
- **THEN** the query runs with the values from the file

#### Scenario: Default configuration file

- **WHEN** the tool is run without `--config` and `./config.json` exists in the working directory
- **THEN** the values from `./config.json` are used

#### Scenario: No default configuration file

- **WHEN** the tool is run without `--config` and `./config.json` does not exist
- **THEN** the tool runs with command-line values and built-in defaults only, without reporting an error about the
  missing file

### Requirement: Precedence of configuration sources

Command-line options and configuration files SHALL be applied in the order they appear on the command line, with later
values overriding earlier ones. Values from the default `./config.json` SHALL be overridden by any explicitly given
option.

#### Scenario: Option after the configuration file

- **WHEN** the configuration file sets `filter.summary` to `Weihnacht.*` and the tool is run with
  `--config cfg.json --filter.summary "Oster.*"`
- **THEN** the summary filter `Oster.*` is used

#### Scenario: Option before the configuration file

- **WHEN** the configuration file sets `filter.summary` to `Weihnacht.*` and the tool is run with
  `--filter.summary "Oster.*" --config cfg.json`
- **THEN** the summary filter `Weihnacht.*` from the file is used

#### Scenario: Option overrides the default configuration file

- **WHEN** `./config.json` sets `filter.summary` to `Weihnacht.*` and the tool is run with `--filter.summary "Oster.*"`
- **THEN** the summary filter `Oster.*` is used

### Requirement: Date and date-time parameters

`--filter.start-date` and `--filter.end-date` SHALL accept ISO 8601 dates and date-times. A value with a UTC offset
SHALL keep that offset. A value without a UTC offset SHALL be interpreted in the system's local timezone. A date
without a time SHALL mean 00:00:00 on that day.

#### Scenario: Date-time with UTC offset

- **WHEN** `--filter.start-date 2025-01-17T10:00:00+01:00` is given
- **THEN** the start of the time window is 2025-01-17 10:00:00 at UTC+01:00

#### Scenario: Date-time without UTC offset

- **WHEN** `--filter.end-date 2025-10-03T23:00` is given and the system timezone is Europe/Berlin
- **THEN** the end of the time window is `2025-10-03T23:00:00+02:00`

#### Scenario: Date only

- **WHEN** `--filter.start-date 2025-10-03` is given and the system timezone is Europe/Berlin
- **THEN** the start of the time window is `2025-10-03T00:00:00+02:00`

#### Scenario: Invalid date

- **WHEN** `--filter.start-date 2025` is given
- **THEN** the tool prints `invalid datetime value (expected ISO 8601 format): '2025'` to stderr
- **AND** exits with code 2

### Requirement: Default time window

When `--filter.start-date` is not given, the start of the time window SHALL be the current local time, truncated to
whole seconds. When `--filter.end-date` is not given, the end of the time window SHALL be 23:59:59 local time of the
current day.

#### Scenario: No dates given

- **WHEN** the tool is run on 2026-03-14 at 15:30:12 local time without `--filter.start-date` and `--filter.end-date`
- **THEN** the time window runs from 2026-03-14 15:30:12 to 2026-03-14 23:59:59 local time

### Requirement: Regular expression parameters

`--filter.summary`, `--filter.description` and `--filter.location` SHALL be validated as Python regular expressions
before the calendar is retrieved.

#### Scenario: Invalid regular expression

- **WHEN** `--filter.summary "["` is given
- **THEN** the tool prints an error naming `--filter.summary` and `invalid RegEx value '['` to stderr
- **AND** exits with code 2 without retrieving the calendar

### Requirement: Time window consistency

The tool SHALL reject a configuration whose start-date is later than its end-date, comparing both as timezone-aware
date-times. It SHALL print `ERROR: invalid configuration / parameters:` followed by a line describing the problem and
the configured dates to stderr, and exit with code 1 without retrieving the calendar. A start-date equal to the
end-date SHALL be accepted.

#### Scenario: Start after end

- **WHEN** `--filter.start-date 2025-01-17T10:00:00+01:00 --filter.end-date 2025-01-17T08:00:00+01:00` is given
- **THEN** the tool reports that the end-date must be after the start-date
- **AND** exits with code 1

#### Scenario: Start without offset after end with offset

- **WHEN** `--filter.start-date 2025-10-08 --filter.end-date 2025-10-06T08:00:00+01:00` is given
- **THEN** the tool reports that the end-date must be after the start-date
- **AND** exits with code 1

#### Scenario: Start equals end

- **WHEN** start-date and end-date are the same instant
- **THEN** the query runs normally

### Requirement: Help and version information

The tool SHALL print usage and a description of every option for `--help` / `-h`, and the program name, package
version, copyright and author for `--version`. Both SHALL exit with code 0 without retrieving a calendar.

#### Scenario: Help

- **WHEN** the tool is run with `--help`
- **THEN** stdout starts with `Usage: icalendar-events-cli`
- **AND** the tool exits with code 0

#### Scenario: Version

- **WHEN** the tool is run with `--version`
- **THEN** stdout contains `icalendar-events-cli` and the installed package version
- **AND** the tool exits with code 0

### Requirement: Exit codes and unexpected errors

The tool SHALL exit with code 0 after writing its output, with code 2 for missing or malformed command-line
arguments, and with code 1 for an inconsistent configuration, a failed calendar download, or any other error. Any
error not covered by a more specific message SHALL be reported on stdout as `ERROR: Any error has occurred!`, followed
by a blank line and `Exception: <error message>`.

#### Scenario: Successful query

- **WHEN** the calendar is retrieved and the output is written
- **THEN** the tool exits with code 0, also when no event matches

#### Scenario: Unexpected error

- **WHEN** an error occurs that has no specific handling, such as unparseable calendar content
- **THEN** the tool prints `ERROR: Any error has occurred!` and the error message on stdout
- **AND** exits with code 1

### Requirement: Message encoding

The tool SHALL write help, version and error messages in UTF-8, on stdout and on stderr, independent of the system
locale and console code page.

#### Scenario: Error message with a character outside the code page

- **WHEN** stderr uses the cp1252 code page and the tool is run with `--filter.summary "[🎉"`
- **THEN** stderr receives the error message naming `invalid RegEx value '[🎉'` in UTF-8, with the character
  unescaped
- **AND** the tool exits with code 2

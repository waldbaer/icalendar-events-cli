# Changelog

All notable changes to this project will be documented in this file.

## [2.0.3] - Unreleased

### Fixes

* jCal output: Write x-filter-date-range in UTC. UTC offsets are not allowed by RFC 7265 and broke re-import ([#78](https://github.com/waldbaer/icalendar-events-cli/pull/78))
* Calendar download: Decode calendars without a declared charset as UTF-8 (RFC 5545) instead of ISO-8859-1 and ignore a leading byte order mark ([#80](https://github.com/waldbaer/icalendar-events-cli/pull/80))
* Human-readable output: Show the event location instead of the description in the `Location:` field ([#81](https://github.com/waldbaer/icalendar-events-cli/pull/81))
* Fixes for Windows OS ([#82](https://github.com/waldbaer/icalendar-events-cli/pull/82))

### Infrastructure

* Run the CI tests on Linux, macOS and Windows instead of only Linux, and fail the CI run on errors ([#82](https://github.com/waldbaer/icalendar-events-cli/pull/82))

## [2.0.2] - 2026-10-15

### Infrastructure

* Add Python 3.15 to tested versions ([#74](https://github.com/waldbaer/icalendar-events-cli/pull/74))

### Dependencies

* Bump icalendar from 7.1.2 to 7.3.0 ([#66](https://github.com/waldbaer/icalendar-events-cli/pull/66), [#75](https://github.com/waldbaer/icalendar-events-cli/pull/75))
* Bump pytz from 2026.2 to 2026.5 ([#75](https://github.com/waldbaer/icalendar-events-cli/pull/75))
* Bump tzlocal from 5.3.1 to 5.4.4 ([#68](https://github.com/waldbaer/icalendar-events-cli/pull/68))
* Bump jsonargparse from 4.42.0 to 4.52.0
* Bump rich-argparse from 1.7.2 to 1.8.0 ([#72](https://github.com/waldbaer/icalendar-events-cli/pull/72))
* Bump pydantic from 2.13.4 to 2.14.1 ([#70](https://github.com/waldbaer/icalendar-events-cli/pull/70))

## [2.0.1] - 2026-05-22

### Dependencies

* Bump icalendar from 7.0.3 to 7.1.2
* Bump recurring-ical-events from 3.8.1 to 3.8.2 ([#39](https://github.com/waldbaer/icalendar-events-cli/pull/58))
* Bump requests from 2.33.0 to 2.33.1 in ([#55](https://github.com/waldbaer/icalendar-events-cli/pull/55))
* Bump pydantic from 2.12.5 to 2.13.3 in ([#57](https://github.com/waldbaer/icalendar-events-cli/pull/57))

## [2.0.0] - 2026-03-14

### Breaking Changes

* Minimum python version increased from 3.9 to 3.10 ([#40](https://github.com/waldbaer/icalendar-events-cli/pull/40))
* `--calendar.encoding` not supported anymore. Encoding defaults to `UTF-8`.
  Caused by removed decoding functionality in icalendar 7.x ([#41](https://github.com/waldbaer/icalendar-events-cli/pull/41))

### Features

* Support [jCal](https://datatracker.ietf.org/doc/html/rfc7265) input format ([#50](https://github.com/waldbaer/icalendar-events-cli/pull/50))
* Support [jCal](https://datatracker.ietf.org/doc/html/rfc7265) output format (`--output.format jcal`) ([#42](https://github.com/waldbaer/icalendar-events-cli/pull/42))

### Dependencies

* Bump recurring-ical-events from 3.8.0 to 3.8.1 ([#39](https://github.com/waldbaer/icalendar-events-cli/pull/39))
* Bump pytz from 2025.2 to 2026.1.post1 ([#51](https://github.com/waldbaer/icalendar-events-cli/pull/51))

## [1.0.2] - 2025-11-01

### Dependencies

* Bump recurring-ical-events from 3.6.0 to 3.8.0
* Bump jsonargparse from 4.38.0 to 4.42.0
* Bump pydantic from 2.11.1 to 2.12.3
* Bump rich-argparse from 1.7.0 to 1.7.2
* Bump requests from 2.32.3 to 2.32.5

## [1.0.1] - 2025-04-02

### Dependencies
- Bump tzlocal from 5.2 to 5.3.1
- Bump pytz from 2024.2 to 2025.2
- Bump recurring-ical-events from 3.4.1 to 3.6.0
- Bump jsonargparse from 4.36.0 to 4.38.0
- Bump rich-argparse from 1.6.0 to 1.7.0
- Bump pydantic from 2.10.5 to 2.11.1

## [1.0.0] - 2025-01-25

### Features
- Filter events by description and location
- Support local file URLs (`file://<abs. path to local file>`)
- Support configuration via JSON (based on [jsonargparse](https://jsonargparse.readthedocs.io/))

### Infrastructure
- Rework to [hyper-modern structure](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/) with [python-pdm](https://pdm-project.org/)
- Implement tests (100% coverage)
- Publish to [PyPI](https://pypi.org/) index

### Fixes
- Invalid start- and end-date in [#7](https://github.com/waldbaer/icalendar-events-cli/pull/7)

### Dependencies
- Bump recurring-ical-events from 3.3.3 to 3.4.1 in [#4](https://github.com/waldbaer/icalendar-events-cli/pull/4)

## [0.1.0] - 2024-11-26

Initial Release

### Features
- Download and parse iCalendar files.
- Filter events with start- and end date.
- Filter events with RegEx on the summary (title) text.
- Different output formats: JSON, logger


# Changelog

All notable changes to this project will be documented in this file.


## [1.0.2] - 2025-11-01

### Dependencies
## What's Changed
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


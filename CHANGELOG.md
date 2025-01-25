# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-01-25

### Features
- Filter events by description and location
- Support local file URLs (`file://<abs. path to local file>`)
- Support configuration via JSON (based on [jsonargparse](https://jsonargparse.readthedocs.io/))

### Infrastructure
- Rework to [hyper-modern structure](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/) with [python-pdm](https://pdm-project.org/)
- Implement tests (100% coverage)
- Publish to [PyPI](https://pypi.org/) index


## [0.1.0] - 2024-11-26

Initial Release

### Features
- Download and parse iCalendar files in
- Filter events with start- and end date.
- Filter events with RegEx on the summary (title) text.
- Different output formats: JSON, logger

### Fixes
- Invalid start- and end-date in #7

### Dependencies
- Bump recurring-ical-events from 3.3.3 to 3.4.1 in #4

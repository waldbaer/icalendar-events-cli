[![PyPI version](https://badge.fury.io/py/icalendar-events-cli.svg)](https://badge.fury.io/py/icalendar-events-cli)
[![MIT License](https://img.shields.io/github/license/waldbaer/icalendar-events-cli?style=flat-square)](https://opensource.org/licenses/MIT)
[![GitHub issues open](https://img.shields.io/github/issues/waldbaer/icalendar-events-cli?style=flat-square)](https://github.com/waldbaer/icalendar-events-cli/issues)
[![GitHub Actions](https://github.com/waldbaer/icalendar-events-cli/actions/workflows/python-pdm.yml/badge.svg?branch=master)](https://github.com/waldbaer/icalendar-events-cli/actions/workflows/python-pdm.yml)


# Command-line tool to read icalendar events

## Introduction

This command-line tool allows users to query and filter [iCalendar (RFC 5545)](https://icalendar.org/RFC-Specifications/iCalendar-RFC-5545/) calendars. It leverages the excellent [recurring-ical-events](https://github.com/niccokunzmann/python-recurring-ical-events) library for parsing and querying the calendar contents.

Leveraging the powerful [jsonargparse](https://jsonargparse.readthedocs.io/) library, this tool supports configuration and control via command-line parameters or a JSON configuration file.

## Features ##
- Download and parse iCalendar files
  - from remote HTTP URL (`https://<path to icalendar server>`)
  - from local file URL (`file://<abs. path to local ICS file>`)
  - configurable encoding
- Filtering
  - by start- and end-date range
  - by event summary, description or location text (RegEx match)
- Different Outputs
  - Formats: JSON, human-readable (pretty printed)
  - Targets: shell (stdout), file

## Changelog
Changes can be followed at [CHANGELOG.md](https://github.com/waldbaer/icalendar-events-cli/blob/master/CHANGELOG.md).

## Requirements ##

 - [Python 3.9](https://www.python.org/)
 - [pip](https://pip.pypa.io/) or [pipx](https://pipx.pypa.io/stable/)

 For development:
 - [python-pdm (package dependency manager)](https://pdm-project.org/)

## Setup

### With pip / pipx
```
pip install icalendar-events-cli
pipx install icalendar-events-cli
```

### Setup directly from github repo / clone
```
git clone https://github.com/waldbaer/icalendar-events-cli.git
cd icalendar-events-cli

python -m venv .venv
source ./.venv/bin/activate
pip install .
```

## Usage

All parameters can be provided either as command-line arguments or through a JSON configuration file (default: `config.json`).
A combination of both methods is also supported.

A common approach is to define the calendar URL and HTTP authentication credentials in the JSON configuration file,
while specifying filters as command-line arguments.
Alternatively, you can define all credentials via command-line parameters or include the applied filters directly in the
JSON configuration file.

The results of all executed queries are returned in human-readable (pretty-printed) or
machine-readable JSON format.
This output can be displayed directly on the shell (stdout) or saved to a file.

The machine-readable JSON output format is designed for seamless integration with automation
platforms, such as [Node-RED](https://nodered.org/), which typically execute the
`icalendar-events-cli` tool.



### Examples

#### Example 1: Query Public Holiday Calendar

- Use human-readable output format
- Pass all parameters as command-line arguments

```
icalendar-events-cli --calendar.url https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics \
  --filter.start-date $(date +%Y)-01-01T02:00:00+02:00 \
  --filter.end-date $(date +%Y)-12-31T02:00:00+01:00 \
  --filter.summary ".*(Weihnacht|Oster).*"

Start Date:         2025-01-01T02:00:00+02:00
End Date:           2025-12-31T02:00:00+01:00
Summary Filter:     .*(Weihnacht|Oster).*
Number of Events:   3

2025-04-20T00:00:00+02:00 -> 2025-04-20T23:59:59+02:00 [86399 sec]     | Ostersonntag  (Brandenburg) | Description: Common local holiday -  Der Ostersonntag ist laut der christlichen Bibel ein Feiertag in Deutschland, um die Auferstehung Jesu Christi zu feiern.
2025-04-21T00:00:00+02:00 -> 2025-04-21T23:59:59+02:00 [86399 sec]     | Ostermontag  | Description: Christian -  Viele Menschen in Deutschland begehen jÃ¤hrlich den Ostermontag am Tag nach dem Ostersonntag. Es ist in allen Bundesstaaten ein Feiertag.
2025-12-25T00:00:00+01:00 -> 2025-12-25T23:59:59+01:00 [86399 sec]     | Weihnachten  | Description: Christian -  Der Weihnachtstag markiert die Geburt Jesu Christi und ist ein gesetzlicher Feiertag in Deutschland. Es ist jedes Jahr am 25. Dezember.
```

#### Example 2: Query School Vacation Calendar

The machine-readable JSON output format is designed for seamless integration with automation platforms, such as [Node-RED](https://nodered.org/), which typically execute the `icalendar-events-cli` tool.

- Use JSON output format++
- Mixed parameter configuration: Pass only end-date as command-line argument.

Create `school-summer-vacation.json` containing calendar URL, summary filter and output format settings:
```
{
  "calendar" : {
      "url" : "https://www.feiertage-deutschland.de/kalender-download/ics/schulferien-baden-wuerttemberg.ics",
      "verify_url": true
  },
  "filter": {
    "summary": "Sommer.*"
  },
  "output": {
    "format": "json"
  }
}
```

Query the calendar for summer vacation until end of next year:
```
icalendar-events-cli --config school-summer-vacation.json --filter.end-date $(($(date +%Y) + 1))-12-31T23:59:59

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


### All Available Parameters and Configuration Options

Details about all available options:

```
Usage: icalendar-events-cli [-h] [--version] [-c CONFIG] --calendar.url URL [--calendar.verify-url {true,false}] [--calendar.user USER]
                            [--calendar.password PASSWORD] [--calendar.encoding ENCODING] [-s START_DATE] [-e END_DATE] [-f SUMMARY]
                            [--filter.description DESCRIPTION] [--filter.location LOCATION] [--output.format {human_readable,json}] [-o FILE]

Command-line tool to read events from a iCalendar (ICS) files. | Version 1.0.2 | Copyright 2023-2025

Default Config File Locations:
  ['./config.json'], Note: no existing default config file found.

Options:
  -h, --help            Show this help message and exit.
  --version             Print version and exit.
  -c, --config CONFIG   Path to JSON configuration file.
  --calendar.url URL    URL of the iCalendar (ICS).
                        Also URLs to local files with schema file://<absolute path to local file> are supported. (required, type: None)
  --calendar.verify-url {true,false}
                        Configure SSL verification of the URL (type: None, default: True)
  --calendar.user USER  Username for calendar URL HTTP authentication (basic authentication) (type: None, default: None)
  --calendar.password PASSWORD
                        Password for calendar URL HTTP authentication (basic authentication) (type: None, default: None)
  --calendar.encoding ENCODING
                        Encoding of the calendar (default: UTF-8)
  -s, --filter.start-date START_DATE
                        Start date/time of event filter by time (ISO format). Default: now (type: datetime_isoformat, default: now)
  -e, --filter.end-date END_DATE
                        End date/time of event filter by time (ISO format). Default: end of today (type: datetime_isoformat, default: end of today)
  -f, --filter.summary SUMMARY
                        RegEx to filter calendar events based on the summary attribute. (type: regex_type, default: None)
  --filter.description DESCRIPTION
                        RegEx to filter calendar events based on the description attribute. (type: regex_type, default: None)
  --filter.location LOCATION
                        RegEx to filter calendar events based on the location attribute. (type: regex_type, default: None)
  --output.format {human_readable,json}
                        Output format. (type: None, default: human_readable)
  -o, --output.file FILE
                        Path of JSON output file. If not set the output is written to console / stdout (type: None, default: None)

```


## Development

### Setup environment

```
pdm install --dev
```

### Update dependencies to latest versions

```
pdm update --unconstrained --save-exact --no-sync
```

### Format / Linter / Tests

```
# Check code style
pdm run format

# Check linter
pdm run lint

# Run tests
pdm run tests
```

### Publish

```
# API token will be requested interactively as password
pdm publish -u __token__

# or to test.pypi.org
pdm publish --repository testpypi -u __token__
```

## Acknowledgments
Special thanks to [recurring-ical-events](https://github.com/niccokunzmann/python-recurring-ical-events) for providing
the core library that powers this tool.


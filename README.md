[![PyPI version](https://badge.fury.io/py/icalendar-events-cli.svg)](https://badge.fury.io/py/icalendar-events-cli)
[![MIT License](https://img.shields.io/github/license/waldbaer/icalendar-events-cli?style=flat-square)](https://opensource.org/licenses/MIT)
[![GitHub issues open](https://img.shields.io/github/issues/waldbaer/icalendar-events-cli?style=flat-square)](https://github.com/waldbaer/icalendar-events-cli/issues)
[![GitHub Actions](https://github.com/waldbaer/icalendar-events-cli/actions/workflows/python-pdm.yml/badge.svg?branch=master)](https://github.com/waldbaer/icalendar-events-cli/actions/workflows/python-pdm.yml)


# Command-line tool to read icalendar events

Command-line tool to read events from a iCalendar (ICS).

## Features ##
- Download and parse iCalendar files.
- Filter events with start- and end date.
- Filter events with RegEx on the summary (title) text.
- Different output formats: JSON, logger

## Changelog
Changes can be followed at [CHANGELOG.md](https://github.com/waldbaer/icalendar-events-cli/blob/master/CHANGELOG.md).

## Requirements ##

 - [Python 3.9](https://www.python.org/)
 - [pip](https://pip.pypa.io/) or [pipx](https://pipx.pypa.io/stable/)

 For development:
 - [python-pdm (package dependency manager)](https://pdm-project.org/)

## Setup

### Setup directly from github repo / clone
```
git clone git@github.com:waldbaer/icalendar-events-cli.git
cd icalendar-events-cli

python -m venv .venv
source ./.venv/bin/activate
pip install .
```

## Usage

For details about the command line arguments please refer to the online help.

```
Usage: icalendar-events-cli [-h] [--version] [-c CONFIG] [--calendar.url URL] [--calendar.verify-url {true,false}]
                            [--calendar.user USER] [--calendar.password PASSWORD] [--calendar.encoding ENCODING] [-f SUMMARY]
                            [-s START_DATE] [-e END_DATE] [--output.format {human_readable,json}] [-o FILE]

Command-line tool to read events from a iCalendar (ICS) files. | Version 1.0.0 | Copyright 2023-2025

Default Config File Locations:
  ['./config.json'], Note: default values below are the ones overridden by the contents of: ./config.json

Options:
  -h, --help            Show this help message and exit.
  --version             Print version and exit.
  -c, --config CONFIG   Path to JSON configuration file.
  --calendar.url URL    URL of the iCalendar (ICS).
                        Also URLs to local files with schema file://<absolute path to local file> are supported. (type: None, default: None)
  --calendar.verify-url {true,false}
                        Configure SSL verification of the URL (type: None, default: True)
  --calendar.user USER  Username for calendar URL HTTP authentication (basic authentication) (type: None, default: None)
  --calendar.password PASSWORD
                        Password for calendar URL HTTP authentication (basic authentication) (type: None, default: None)
  --calendar.encoding ENCODING
                        Encoding of the calendar (default: UTF-8)
  -f, --filter.summary SUMMARY
                        RegEx to filter calendar events based on summary field. (default: .*)
  -s, --filter.start-date START_DATE
                        Start date/time of event filter by time (ISO format). Default: now (type: _datetime_fromisoformat, default: 2025-01-21 21:29:13+01:00)
  -e, --filter.end-date END_DATE
                        End date/time of event filter by time (ISO format). Default: end of today (type: _datetime_fromisoformat, default: 2025-01-21 23:59:59+01:00)
  --output.format {human_readable,json}
                        Output format. (type: None, default: human_readable)
  -o, --output.file FILE
                        Path of JSON output file. If not set the output is written to console / stdout (type: None, default: None)

```

### Examples

#### Example 1: Output via logger

```
icalendar-events-cli --url https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics \
  --filter.start-date $(date +%Y)-01-01T02:00:00+02:00 \
  --filter.end-date $(date +%Y)-12-31T02:00:00+01:00 \
  -f ".*(Weihnacht|Oster).*"
Start Date:       2025-01-01T02:00:00+02:00
End Date:         2025-12-31T02:00:00+01:00
Summary Filter:   .*(Weihnacht|Oster).*
Number of Events: 3
2025-04-20T00:00:00+02:00 -> 2025-04-20T23:59:59+02:00 [86399 sec]     | Ostersonntag  (Brandenburg) | Description: Common local holiday -  Der Ostersonntag ist laut der christlichen Bibel ein Feiertag in Deutschland, um die Auferstehung Jesu Christi zu feiern.
2025-04-21T00:00:00+02:00 -> 2025-04-21T23:59:59+02:00 [86399 sec]     | Ostermontag  | Description: Christian -  Viele Menschen in Deutschland begehen jÃ¤hrlich den Ostermontag am Tag nach dem Ostersonntag. Es ist in allen Bundesstaaten ein Feiertag.
2025-12-25T00:00:00+01:00 -> 2025-12-25T23:59:59+01:00 [86399 sec]     | Weihnachten  | Description: Christian -  Der Weihnachtstag markiert die Geburt Jesu Christi und ist ein gesetzlicher Feiertag in Deutschland. Es ist jedes Jahr am 25. Dezember.
```

#### Example 1: Output as JSON

The machine-readable JSON output format is designed for seamless integration with automation platforms, such as [Node-RED](https://nodered.org/), which typically execute the `icalendar-events-cli` tool.

```
icalendar-events-cli --url https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics \
  --filter.start-date $(date +%Y)-01-01T02:00:00+02:00 \
  --filter.end-date $(date +%Y)-12-31T02:00:00+01:00 \
  -f ".*Pfingst.*" --output.format json
{
  "start-date": "2025-01-01T02:00:00+02:00",
  "end-date": "2025-12-31T02:00:00+01:00",
  "summary-filter": ".*Pfingst.*",
  "events": [
    {
      "start-date": "2025-06-08T00:00:00+02:00",
      "end-date": "2025-06-09T23:59:59+02:00",
      "summary": "Pfingstsonntag  (Brandenburg)",
      "description": "Common local holiday -  Pfingsten ist ein christlicher Feiertag, um an die Herabkunft des Heiligen Geistes auf die Nachfolger Jesu zu erinnern."
    },
    {
      "start-date": "2025-06-09T00:00:00+02:00",
      "end-date": "2025-06-10T23:59:59+02:00",
      "summary": "Pfingstmontag ",
      "description": "Christian -  Der zweite Pfingsttag ist, der auf den Montag nach Pfingsten (oder Pfingstsonntag) fällt, ist ein gesetzlicher Feiertag in Deutschland."
    }
  ]
}
```

## Acknowledgments
Special thanks to [recurring-ical-events](https://github.com/niccokunzmann/python-recurring-ical-events) for providing
the core library that powers this tool.


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
usage: icalendar-events-cli [-h] [--version] [--verbose] -u URL [-b BASICAUTH] [-f SUMMARYFILTER] [-s STARTDATE] -e ENDDATE [-o {logger,json}] [-c ENCODING]

Command-line tool to read events from a iCalendar (ICS).

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --verbose, -v         Increase log-level. -v: INFO, -vv DEBUG, ... Default: WARNING
  -u, --url URL         icalendar URL to be parsed.
  -b, --basicAuth BASICAUTH
                        Basic authentication for URL in format "<user>:<password>".
  -f, --summaryFilter SUMMARYFILTER
                        RegEx to filter calendar events based on summary field.
  -s, --startDate STARTDATE
                        Start date/time of event filter by time (ISO format). Default: now
  -e, --endDate ENDDATE
                        End date/time of event filter by time (ISO format).
  -o, --outputFormat {logger,json}
                        Output format.
  -c, --encoding ENCODING
                        Encoding of the calendar. Default: UTF-8
```

### Examples

#### Example 1: Output via logger

```
icalendar-events-cli --url https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics \
  --startDate $(date +%Y)-01-01T02:00:00+02:00 \
  --endDate $(date +%Y)-12-31T02:00:00+01:00 \
  -f ".*(Weihnacht|Oster).*" -vv
2025-01-19 20:10:40 DEBUG: Starting new HTTPS connection (1): www.thunderbird.net:443
2025-01-19 20:10:40 DEBUG: https://www.thunderbird.net:443 "GET /media/caldata/autogen/GermanHolidays.ics HTTP/1.1" 200 26910
2025-01-19 20:10:40 DEBUG: Get calendar events between 2025-01-01 02:00:00 and 2025-12-31 02:00:00...
2025-01-19 20:10:40 INFO: Start Date:       2025-01-01T02:00:00+02:00
2025-01-19 20:10:40 INFO: End Date:         2025-12-31T02:00:00+01:00
2025-01-19 20:10:40 INFO: Summary Filter:   .*(Weihnacht|Oster).*
2025-01-19 20:10:40 INFO: Number of Events: 3
2025-01-19 20:10:40 INFO: 2025-04-20T00:00:00+02:00 -> 2025-04-21T23:59:59+02:00 [172799 sec]    | Ostersonntag  (Brandenburg) | Description: Common local holiday -  Der Ostersonntag ist laut der christlichen Bibel ein Feiertag in Deutschland, um die Auferstehung Jesu Christi zu feiern.
2025-01-19 20:10:40 INFO: 2025-04-21T00:00:00+02:00 -> 2025-04-22T23:59:59+02:00 [172799 sec]    | Ostermontag  | Description: Christian -  Viele Menschen in Deutschland begehen jÃ¤hrlich den Ostermontag am Tag nach dem Ostersonntag. Es ist in allen Bundesstaaten ein Feiertag.
2025-01-19 20:10:40 INFO: 2025-12-25T00:00:00+01:00 -> 2025-12-26T23:59:59+01:00 [172799 sec]    | Weihnachten  | Description: Christian -  Der Weihnachtstag markiert die Geburt Jesu Christi und ist ein gesetzlicher Feiertag in Deutschland. Es ist jedes Jahr am 25. Dezember.
```

#### Example 1: Output as JSON

The machine-readable JSON output format is designed for seamless integration with automation platforms, such as [Node-RED](https://nodered.org/), which typically execute the `icalendar-events-cli` tool.

```
icalendar-events-cli --url https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics \
  --startDate $(date +%Y)-01-01T02:00:00+02:00 \
  --endDate $(date +%Y)-12-31T02:00:00+01:00 \
  -f ".*Pfingst.*" --outputFormat json
{
  "startDate": "2025-01-01T02:00:00+02:00",
  "endDate": "2025-12-31T02:00:00+01:00",
  "summaryFilter": ".*Pfingst.*",
  "events": [
    {
      "startDate": "2025-06-08T00:00:00+02:00",
      "endDate": "2025-06-09T23:59:59+02:00",
      "summary": "Pfingstsonntag  (Brandenburg)",
      "description": "Common local holiday -  Pfingsten ist ein christlicher Feiertag, um an die Herabkunft des Heiligen Geistes auf die Nachfolger Jesu zu erinnern."
    },
    {
      "startDate": "2025-06-09T00:00:00+02:00",
      "endDate": "2025-06-10T23:59:59+02:00",
      "summary": "Pfingstmontag ",
      "description": "Christian -  Der zweite Pfingsttag ist, der auf den Montag nach Pfingsten (oder Pfingstsonntag) fällt, ist ein gesetzlicher Feiertag in Deutschland."
    }
  ]
}
```

## Acknowledgments
Special thanks to [recurring-ical-events](https://github.com/niccokunzmann/python-recurring-ical-events) for providing
the core library that powers this tool.


[![MIT License](https://img.shields.io/github/license/waldbaer/icalendar-events-cli?style=flat-square)](https://opensource.org/licenses/MIT)
[![GitHub issues open](https://img.shields.io/github/issues/waldbaer/icalendar-events-cli?style=flat-square)](https://github.com/waldbaer/icalendar-events-cli/issues)


# Command-line tool to read icalendar events

Command-line tool to read events from a iCalendar (ICS).

## Requirements ##
 - [Python 3](https://www.python.org/)
 - [virtualenv](https://virtualenv.readthedocs.org)
 - [pip (package manager)](https://pip.pypa.io/)
 - [recurring-ical-events](https://github.com/niccokunzmann/python-recurring-ical-events)
 - [urllib3](https://urllib3.readthedocs.io)
 - [tzlocal](https://github.com/regebro/tzlocal)

## Setup
```
# Setup virtualenv
python3 -m venv virtualenv
source ./virtualenv/bin/activate
# or
./setup-venv.h
source ./virtualenv/bin/activate
```

## Key features ##
- Download and parse iCalendar files.
- Filter events with start- and end date.
- Filter events with RegEx on the summary (title) text.
- Different output formats: JSON, logger

## Usage

For details about the command line arguments please refer to the online help.

```
./icalendar-events-cli.py --help
```

### Output via logger
```
$> ./icalendar-events-cli.py --url https://www.thunderbird.net/media/caldata/autogen/Germany-Holidays.ics --startDate
 2023-01-01T02:00:00+02:00 --endDate 2023-12-31T02:00:00+01:00 -f ".*(Weihnacht|Oster).*" -vv
2023-07-28 21:14:48 DEBUG: Starting new HTTPS connection (1): www.thunderbird.net:443
2023-07-28 21:14:48 DEBUG: https://www.thunderbird.net:443 "GET /media/caldata/autogen/Germany-Holidays.ics HTTP/1.1" 200 0
2023-07-28 21:14:48 DEBUG: Get calendar events between 2023-01-01 02:00:00 and 2023-12-31 02:00:00...
2023-07-28 21:14:48 INFO: Start Date:       2023-01-01T02:00:00+02:00
2023-07-28 21:14:48 INFO: End Date:         2023-12-31T02:00:00+01:00
2023-07-28 21:14:48 INFO: Summary Filter:   .*(Weihnacht|Oster).*
2023-07-28 21:14:48 INFO: Number of Events: 5
2023-07-28 21:14:48 INFO: 2023-04-09T00:00:00+02:00 -> 2023-04-10T23:59:59+02:00 [172799 sec]    | Ostern (All except BB)
2023-07-28 21:14:48 INFO: 2023-04-09T00:00:00+02:00 -> 2023-04-10T23:59:59+02:00 [172799 sec]    | Ostern (Brandenburg)
2023-07-28 21:14:48 INFO: 2023-04-10T00:00:00+02:00 -> 2023-04-11T23:59:59+02:00 [172799 sec]    | Ostermontag
2023-07-28 21:14:48 INFO: 2023-12-25T00:00:00+01:00 -> 2023-12-26T23:59:59+01:00 [172799 sec]    | Erster Weihnachtstag
2023-07-28 21:14:48 INFO: 2023-12-26T00:00:00+01:00 -> 2023-12-27T23:59:59+01:00 [172799 sec]    | Zweiter Weihnachtstag

```

### Output as JSON

Useful for further processing
```
./icalendar-events-cli.py --url https://www.thunderbird.net/media/caldata/autogen/Germany-Holidays.ics --startDate 2023-01-01T02:00:00+02:00 --endDate 2023-12-31T02:00:00+01:00 -f ".*Sommer.*" --outputFormat json
{
  "startDate": "2023-01-01T02:00:00+02:00",
  "endDate": "2023-12-31T02:00:00+01:00",
  "summaryFilter": ".*Sommer.*",
  "events": [
    {
      "start:": "2023-03-26T00:00:00+01:00",
      "end": "2023-03-27T23:59:59+02:00",
      "summary": "Beginn der Sommerzeit"
    },
    {
      "start:": "2023-10-29T00:00:00+02:00",
      "end": "2023-10-30T23:59:59+01:00",
      "summary": "Ende der Sommerzeit"
    }
  ]
}
```
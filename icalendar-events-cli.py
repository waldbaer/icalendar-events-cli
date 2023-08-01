#!/usr/bin/env python3

# ---- Imports --------------------------------------------------------------------------------------------------------
import sys
import traceback
import argparse
import logging
from enum import Enum

import icalendar
# https://github.com/niccokunzmann/python-recurring-ical-events
import recurring_ical_events
# https://urllib3.readthedocs.io/en/stable/user-guide.html
import urllib3

import datetime
from tzlocal import get_localzone
import pytz

import re
import json


# ---- Main -----------------------------------------------------------------------------------------------------------
__author__ = "Sebastian Waldvogel"
__copyright__ = "Copyright 2023-2022, Sebastian Waldvogel"
__license__ = "MIT"
__version__ = '1.0.0'

__local_timezone = pytz.timezone(get_localzone().key)

class OutputFormat(Enum):
  LOGGER = 'logger' # Logger
  JSON = 'json' # JSON hierarchy

  def __str__(self):
      return self.value

def main():
  args = ParseCommandLineArguments()
  ConfigureLogging(args)

  calendar_ics = DownloadIcs(args)
  events = ParseCalendar(args, calendar_ics)
  events = FilterEvents(args, events)
  events = SortEvents(args, events)
  OutputEvents(args, events)

def ConfigureLogging(args):
  args.verbose = 40 - (10 * args.verbose) if args.verbose > 0 else 0
  if(args.outputFormat == OutputFormat.LOGGER):
    # Enforce INFO level if output format LOGGER is selected.
    # https://docs.python.org/3/library/logging.html#levels
    args.verbose = 20 if args.verbose > 20 else args.verbose
  logging.basicConfig(level=args.verbose,
                      format='%(asctime)s %(levelname)s: %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')

def ParseCommandLineArguments():
  # Parse command line arguments
  argparser = argparse.ArgumentParser(description='icalendar events cli tool')

  argparser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
  argparser.add_argument('--verbose', '-v', action='count', default=1, help='Increase log-level. -v: INFO, -vv DEBUG, ... Default: WARNING')
  argparser.add_argument('-u', '--url', dest='url', required=True, help='icalendar URL to be parsed.')
  argparser.add_argument('-b', '--basicAuth', dest='basicAuth', help='Basic authentication for URL in format "<user>:<password>".')
  argparser.add_argument('-f', '--summaryFilter', dest='summaryFilter', help='RegEx to filter calendar events based on summary field.')
  argparser.add_argument('-s', '--startDate', type=datetime.datetime.fromisoformat, help='Start date/time of event filter by time (ISO format). Default: now',
                         default=__local_timezone.localize(datetime.datetime.now()).replace(microsecond=0))
  argparser.add_argument('-e', '--endDate', type=datetime.datetime.fromisoformat, required=True, help='End date/time of event filter by time (ISO format).')
  argparser.add_argument('-o', '--outputFormat', default=OutputFormat.LOGGER, type=OutputFormat, choices=list(OutputFormat), help='Output format.')
  argparser.add_argument('-c', '--encoding', dest='encoding', default='UTF-8', help='Encoding of the calendar. Default: UTF-8')

  return argparser.parse_args()

def DownloadIcs(args):
  headers = None
  if(args.basicAuth != None):
    headers = urllib3.make_headers(basic_auth=args.basicAuth)

  resp = urllib3.request("GET", args.url, headers=headers)
  if(resp.status != 200):
    logging.error(f"Failed to download ical contents from URL '{resp.url}'. Response status: {resp.reason} (status {resp.status})")
    sys.exit(1)
  return resp.data

def ParseCalendar(args, calendar_ics):
  calendar = icalendar.Calendar.from_ical(calendar_ics)
  logging.debug(f'Get calendar events between {args.startDate.strftime("%Y-%m-%d %H:%M:%S")} and {args.endDate.strftime("%Y-%m-%d %H:%M:%S")}...')
  calendar_components = ["VEVENT"] # Only events
  return recurring_ical_events.of(calendar, components=calendar_components).between(args.startDate, args.endDate)

def FilterEvents(args, events):
  if(args.summaryFilter != None):
    return filter(lambda event: re.match(args.summaryFilter, event.decoded('SUMMARY').decode(args.encoding)) != None, events)
  else:
    return events

def SortEvents(args, events):
  return sorted(events, key=GetEventDtStart, reverse=False)

def OutputEvents(args, events):
  if(args.outputFormat == OutputFormat.JSON):
    events_output = []
    for event in events:
      event_output = {"startDate": GetEventDtStart(event).isoformat(),
                      "endDate": GetEventDtEnd(event).isoformat(),
                      "summary": GetEventSummary(args, event)}
      description = GetEventDescription(args, event)
      if(description != None): event_output["description"] = description

      location = GetEventLocation(args, event)
      if(location != None): event_output["location"] = location
      events_output.append(event_output)

    json_hierarchy = {
      "startDate": args.startDate.isoformat(),
      "endDate": args.endDate.isoformat(),
      "summaryFilter" : args.summaryFilter,
      "events": events_output
      }
    json_string = json.dumps(json_hierarchy, indent = 2, ensure_ascii=False)
    print(json_string)
  elif (args.outputFormat == OutputFormat.LOGGER):
    logging.info(f"Start Date:       {args.startDate.isoformat()}")
    logging.info(f"End Date:         {args.endDate.isoformat()}")
    logging.info(f"Summary Filter:   {args.summaryFilter}")
    logging.info(f"Number of Events: {len(events)}")

    for event in events:
      start = GetEventDtStart(event)
      end = GetEventDtEnd(event)
      summary = GetEventSummary(args, event)
      description = GetEventDescription(args, event)
      location = GetEventLocation(args, event)

      duration = end - start
      start_end_string = f"{start.isoformat()} -> {end.isoformat()} [{duration.total_seconds():.0f} sec]"
      opt_description_string = f" | Description: {description}" if description != None else ""
      opt_location_string = f" | Location: {description}" if location != None else ""

      logging.info(f"{start_end_string : <70} | {summary}{opt_description_string}{opt_location_string}")

# ---- icalender access utilities ----
def GetEventStringAttribute(args, event, attribute_name):
  attribute = event.decoded(attribute_name, default=None)
  if(attribute != None):
    attribute = attribute.decode(args.encoding)
  return attribute

def GetEventSummary(args, event):
  return GetEventStringAttribute(args, event, 'SUMMARY')

def GetEventDescription(args, event):
  return GetEventStringAttribute(args, event, 'DESCRIPTION')

def GetEventLocation(args, event):
  return GetEventStringAttribute(args, event, 'LOCATION')

def GetEventDtStart(event):
  start = event.decoded('DTSTART')
  if(type(start) == datetime.date):
    # Convert full-day event to datetime
    start = datetime.datetime.combine(start, datetime.datetime.min.time())
    start = __local_timezone.localize(start)
  return start

def GetEventDtEnd(event):
  end = event.decoded('DTEND')
  if(type(end) == datetime.date):
    # Convert full-day event to datetime
    end = datetime.datetime.combine(end, datetime.datetime.max.time()).replace(microsecond=0)
    end = __local_timezone.localize(end)
  return end


# ---- Entrypoint -----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
  try:
    main()
  except SystemExit:
    sys.exit(1)
  except BaseException:
    print("ERROR: Any error has occured! Traceback:\r\n" + traceback.format_exc())
    sys.exit(1)
  sys.exit(0)

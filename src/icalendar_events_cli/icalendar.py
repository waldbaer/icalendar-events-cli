"""Access to icalendar objects and hierarchies."""

# ---- Imports ---------------------------------------------------------------------------------------------------------
import datetime
import logging
import re

import icalendar
import pytz
import recurring_ical_events
from icalendar.cal import Event

# https://urllib3.readthedocs.io/en/stable/user-guide.html
from recurring_ical_events import CalendarQuery
from tzlocal import get_localzone

# ---- Globals ---------------------------------------------------------------------------------------------------------
__local_timezone = pytz.timezone(get_localzone().key)


# ---- Functions -------------------------------------------------------------------------------------------------------


def parse_calendar(args: dict, calendar_ics: str) -> CalendarQuery:
    """Parse the calendar.

    Arguments:
        args: Configuration hierarchy.
        calendar_ics: Calendar RAW content string.

    Returns:
        CalendarQuery: Parsed CalendarQuery.
    """
    calendar = icalendar.Calendar.from_ical(calendar_ics)
    logging.debug(
        "Get calendar events between %s and %s...",
        args.startDate.strftime("%Y-%m-%d %H:%M:%S"),
        args.endDate.strftime("%Y-%m-%d %H:%M:%S"),
    )
    calendar_components = ["VEVENT"]  # Only events
    return recurring_ical_events.of(calendar, components=calendar_components).between(args.startDate, args.endDate)


def filter_events(events: CalendarQuery, summary_filter: str, encoding: str) -> CalendarQuery:
    """Filter the calendar.

    Arguments:
        events: Calendar to be filtered.
        summary_filter: Events summary filter expression (RegEx)
        encoding: Summary attribute encoding

    Returns:
        CalendarQuery: Filtered calendar.
    """
    return filter(
        lambda event: re.match(summary_filter, event.decoded("SUMMARY").decode(encoding)) is not None,
        events,
    )


def get_event_string_attribute(args: dict, event: Event, attribute_name: str) -> str:
    """Get any string attribute from event.

    Arguments:
        args: Configuration hierarchy including the encoding settings.
        event: Calendar Event.
        attribute_name: Attribute name to be accessed.

    Returns:
        Decoded attribute value.
    """
    attribute = event.decoded(attribute_name, default=None)
    if attribute is not None:
        attribute = attribute.decode(args.encoding)
    return attribute


def get_event_summary(args: dict, event: Event) -> str:
    """Get 'SUMMARY' attribute of calendar event.

    Arguments:
        args: Configuration hierarchy including the output settings.
        event: Calendar Event.

    Returns:
        Summary attribute.
    """
    return get_event_string_attribute(args, event, "SUMMARY")


def get_event_description(args: dict, event: Event) -> str:
    """Get 'DESCRIPTION' attribute of calendar event.

    Arguments:
        args: Configuration hierarchy including the output settings.
        event: Calendar Event.

    Returns:
        Description attribute.
    """
    return get_event_string_attribute(args, event, "DESCRIPTION")


def get_event_location(args: dict, event: Event) -> str:
    """Get 'LOCATION' attribute of calendar event.

    Arguments:
        args: Configuration hierarchy including the output settings.
        event: Calendar Event.

    Returns:
        Location attribute.
    """
    return get_event_string_attribute(args, event, "LOCATION")


def get_event_dtstart(event: Event) -> datetime.date:
    """Get 'DTSTART' start-date of calendar event.

    Arguments:
        event: Calendar Event.

    Returns:
        Start Date.
    """
    start = event.decoded("DTSTART")
    if isinstance(start, datetime.date):
        # Convert full-day event to datetime
        start = datetime.datetime.combine(start, datetime.datetime.min.time())
        start = __local_timezone.localize(start)
    return start


def get_event_dtend(event: Event) -> datetime.date:
    """Get 'DTEND' end-date of calendar event.

    Arguments:
        event: Calendar Event.

    Returns:
        End Date.
    """
    end = event.decoded("DTEND")
    if isinstance(end, datetime.date):
        # Convert full-day event to datetime
        end = datetime.datetime.combine(end, datetime.datetime.max.time()).replace(microsecond=0)
        end = __local_timezone.localize(end)
    return end

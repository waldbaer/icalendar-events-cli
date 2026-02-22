"""Access to icalendar objects and hierarchies."""

# ---- Imports ---------------------------------------------------------------------------------------------------------
import re
from datetime import date, datetime, timedelta

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


def parse_calendar(calendar_ics: str, filter_config: dict) -> CalendarQuery:
    """Parse the calendar.

    Arguments:
        calendar_ics: Calendar RAW content string.
        filter_config: Filter configuration hierarchy.

    Returns:
        CalendarQuery: Parsed CalendarQuery.
    """
    calendar = icalendar.Calendar.from_ical(calendar_ics)
    calendar_components = ["VEVENT"]  # Only events
    return recurring_ical_events.of(calendar, components=calendar_components).between(
        filter_config.start_date, filter_config.end_date
    )


def filter_events(events: CalendarQuery, filter_config: dict) -> CalendarQuery:
    """Filter the calendar.

    Arguments:
        events: Calendar to be filtered.
        filter_config: Filter config hierarchy

    Returns:
        CalendarQuery: Filtered calendar.
    """
    if filter_config.summary is not None:
        events = filter(
            lambda event: (
                (summary := get_event_summary(event)) is not None
                and re.match(filter_config.summary, summary) is not None
            ),
            events,
        )

    if filter_config.description is not None:
        events = filter(
            lambda event: (
                (description := get_event_description(event)) is not None
                and re.match(filter_config.description, description) is not None
            ),
            events,
        )

    if filter_config.location is not None:
        events = filter(
            lambda event: (
                (location := get_event_location(event)) is not None
                and re.match(filter_config.location, location) is not None
            ),
            events,
        )

    return events


def get_event_summary(event: Event) -> str:
    """Get 'SUMMARY' attribute of calendar event.

    Arguments:
        event: Calendar Event.

    Returns:
        Summary attribute.
    """
    return event.decoded("SUMMARY", default=None)


def get_event_description(event: Event) -> str:
    """Get 'DESCRIPTION' attribute of calendar event.

    Arguments:
        event: Calendar Event.

    Returns:
        Description attribute.
    """
    return event.decoded("DESCRIPTION", default=None)


def get_event_location(event: Event) -> str:
    """Get 'LOCATION' attribute of calendar event.

    Arguments:
        event: Calendar Event.

    Returns:
        Location attribute.
    """
    return event.decoded("LOCATION", default=None)


def get_event_dtstart(event: Event) -> date:
    """Get 'DTSTART' start-date of calendar event.

    Arguments:
        event: Calendar Event.

    Returns:
        Start Date.
    """
    start = event.decoded("DTSTART")
    if isinstance(start, date) and not isinstance(start, datetime):
        # Convert full-day event to datetime
        start = datetime.combine(start, datetime.min.time())
        start = __local_timezone.localize(start)
    return start


def get_event_dtend(event: Event) -> date:
    """Get 'DTEND' end-date of calendar event.

    Arguments:
        event: Calendar Event.

    Returns:
        End Date.
    """
    end = event.decoded("DTEND")
    if end.resolution == timedelta(days=1):
        # For full-day events the DTEND is always one day after DTSTART.
        # Therefore subtract 1 day and then set time to end of day
        end -= timedelta(days=1)
        end = datetime.combine(end, datetime.max.time()).replace(microsecond=0)
        end = __local_timezone.localize(end)
    return end

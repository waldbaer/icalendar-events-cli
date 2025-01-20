"""Handling of different output formats."""

# ---- Imports ---------------------------------------------------------------------------------------------------------
import json
from enum import Enum

from recurring_ical_events import CalendarQuery

from .icalendar import get_event_description, get_event_dtend, get_event_dtstart, get_event_location, get_event_summary

# ---- Functions -------------------------------------------------------------------------------------------------------


class OutputFormat(Enum):
    """All possible output formats."""

    LOGGER = "logger"  # Logger
    JSON = "json"  # JSON hierarchy

    def __str__(self) -> str:
        """Convert enum into string representation.

        Returns:
            Str: String representation of the enum value.
        """
        return self.value


def output_events(args: dict, events: CalendarQuery) -> None:
    """Output the calendar.

    Arguments:
        args: Configuration hierarchy including the output settings.
        events: Calendar events.
    """
    sorted_events = _sort_events(events)

    if args.outputFormat == OutputFormat.JSON:
        output_json(args, sorted_events)
    elif args.outputFormat == OutputFormat.LOGGER:
        output_logger(args, sorted_events)


def output_json(args: dict, events: CalendarQuery) -> None:
    """Output the events in JSON format.

    Arguments:
        args: Configuration hierarchy including the output settings.
        events: Calendar events.
    """
    events_output = []
    for event in events:
        event_output = {
            "startDate": get_event_dtstart(event).isoformat(),
            "endDate": get_event_dtend(event).isoformat(),
            "summary": get_event_summary(args, event),
        }
        description = get_event_description(args, event)
        if description is not None:
            event_output["description"] = description

        location = get_event_location(args, event)
        if location is not None:
            event_output["location"] = location
        events_output.append(event_output)

    json_hierarchy = {
        "startDate": args.startDate.isoformat(),
        "endDate": args.endDate.isoformat(),
        "summaryFilter": args.summaryFilter,
        "events": events_output,
    }
    json_string = json.dumps(json_hierarchy, indent=2, ensure_ascii=False)
    print(json_string)


def output_logger(args: dict, events: CalendarQuery) -> None:
    """Output the events in human readble format to the logger.

    Arguments:
        args: Configuration hierarchy including the output settings.
        events: Calendar events.
    """
    print(f"Start Date:       {args.startDate.isoformat()}")
    print(f"End Date:         {args.endDate.isoformat()}")
    print(f"Summary Filter:   {args.summaryFilter}")
    print(f"Number of Events: {len(events)}")

    for event in events:
        start = get_event_dtstart(event)
        end = get_event_dtend(event)
        summary = get_event_summary(args, event)
        description = get_event_description(args, event)
        location = get_event_location(args, event)

        duration = end - start
        start_end_string = f"{start.isoformat()} -> {end.isoformat()} [{duration.total_seconds():.0f} sec]"
        opt_description_string = f" | Description: {description}" if description is not None else ""
        opt_location_string = f" | Location: {description}" if location is not None else ""

        print(f"{start_end_string: <70} | {summary}{opt_description_string}{opt_location_string}")


def _sort_events(events: CalendarQuery) -> CalendarQuery:
    """Sort calendar.

    Arguments:
       events: Calendar to be sorted.

    Returns:
        CalendarQuery: Sorted calendar.
    """
    return sorted(events, key=get_event_dtstart, reverse=False)

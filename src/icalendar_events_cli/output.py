"""Handling of different output target and formats."""

# ---- Imports ---------------------------------------------------------------------------------------------------------
import json
import os
import sys
from enum import Enum

from recurring_ical_events import CalendarQuery

from .icalendar import get_event_description, get_event_dtend, get_event_dtstart, get_event_location, get_event_summary

# ---- Functions -------------------------------------------------------------------------------------------------------


class OutputFormat(Enum):
    """All possible output formats."""

    human_readable = "human_readable"  # pylint: disable=invalid-name;reason=camel_case style wanted for cli param
    json = "json"  # pylint: disable=invalid-name;reason=camel_case style wanted for cli param


def output_events(events: CalendarQuery, config: dict) -> None:
    """Output the calendar.

    Arguments:
        events: Calendar events.
        config: Configuration hierarchy.
    """
    sorted_events = _sort_events(events)

    if config.output.format == OutputFormat.json:
        output_json(sorted_events, config)
    else:
        output_human_readable(sorted_events, config)


def output_json(events: CalendarQuery, config: dict) -> None:
    """Output the events in JSON format.

    Arguments:
        events: Calendar events.
        config: Configuration hierarchy.
    """
    filters = {"start-date": config.filter.start_date.isoformat(), "end-date": config.filter.end_date.isoformat()}
    if config.filter.summary:
        filters["summary"] = config.filter.summary
    if config.filter.description:
        filters["description"] = config.filter.description
    if config.filter.location:
        filters["location"] = config.filter.location

    # Detailed Events List
    events_output = []
    for event in events:
        event_output = {
            "start-date": get_event_dtstart(event).isoformat(),
            "end-date": get_event_dtend(event).isoformat(),
            "summary": get_event_summary(event, config.calendar.encoding),
        }
        description = get_event_description(event, config.calendar.encoding)
        if description is not None:
            event_output["description"] = description

        location = get_event_location(event, config.calendar.encoding)
        if location is not None:
            event_output["location"] = location
        events_output.append(event_output)

    json_hierarchy = {"filter": filters, "events": events_output}

    # Finally output the JSON hierarchy to stdout or the configured file
    if config.output.file is None:
        json.dump(json_hierarchy, fp=sys.stdout, indent=2, ensure_ascii=False)
    else:
        with open(config.output.file, "w", encoding="utf-8") as file:
            json.dump(json_hierarchy, fp=file, indent=2, ensure_ascii=False)


def output_human_readable(events: CalendarQuery, config: dict) -> None:
    """Output the events in human readable format.

    Arguments:
        events: Calendar events.
        config: Configuration hierarchy.
    """
    output = []

    output.append(f"Start Date:         {config.filter.start_date.isoformat()}")
    output.append(f"End Date:           {config.filter.end_date.isoformat()}")
    if config.filter.summary:
        output.append(f"Summary Filter:     {config.filter.summary}")
    if config.filter.description:
        output.append(f"Description Filter: {config.filter.description}")
    if config.filter.location:
        output.append(f"Location Filter:    {config.filter.location}")
    output.append(f"Number of Events:   {len(events)}{os.linesep}")

    for event in events:
        start = get_event_dtstart(event)
        end = get_event_dtend(event)
        summary = get_event_summary(event, config.calendar.encoding)
        description = get_event_description(event, config.calendar.encoding)
        location = get_event_location(event, config.calendar.encoding)

        duration = end - start
        start_end_string = f"{start.isoformat()} -> {end.isoformat()} [{duration.total_seconds():.0f} sec]"
        opt_description_string = f" | Description: {description}" if description is not None else ""
        opt_location_string = f" | Location: {description}" if location is not None else ""

        output.append(f"{start_end_string: <70} | {summary}{opt_description_string}{opt_location_string}")

    # build final output string incl. line separators
    output = os.linesep.join(output)

    # Finally output to stdout or the configured file
    if config.output.file is None:
        print(output)
    else:
        with open(config.output.file, "w", encoding="utf-8") as file:
            file.write(output)


def _sort_events(events: CalendarQuery) -> CalendarQuery:
    """Sort calendar.

    Arguments:
       events: Calendar to be sorted.

    Returns:
        CalendarQuery: Sorted calendar.
    """
    return sorted(events, key=get_event_dtstart, reverse=False)

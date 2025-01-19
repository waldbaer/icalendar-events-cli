"""Argument parsing."""

# ---- Imports ----
import argparse
import datetime

import pytz
from tzlocal import get_localzone

from .output import OutputFormat

# ---- Constants & Types -----------------------------------------------------------------------------------------------


# ---- CommandLine parser ----------------------------------------------------------------------------------------------


def parse_config(prog: str, version: str, copy_right: str, author: str, arg_list: list[str] | None = None) -> dict:
    """Parse the configuration from CLI and/or configuration JSON file.

    Arguments:
        prog: Program name.
        version: Program version.
        copy_right: Copyright info.
        author: Author info.
        arg_list: Optional command line arguments list.

    Returns:
        Dict: Parsed configuration options.
    """
    argparser = argparse.ArgumentParser(
        prog=prog, description="Command-line tool to read events from a iCalendar (ICS)."
    )

    local_timezone = pytz.timezone(get_localzone().key)

    argparser.add_argument("--version", action="version", version=f"{version}\n{copy_right} {author}")
    argparser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=1,
        help="Increase log-level. -v: INFO, -vv DEBUG, ... Default: WARNING",
    )
    argparser.add_argument("-u", "--url", dest="url", required=True, help="icalendar URL to be parsed.")
    argparser.add_argument(
        "-b", "--basicAuth", dest="basicAuth", help='Basic authentication for URL in format "<user>:<password>".'
    )
    argparser.add_argument(
        "-f", "--summaryFilter", dest="summaryFilter", help="RegEx to filter calendar events based on summary field."
    )
    argparser.add_argument(
        "-s",
        "--startDate",
        type=datetime.datetime.fromisoformat,
        help="Start date/time of event filter by time (ISO format). Default: now",
        default=local_timezone.localize(datetime.datetime.now()).replace(microsecond=0),
    )
    argparser.add_argument(
        "-e",
        "--endDate",
        type=datetime.datetime.fromisoformat,
        required=True,
        help="End date/time of event filter by time (ISO format).",
    )
    argparser.add_argument(
        "-o",
        "--outputFormat",
        default=OutputFormat.LOGGER,
        type=OutputFormat,
        choices=list(OutputFormat),
        help="Output format.",
    )
    argparser.add_argument(
        "-c", "--encoding", dest="encoding", default="UTF-8", help="Encoding of the calendar. Default: UTF-8"
    )

    return argparser.parse_args(args=arg_list)

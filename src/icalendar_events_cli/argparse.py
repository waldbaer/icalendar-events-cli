"""Argument parsing."""

# ---- Imports ----
import re
import sys
from argparse import ArgumentTypeError
from datetime import datetime
from typing import Optional

import pytz
from jsonargparse import ArgumentParser, DefaultHelpFormatter
from pydantic import SecretStr
from rich_argparse import RawTextRichHelpFormatter
from tzlocal import get_localzone

from .output import OutputFormat

# ---- Globals ---------------------------------------------------------------------------------------------------------

_local_timezone = pytz.timezone(get_localzone().key)


# ---- CommandLine parser ----------------------------------------------------------------------------------------------
class HelpFormatter(DefaultHelpFormatter, RawTextRichHelpFormatter):
    """Custom CLI help formatter: Combined DefaultHelpFormatter and RichHelpFormatter."""


def parse_config(prog: str, version: str, copy_right: str, author: str, arg_list: Optional[list[str]] = None) -> dict:
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
    arg_parser = ArgumentParser(
        prog=prog,
        description="Command-line tool to read events from a iCalendar (ICS) files."
        + f" | Version {version} | {copy_right}",
        version=f"| Version {version}\n{copy_right} {author}",
        default_config_files=["./config.json"],
        print_config=None,
        env_prefix="ICALENDAR_EVENTS_CLI",
        default_env=False,
        formatter_class=HelpFormatter,
    )

    arg_parser.add_argument("-c", "--config", action="config", help="""Path to JSON configuration file.""")

    # ---- Calendar URL / access ----
    arg_parser.add_argument(
        "--calendar.url",
        type=str,
        required=True,
        help="""URL of the iCalendar (ICS).
Also URLs to local files with schema file://<absolute path to local file> are supported.""",
    )
    arg_parser.add_argument(
        "--calendar.verify-url",
        type=bool,
        default=True,
        help="Configure SSL verification of the URL",
    )
    arg_parser.add_argument(
        "--calendar.user",
        type=SecretStr,
        help="Username for calendar URL HTTP authentication (basic authentication)",
    )
    arg_parser.add_argument(
        "--calendar.password",
        type=SecretStr,
        help="Password for calendar URL HTTP authentication (basic authentication)",
    )
    arg_parser.add_argument("--calendar.encoding", default="UTF-8", help="Encoding of the calendar")

    # ---- Filtering ----

    arg_parser.add_argument(
        "-s",
        "--filter.start-date",
        type=datetime_isoformat,
        default=_local_timezone.localize(datetime.now().replace(microsecond=0)).replace(microsecond=0),
        help="Start date/time of event filter by time (ISO format). Default: now",
    )
    arg_parser.add_argument(
        "-e",
        "--filter.end-date",
        type=datetime_isoformat,
        default=_local_timezone.localize(datetime.combine(datetime.now(), datetime.max.time())).replace(microsecond=0),
        help="End date/time of event filter by time (ISO format). Default: end of today",
    )

    arg_parser.add_argument(
        "-f",
        "--filter.summary",
        type=regex_type,
        required=False,
        default=None,
        help="RegEx to filter calendar events based on the summary attribute.",
    )

    arg_parser.add_argument(
        "--filter.description",
        type=regex_type,
        required=False,
        default=None,
        help="RegEx to filter calendar events based on the description attribute.",
    )

    arg_parser.add_argument(
        "--filter.location",
        type=regex_type,
        required=False,
        default=None,
        help="RegEx to filter calendar events based on the location attribute.",
    )

    # ---- Output ----
    arg_parser.add_argument(
        "--output.format",
        default=OutputFormat.human_readable,
        type=OutputFormat,
        help="Output format.",
    )

    arg_parser.add_argument(
        "-o",
        "--output.file",
        type=Optional[str],
        help="Path of JSON output file. If not set the output is written to console / stdout",
    )

    # ---- Finally parse the inputs  ----
    config = arg_parser.parse_args(args=arg_list)

    # ---- Post-parse validation ----
    _validate_config(config)

    return config


def datetime_isoformat(arg: str) -> datetime:
    """Convert isoformat cli argument to datetime.

    Arguments:
        arg: cli argument in ISO format

    Raises:
        ArgumentTypeError: in case the parsing failed

    Returns:
        Parsed datetime instance.
    """
    try:
        dt = datetime.fromisoformat(str(arg))
    except ValueError:
        raise ArgumentTypeError(f"invalid datetime value (expected ISO 8601 format): '{arg}'") from None

    if dt.tzinfo is None:
        dt = _local_timezone.localize(dt)
    return dt


def regex_type(arg: str) -> str:
    """Check if a string is a valid RegEx.

    Arguments:
        arg: cli argument to be checked

    Raises:
        ArgumentTypeError: in case the parsing failed

    Returns:
        unmodified string argument
    """
    try:
        re.compile(arg)
    except re.error as e:
        raise ArgumentTypeError(f"invalid RegEx value '{arg}': {e}") from None
    return arg


def _validate_config(config: dict) -> None:
    """Validate the configuration.

    Arguments:
        config: Parsed configuration hierarchy.
    """
    found_config_issues = []

    if config.filter.start_date > config.filter.end_date:
        found_config_issues.append(
            "filter.end-date must be after filter.start-state"
            + f" (configured: {config.filter.start_date} -> {config.filter.end_date})"
        )

    # Finally report all found issues
    if found_config_issues:
        print("ERROR: invalid configuration / parameters:", file=sys.stderr)
        for found_config_issue in found_config_issues:
            print(f"- {found_config_issue}", file=sys.stderr)
        sys.exit(1)

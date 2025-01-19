"""Argument parsing."""

# ---- Imports ----
from datetime import datetime
from typing import Optional

import pytz
from jsonargparse import ArgumentParser, DefaultHelpFormatter
from pydantic import SecretStr
from rich_argparse import RawTextRichHelpFormatter
from tzlocal import get_localzone

from .output import OutputFormat


# ---- CommandLine parser ----------------------------------------------------------------------------------------------
class E3DCCliHelpFormatter(DefaultHelpFormatter, RawTextRichHelpFormatter):
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
    argparser = ArgumentParser(
        prog=prog,
        description="Command-line tool to read events from a iCalendar (ICS) files."
        + f" | Version {version} | {copy_right}",
        version=f"| Version {version}\n{copy_right} {author}",
        default_config_files=["./config.json"],
        print_config=None,
        env_prefix="ICALENDAR_EVENTS_CLI",
        default_env=False,
        formatter_class=E3DCCliHelpFormatter,
    )

    argparser.add_argument("-c", "--config", action="config", help="""Path to JSON configuration file.""")

    # ---- Calendar URL / access ----
    argparser.add_argument("--calendar.url", type=str, help="URL of the iCalendar (ICS)")
    argparser.add_argument(
        "--calendar.verify-url",
        type=bool,
        default=True,
        help="Configure SSL verification of the URL",
    )
    argparser.add_argument(
        "--calendar.user",
        type=SecretStr,
        help="Username for calendar URL HTTP authentication (basic authentication)",
    )
    argparser.add_argument(
        "--calendar.password",
        type=SecretStr,
        help="Password for calendar URL HTTP authentication (basic authentication)",
    )
    argparser.add_argument("--calendar.encoding", default="UTF-8", help="Encoding of the calendar")

    # ---- Filtering ----
    argparser.add_argument(
        "-f",
        "--filter.summary",
        default=".*",
        help="RegEx to filter calendar events based on summary field.",
    )

    local_timezone = pytz.timezone(get_localzone().key)
    argparser.add_argument(
        "-s",
        "--filter.start-date",
        type=_datetime_fromisoformat,
        default=local_timezone.localize(datetime.now().replace(microsecond=0)).replace(microsecond=0),
        help="Start date/time of event filter by time (ISO format). Default: now",
    )
    argparser.add_argument(
        "-e",
        "--filter.end-date",
        type=_datetime_fromisoformat,
        default=local_timezone.localize(datetime.combine(datetime.now(), datetime.max.time())).replace(microsecond=0),
        help="End date/time of event filter by time (ISO format). Default: end of today",
    )

    # ---- Output ----
    argparser.add_argument(
        "--output.format",
        default=OutputFormat.human_readable,
        type=OutputFormat,
        help="Output format.",
    )

    argparser.add_argument(
        "-o",
        "--output.file",
        type=Optional[str],
        help="Path of JSON output file. If not set the output is written to console / stdout",
    )

    # ---- Finally parse the inputs  ----
    args = argparser.parse_args(args=arg_list)

    return args


def _datetime_fromisoformat(arg: str) -> datetime:
    """Convert isoformat cli argument to datetime.

    Arguments:
        arg: cli argument in ISO format

    Returns:
        Parsed datetime instance.
    """
    return datetime.fromisoformat(str(arg))

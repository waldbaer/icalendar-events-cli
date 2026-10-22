"""Commandline interface entry point."""

# ---- Imports --------------------------------------------------------------------------------------------------------
import importlib.metadata

from .argparse import parse_config
from .constants import Os
from .downloader import download_calendar
from .icalendar import filter_events, parse_calendar, recurring_calendar
from .output import output_events

# ---- Module Meta-Data ------------------------------------------------------------------------------------------------
__prog__ = "icalendar-events-cli"
__dist_name__ = "icalendar_events_cli"
__copyright__ = "Copyright 2023-2026"
__author__ = "Sebastian Waldvogel"

# ---- Main -----------------------------------------------------------------------------------------------------------


def cli(arg_list: list[str] | None = None) -> int:
    """Main command line handling entry point.

    Arguments:
        arg_list: Optional list of command line arguments. Only needed for testing.
                  Productive __main__ will call the API without any argument.

    Returns:
        Numeric exit code
    """
    try:
        config = parse_config(
            prog=__prog__,
            version=importlib.metadata.version(__dist_name__),
            copy_right=__copyright__,
            author=__author__,
            arg_list=arg_list,
        )
        return _main_logic(config)

    except SystemExit as e:
        return e.code

    except BaseException as e:  # pylint: disable=broad-exception-caught;reason=Explicitly capture all exceptions thrown during execution.
        print(
            f"ERROR: Any error has occurred!{Os.linesep}{Os.linesep}Exception: {str(e)}"
            # f"Detailed Traceback: {traceback.format_exc()}"
        )
        return Os.EX_ERROR


def _main_logic(config: dict) -> int:
    """Main program logic.

    Arguments:
        config: Configuration hierarchy

    Returns:
        Numeric exit code
    """
    calendar_string = download_calendar(config.calendar)
    calendar = parse_calendar(calendar_string)
    events = recurring_calendar(calendar, config.filter)
    events = filter_events(events, config.filter)
    output_events(calendar, events, config)

    return Os.EX_OK

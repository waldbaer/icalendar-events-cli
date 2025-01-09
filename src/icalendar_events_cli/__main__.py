"""Commandline interface entry point."""

# ---- Imports --------------------------------------------------------------------------------------------------------
import importlib.metadata
import os

from .argparse import parse_config
from .downloader import download_ics
from .icalendar import filter_events, parse_calendar
from .output import configure_logging, logging, output_events

# ---- Module Meta-Data ------------------------------------------------------------------------------------------------
__prog__ = "icalendar-events-cli"
__dist_name__ = "icalendar_events_cli"
__copyright__ = "Copyright 2023-2025"
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
        args = parse_config(
            prog=__prog__,
            version=importlib.metadata.version(__dist_name__),
            copy_right=__copyright__,
            author=__author__,
            arg_list=arg_list,
        )
        return _main_logic(args)

    except SystemExit as e:
        return e.code

    except BaseException as e:  # pylint: disable=broad-exception-caught;reason=Explicitely capture all exceptions thrown during execution.
        logging.error(
            f"Any error has occured!{os.linesep}{os.linesep}Exception: {str(e)}"
            # f"Detailed Traceback: {traceback.format_exc()}"
        )
        return 1


def _main_logic(args: dict) -> int:
    configure_logging(args)

    calendar_ics = download_ics(args)
    events = parse_calendar(args, calendar_ics)
    if args.summaryFilter is not None:
        events = filter_events(events, args.summaryFilter, args.encoding)
    output_events(args, events)

    return os.EX_OK

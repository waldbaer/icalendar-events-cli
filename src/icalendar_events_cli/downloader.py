"""ICS calender file downloader."""

# ---- Imports ---------------------------------------------------------------------------------------------------------
import sys

import requests

# ---- Functions -------------------------------------------------------------------------------------------------------


def download_ics(args: dict) -> str:
    """Download ICS calendar file from URL.

    Arguments:
        args: Configuration hierarchy.

    Returns:
        str: Downloaded file content.
    """
    session = requests.Session()
    if args.basicAuth is not None:
        user_password = args.basicAuth.split(":")
        session.auth = (user_password[0], user_password[1])
    response = session.get(url=args.url)
    if response.status_code != 200:
        print(
            f"ERROR: Failed to download ical contents from URL '{response.url}'. "
            + f"Response status: {response.reason} (status {response.status_code})",
        )
        sys.exit(1)
    return response.text

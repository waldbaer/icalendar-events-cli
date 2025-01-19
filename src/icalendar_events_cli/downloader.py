"""ICS calender file downloader."""

# ---- Imports ---------------------------------------------------------------------------------------------------------
import sys

import requests

# ---- Functions -------------------------------------------------------------------------------------------------------


def download_ics(calendard_config: dict) -> str:
    """Download ICS calendar file from URL.

    Arguments:
        calendard_config: Calendar configuration hierarchy.

    Returns:
        str: Downloaded file content.
    """
    session = requests.Session()
    if calendard_config.user is not None and calendard_config.password is not None:
        session.auth = (calendard_config.user.get_secret_value(), calendard_config.password.get_secret_value())
    response = session.get(url=calendard_config.url, verify=calendard_config.verify_url)
    if response.status_code != 200:
        print(
            f"ERROR: Failed to download ical contents from URL '{response.url}'. "
            + f"Response status: {response.reason} (status {response.status_code})",
        )
        sys.exit(1)
    return response.text

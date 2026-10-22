"""Calender file downloader."""

# ---- Imports ---------------------------------------------------------------------------------------------------------
import sys
from email.message import Message

import requests
from requests_file import FileAdapter

from .constants import Os, StringEncoding

# ---- Functions -------------------------------------------------------------------------------------------------------


def download_calendar(calendar_config: dict) -> str:
    """Download calendar file from URL.

    The content is decoded with the charset declared by the server, or as UTF-8 if none is declared. Bytes that are
    invalid in that charset are replaced with U+FFFD. A leading byte order mark is removed.

    Arguments:
        calendar_config: Calendar configuration hierarchy.

    Returns:
        str: Downloaded file content.
    """
    session = requests.Session()
    session.mount("file://", FileAdapter())

    if calendar_config.user is not None and calendar_config.password is not None:
        session.auth = (calendar_config.user.get_secret_value(), calendar_config.password.get_secret_value())
    response = session.get(url=calendar_config.url, verify=calendar_config.verify_url)
    if response.status_code != 200:
        print(
            f"ERROR: Failed to download ical contents from URL '{response.url}'. "
            + f"Response status: {response.reason} (status {response.status_code})",
        )
        sys.exit(Os.EX_ERROR)

    # Default charset: RFC 5545, section 3.1.4
    response.encoding = _get_declared_charset(response) or StringEncoding.UTF_8
    return response.text.removeprefix(StringEncoding.BYTE_ORDER_MARK)


def _get_declared_charset(response: requests.Response) -> str | None:
    """Get the charset declared in the Content-Type header of a response.

    Unlike requests, this does not fall back to ISO-8859-1 for text/* types without a declared charset.

    Arguments:
        response: Response of the calendar download.

    Returns:
        str | None: Declared charset in lower case, or None if no charset is declared.
    """
    message = Message()
    message["Content-Type"] = response.headers.get("Content-Type", "")
    return message.get_content_charset()

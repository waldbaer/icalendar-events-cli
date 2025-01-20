"""Test of general commands."""

import os
import re
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pytest
import pytz
from click import DateTime
from pytest_httpserver import HTTPServer
from tzlocal import get_localzone

from tests.util_runner import run_cli, run_cli_stdout_json


# ---- Utilities -------------------------------------------------------------------------------------------------------
@dataclass
class ExpectedEvent:
    """Expectation of an event and it's data (summary, description, location, ...)."""

    summary: str
    description: Optional[str]
    location: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]

    def __init__(
        self,
        summary: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> None:
        """Construct.

        Arguments:
            summary: Event summary
            description: Event description
            location: Event location
            start_date: Start date
            end_date: End date
        """
        self.summary = summary
        self.description = description
        self.location = location
        self.start_date = start_date
        self.end_date = end_date


def localized_date_time(*args: any, **kwargs: any) -> DateTime:
    """Build a localized datetime instance.

    Arguments:
        args: Generic arguments list forwarded to datetime constructor.
        kwargs: Generic keyword arguments forwarded to datetime constructor.

    Returns:
        Localized datetime instance.
    """
    local_timezone = pytz.timezone(get_localzone().key)
    return local_timezone.localize(datetime(*args, **kwargs))


def prepare_local_httpserver_mock(calendar_url: str, username: str, password: str, httpserver: HTTPServer) -> None:
    """Prepare HTTP server mock.

    Arguments:
        calendar_url: ICS calendar URL,
        username: Username for basicAuth
        password: Password for basicAuth
        httpserver: Mocked HTTP server
    """
    local_file_path = f"tests/ics_examples{calendar_url}"
    local_file = open(local_file_path, encoding="UTF-8")
    ics_file_content = local_file.read()
    assert ics_file_content != ""
    expected_headers = None
    if username != "" and password != "":
        expected_headers = {
            "Authorization": (f"Basic {b64encode(bytes(f'{username}:{password}', encoding='ascii')).decode('ascii')}")
        }

    httpserver.expect_request(
        calendar_url,
        headers=expected_headers,
    ).respond_with_data(ics_file_content)


def build_basicauth_cli_arg(username: str, password: str) -> str:
    """Build --basicAuth cli argument.

    Arguments:
        username: Username for basicAuth
        password: Password for basicAuth

    Returns:
        cli argument for --basicAuth
    """
    basic_auth = ""
    if username != "" and password != "":
        basic_auth = f"--basicAuth '{username}:{password}' "
    return basic_auth


# ---- Testcases -------------------------------------------------------------------------------------------------------


# ---- Happy Path Tests ---------------------------------------------------------------------------

test_queries = [
    # ---- Public calendars ---------------------------------------------------
    # Thunderbird Holiday Calender 2024 / 2025 - Multimatch with RegEx
    # https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics
    (
        "/GermanHolidays.ics",
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2026, month=12, day=31, hour=23, minute=59, second=59),
        ".*Oster(sonntag|montag).*",
        [
            ExpectedEvent(
                summary="Ostersonntag.*",
                description=".*Common local holiday*",
                location=None,
                start_date=localized_date_time(year=2025, month=4, day=20, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=4, day=20, hour=23, minute=59, second=59),
            ),
            ExpectedEvent(
                summary="Ostermontag.*",
                description=".*Tag nach dem Ostersonntag*",
                location=None,
                start_date=localized_date_time(year=2025, month=4, day=21, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=4, day=21, hour=23, minute=59, second=59),
            ),
            ExpectedEvent(
                summary="Ostersonntag.*",
                description=".*Common local holiday*",
                location=None,
                start_date=localized_date_time(year=2026, month=4, day=5, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2026, month=4, day=5, hour=23, minute=59, second=59),
            ),
            ExpectedEvent(
                summary="Ostermontag.*",
                description=".*Tag nach dem Ostersonntag*",
                location=None,
                start_date=localized_date_time(year=2026, month=4, day=6, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2026, month=4, day=6, hour=23, minute=59, second=59),
            ),
        ],
        # no basicAuth
        "",
        "",
    ),
    # Thunderbird Holiday Calender 2024 / 2025 - SingleMatch with RegEx
    # https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics
    (
        "/GermanHolidays.ics",
        localized_date_time(year=2025, month=10, day=3, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=10, day=4, hour=23, minute=59, second=59),
        ".*Einheit.*",
        [
            ExpectedEvent(
                summary="Tag der Deutschen Einheit",
                description=".*Wiedervereinigung Deutschlands.*",
                location=None,
                start_date=localized_date_time(year=2025, month=10, day=3, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=10, day=3, hour=23, minute=59, second=59),
            )
        ],
        # no basicAuth
        "",
        "",
    ),
    # ---- Synthetic calendards with recurring events -------------------------
    # Recurring daily with until date
    (
        "/recurring_events.ics",
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=2, day=28, hour=23, minute=59, second=59),
        "recurring_event_daily_until_3days",
        [
            ExpectedEvent(
                summary="recurring_event_daily_until_3days",
                description="description_recurring_event_daily_until_3days",
                location="location_recurring_event_daily_until_3days",
                start_date=localized_date_time(year=2025, month=1, day=1, hour=19, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=1, day=1, hour=20, minute=0, second=0),
            ),
            ExpectedEvent(
                summary="recurring_event_daily_until_3days",
                description="description_recurring_event_daily_until_3days",
                location="location_recurring_event_daily_until_3days",
                start_date=localized_date_time(year=2025, month=1, day=2, hour=19, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=1, day=2, hour=20, minute=0, second=0),
            ),
            ExpectedEvent(
                summary="recurring_event_daily_until_3days",
                description="description_recurring_event_daily_until_3days",
                location="location_recurring_event_daily_until_3days",
                start_date=localized_date_time(year=2025, month=1, day=3, hour=19, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=1, day=3, hour=20, minute=0, second=0),
            ),
        ],
        # with dummy basicAuth
        "dummy_user",
        "test_password",
    ),
    # Recurring every second day.
    (
        "/recurring_events.ics",
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=2, day=28, hour=23, minute=59, second=59),
        "recurring_event_every_second_day_count2",
        [
            ExpectedEvent(
                summary="recurring_event_every_second_day_count2",
                description="description_recurring_event_every_second_day_count2",
                location="location_recurring_event_every_second_day_count2",
                start_date=localized_date_time(year=2025, month=1, day=1, hour=11, minute=12, second=13),
                end_date=localized_date_time(year=2025, month=1, day=1, hour=14, minute=15, second=16),
            ),
            ExpectedEvent(
                summary="recurring_event_every_second_day_count2",
                description="description_recurring_event_every_second_day_count2",
                location="location_recurring_event_every_second_day_count2",
                start_date=localized_date_time(year=2025, month=1, day=3, hour=11, minute=12, second=13),
                end_date=localized_date_time(year=2025, month=1, day=3, hour=14, minute=15, second=16),
            ),
        ],
        # no basicAuth
        "",
        "",
    ),
    # Recurring weekly.
    (
        "/recurring_events.ics",
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=2, day=28, hour=23, minute=59, second=59),
        "recurring_event_weekly_2weeks",
        [
            ExpectedEvent(
                summary="recurring_event_weekly_2weeks",
                description="description_recurring_event_weekly_2weeks",
                location=None,  # no location expected
                start_date=localized_date_time(year=2025, month=1, day=1, hour=9, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=1, day=1, hour=17, minute=0, second=0),
            ),
            ExpectedEvent(
                summary="recurring_event_weekly_2weeks",
                description="description_recurring_event_weekly_2weeks",
                location=None,  # no location expected
                start_date=localized_date_time(year=2025, month=1, day=8, hour=9, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=1, day=8, hour=17, minute=0, second=0),
            ),
        ],
        # no basicAuth
        "",
        "",
    ),
    # Recurring weekly. Query only first week.
    (
        "/recurring_events.ics",
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=1, day=7, hour=23, minute=59, second=59),
        "recurring_event_weekly_2weeks",
        [
            ExpectedEvent(
                summary="recurring_event_weekly_2weeks",
                description="description_recurring_event_weekly_2weeks",
                location=None,  # no location expected
                start_date=localized_date_time(year=2025, month=1, day=1, hour=9, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=1, day=1, hour=17, minute=0, second=0),
            )
        ],
        # no basicAuth
        "",
        "",
    ),
    # Recurring monthly.
    (
        "/recurring_events.ics",
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=12, day=31, hour=23, minute=59, second=59),
        "recurring_event_monthly_3months",
        [
            ExpectedEvent(
                summary="recurring_event_monthly_3months",
                description=None,  # no description expected
                location="location_recurring_event_monthly_3months",
                start_date=localized_date_time(year=2025, month=7, day=1, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=7, day=3, hour=23, minute=59, second=59),
            ),
            ExpectedEvent(
                summary="recurring_event_monthly_3months",
                description=None,  # no description expected
                location="location_recurring_event_monthly_3months",
                start_date=localized_date_time(year=2025, month=8, day=1, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=8, day=3, hour=23, minute=59, second=59),
            ),
            ExpectedEvent(
                summary="recurring_event_monthly_3months",
                description=None,  # no description expected
                location="location_recurring_event_monthly_3months",
                start_date=localized_date_time(year=2025, month=9, day=1, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=9, day=3, hour=23, minute=59, second=59),
            ),
        ],
        # no basicAuth
        "",
        "",
    ),
    # Recurring yearly.
    (
        "/recurring_events.ics",
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2035, month=12, day=31, hour=23, minute=59, second=59),
        "recurring_event_yearly_2years_with_fullday_event",
        [
            ExpectedEvent(
                summary="recurring_event_yearly_2years_with_fullday_event",
                description=None,  # no description expected
                location=None,  # no location expected,
                start_date=localized_date_time(year=2025, month=5, day=1, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2025, month=5, day=1, hour=23, minute=59, second=59),
            ),
            ExpectedEvent(
                summary="recurring_event_yearly_2years_with_fullday_event",
                description=None,  # no description expected
                location=None,  # no location expected,
                start_date=localized_date_time(year=2026, month=5, day=1, hour=0, minute=0, second=0),
                end_date=localized_date_time(year=2026, month=5, day=1, hour=23, minute=59, second=59),
            ),
        ],
        # no basicAuth
        "",
        "",
    ),
    # ---- Other known issues ----
    # github issue #6
    (
        "/other_examples.ics",
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=12, day=31, hour=23, minute=59, second=59),
        "github_issue_#6",
        [
            ExpectedEvent(
                summary="github_issue_#6",
                description="https://github.com/waldbaer/icalendar-events-cli/issues/6",
                location=None,
                start_date=localized_date_time(year=2025, month=1, day=23, hour=18, minute=15, second=0),
                end_date=localized_date_time(year=2025, month=1, day=23, hour=19, minute=25, second=0),
            ),
        ],
        # no basicAuth
        "",
        "",
    ),
]


@pytest.mark.parametrize(
    "calendar_url,start_date,end_date,summary_filter,expected_events,username,password",
    test_queries,
)
def test_ct_valid_query_outputformat_json(
    calendar_url: str,
    start_date: datetime,
    end_date: datetime,
    summary_filter: str,
    expected_events: list[ExpectedEvent],
    username: str,
    password: str,
    httpserver: HTTPServer,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test calendar queries with output format 'JSON'.

    Arguments:
        calendar_url: ICS calendar URL,
        start_date: Start Date
        end_date: End Date,
        summary_filter: Summary Filter
        expected_events: List of expected events
        username: Username for basicAuth
        password: Password for basicAuth
        httpserver: Mocked HTTP server
        capsys: System capture
    """
    prepare_local_httpserver_mock(calendar_url, username, password, httpserver)

    # Run icalendar-events-cli
    calendar_url = httpserver.url_for(calendar_url)
    basic_auth = build_basicauth_cli_arg(username, password)
    args = (
        f"--url {calendar_url} {basic_auth}"
        + f"--startDate {start_date.isoformat()} --endDate {end_date.isoformat()}"
        + f" --summaryFilter {summary_filter} --outputFormat json"
    )

    cli_result = run_cli_stdout_json(args, capsys)
    assert cli_result.exit_code == os.EX_OK

    json_output = cli_result.stdout_as_json
    assert json_output["startDate"] == start_date.isoformat()
    assert json_output["endDate"] == end_date.isoformat()
    assert json_output["summaryFilter"] == summary_filter

    events = json_output["events"]
    assert len(events) == len(expected_events)

    for events_index, expected_event in enumerate(expected_events):
        assert re.match(expected_event.summary, events[events_index]["summary"])
        assert expected_event.start_date.isoformat() == events[events_index]["startDate"]
        assert expected_event.end_date.isoformat() == events[events_index]["endDate"]

        if expected_event.description is not None:
            assert re.match(expected_event.description, events[events_index]["description"])
        else:
            assert "description" not in events[events_index]

        if expected_event.location is not None:
            assert re.match(expected_event.location, events[events_index]["location"])
        else:
            assert "location" not in events[events_index]


@pytest.mark.parametrize(
    "calendar_url,start_date,end_date,summary_filter,expected_events,username,password", test_queries
)
def test_ct_valid_query_outputformat_humanreadable(
    calendar_url: str,
    start_date: datetime,
    end_date: datetime,
    summary_filter: str,
    expected_events: list[ExpectedEvent],
    username: str,
    password: str,
    httpserver: HTTPServer,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test calendar queries with output format 'human readable'.

    Arguments:
        calendar_url: ICS calendar URL,
        start_date: Start Date
        end_date: End Date,
        summary_filter: Summary Filter
        expected_events: List of expected events
        username: Username for basicAuth
        password: Password for basicAuth
        httpserver: Mocked HTTP server
        capsys: System capture
    """
    prepare_local_httpserver_mock(calendar_url, username, password, httpserver)

    # Run icalendar-events-cli
    calendar_url = httpserver.url_for(calendar_url)
    basic_auth = build_basicauth_cli_arg(username, password)
    args = (
        f"--url {calendar_url} {basic_auth}"
        + f" --startDate {start_date.isoformat()} --endDate {end_date.isoformat()}"
        + f" --summaryFilter {summary_filter} --outputFormat logger --verbose"
    )

    cli_result = run_cli(args, capsys)
    assert cli_result.exit_code == os.EX_OK

    output_lines = cli_result.stdout_lines
    header_lines = 4  # start / enddate, summary filter, number of events
    assert len(output_lines) >= (header_lines + len(expected_events))

    assert f"Start Date:       {start_date.strftime('%Y-%m-%d')}" in output_lines[0]
    assert f"End Date:         {end_date.strftime('%Y-%m-%d')}" in output_lines[1]
    assert f"Summary Filter:   {summary_filter}" in output_lines[2]
    assert f"Number of Events: {len(expected_events)}" in output_lines[3]

    events_output_lines = output_lines[header_lines:]

    for events_index, expected_event in enumerate(expected_events):
        expected_start_end = f"{expected_event.start_date.isoformat()} -> {expected_event.end_date.isoformat()}"
        assert events_output_lines[events_index].startswith(expected_start_end)

        assert re.match(f".*| {expected_event.summary} |.*", events_output_lines[events_index])
        if expected_event.description is not None:
            assert re.match(f".*| {expected_event.description} |.*", events_output_lines[events_index])
        if expected_event.location is not None:
            assert re.match(f".*| {expected_event.location} |.*", events_output_lines[events_index])


# ---- Negative Tests -----------------------------------------------------------------------------


def test_ct_invalid_url(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test a calendar query with an invalid (not existing) URL.

    Arguments:
        capsys: System capture
    """
    invalid_url = "https://www.INVALID_URL.123/INVALID_ICS_FILE.icsx"
    args = f"--url {invalid_url} --startDate 2025-01-01 --endDate 2025-01-17 -f xxx --outputFormat json"

    cli_result = run_cli(args, capsys)

    assert cli_result.exit_code != 0
    assert "Failed to resolve" in cli_result.stdout
    assert "Name or service not known" in cli_result.stdout


def test_ct_failing_server_response(httpserver: HTTPServer, capsys: pytest.CaptureFixture[str]) -> None:
    """Test that ICS file download fails with HTTP error.

    Arguments:
        httpserver: Mocked HTTP server
        capsys: System capture
    """
    calendar_url = "calendar.ics"
    httpserver.expect_request(calendar_url).respond_with_data("not found", status=404)
    calendar_url = httpserver.url_for(calendar_url)

    start_date = localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0).isoformat()
    end_date = localized_date_time(year=2025, month=2, day=1, hour=0, minute=0, second=0).isoformat()
    args = f"--url {calendar_url} --startDate {start_date} --endDate {end_date} -f invalid --outputFormat json"

    cli_result = run_cli(args, capsys)
    assert cli_result.exit_code != os.EX_OK

    assert "Failed to download ical contents from URL" in cli_result.stdout

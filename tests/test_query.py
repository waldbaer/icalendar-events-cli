"""Test of general commands."""

import logging
import os
import re
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime

import pytest
from pytest_httpserver import HTTPServer

from tests.util_runner import run_cli, run_cli_stdout_json


# ---- Utilities -------------------------------------------------------------------------------------------------------
@dataclass
class ExpectedEvent:
    """Expectation of an event and it's data (summary, description, location, ...)."""

    summary: str
    description: str | None
    location: str | None

    def __init__(self, summary: str, description: str | None = None, location: str | None = None) -> None:
        """Construct.

        Arguments:
            summary: Event summary
            description: Event description
            location: Event location
        """
        self.summary = summary
        self.description = description
        self.location = location


# ---- Testcases -------------------------------------------------------------------------------------------------------


# ---- Happy Path Tests ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "calendar_url,start_date,end_date,summary_filter,expected_events,username,password",
    [
        # Thunderbird Holiday Calender 2024 / 2025 - Multimatch with RegEx
        # https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics
        (
            "/GermanHolidays.ics",
            datetime(year=datetime.today().year, month=1, day=1, hour=0, minute=0, second=0),
            datetime(year=datetime.today().year, month=12, day=31, hour=23, minute=59, second=59),
            ".*Oster.*",
            [
                ExpectedEvent("Ostersonntag.*", ".*Common local holiday*"),
                ExpectedEvent("Ostermontag.*", ".*Tag nach dem Ostersonntag*"),
            ],
            # no basicAuth
            "",
            "",
        ),
        # Thunderbird Holiday Calender 2024 / 2025 - SingleMatch with RegEx
        # https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics
        (
            "/GermanHolidays.ics",
            datetime(year=datetime.today().year, month=10, day=3, hour=0, minute=0, second=0),
            datetime(year=datetime.today().year, month=10, day=4, hour=23, minute=59, second=59),
            ".*Einheit.*",
            [ExpectedEvent("Tag der Deutschen Einheit", ".*Wiedervereinigung Deutschlands.*")],
            # no basicAuth
            "",
            "",
        ),
        # Recurring daily with until date: 10 total events expected
        (
            "/recurring_events.ics",
            datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0),
            datetime(year=2025, month=2, day=28, hour=23, minute=59, second=59),
            "recurring_event_daily_until_10days",
            [
                ExpectedEvent(
                    "recurring_event_daily_until_10days",
                    "description_recurring_event_daily_until_10days",
                    "location_recurring_event_daily_until_10days",
                )
            ]
            * 10,
            # with dummy basicAuth
            "dummy_user",
            "test_password",
        ),
        # Recurring every second day. 20 total events expected.
        (
            "/recurring_events.ics",
            datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0),
            datetime(year=2025, month=2, day=28, hour=23, minute=59, second=59),
            "recurring_event_every_second_day_count20",
            [
                ExpectedEvent(
                    "recurring_event_every_second_day_count20",
                    "description_recurring_event_every_second_day_count20",
                    "location_recurring_event_every_second_day_count20",
                )
            ]
            * 20,
            # no basicAuth
            "",
            "",
        ),
        # Recurring weekly. 20 total events expected.
        (
            "/recurring_events.ics",
            datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0),
            datetime(year=2025, month=2, day=28, hour=23, minute=59, second=59),
            "recurring_event_weekly_2months",
            [
                ExpectedEvent(
                    "recurring_event_weekly_2months",
                    "description_recurring_event_weekly_2months",
                    None,  # no location expected
                )
            ]
            * 8,
            # no basicAuth
            "",
            "",
        ),
        # Recurring weekly. Query only first of the two months. 10 total events expected.
        (
            "/recurring_events.ics",
            datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0),
            datetime(year=2025, month=1, day=31, hour=23, minute=59, second=59),
            "recurring_event_weekly_2months",
            [
                ExpectedEvent(
                    "recurring_event_weekly_2months",
                    "description_recurring_event_weekly_2months",
                    None,  # no location expected
                )
            ]
            * 5,  # 5 weeks starting from 01.01 in 31 days january
            # no basicAuth
            "",
            "",
        ),
        # Recurring monthly. Second half year expected.
        (
            "/recurring_events.ics",
            datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0),
            datetime(year=2025, month=12, day=31, hour=23, minute=59, second=59),
            "recurring_event_monthly_6months",
            [
                ExpectedEvent(
                    "recurring_event_monthly_6months",
                    None,  # no description expected
                    "location_recurring_event_monthly_6months",
                )
            ]
            * 6,
            # no basicAuth
            "",
            "",
        ),
        # Recurring yearly. 10 years expected.
        (
            "/recurring_events.ics",
            datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0),
            datetime(year=2035, month=12, day=31, hour=23, minute=59, second=59),
            "recurring_event_yearly_10years",
            [
                ExpectedEvent(
                    "recurring_event_yearly_10years",
                    None,  # no description expected
                    None,  # no location expected
                )
            ]
            * 10,
            # no basicAuth
            "",
            "",
        ),
    ],
)
def test_ct_valid_query(
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
    """Test a calendar query.

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
    # Prepare HTTP server mock
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

    # Run icalendar-events-cli
    calendar_url = httpserver.url_for(calendar_url)
    basic_auth = ""
    if username != "" and password != "":
        basic_auth = f"--basicAuth '{username}:{password}' "
    args = (
        f"--url {calendar_url} {basic_auth}"
        + f"--startDate {start_date.isoformat()} --endDate {end_date.isoformat()}"
        + f" -f {summary_filter} --outputFormat json"
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
        if expected_event.description is not None:
            assert re.match(expected_event.description, events[events_index]["description"])
        if expected_event.location is not None:
            assert re.match(expected_event.location, events[events_index]["location"])


@pytest.mark.parametrize(
    "calendar_url,start_date,end_date,summary_filter,expected_events",
    [
        (
            "/recurring_events.ics",
            datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0),
            datetime(year=2025, month=2, day=28, hour=23, minute=59, second=59),
            "recurring_event_daily_until_10days",
            [
                ExpectedEvent(
                    "recurring_event_daily_until_10days",
                    "description_recurring_event_daily_until_10days",
                    "location_recurring_event_daily_until_10days",
                )
            ]
            * 10,
        ),
        # Without description and location
        (
            "/recurring_events.ics",
            datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0),
            datetime(year=2035, month=12, day=31, hour=23, minute=59, second=59),
            "recurring_event_yearly_10years",
            [
                ExpectedEvent(
                    "recurring_event_yearly_10years",
                    None,  # no description expected
                    None,  # no location expected
                )
            ]
            * 10,
        ),
    ],
)
def test_ct_valid_query_output_humanreadable(
    calendar_url: str,
    start_date: datetime,
    end_date: datetime,
    summary_filter: str,
    expected_events: list[ExpectedEvent],
    httpserver: HTTPServer,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test a calendar query.

    Arguments:
        calendar_url: ICS calendar URL,
        start_date: Start Date
        end_date: End Date,
        summary_filter: Summary Filter
        expected_events: List of expected events
        httpserver: Mocked HTTP server
        caplog: Log capture
        capsys: System capture
    """
    # Prepare HTTP server mock
    local_file_path = f"tests/ics_examples{calendar_url}"
    local_file = open(local_file_path, encoding="UTF-8")
    ics_file_content = local_file.read()
    assert ics_file_content != ""
    httpserver.expect_request(calendar_url).respond_with_data(ics_file_content)

    # Run icalendar-events-cli
    calendar_url = httpserver.url_for(calendar_url)
    args = (
        f"--url {calendar_url} --startDate {start_date.isoformat()} --endDate {end_date.isoformat()}"
        + f" --summaryFilter {summary_filter} --outputFormat logger --verbose"
    )

    with caplog.at_level(logging.INFO):
        cli_result = run_cli(args, capsys)
        assert cli_result.exit_code == os.EX_OK

    assert f"Start Date:       {start_date.strftime('%Y-%m-%d')}" in caplog.text
    assert f"End Date:         {end_date.strftime('%Y-%m-%d')}" in caplog.text
    assert f"Summary Filter:   {summary_filter}" in caplog.text
    assert f"Number of Events: {len(expected_events)}" in caplog.text


# ---- Negative Tests -----------------------------------------------------------------------------


def test_ct_invalid_url(
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test a calendar query with an invalid (not existing) URL.

    Arguments:
        caplog: Log capture
        capsys: System capture
    """
    invalid_url = "https://www.INVALID_URL.123/INVALID_ICS_FILE.icsx"
    args = f"--url {invalid_url} --startDate 2025-01-01 --endDate 2025-01-17 -f xxx --outputFormat json"

    with caplog.at_level(logging.INFO):
        cli_result = run_cli(args, capsys)

    assert cli_result.exit_code != 0
    assert "Failed to resolve" in caplog.text
    assert "Name or service not known" in caplog.text


def test_ct_failing_server_response(
    httpserver: HTTPServer, capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture
) -> None:
    """Test that ICS file download fails with HTTP error.

    Arguments:
        httpserver: Mocked HTTP server
        capsys: System capture
        caplog: Logging capture fixture
    """
    calendar_url = "calendar.ics"
    httpserver.expect_request(calendar_url).respond_with_data("not found", status=404)
    calendar_url = httpserver.url_for(calendar_url)

    start_date = datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0).isoformat()
    end_date = datetime(year=2025, month=2, day=1, hour=0, minute=0, second=0).isoformat()
    args = f"--url {calendar_url} --startDate {start_date} --endDate {end_date} -f invalid --outputFormat json"

    with caplog.at_level(logging.WARNING):
        cli_result = run_cli(args, capsys)
        assert cli_result.exit_code != os.EX_OK

    assert "Failed to download ical contents from URL" in caplog.text

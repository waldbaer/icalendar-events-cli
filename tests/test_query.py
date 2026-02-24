"""Test of general commands."""

import os
import re
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime

import pytest
import pytz
from pytest_httpserver import HTTPServer
from tzlocal import get_localzone

from tests.util_runner import run_cli, run_cli_json


# ---- Utilities -------------------------------------------------------------------------------------------------------
@dataclass
class ExpectedEvent:
    """Expectation of an event and it's data (summary, description, location, ...)."""

    summary: str
    description: str | None
    location: str | None
    start_date: datetime | None
    end_date: datetime | None

    def __init__(
        self,
        summary: str,
        description: str | None = None,
        location: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
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


def localized_date_time(*args: any, **kwargs: any) -> datetime:
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
    cli_arg = ""
    if username != "" and password != "":
        cli_arg = f" --calendar.user={username} --calendar.password={password} "
    return cli_arg


def build_filter_cli_arg(filter_summary: str, filter_description: str, filter_location: str) -> str:
    """Build --filter.summary/description/location cli arguments.

    Arguments:
        filter_summary: Optional summary filter
        filter_description: Optional description filter
        filter_location: Optional location filter

    Returns:
        cli filter arguments
    """
    cli_arg = ""
    if filter_summary != "":
        cli_arg += f" --filter.summary {filter_summary}"
    if filter_description != "":
        cli_arg += f" --filter.description {filter_description}"
    if filter_location != "":
        cli_arg += f" --filter.location {filter_location}"
    return cli_arg


def build_output_file_cli_arg(output_path: str | None) -> str:
    """Build --output.file cli argument.

    Arguments:
        output_path: Optional output file path

    Returns:
        cli argument for --output.file
    """
    cli_arg = ""
    if output_path is not None:
        cli_arg = f" --output.file={output_path} "
    return cli_arg


# ---- Testcases -------------------------------------------------------------------------------------------------------


# ---- Happy Path Tests ---------------------------------------------------------------------------

test_queries = [
    # ---- Public calendars ---------------------------------------------------
    # Thunderbird Holiday Calender 2024 / 2025 - Multimatch with RegEx
    # https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics
    (
        "/GermanHolidays.ics",
        # filter
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2026, month=12, day=31, hour=23, minute=59, second=59),
        ".*Oster(sonntag|montag).*",
        "",
        "",
        # expected events
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
        # filter
        localized_date_time(year=2025, month=10, day=3, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=10, day=4, hour=23, minute=59, second=59),
        ".*Einheit.*",
        "",
        "",
        # expected events
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
        # filter
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=2, day=28, hour=23, minute=59, second=59),
        "recurring_event_daily_until_3days",
        "description_recurring_event_daily_until_3days",
        "location_recurring_event_daily_until_3days",
        # expected events
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
        # filter
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=2, day=28, hour=23, minute=59, second=59),
        "",
        "description_recurring_event_every_second_day_count2",
        "",
        # expected events
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
        # filter
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=2, day=28, hour=23, minute=59, second=59),
        "recurring_event_weekly_2weeks",
        "",
        "",
        [
            # expected events
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
        # filter
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=1, day=7, hour=23, minute=59, second=59),
        "recurring_event_weekly_2weeks",
        "",
        "",
        # expected events
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
        # filter
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=12, day=31, hour=23, minute=59, second=59),
        "",
        "",
        "location_recurring_event_monthly_3months",
        # expected events
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
        # filter
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2035, month=12, day=31, hour=23, minute=59, second=59),
        "recurring_event_yearly_2years_with_fullday_event",
        "",
        "",
        # expected events
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
        # filter
        localized_date_time(year=2025, month=1, day=1, hour=0, minute=0, second=0),
        localized_date_time(year=2025, month=12, day=31, hour=23, minute=59, second=59),
        "github_issue_#6",
        "",
        "",
        # expected events
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
    "calendar_url,start_date,end_date,filter_summary,filter_description,filter_location,"
    + "expected_events,username,password",
    test_queries,
)
@pytest.mark.parametrize("output_file", [None, "icalendar_events_cli_test.json"])
def test_ct_valid_query_outputformat_json(
    calendar_url: str,
    start_date: datetime,
    end_date: datetime,
    filter_summary: str,
    filter_description: str,
    filter_location: str,
    expected_events: list[ExpectedEvent],
    username: str,
    password: str,
    output_file: str | None,
    httpserver: HTTPServer,
    tmp_path: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test calendar queries with output format 'JSON'.

    Arguments:
        calendar_url: ICS calendar URL,
        start_date: Start Date
        end_date: End Date,
        filter_summary: summary filter
        filter_description: description filter
        filter_location: location filter
        expected_events: List of expected events
        username: Username for basicAuth
        password: Password for basicAuth
        output_file: JSON output file name. If not set JSON output is written to console / stdout.
        httpserver: Mocked HTTP server
        tmp_path: Temporary unique file path provided by built-in fixture.
        capsys: System capture
    """
    prepare_local_httpserver_mock(calendar_url, username, password, httpserver)

    # Run icalendar-events-cli
    calendar_url = httpserver.url_for(calendar_url)
    output_path = f"{tmp_path}/{output_file}" if output_file else None
    args = (
        f"--output.format json --calendar.url {calendar_url}"
        + build_basicauth_cli_arg(username, password)
        + f" --filter.start-date {start_date.isoformat()} --filter.end-date {end_date.isoformat()}"
        + build_filter_cli_arg(filter_summary, filter_description, filter_location)
        + build_output_file_cli_arg(output_path)
    )

    cli_result = run_cli_json(args, capsys, output_path)
    assert cli_result.exit_code == os.EX_OK

    json_output = None
    if output_path is None:
        json_output = cli_result.stdout_as_json
    else:
        json_output = cli_result.fileout_as_json
    assert json_output is not None

    json_filter = json_output["filter"]
    assert json_filter["start-date"] == start_date.isoformat()
    assert json_filter["end-date"] == end_date.isoformat()
    if filter_summary:
        assert json_filter["summary"] == filter_summary
    if filter_description:
        assert json_filter["description"] == filter_description
    if filter_location:
        assert json_filter["location"] == filter_location

    json_events = json_output["events"]
    assert len(json_events) == len(expected_events)

    for events_index, expected_event in enumerate(expected_events):
        assert re.match(expected_event.summary, json_events[events_index]["summary"])
        assert expected_event.start_date.isoformat() == json_events[events_index]["start-date"]
        assert expected_event.end_date.isoformat() == json_events[events_index]["end-date"]

        if expected_event.description is not None:
            assert re.match(expected_event.description, json_events[events_index]["description"])
        else:
            assert "description" not in json_events[events_index]

        if expected_event.location is not None:
            assert re.match(expected_event.location, json_events[events_index]["location"])
        else:
            assert "location" not in json_events[events_index]


@pytest.mark.parametrize(
    "calendar_url,start_date,end_date,filter_summary,filter_description,filter_location,"
    + "expected_events,username,password",
    test_queries,
)
@pytest.mark.parametrize("output_file", [None, "icalendar_events_cli_test.json"])
def test_ct_valid_query_outputformat_jcal(
    calendar_url: str,
    start_date: datetime,
    end_date: datetime,
    filter_summary: str,
    filter_description: str,
    filter_location: str,
    expected_events: list[ExpectedEvent],
    username: str,
    password: str,
    output_file: str | None,
    httpserver: HTTPServer,
    tmp_path: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test calendar queries with output format 'jCal'.

    Arguments:
        calendar_url: ICS calendar URL,
        start_date: Start Date
        end_date: End Date,
        filter_summary: summary filter
        filter_description: description filter
        filter_location: location filter
        expected_events: List of expected events
        username: Username for basicAuth
        password: Password for basicAuth
        output_file: JSON output file name. If not set JSON output is written to console / stdout.
        httpserver: Mocked HTTP server
        tmp_path: Temporary unique file path provided by built-in fixture.
        capsys: System capture
    """
    prepare_local_httpserver_mock(calendar_url, username, password, httpserver)

    # Run icalendar-events-cli
    calendar_url = httpserver.url_for(calendar_url)
    output_path = f"{tmp_path}/{output_file}" if output_file else None
    args = (
        f"--output.format jcal --calendar.url {calendar_url}"
        + build_basicauth_cli_arg(username, password)
        + f" --filter.start-date {start_date.isoformat()} --filter.end-date {end_date.isoformat()}"
        + build_filter_cli_arg(filter_summary, filter_description, filter_location)
        + build_output_file_cli_arg(output_path)
    )

    cli_result = run_cli_json(args, capsys, output_path)
    assert cli_result.exit_code == os.EX_OK

    json_output = None
    if output_path is None:
        json_output = cli_result.stdout_as_json
    else:
        json_output = cli_result.fileout_as_json
    assert json_output is not None

    assert json_output[0] == "vcalendar"

    # Verify jCal properties (meta-data)
    jcal_properties = json_output[1]

    assert any(
        prop[0] == "x-filter-date-range"
        and prop[1] == {}
        and prop[2] == "period"
        and prop[3] == [start_date.isoformat(), end_date.isoformat()]
        for prop in jcal_properties
    )
    if filter_summary:
        assert any(
            prop[0] == "x-filter-summary" and prop[1] == {} and prop[2] == "text" and prop[3] == filter_summary
            for prop in jcal_properties
        )
    if filter_description:
        assert any(
            prop[0] == "x-filter-description" and prop[1] == {} and prop[2] == "text" and prop[3] == filter_description
            for prop in jcal_properties
        )
    if filter_location:
        assert any(
            prop[0] == "x-filter-location" and prop[1] == {} and prop[2] == "text" and prop[3] == filter_location
            for prop in jcal_properties
        )

    # Verify jCal components (=filtered events)
    jcal_components = json_output[2]
    assert len(jcal_components) == len(expected_events)

    for events_index, expected_event in enumerate(expected_events):
        jcal_event = jcal_components[events_index]
        assert jcal_event[0] == "vevent"
        jcal_event_attribs = jcal_event[1]

        assert any(
            attrib[0] == "summary" and re.match(expected_event.summary, attrib[3]) for attrib in jcal_event_attribs
        )
        assert any(
            attrib[0] == "dtstart" and re.match(expected_event.start_date.date().isoformat(), attrib[3])
            for attrib in jcal_event_attribs
        )
        # assert any(
        #    attrib[0] == "dtend" and re.match(expected_event.end_date.date().isoformat(), attrib[3])
        #    for attrib in jcal_event_attribs
        # )

        if expected_event.description is not None:
            assert any(
                attrib[0] == "description" and re.match(expected_event.description, attrib[3])
                for attrib in jcal_event_attribs
            )
        else:
            assert not any(attrib[0] == "description" for attrib in jcal_event_attribs)

        if expected_event.location is not None:
            assert any(
                attrib[0] == "location" and re.match(expected_event.location, attrib[3])
                for attrib in jcal_event_attribs
            )
        else:
            assert not any(attrib[0] == "location" for attrib in jcal_event_attribs)

    # Try to parse the output with iCalendar jCal
    # calendar = Calendar.from_jcal(json_output)
    # assert calendar is not None


@pytest.mark.parametrize(
    "calendar_url,start_date,end_date,filter_summary,filter_description,filter_location,"
    + "expected_events,username,password",
    test_queries,
)
@pytest.mark.parametrize("output_file", [None, "icalendar_events_cli_test.json"])
def test_ct_valid_query_outputformat_humanreadable(
    calendar_url: str,
    start_date: datetime,
    end_date: datetime,
    filter_summary: str,
    filter_description: str,
    filter_location: str,
    expected_events: list[ExpectedEvent],
    username: str,
    password: str,
    output_file: str | None,
    httpserver: HTTPServer,
    tmp_path: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test calendar queries with output format 'human readable'.

    Arguments:
        calendar_url: ICS calendar URL,
        start_date: Start Date
        end_date: End Date,
        filter_summary: summary filter
        filter_description: description filter
        filter_location: location filter
        expected_events: List of expected events
        username: Username for basicAuth
        password: Password for basicAuth
        output_file: JSON output file name. If not set JSON output is written to console / stdout.
        httpserver: Mocked HTTP server
        tmp_path: Temporary unique file path provided by built-in fixture.
        capsys: System capture
    """
    prepare_local_httpserver_mock(calendar_url, username, password, httpserver)

    # Run icalendar-events-cli
    calendar_url = httpserver.url_for(calendar_url)
    output_path = f"{tmp_path}/{output_file}" if output_file else None
    args = (
        f"--output.format human_readable --calendar.url {calendar_url} --calendar.verify-url false"
        + build_basicauth_cli_arg(username, password)
        + f" --filter.start-date {start_date.isoformat()} --filter.end-date {end_date.isoformat()}"
        + build_output_file_cli_arg(output_path)
        + build_filter_cli_arg(filter_summary, filter_description, filter_location)
    )

    cli_result = run_cli(args, capsys, output_path)
    assert cli_result.exit_code == os.EX_OK

    output_lines = None
    if output_path is None:
        output_lines = cli_result.stdout_lines
    else:
        output_lines = cli_result.fileout_lines
    assert output_lines is not None
    joined_lines = "\n".join(output_lines)

    assert f"Start Date:         {start_date.strftime('%Y-%m-%d')}" in joined_lines
    assert f"End Date:           {end_date.strftime('%Y-%m-%d')}" in joined_lines
    if filter_summary != "":
        assert f"Summary Filter:     {filter_summary}" in joined_lines
    if filter_description != "":
        assert f"Description Filter: {filter_description}" in joined_lines
    if filter_location != "":
        assert f"Location Filter:    {filter_location}" in joined_lines
    assert f"Number of Events:   {len(expected_events)}" in joined_lines

    header_lines = 4  # start- / end-date, number of events, empty line at end
    if filter_summary != "":
        header_lines += 1
    if filter_description != "":
        header_lines += 1
    if filter_location != "":
        header_lines += 1

    events_output_lines = output_lines[header_lines:]
    assert len(events_output_lines) == len(expected_events)

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
    args = (
        f"--calendar.url {invalid_url} --filter.start-date 2025-01-01 --filter.end-date 2025-01-17"
        + " --filter.summary xxx --output.format json"
    )

    cli_result = run_cli(args, capsys)

    assert cli_result.exit_code != 0
    assert "Max retries exceeded with url" in cli_result.stdout


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
    args = (
        f"--calendar.url {calendar_url} --filter.start-date {start_date} --filter.end-date {end_date}"
        + " --filter.summary invalid --output.format json"
    )

    cli_result = run_cli(args, capsys)
    assert cli_result.exit_code != os.EX_OK

    assert "Failed to download ical contents from URL" in cli_result.stdout

"""Test of general commands."""

import importlib
import re

import pytest

from icalendar_events_cli.__main__ import __dist_name__, __prog__
from icalendar_events_cli.constants import Os
from tests.util_runner import run_cli

# ---- Testcases -------------------------------------------------------------------------------------------------------


def test_ct_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the --help option.

    Arguments:
        capsys: System capture
    """
    args = "--help"

    cli_result = run_cli(args, capsys)

    assert cli_result.exit_code == Os.EX_OK
    assert cli_result.stdout.startswith(f"Usage: {__prog__}")


def test_ct_version(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the --version option.

    Arguments:
        capsys: System capture
    """
    args = "--version"

    cli_result = run_cli(args, capsys)

    assert cli_result.exit_code == Os.EX_OK
    assert importlib.metadata.version(__dist_name__) in cli_result.stdout
    assert importlib.metadata.version(__prog__) in cli_result.stdout


@pytest.mark.parametrize(
    "cli_args,expected_output",
    [
        (
            "",
            r"the following arguments are required: calendar\.url",
        ),
        (
            "--filter.start-date 2025",
            r"invalid datetime value \(expected ISO 8601 format\): '2025'",
        ),
        (
            "--filter.start-date 2025-01-17T10:00:00+01:00 --filter.end-date 2025-01-17T08:00:00+01:00 "
            + "--calendar.url=dummy",
            r"filter\.end-date must be after filter\.start-date",
        ),
        # compare localized and not-localized dates
        (
            "--filter.start-date 2025-10-08 --filter.end-date 2025-10-06T08:00:00+01:00 --calendar.url=dummy",
            r"filter\.end-date must be after filter\.start-date",
        ),
        # invalid summary filter RegEx
        (
            "--filter.summary [ --calendar.url=dummy",
            r"--filter\.summary.*invalid RegEx value '\['",
        ),
    ],
)
def test_ct_invalid_arguments(cli_args: str, expected_output: str, capsys: pytest.CaptureFixture[str]) -> None:
    """Test that invalid cli arguments are detected.

    Arguments:
        cli_args: Tested command line arguments
        expected_output: Expected output (RegEx)
        capsys: System capture
    """
    cli_result = run_cli(cli_args, capsys)
    assert cli_result.exit_code != Os.EX_OK

    assert re.search(expected_output, cli_result.stderr, re.MULTILINE)

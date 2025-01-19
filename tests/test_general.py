"""Test of general commands."""

import importlib
import os

import pytest

from icalendar_events_cli.__main__ import __dist_name__, __prog__
from tests.util_runner import run_cli

# ---- Testcases -------------------------------------------------------------------------------------------------------


def test_ct_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the --help option.

    Arguments:
        capsys: System capture
    """
    args = "--help"

    cli_result = run_cli(args, capsys)

    assert cli_result.exit_code == os.EX_OK
    assert cli_result.stdout.startswith(f"Usage: {__prog__}")


def test_ct_version(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the --version option.

    Arguments:
        capsys: System capture
    """
    args = "--version"

    cli_result = run_cli(args, capsys)

    assert cli_result.exit_code == os.EX_OK
    assert importlib.metadata.version(__dist_name__) in cli_result.stdout
    assert importlib.metadata.version(__prog__) in cli_result.stdout


def test_ct_invalid_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that invalid cli arguments are detected.

    Arguments:
        capsys: System capture
    """
    args = "--filter.start-date 2025"

    cli_result = run_cli(args, capsys)
    assert cli_result.exit_code != os.EX_OK

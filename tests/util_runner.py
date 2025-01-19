"""Utility for tool runner."""

import json
import shlex
from ast import Dict
from dataclasses import dataclass

import pytest

from icalendar_events_cli.__main__ import cli

# ---- Utilities -------------------------------------------------------------------------------------------------------


@dataclass
class CliResult:
    """Class containing results of CLI run."""

    exit_code: int
    stdout: str
    stdout_as_json: dict | None

    def __init__(self, exit_code: int, stdout: str, stdout_as_json: dict | None = None) -> None:
        """Construct.

        Arguments:
            exit_code: Numeric process exit code
            stdout: Captured stdout
            stdout_as_json: Optional stdout parsed as JSON
        """
        self.exit_code = exit_code
        self.stdout = stdout
        self.stdout_as_json = stdout_as_json


def run_cli(cli_args: str, capsys: pytest.CaptureFixture) -> CliResult:
    """Run the command line util with the passed arguments.

    Arguments:
        cli_args: The command line arguments string passed.
        capsys: System capture

    Returns:
        str: Captured stdout
    """
    exit_code = cli(shlex.split(cli_args))
    capture_result = capsys.readouterr()
    stdout = capture_result.out.rstrip()
    return CliResult(exit_code, stdout)


def run_cli_stdout_json(cli_args: str, capsys: pytest.CaptureFixture) -> Dict:
    """Run the command line util with the passed arguments and capture the outputs from a JSON file.

    Arguments:
        cli_args: The command line arguments string passed.
        capsys: System capture

    Returns:
        Dict: Parsed JSON output from stdout.
    """
    cli_result = run_cli(cli_args, capsys)

    assert cli_result.stdout != ""
    parsed_json = json.loads(cli_result.stdout)

    cli_result.stdout_as_json = parsed_json
    return cli_result

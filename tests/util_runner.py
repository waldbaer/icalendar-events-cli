"""Utility for tool runner."""

import json
import os
import shlex
from dataclasses import dataclass
from typing import Dict, List

import pytest

from icalendar_events_cli.__main__ import cli

# ---- Utilities -------------------------------------------------------------------------------------------------------


@dataclass
class CliResult:
    """Class containing results of CLI run."""

    exit_code: int
    stdout: str
    stderr: str
    stdout_lines: List[str]
    stdout_as_json: dict | None
    fileout: str
    fileout_lines: List[str]
    fileout_as_json: dict | None

    def __init__(
        self,
        exit_code: int,
        stdout: str,
        stderr: str,
        stdout_lines: List[str],
        stdout_as_json: dict | None = None,
        fileout: str = None,
        fileout_lines: List[str] = None,
        fileout_as_json: dict | None = None,
    ) -> None:
        """Construct.

        Arguments:
            exit_code: Numeric process exit code
            stdout: Captured stdout
            stderr: Captured stderr
            stdout_lines: Captured stdout splitted into individual lines
            stdout_as_json: Optional stdout parsed as JSON
            fileout: Captured output in output file
            fileout_lines: Captured output in output file splitted into individual lines
            fileout_as_json: Optional output file parsed as JSON
        """
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.stdout_lines = stdout_lines
        self.stdout_as_json = stdout_as_json
        self.fileout = fileout
        self.fileout_lines = fileout_lines
        self.fileout_as_json = fileout_as_json


def run_cli(cli_args: str, capsys: pytest.CaptureFixture, output_path: str | None = None) -> CliResult:
    """Run the command line util with the passed arguments.

    Arguments:
        cli_args: The command line arguments string passed.
        capsys: System capture
        output_path: If set get the JSON from this file instead from stdout

    Returns:
        str: Captured stdout
    """
    exit_code = cli(shlex.split(cli_args))
    capture_result = capsys.readouterr()
    stdout = capture_result.out.rstrip()
    stderr = capture_result.err.rstrip()
    stdout_lines = stdout.splitlines()
    fileout = None
    fileout_lines = None
    if output_path is not None:
        with open(file=output_path, encoding="UTF-8") as file:
            fileout_lines = file.readlines()
            fileout = os.linesep.join(fileout_lines)
    return CliResult(
        exit_code, stdout, stderr, stdout_lines, stdout_as_json=None, fileout=fileout, fileout_lines=fileout_lines
    )


def run_cli_json(cli_args: str, capsys: pytest.CaptureFixture, output_path: str | None = None) -> Dict:
    """Run the command line util with the passed arguments and capture the outputs from a JSON file.

    Arguments:
        cli_args: The command line arguments string passed.
        capsys: System capture
        output_path: If set get the JSON from this file instead from stdout

    Returns:
        Dict: Parsed JSON output from stdout.
    """
    cli_result = run_cli(cli_args, capsys, output_path)

    if output_path is None:
        assert cli_result.stdout != ""
        stdout_as_json = json.loads(cli_result.stdout)
        assert stdout_as_json is not None
        cli_result.stdout_as_json = stdout_as_json
    else:
        fileout_as_json = json.loads(cli_result.fileout)
        assert fileout_as_json is not None
        cli_result.fileout_as_json = fileout_as_json

    return cli_result

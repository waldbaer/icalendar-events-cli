# Proposal

## Why

On Windows, Python 3.10 to 3.14 encode stdout with the ANSI code page (usually cp1252) when it is a pipe or a
redirect, which is how Node-RED runs the tool. A simulation with a cp1252 stdout showed:

- `ä` is written as the single byte `0xE4`, which a UTF-8 reader such as Node-RED decodes as garbage.
- A character outside the code page, such as an emoji in an event summary, aborts the output halfway with
  `'charmap' codec can't encode character`, leaving incomplete JSON on stdout.

Python 3.15 defaults to UTF-8 (PEP 686), so the same query behaves differently depending on the Python version. File
output is already UTF-8 by spec.

## What Changes

- The result is written to stdout in UTF-8 in every format, independent of the system locale and console code page.
- Help, version and error messages on stdout and stderr are UTF-8 too. Today stderr writes characters outside the
  code page as escapes such as `\U0001f389`, and stdout messages use the code page.
- Line endings do not change. They are fixed in `fix-ci-os-matrix` (pull request #82).
- `CHANGELOG.md` gets a fix entry, and the README states that output is UTF-8.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `event-output`: "Output target" requires UTF-8 on stdout, as it already does for files.
- `cli-configuration`: new requirement "Message encoding" for help, version and error messages.

## Impact

- Code: `src/icalendar_events_cli/__main__.py` (stream setup at the start of `cli()`).
- Tests: new tests that run the CLI with a cp1252 stdout and stderr.
- Docs: `CHANGELOG.md`, `README.md` (automation section).
- Compatibility: on Windows with Python 3.10 to 3.14, piped output changes from the ANSI code page to UTF-8. On Linux
  and macOS it changes only for systems with a non-UTF-8 locale. Output on the Windows console looks the same. This
  restores the behavior JSON consumers expect and fits a patch release.

# Spec Delta

## ADDED Requirements

### Requirement: Line endings

In every output format, on stdout and in output files, each line break SHALL be written as the platform's line
separator, exactly once: CR LF on Windows, LF on Linux and macOS.

#### Scenario: Human-readable output to a file on Windows

- **WHEN** the tool runs on Windows with `--output.format human_readable --output.file out.txt` and two events match
- **THEN** every line break in `out.txt` is CR LF
- **AND** `out.txt` contains no CR CR LF sequence

#### Scenario: Human-readable output on Linux

- **WHEN** the tool runs on Linux with `--output.format human_readable`
- **THEN** every line on stdout ends with LF and stdout contains no CR

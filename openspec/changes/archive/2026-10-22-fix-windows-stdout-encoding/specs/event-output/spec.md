# Spec Delta

## MODIFIED Requirements

### Requirement: Output target

The tool SHALL write the result to stdout in UTF-8 when `output.file` is not set, independent of the system locale
and console code page. When `output.file` is set, the tool SHALL write the result to that file in UTF-8, replacing
any existing content, and SHALL NOT write the result to stdout.

#### Scenario: Output to stdout

- **WHEN** no `--output.file` is given
- **THEN** the result is printed on stdout

#### Scenario: Output to a file

- **WHEN** `--output.file ./GermanHolidays.json` is given
- **THEN** the result is written to `./GermanHolidays.json`
- **AND** nothing is printed on stdout

#### Scenario: Non-ASCII text on a stdout with another code page

- **WHEN** stdout uses the cp1252 code page, as a pipe does on Windows with Python 3.10 to 3.14, and the result
  contains `jährlich`
- **THEN** stdout receives the UTF-8 bytes of `jährlich`

#### Scenario: Character outside the code page

- **WHEN** stdout uses the cp1252 code page and an event summary contains the character 🎉
- **THEN** the complete result is written to stdout in UTF-8
- **AND** the tool exits with code 0

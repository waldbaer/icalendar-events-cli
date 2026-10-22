# Spec Delta

## MODIFIED Requirements

### Requirement: Text decoding

The tool SHALL decode the calendar content as UTF-8 unless the server explicitly declares a different charset. A
leading byte order mark SHALL be ignored. Bytes that are invalid in the charset used SHALL be replaced with the
Unicode replacement character U+FFFD instead of aborting the query.

#### Scenario: Local UTF-8 file with non-ASCII characters

- **WHEN** a `file://` calendar contains the UTF-8 text `jährlich`
- **THEN** the output contains `jährlich`

#### Scenario: HTTP response without charset

- **WHEN** a server returns a UTF-8 calendar containing `jährlich` with `Content-Type: text/calendar` and no charset
- **THEN** the output contains `jährlich`

#### Scenario: HTTP response with a declared charset

- **WHEN** a server returns an ISO-8859-1 encoded calendar containing `jährlich` with
  `Content-Type: text/calendar; charset=ISO-8859-1`
- **THEN** the output contains `jährlich`

#### Scenario: UTF-8 byte order mark

- **WHEN** the calendar content starts with the UTF-8 byte order mark and no charset is declared
- **THEN** the calendar is parsed as if the byte order mark were absent

#### Scenario: Content that is not valid UTF-8

- **WHEN** a server returns an ISO-8859-1 encoded calendar containing `jährlich` with `Content-Type: text/calendar`
  and no charset
- **THEN** the query succeeds and the output contains `j�hrlich`, with U+FFFD in place of the invalid byte

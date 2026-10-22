# calendar-source Specification

## Purpose

Retrieves the calendar from a remote HTTP(S) server or a local file and parses it, detecting automatically whether
it is in iCalendar (RFC 5545) or jCal (RFC 7265) format.

## Requirements

### Requirement: Retrieve a calendar over HTTP(S)

The tool SHALL retrieve the calendar with an HTTP GET request to the configured `calendar.url` when it uses the
`http://` or `https://` scheme.

#### Scenario: Remote calendar

- **WHEN** `--calendar.url https://www.thunderbird.net/media/caldata/autogen/GermanHolidays.ics` is given
- **THEN** the tool downloads the calendar from that URL and queries its events

### Requirement: Retrieve a calendar from a local file

The tool SHALL read the calendar from the local file system when `calendar.url` uses the `file://` scheme followed by
an absolute path.

#### Scenario: Local calendar file

- **WHEN** `--calendar.url file:///home/user/GermanHolidays.json` is given and the file exists
- **THEN** the tool reads and queries that file

#### Scenario: Local file does not exist

- **WHEN** `--calendar.url file:///nonexistent.ics` is given
- **THEN** the tool reports a download failure for that URL, including the "No such file or directory" reason
- **AND** exits with code 1

### Requirement: HTTP basic authentication

When both `calendar.user` and `calendar.password` are configured, the tool SHALL send them as HTTP basic
authentication credentials. When either is missing, the tool SHALL send the request without credentials. The tool
SHALL NOT include the configured credentials in its output.

#### Scenario: Credentials configured

- **WHEN** `--calendar.user dummy_user --calendar.password test_password` is given
- **THEN** the request carries the header `Authorization: Basic <base64 of "dummy_user:test_password">`

#### Scenario: Only a username configured

- **WHEN** `--calendar.user dummy_user` is given without a password
- **THEN** the request carries no `Authorization` header

### Requirement: TLS certificate verification

The tool SHALL verify the server's TLS certificate for `https://` URLs by default. When `calendar.verify-url` is
`false`, the tool SHALL skip that verification.

#### Scenario: Verification disabled

- **WHEN** `--calendar.verify-url false` is given for a server with a self-signed certificate
- **THEN** the calendar is downloaded without a certificate error

### Requirement: Download failure handling

When the response status is anything other than 200, the tool SHALL print
`ERROR: Failed to download ical contents from URL '<url>'. Response status: <reason> (status <code>)` on stdout and
exit with code 1 without producing calendar output. When no response is received at all (for example the host cannot
be resolved or the connection is refused), the tool SHALL report the error as an unexpected error and exit with
code 1.

#### Scenario: Server returns an error status

- **WHEN** the server answers the calendar request with status 404
- **THEN** stdout contains `Failed to download ical contents from URL`
- **AND** the tool exits with code 1

#### Scenario: Host cannot be reached

- **WHEN** `--calendar.url https://www.INVALID_URL.123/INVALID_ICS_FILE.icsx` is given
- **THEN** the tool prints the connection error (for example `Max retries exceeded with url`) on stdout
- **AND** exits with code 1

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

### Requirement: Automatic input format detection

The tool SHALL detect the calendar format from the content, independent of the URL's file extension or the response's
content type: content that is valid JSON SHALL be parsed as jCal (RFC 7265), and any other content SHALL be parsed as
iCalendar (RFC 5545).

#### Scenario: iCalendar input

- **WHEN** the retrieved content starts with `BEGIN:VCALENDAR`
- **THEN** it is parsed as iCalendar and its events are queried

#### Scenario: jCal input

- **WHEN** the retrieved content is a JSON array starting with `"vcalendar"`
- **THEN** it is parsed as jCal and the same query returns the same events as for the equivalent iCalendar file

#### Scenario: Unparseable content

- **WHEN** the retrieved content is neither valid JSON nor valid iCalendar, for example the text `hello`
- **THEN** the tool reports the parse error as an unexpected error
- **AND** exits with code 1

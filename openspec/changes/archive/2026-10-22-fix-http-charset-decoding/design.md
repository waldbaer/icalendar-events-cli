# Design

## Context

`download_calendar` returns `response.text`, so requests chooses the charset:

- the charset from the `Content-Type` header, when one is declared;
- ISO-8859-1 for any `text/*` type without a charset (an old HTTP/1.1 default that RFC 7231 dropped);
- a guess based on the content when there is no `Content-Type` at all. This is always the case for `file://`,
  because requests-file only sends `Content-Length`.

The tests never reach the no-charset path: pytest-httpserver's `respond_with_data(str)` sends
`text/plain; charset=utf-8`.

A UTF-8 byte order mark that stays in the decoded text breaks iCalendar parsing (`Content line could not be parsed
into parts`). `json.loads` rejects it too, so jCal detection falls back to iCalendar and fails.

## Goals / Non-Goals

**Goals:**

- Decoding gives the same result whatever the platform's default encoding is (for example cp1252 on Windows), and it
  never guesses from the content.

**Non-Goals:**

- Bringing back a `--calendar.encoding` option (removed in 2.0.0).
- Detecting non-UTF-8 content heuristically.
- Byte order marks of UTF-16 or UTF-32.

## Decisions

1. **Decode in the downloader and keep passing text to the parsers.** The alternative, handing raw bytes to
   icalendar and `json.loads`, would ignore a declared charset and split decoding between two parsers.

2. **Read the declared charset with `email.message.Message.get_content_charset()`** from the standard library. It
   parses `Content-Type` parameters, including quoting and case. Rejected alternatives:
   - `requests.utils.get_encoding_from_headers`: it returns ISO-8859-1 for undeclared `text/*`, so a declared charset
     cannot be told apart from the default.
   - `requests.utils._parse_content_type_header`: private API.
   - A hand-written regex: easy to get quoting and case wrong.

3. **Without a declared charset, set `response.encoding = "utf-8"` and keep using `response.text`.** `response.text`
   already replaces invalid bytes with U+FFFD. Rejected alternatives:
   - Strict decoding: a single bad byte in one description would abort the whole query for the calling automation.
   - Falling back to ISO-8859-1 when UTF-8 decoding fails: this contradicts the UTF-8 default and makes the result
     depend on the content.

4. **Strip one leading U+FEFF from the decoded text, whatever the charset.** This covers a byte order mark both with
   and without a declared UTF-8 charset. The `utf-8-sig` codec would cover only the undeclared case.

5. **Test data is generated from the existing UTF-8 fixtures at test time**: re-encoded to ISO-8859-1, or prefixed
   with a byte order mark. The bytes are served through pytest-httpserver with an explicit `content_type`
   (`respond_with_data(data, content_type="text/calendar")`), which sends no charset. The `file://` test builds its
   URL with `pathlib.Path(...).absolute().as_uri()`, so the URL is also valid on Windows (`file:///C:/...`).

A throwaway prototype of decisions 2 to 4 decoded `GermanHolidays.ics` correctly when served as UTF-8 over HTTP
without a charset, as UTF-8 with a byte order mark, and through `file://`. It produced `j\uFFFDhrlich` for ISO-8859-1
content without a charset.

## Risks / Trade-offs

- [A server that sends ISO-8859-1 content without a charset now shows U+FFFD instead of accented characters] → RFC
  5545 requires UTF-8, and such a server only worked by accident. The changelog entry states the new behavior.
- [`file://` URLs look different on Windows] → tests build them with `Path.as_uri()`, and CI runs on Windows.
- [Removing a leading U+FEFF changes content that starts with it on purpose] → no valid iCalendar or jCal document
  starts with that character.

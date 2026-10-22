# Design

## Context

- Results go to stdout through `print()` (human-readable) and `json.dump(fp=sys.stdout)` (JSON, jCal). Error messages
  use `print()` on stdout, and jsonargparse writes argument errors to stderr.
- Python picks the stream encodings at startup. On Windows with Python 3.10 to 3.14, a console uses UTF-8 (PEP 528),
  but a pipe or redirect uses the ANSI code page. stdout uses `errors="strict"`, stderr `errors="backslashreplace"`.
  Python 3.15 enables UTF-8 mode by default (PEP 686). On Linux and macOS the locale decides, and a C or POSIX locale
  is coerced to UTF-8.
- pytest's `capsys` replaces the streams with UTF-8 buffers, so the existing tests never see the code page problem.

## Goals / Non-Goals

**Goals:**

- UTF-8 on stdout and stderr on every platform and supported Python version.

**Non-Goals:**

- Changing line endings. See `fix-ci-os-matrix` (pull request #82).
- Writing a byte order mark.
- Changing where messages go (stdout or stderr).

## Decisions

- **Reconfigure both streams at the start of `cli()`.** For `sys.stdout` and `sys.stderr`, call
  `reconfigure(encoding="utf-8")` when the stream supports it, keeping each stream's error handler and newline
  setting. Doing this before argument parsing covers results, help, version and error messages in one place.
  - *Alternative:* encode the result and write bytes to `sys.stdout.buffer` in each output function. Rejected,
    because it leaves messages out and needs the same code in three places.
  - *Alternative:* tell users to set `PYTHONUTF8=1`. Rejected, because every Node-RED flow would need it, and the
    default should be correct.
- **Skip streams without `reconfigure()`.** `sys.stdout` can be `None` (for example under `pythonw`) or replaced by
  an embedding application with a stream that has no `reconfigure()`. Such streams are left as they are.
- **Keep `errors` unchanged.** UTF-8 can encode every string the tool produces, because downloaded text is decoded
  with replacement characters and contains no lone surrogates.

## Risks / Trade-offs

- [Callers that decode the tool's piped output with the Windows code page] → They now get UTF-8. JSON consumers
  expect UTF-8 (RFC 8259, section 8.1), and Python 3.15 does the same anyway. Changelog entry.
- [Linux or macOS systems with a non-UTF-8 locale] → Output becomes UTF-8 there too, consistent with file output.
  Such locales are rare.
- [`cli()` changes process-wide streams when used as a library] → `cli()` is the console entry point, and the tests
  call it the same way. Documented in the docstring.
- [Windows console] → Already UTF-8, so reconfiguring changes nothing visible.

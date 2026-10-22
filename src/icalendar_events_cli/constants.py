"""Constants shared across the package."""

# ---- Classes ---------------------------------------------------------------------------------------------------------


class Os:  # pylint: disable=too-few-public-methods;reason=Namespace for constants only.
    r"""Platform-independent replacements for constants of the os module.

    Used like the os module, e.g. Os.linesep instead of os.linesep. The os constants are not usable on all supported
    platforms and Python versions.

    Attributes:
        EX_OK: Exit code for successful termination (0). Same value as os.EX_OK, which is missing on Windows before
            Python 3.11.
        EX_ERROR: Exit code for a general error (1), e.g. an invalid configuration or a failed calendar download.
        linesep: Line separator for text written to stdout or to files opened in text mode ("\n"). Python translates
            it to the platform line ending when writing, so the output gets "\r\n" on Windows. Do not use
            os.linesep for this: it is "\r\n" on Windows, which Python writes as "\r\r\n".
    """

    EX_OK = 0
    EX_ERROR = 1
    linesep = "\n"


class StringEncoding:  # pylint: disable=too-few-public-methods;reason=Namespace for constants only.
    r"""Constants for string encodings.

    Attributes:
        UTF_8: Name of the UTF-8 encoding ("utf-8"), as accepted by open(), str.encode() and bytes.decode(). Encoding
            of output files and default charset of downloaded calendars (RFC 5545).
        BYTE_ORDER_MARK: Byte order mark, the Unicode character U+FEFF ("﻿"). Some programs put it at the start of
            a text to mark its encoding. It is not part of the content and is removed from downloaded calendars.
    """

    UTF_8 = "utf-8"
    BYTE_ORDER_MARK = "﻿"

import logging
import sys


# ANSI colour codes
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_CYAN   = "\033[96m"
_GREEN  = "\033[92m"
_YELLOW = "\033[93m"
_RED    = "\033[91m"
_PURPLE = "\033[95m"
_GREY   = "\033[90m"

# Map each log level to a colour
_LEVEL_COLOUR = {
    "DEBUG":    _CYAN,
    "INFO":     _GREEN,
    "WARNING":  _YELLOW,
    "ERROR":    _RED,
    "CRITICAL": _PURPLE,
}


class _CustomFormatter(logging.Formatter):
    """
    Formats every log line as:

        LEVEL   │  module.name  │  message

    No timestamp. Colour is applied to the level label only so the module
    name and message stay easy to read.
    """

    def format(self, record: logging.LogRecord) -> str:
        colour  = _LEVEL_COLOUR.get(record.levelname, _RESET)
        level   = f"{record.levelname:<8}"          # pad to 8 chars for alignment
        module  = f"{record.name:<35}"              # pad module name for alignment
        message = record.getMessage()

        line = (
            f"{_BOLD}{colour}{level}{_RESET}"
            f"  {_GREY}{module}{_RESET}"
            f"  {message}"
        )

        if record.exc_info:
            line += f"\n{self.formatException(record.exc_info)}"

        return line


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger for the given module name.

    Usage in any module:
        from logger import get_logger
        logger = get_logger(__name__)
        logger.info("Session created: %s", session_id)

    Output example:
        INFO      database.models                    Session created: abc-123
        ERROR     api.interview                      Failed to start interview
    """
    logger = logging.getLogger(name)

    # Only add the handler once — avoids duplicate lines on hot-reload
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_CustomFormatter())
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger

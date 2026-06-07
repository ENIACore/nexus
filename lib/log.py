#!/usr/bin/env python3
# Logger functionality with rotating logs for Nexus scripts - /opt/nexus/lib/log.py

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import print_error, print_info

# ------------------------------------------------------------------------------
# Private State
# ------------------------------------------------------------------------------
_NEXUS_LOG_FILE: Path | None = None
_NEXUS_MAX_LOG_LINES: int = 1000
_NEXUS_LOG_COUNT: int = 0
_NEXUS_LOG_INITIALIZED: bool = False


# ------------------------------------------------------------------------------
# Public Functions
# ------------------------------------------------------------------------------


def init_logger(log_file: str, max_lines: int = 1000) -> bool:
    """Initialize the logger with a file path and optional max lines.

    Args:
        log_file: Path to log file (required)
        max_lines: Maximum lines before rotation (default: 1000)

    Returns:
        True on success, False on failure
    """
    global \
        _NEXUS_LOG_FILE, \
        _NEXUS_MAX_LOG_LINES, \
        _NEXUS_LOG_COUNT, \
        _NEXUS_LOG_INITIALIZED

    if not log_file:
        print_error("ERROR: Log file path is required.")
        print_error("Usage: init_logger(log_file, max_lines=1000)")
        return False

    if not isinstance(max_lines, int) or max_lines <= 0:
        print_error("ERROR: max_lines must be a positive integer.")
        return False

    log_path = Path(log_file)
    log_dir = log_path.parent

    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            print_error(f"ERROR: Could not create log directory: {log_dir}")
            return False

    _NEXUS_LOG_FILE = log_path
    _NEXUS_MAX_LOG_LINES = max_lines
    _NEXUS_LOG_COUNT = 0
    _NEXUS_LOG_INITIALIZED = True
    return True


def log(message: str = "") -> bool:
    """Log a message with timestamp to both stdout and the log file.

    Args:
        message: Message to log

    Returns:
        True on success, False if logger not initialized
    """
    global _NEXUS_LOG_COUNT

    if not _NEXUS_LOG_INITIALIZED:
        print_error("ERROR: Logger not initialized. Call init_logger first.")
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"

    print_info(log_entry)

    assert _NEXUS_LOG_FILE is not None
    with open(_NEXUS_LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

    _NEXUS_LOG_COUNT += 1

    if _NEXUS_LOG_COUNT % 15 == 0:
        _rotate_log()

    return True


def get_log_file() -> str:
    """Get the current log file path.

    Returns:
        The log file path as a string, or empty string if not initialized
    """
    return str(_NEXUS_LOG_FILE) if _NEXUS_LOG_FILE else ""


# ------------------------------------------------------------------------------
# Private Functions
# ------------------------------------------------------------------------------


def _rotate_log() -> None:
    """Rotate the log file if it exceeds the maximum line count.
    Keeps only the most recent _NEXUS_MAX_LOG_LINES lines.
    """
    if not _NEXUS_LOG_FILE or not _NEXUS_LOG_FILE.exists():
        return

    lines = _NEXUS_LOG_FILE.read_text().splitlines()
    if len(lines) > _NEXUS_MAX_LOG_LINES:
        trimmed = lines[-_NEXUS_MAX_LOG_LINES:]
        tmp = _NEXUS_LOG_FILE.with_suffix(".tmp")
        tmp.write_text("\n".join(trimmed) + "\n")
        tmp.replace(_NEXUS_LOG_FILE)


init_logger("/tmp/test.log")
log("test log")

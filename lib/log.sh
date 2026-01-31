#!/bin/bash
# Logger functionality with rotating logs for Nexus scripts - /opt/nexus/lib/log.sh

source "/opt/nexus/lib/print.sh"
source "/etc/nexus/conf/conf.sh"

set -o nounset

# ------------------------------------------------------------------------------
# Private State
# ------------------------------------------------------------------------------

_NEXUS_LOG_FILE=""
_NEXUS_MAX_LOG_LINES=1000
_NEXUS_LOG_COUNT=0
_NEXUS_LOG_INITIALIZED=0

# ------------------------------------------------------------------------------
# Public Functions
# ------------------------------------------------------------------------------

# Initialize the logger with a file path and optional max lines.
#
# Arguments:
#   $1 - Path to log file (required)
#   $2 - Maximum lines before rotation (optional, default: 1000)
#
# Returns:
#   0 on success, 1 on failure
init_logger() {
    local log_file="${1:-}"
    local max_lines="${2:-1000}"

    if [[ -z "${log_file}" ]]; then
        print_error "ERROR: Log file path is required." >&2
        print_error "Usage: init_logger <log_file> [max_lines]" >&2
        return 1
    fi

    if ! [[ "${max_lines}" =~ ^[0-9]+$ ]]; then
        print_error "ERROR: max_lines must be a positive integer." >&2
        return 1
    fi

    local log_dir
    log_dir="$(dirname "${log_file}")"

    if [[ ! -d "${log_dir}" ]]; then
        if ! mkdir -p "${log_dir}" 2>/dev/null; then
            print_error "ERROR: Could not create log directory: ${log_dir}" >&2
            return 1
        fi
    fi

    _NEXUS_LOG_FILE="${log_file}"
    _NEXUS_MAX_LOG_LINES="${max_lines}"
    _NEXUS_LOG_COUNT=0
    _NEXUS_LOG_INITIALIZED=1

    return 0
}

# Log a message with timestamp to both stdout and the log file.
#
# Arguments:
#   $1 - Message to log
#
# Returns:
#   0 on success, 1 if logger not initialized
log() {
    if [[ "${_NEXUS_LOG_INITIALIZED}" -eq 0 ]]; then
        print_error "ERROR: Logger not initialized. Call init_logger first." >&2
        return 1
    fi

    local message="${1:-}"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local log_entry="[${timestamp}] ${message}"

    print_info "${log_entry}"
    echo "${log_entry}" >> "${_NEXUS_LOG_FILE}"

    ((_NEXUS_LOG_COUNT++))

    if ((_NEXUS_LOG_COUNT % 15 == 0)); then
        _rotate_log
    fi

    return 0
}

# Get the current log file path.
#
# Returns:
#   Prints the log file path to stdout
get_log_file() {
    echo "${_NEXUS_LOG_FILE}"
}

# ------------------------------------------------------------------------------
# Private Functions
# ------------------------------------------------------------------------------

# Rotate the log file if it exceeds the maximum line count.
# Keeps only the most recent MAX_LOG_LINES lines.
_rotate_log() {
    [[ ! -f "${_NEXUS_LOG_FILE}" ]] && return 0

    local line_count
    line_count="$(wc -l < "${_NEXUS_LOG_FILE}")"

    if [[ "${line_count}" -gt "${_NEXUS_MAX_LOG_LINES}" ]]; then
        tail -n "${_NEXUS_MAX_LOG_LINES}" "${_NEXUS_LOG_FILE}" > "${_NEXUS_LOG_FILE}.tmp"
        mv "${_NEXUS_LOG_FILE}.tmp" "${_NEXUS_LOG_FILE}"
    fi

    return 0
}

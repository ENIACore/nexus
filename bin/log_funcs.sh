#!/bin/bash
# Logging functions for script files
# REQUIRED: Set LOG_FILE and MAX_LOG_LINES before sourcing this file

LOG_COUNT=0

# Function to validate required variables are set
validate_log_config() {
    local errors=0
    
    if [[ -z ${LOG_FILE} ]]; then
        echo "ERROR: LOG_FILE is not set. Cannot use log() function." >&2
        errors=1
    fi
    
    if [[ -z ${MAX_LOG_LINES} ]]; then
        echo "ERROR: MAX_LOG_LINES is not set. Cannot use log() function." >&2
        errors=1
    fi
    
    if [[ $errors -eq 1 ]]; then
        return 1
    fi
    
    # Create log directory if it doesn't exist
    local log_dir=$(dirname "$LOG_FILE")
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir" 2>/dev/null
        if [[ $? -ne 0 ]]; then
            echo "ERROR: Could not create log directory: $log_dir" >&2
            return 1
        fi
    fi
    
    return 0
}

# Function to log messages with timestamp
log() {
    # Validate configuration on first call
    if [[ $LOG_COUNT -eq 0 ]]; then
        if ! validate_log_config; then
            echo "ERROR: Logging configuration invalid. Exiting." >&2
            exit 1
        fi
    fi
    
    # Rotate every 15 calls (0, 15, 30, 45, etc.)
    if (( LOG_COUNT % 15 == 0 )); then
        rotate_log
    fi
    
    ((LOG_COUNT++))
    
    # Output to both console and log file
    local log_message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$log_message"
    echo "$log_message" >> "$LOG_FILE"
}

# Function to rotate log file if it exceeds MAX_LOG_LINES
rotate_log() {
    if [[ -f "$LOG_FILE" ]]; then
        line_count=$(wc -l < "$LOG_FILE")
        if [[ $line_count -gt $MAX_LOG_LINES ]]; then
            # Keep only the last MAX_LOG_LINES lines
            tail -n $MAX_LOG_LINES "$LOG_FILE" > "${LOG_FILE}.tmp"
            mv "${LOG_FILE}.tmp" "$LOG_FILE"
        fi
    fi
}

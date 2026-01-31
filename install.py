#!/usr/bin/env python3
"""
Nexus Server Installation Script
"""

import sys


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_error(message):
    """Print error message in red"""
    print(f"{Colors.RED}{Colors.BOLD}[ERROR]{Colors.RESET} {Colors.RED}{message}{Colors.RESET}")


def print_success(message):
    """Print success message in green"""
    print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS]{Colors.RESET} {Colors.GREEN}{message}{Colors.RESET}")


def print_warning(message):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}{Colors.BOLD}[WARNING]{Colors.RESET} {Colors.YELLOW}{message}{Colors.RESET}")


def print_info(message):
    """Print info message in blue"""
    print(f"{Colors.BLUE}{Colors.BOLD}[INFO]{Colors.RESET} {Colors.BLUE}{message}{Colors.RESET}")


def print_step(message):
    """Print step message in cyan"""
    print(f"{Colors.CYAN}{Colors.BOLD}[STEP]{Colors.RESET} {Colors.CYAN}{message}{Colors.RESET}")


def print_header(message):
    """Print header message in magenta"""
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{Colors.BOLD}{message.center(60)}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")


if __name__ == "__main__":
    print_header("NEXUS SERVER INSTALLATION")
    print_info("Starting installation process...")

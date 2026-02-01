#!/usr/bin/env python3
"""
Nexus Server Installation Script
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path


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


def run_command(command, description=None):
    """Run a shell command and handle errors"""
    if description:
        print_info(description)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        print_error(f"Error: {e.stderr}")
        sys.exit(1)


def create_directories():
    """Create necessary system directories"""
    print_step("Creating system directories...")
    
    directories = [
        "/opt/nexus",
        "/var/log/nexus",
        "/etc/nexus",
        "/etc/nexus/keys"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print_success(f"Created directory: {directory}")
        except Exception as e:
            print_error(f"Failed to create directory {directory}: {e}")
            sys.exit(1)


def clone_repository():
    """Clone the nexus repository"""
    print_step("Cloning nexus repository...")
    
    repo_url = "https://github.com/ENIACore/nexus.git"
    clone_path = "/tmp/nexus"
    
    # Remove existing clone if present
    if Path(clone_path).exists():
        shutil.rmtree(clone_path)
    
    run_command(f"git clone {repo_url} {clone_path}", "Cloning repository...")
    print_success(f"Repository cloned to {clone_path}")
    
    return clone_path

def copy_repo_path(repo_path):
    """Copy files or directories from repository to /opt/nexus"""
    print_step("Copying paths to /opt/nexus...")

    repo_root = Path(repo_path)

    # Define paths to copy: (source_relative_path, destination_relative_path)
    paths_to_copy = [
        # Cloudflare files
        ("cloudflare/setup.sh", "cloudflare/setup.sh"),
        ("cloudflare/schedule.sh", "cloudflare/schedule.sh"),
        ("cloudflare/update_dns.sh", "cloudflare/update_dns.sh"),
        ("cloudflare/create_cert.sh", "cloudflare/create_cert.sh"),

        # Nginx files
        ("nginx/setup.sh", "nginx/setup.sh"),
        ("nginx/reload.sh", "nginx/reload.sh"),
        ("nginx/update.sh", "nginx/update.sh"),
        ("nginx/tail-logs.sh", "nginx/tail-logs.sh"),

        # Nginx directories
        ("nginx/conf", "nginx/conf"),
        ("nginx/conf.d", "nginx/conf.d"),
        ("nginx/snippets", "nginx/snippets"),
        ("nginx/sites-available", "nginx/sites-available"),

        # Fail2ban files
        ("f2b/setup.sh", "f2b/setup.sh"),
        ("f2b/reload.sh", "f2b/reload.sh"),
        ("f2b/status.sh", "f2b/status.sh"),

        # ufw files
        ("ufw/setup.sh", "ufw/setup.sh"),
        ("ufw/schedule.sh", "ufw/schedule.sh"),
        ("ufw/update.sh", "ufw/update.sh"),

        # Jellyfin files
        ("jelly/setup.sh", "jelly/setup.sh"),

        # Nextcloud files
        ("nextcloud/setup.sh", "nextcloud/setup.sh"),

        # qBittorrent files
        ("qbit/setup.sh", "qbit/setup.sh"),

        # Vaultwarden files
        ("vault/setup.sh", "vault/setup.sh"),

        # RAID files
        ("RAID/setup.sh", "RAID/setup.sh"),
        ("RAID/start.sh", "RAID/start.sh"),
        ("RAID/stop.sh", "RAID/stop.sh"),
        ("RAID/status.sh", "RAID/status.sh"),

        # Central script files
        ("lib/checks.sh", "lib/checks.sh"),
        ("lib/print.sh", "lib/print.sh"),
        ("lib/log.sh", "lib/log.sh"),
    ]

    for src_rel, dst_rel in paths_to_copy:
        src = repo_root / src_rel
        dst = Path("/opt/nexus") / dst_rel

        if not src.exists():
            print_warning(f"Source path not found: {src}")
            continue

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)

            if src.is_dir():
                # Copy directory
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print_success(f"Copied directory {src_rel} -> {dst_rel}")
            else:
                # Copy file
                shutil.copy2(src, dst)
                print_success(f"Copied file {src_rel} -> {dst_rel}")
        except Exception as e:
            print_error(f"Failed to copy {src_rel}: {e}")
            sys.exit(1)

def copy_template_files(repo_path):
    """Copy template files from keys/ to /etc/nexus/keys"""
    print_step("Copying template files to /etc/nexus/keys...")

    repo_root = Path(repo_path)
    keys_src = repo_root / "keys"
    keys_dst = Path("/etc/nexus/keys")

    if not keys_src.exists():
        print_warning(f"Keys directory not found: {keys_src}")
        return

    # Find all .template files
    template_files = list(keys_src.glob("*.template"))

    if not template_files:
        print_warning("No template files found in keys directory")
        return

    copied_files = []
    for template_file in template_files:
        dst_file = keys_dst / template_file.name
        try:
            shutil.copy2(template_file, dst_file)
            # Remove .template extension for the actual config file name
            config_file = keys_dst / template_file.name.replace('.template', '')
            copied_files.append(config_file.name)
            print_success(f"Copied {template_file.name} -> /etc/nexus/keys/")
        except Exception as e:
            print_error(f"Failed to copy {template_file.name}: {e}")
            sys.exit(1)

    # Print required configuration files
    print_header("REQUIRED CONFIGURATION FILES")
    print_info("The following template files have been copied to /etc/nexus/keys/")
    print_info("You must fill out these files with your actual credentials:\n")

    for config_file in sorted(copied_files):
        print(f"  {Colors.YELLOW}{Colors.BOLD}•{Colors.RESET} {Colors.WHITE}{config_file}{Colors.RESET}")

    print(f"\n{Colors.CYAN}Location: /etc/nexus/keys/{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠ Remove the .template extension and fill in your credentials{Colors.RESET}\n")

def cleanup_temp_files():
    """Remove temporary repository clone"""
    print_step("Cleaning up temporary files...")

    temp_repo = "/tmp/nexus"
    if Path(temp_repo).exists():
        try:
            shutil.rmtree(temp_repo)
            print_success(f"Removed temporary directory: {temp_repo}")
        except Exception as e:
            print_warning(f"Failed to remove {temp_repo}: {e}")

def create_config():
    """Create configuration file with domain settings"""
    print_step("Creating configuration file...")

    # Get domain from user
    domain = input(f"{Colors.CYAN}Enter your root domain (e.g., example.com): {Colors.RESET}").strip()

    if not domain:
        print_error("Domain cannot be empty")
        sys.exit(1)

    # Get RAID mount path from user
    raid_mount = input(f"{Colors.CYAN}Enter your RAID mount path (e.g., /mnt/RAID): {Colors.RESET}").strip()

    if not raid_mount:
        print_error("RAID mount path cannot be empty")
        sys.exit(1)

    # Get RAID device from user
    raid_device = input(f"{Colors.CYAN}Enter your RAID device (e.g., /dev/md0) [default: /dev/md0]: {Colors.RESET}").strip()
    if not raid_device:
        raid_device = "/dev/md0"

    # Extract relative device name (e.g., md0 from /dev/md0)
    raid_rel_device = raid_device.split('/')[-1]

    # Create config directory
    config_dir = Path("/etc/nexus/conf")
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create config file content
    config_content = f"""#!/bin/bash
# Nexus Configuration File - /etc/nexus/conf/conf.sh

# Nexus domain and subdomains
export NEXUS_DOMAIN="{domain}"
export NEXUS_WILDCARD_DOMAIN="*.{domain}"
export NEXUS_JELLY_SUBDOMAIN="jelly.{domain}"
export NEXUS_QBIT_SUBDOMAIN="qbit.{domain}"
export NEXUS_VAULT_SUBDOMAIN="vault.{domain}"
export NEXUS_NEXTCLOUD_SUBDOMAIN="nextcloud.{domain}"

# Nexus service user
export NEXUS_USER=nexus

# Nexus main log dir
export NEXUS_LOG_DIR="/var/log/nexus"

# Nexus main opt and etc dir
export NEXUS_OPT_DIR="/opt/nexus"
export NEXUS_ETC_DIR="/etc/nexus"

# RAID configuration
export NEXUS_RAID_DEVICE="{raid_device}"
export NEXUS_REL_RAID_DEVICE="{raid_rel_device}"
export NEXUS_RAID_MOUNT="{raid_mount}"
"""

    # Write config file
    config_file = config_dir / "conf.sh"
    config_file.write_text(config_content)

    print_success(f"Configuration file created at {config_file}")
    print_info(f"Root domain: {domain}")
    print_info(f"RAID mount path: {raid_mount}")


if __name__ == "__main__":
    print_header("NEXUS SERVER INSTALLATION")
    
    # Check if running as root
    if os.geteuid() != 0:
        print_error("This script must be run as root")
        sys.exit(1)
    
    create_directories()
    repo_path = clone_repository()
    copy_repo_path(repo_path)
    copy_template_files(repo_path)
    create_config()
    cleanup_temp_files()

    print_success("Initial setup complete!")

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
        "/etc/nexus"
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

def copy_repo_files(repo_path):
    """Copy specific files from repository to /opt/nexus"""
    print_step("Copying files to /opt/nexus...")
    
    repo_root = Path(repo_path)
    
    # Define files to copy: (source_relative_path, destination_subdirectory)
    files_to_copy = [
        # Cloudflare files
        ("cloudflare/setup.sh", "cloudflare"),

        # Central script files
        ("lib/checks.sh", "lib"),
        ("lib/print.sh", "lib"),
    ]
    
    for src_rel, dst_subdir in files_to_copy:
        src = repo_root / src_rel
        dst = Path("/opt/nexus") / dst_subdir / src.name
        
        if not src.exists():
            print_warning(f"Source file not found: {src}")
            continue
        
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print_success(f"Copied {src_rel} -> {dst_subdir}/{src.name}")
        except Exception as e:
            print_error(f"Failed to copy {src_rel}: {e}")
            sys.exit(1)

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
    
    # Create config directory
    config_dir = Path("/etc/nexus/conf")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create config file content
    config_content = f"""export NEXUS_DOMAIN={domain}
export NEXUS_JELLY_SUBDOMAIN=jelly.{domain}
export NEXUS_QBIT_SUBDOMAIN=qbit.{domain}
export NEXUS_VAULT_SUBDOMAIN=vault.{domain}
export NEXUS_NEXTCLOUD_SUBDOMAIN=nextcloud.{domain}

export NEXUS_USER=nexus
"""
    
    # Write config file
    config_file = config_dir / "config.sh"
    config_file.write_text(config_content)
    
    print_success(f"Configuration file created at {config_file}")
    print_info(f"Root domain: {domain}")


if __name__ == "__main__":
    print_header("NEXUS SERVER INSTALLATION")
    
    # Check if running as root
    if os.geteuid() != 0:
        print_error("This script must be run as root")
        sys.exit(1)
    
    create_directories()
    repo_path = clone_repository()
    copy_repo_files(repo_path)
    create_config()
    cleanup_temp_files()
    
    print_success("Initial setup complete!")

#!/usr/bin/env python3
# Config management for server-configs - /usr/local/sbin/_lib/config.py

import json
import sys
from pathlib import Path

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import (
    get_input,
    print_error,
    print_group_end,
    print_group_start,
    print_group_step,
    print_info,
    print_success,
    print_warning,
)

# Server paths
SERVER_BIN = "/usr/local/sbin"
SERVER_ENV_PATH = Path(f"{SERVER_BIN}/source-env")
SERVER_CLONE_PATH = Path("/tmp/server-configs")
SERVER_CONFIG_PATH = Path("/etc/server")
SERVER_CONFIG_FILE_PATH = SERVER_CONFIG_PATH / "config.json"

# Service paths
CF_CONFIG_PATH = Path("/etc/cloudflare")
NGINX_CONFIG_PATH = Path("/etc/nginx")
F2B_CONFIG_PATH = Path("/etc/f2b")
UFW_CONFIG_PATH = Path("/etc/ufw")
JELLY_CONFIG_PATH = Path("/etc/jelly")
JFA_CONFIG_PATH = Path("/etc/jfa")
NEXTCLOUD_CONFIG_PATH = Path("/etc/nextcloud")
JACKETT_CONFIG_PATH = Path("/etc/jackett")
VAULT_CONFIG_PATH = Path("/etc/vault")
RAID_CONFIG_PATH = Path("/etc/raid")
MC_CONFIG_PATH = Path("/etc/mc")

# Ubuntu settings
SERVER_USER: str = "server"

# Docker settings
DOCKER_NETWORK_NAME: str = "server-net"
DOCKER_NETWORK_SUBNET: str = "172.18.0.0/16"
DOCKER_NETWORK_GATEWAY: str = "172.18.0.1"


def load_config() -> dict:
    """Load config from disk. Returns empty dict if file does not exist."""
    if not SERVER_CONFIG_FILE_PATH.exists():
        return {}
    try:
        return json.loads(SERVER_CONFIG_FILE_PATH.read_text())
    except json.JSONDecodeError as e:
        print_error(f"Config file is malformed: {e}")
        print_error(f"Fix or delete {SERVER_CONFIG_FILE_PATH} and re-run")
        sys.exit(1)


def save_config(data: dict) -> None:
    """Write config dict to disk, creating parent directories if needed."""
    try:
        SERVER_CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        SERVER_CONFIG_FILE_PATH.write_text(json.dumps(data, indent=2) + "\n")
        SERVER_CONFIG_FILE_PATH.chmod(0o600)
    except OSError as e:
        print_error(f"Failed to write config: {e}")
        sys.exit(1)


def get_config_value(key: str) -> str | None:
    """Return a single value from config by key, or None if not set."""
    return load_config().get(key)


def set_config_value(key: str, value: str) -> None:
    """Set a single key in config, overwriting if it already exists."""
    config = load_config()
    existed = key in config
    config[key] = value
    save_config(config)
    if existed:
        print_info(f"Config updated: {key}")
    else:
        print_success(f"Config saved: {key}")


def require_config_value(key: str) -> str:
    """Return config value for key, exit with error if not set."""
    value = get_config_value(key)
    if not value:
        print_error(f"Required config key '{key}' is not set")
        print_error(
            f"Run the setup script or set it with set_config_value('{key}', ...)"
        )
        sys.exit(1)
    return value


def prompt_and_save(
    key: str, prompt: str, default: str = "", secret: bool = False
) -> str:
    """Prompt user for a value, save it to config, and return it.
    Always prompts — use ensure_config_value() to skip if already set.
    Uses the current saved value as the default if no default provided.
    """
    config = load_config()
    effective_default = default or config.get(key, "")
    value = get_input(prompt, default=effective_default, secret=secret)
    if not value:
        print_error(f"No value provided for '{key}'")
        sys.exit(1)
    config[key] = value
    save_config(config)
    if secret:
        print_success(f"Saved: {key} = ****")
    else:
        print_success(f"Saved: {key} = {value}")
    return value


def print_config() -> None:
    """Pretty-print all current config values."""
    config = load_config()
    if not config:
        print_warning("No config found — nothing saved yet")
        return
    print_group_start(f"Current config ({SERVER_CONFIG_FILE_PATH})")
    for key, value in config.items():
        print_group_step(f"{key} = {value}")
    print_group_end()


def clear_config() -> None:
    """Delete the config file entirely."""
    if SERVER_CONFIG_FILE_PATH.exists():
        SERVER_CONFIG_FILE_PATH.unlink()
        print_success("Config cleared")
    else:
        print_warning("No config file to clear")

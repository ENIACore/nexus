#!/usr/bin/env python3
"""
Cloudflare management tool for DNS updates and SSL certificates.

Commands:
  python3 cloudflare.py setup        - Create log directories
  python3 cloudflare.py update-dns   - Update DNS A records to current IP
  python3 cloudflare.py schedule     - Set up cron job for DNS updates
  python3 cloudflare.py create-cert  - Create SSL certificates with certbot
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional
import urllib.error
import urllib.request


# -----------------------------
# Configuration
# -----------------------------

@dataclass(frozen=True)
class Config:
    # Project layout
    base_dir: Path = Path(__file__).resolve().parent.parent
    keys_dir: Path = base_dir / "keys"

    # Logging
    log_dir: Path = Path("/var/log/nexus/cloudflare")
    log_file: Path = log_dir / "dns.log"
    max_log_bytes: int = 512_000   # ~500KB
    log_backups: int = 3

    # Domain / records
    domain: str = "lamkin.dev"
    records: tuple[str, ...] = ("lamkin.dev", "*.lamkin.dev")

    # Cron
    cron_schedule: str = "*/5 * * * *"
    cron_file: Path = Path("/etc/cron.d/cloudflare-dns")
    cron_user: str = "nexus"

    def cloudflare_token(self) -> str:
        """
        Load Cloudflare API token.

        Preferred:
          - environment variable CF_API_TOKEN

        Fallback:
          - parse keys/cloudflare.sh containing: export CF_API_KEY=...
        """
        env_token = os.getenv("CF_API_TOKEN")
        if env_token:
            return env_token.strip()

        key_file = self.keys_dir / "cloudflare.sh"
        if not key_file.exists():
            raise FileNotFoundError(
                f"Cloudflare key file not found: {key_file}\n"
                f"Create it from the template: cp {self.keys_dir}/cloudflare.sh.template {key_file}\n"
                f"Or set CF_API_TOKEN in the environment."
            )

        with key_file.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export CF_API_KEY="):
                    value = line.split("=", 1)[1].strip()

                    # Strip quotes if present: "token" or 'token'
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1].strip()

                    # Strip inline comments: token # comment
                    if " #" in value:
                        value = value.split(" #", 1)[0].strip()
                    if value == "<value>" or not value:
                        raise ValueError(
                            f"API key not set properly in {key_file}.\n"
                            "Edit the file and set CF_API_KEY, or set CF_API_TOKEN env var."
                        )
                    return value

        raise ValueError(f"CF_API_KEY not found in {key_file}.")


# -----------------------------
# Logging
# -----------------------------

def build_logger(cfg: Config) -> Logger:
    cfg.log_dir.mkdir(parents=True, exist_ok=True)

    import logging
    logger = logging.getLogger("cloudflare")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # File rotation by size
    file_handler = RotatingFileHandler(
        filename=str(cfg.log_file),
        maxBytes=cfg.max_log_bytes,
        backupCount=cfg.log_backups,
        encoding="utf-8",
    )
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(fmt)

    # Console output (useful when running manually)
    console = logging.StreamHandler()
    console.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console)
    return logger


# -----------------------------
# Cloudflare API client (urllib)
# -----------------------------

class CloudflareAPIError(RuntimeError):
    pass


class CloudflareAPI:
    BASE_URL = "https://api.cloudflare.com/client/v4"

    def __init__(self, token: str, logger: Logger):
        self._token = token
        self._logger = logger

    def _request(self, method: str, endpoint: str, data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                return payload
        except urllib.error.HTTPError as e:
            details = e.read().decode("utf-8", errors="replace")
            raise CloudflareAPIError(f"HTTP {e.code} {e.reason} for {method} {endpoint}: {details}") from e
        except urllib.error.URLError as e:
            raise CloudflareAPIError(f"Network error for {method} {endpoint}: {e}") from e

    def get_zone_id(self, zone_name: str) -> str:
        self._logger.info("Retrieving Zone ID for %s...", zone_name)
        resp = self._request("GET", f"/zones?name={zone_name}")
        if not resp.get("success") or not resp.get("result"):
            raise CloudflareAPIError(f"Could not get Zone ID for {zone_name}: {resp}")
        return resp["result"][0]["id"]

    def get_dns_record(self, zone_id: str, record_name: str, record_type: str = "A") -> dict[str, Any]:
        resp = self._request("GET", f"/zones/{zone_id}/dns_records?name={record_name}&type={record_type}")
        if not resp.get("success") or not resp.get("result"):
            raise CloudflareAPIError(f"Could not get DNS record for {record_name} ({record_type}): {resp}")
        return resp["result"][0]

    def update_dns_record(self, zone_id: str, record_id: str, record_name: str, ip: str, proxied: bool = True) -> None:
        data = {"type": "A", "name": record_name, "content": ip, "ttl": 1, "proxied": proxied}
        resp = self._request("PUT", f"/zones/{zone_id}/dns_records/{record_id}", data=data)
        if not resp.get("success"):
            raise CloudflareAPIError(f"Failed updating {record_name}: {resp}")


# -----------------------------
# Helpers
# -----------------------------

def get_public_ipv4(logger: Logger) -> str:
    logger.info("Detecting public IPv4 address...")
    services = [
        "https://api.ipify.org",
        "https://icanhazip.com",
        "https://ifconfig.me",
    ]

    last_error: Optional[Exception] = None
    for url in services:
        try:
            with urllib.request.urlopen(url, timeout=7) as resp:
                ip = resp.read().decode("utf-8").strip()
                if ip:
                    logger.info("Current IPv4 address: %s", ip)
                    return ip
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Could not determine public IP address. Last error: {last_error}")


# -----------------------------
# Commands
# -----------------------------

def cmd_setup(_: argparse.Namespace, cfg: Config) -> int:
    print(f"Creating cloudflare log directory at {cfg.log_dir}...")
    cfg.log_dir.mkdir(parents=True, exist_ok=True)

    # Optional: set ownership/permissions (best-effort)
    try:
        subprocess.run(["sudo", "chown", f"{cfg.cron_user}:{cfg.cron_user}", str(cfg.log_dir)], check=True)
        subprocess.run(["sudo", "chmod", "755", str(cfg.log_dir)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: could not set ownership/permissions: {e}")

    print(f"Logs will be written to: {cfg.log_file}")
    return 0


def cmd_update_dns(_: argparse.Namespace, cfg: Config) -> int:
    logger = build_logger(cfg)

    try:
        public_ip = get_public_ipv4(logger)

        token = cfg.cloudflare_token()
        api = CloudflareAPI(token, logger)

        zone_id = api.get_zone_id(cfg.domain)
        logger.info("Zone ID: %s", zone_id)

        all_ok = True
        for record_name in cfg.records:
            record = api.get_dns_record(zone_id, record_name, "A")
            record_id = record["id"]
            current_content = record.get("content", "")

            if current_content == public_ip:
                logger.info("No change for %s (already %s)", record_name, public_ip)
                continue

            logger.info("Updating %s: %s -> %s", record_name, current_content, public_ip)
            api.update_dns_record(zone_id, record_id, record_name, public_ip, proxied=True)
            logger.info("SUCCESS: Updated %s to %s", record_name, public_ip)

        logger.info("DNS update complete.")
        return 0 if all_ok else 1

    except Exception as e:
        logger.error("ERROR: %s", e)
        return 1


def cmd_schedule(_: argparse.Namespace, cfg: Config) -> int:
    script_path = Path(__file__).resolve()
    python_path = "/usr/bin/python3"  # reliable for cron; adjust if needed

    cron_content = f"""# Cloudflare DNS updater - runs as {cfg.cron_user}
# Updates DNS records every 5 minutes and on reboot

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Run on boot
@reboot {cfg.cron_user} {python_path} {script_path} update-dns

# Run every 5 minutes
{cfg.cron_schedule} {cfg.cron_user} {python_path} {script_path} update-dns
"""

    # If file exists and content matches, do nothing
    if cfg.cron_file.exists():
        existing = cfg.cron_file.read_text(encoding="utf-8", errors="replace")
        if existing == cron_content:
            print(f"Cron job already up to date at {cfg.cron_file}")
            return 0
        print(f"Updating existing cron job at {cfg.cron_file}...")

    else:
        print(f"Creating system cron job at {cfg.cron_file}...")

    # Write with sudo tee
    proc = subprocess.Popen(
        ["sudo", "tee", str(cfg.cron_file)],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    _, err = proc.communicate(cron_content.encode("utf-8"))
    if proc.returncode != 0:
        print(f"Failed to write cron file: {err.decode('utf-8', errors='replace')}")
        return 1

    subprocess.run(["sudo", "chmod", "644", str(cfg.cron_file)], check=True)

    print("System cron job installed.")
    print(f"DNS update will run every 5 minutes as user '{cfg.cron_user}'.")
    return 0


def cmd_create_cert(_: argparse.Namespace, cfg: Config) -> int:
    cf_ini = cfg.keys_dir / "cloudflare.ini"
    if not cf_ini.exists():
        print(f"ERROR: Cloudflare credentials file not found: {cf_ini}")
        print("Create it from the template:")
        print(f"  cp {cfg.keys_dir}/cloudflare.ini.template {cf_ini}")
        print(f"  chmod 600 {cf_ini}")
        return 1

    print("Running certbot to create certificates...")
    try:
        subprocess.run(
            [
                "sudo", "certbot", "certonly",
                "--dns-cloudflare",
                "--dns-cloudflare-credentials", str(cf_ini),
                "--dns-cloudflare-propagation-seconds", "60",
                "-d", f"*.{cfg.domain}",
                "-d", cfg.domain,
            ],
            check=True,
        )

        print("\nVerifying certbot renewal timer is working...")
        subprocess.run(["sudo", "systemctl", "status", "certbot.timer"])

        print("\nVerifying certbot renewal functions...")
        subprocess.run(["sudo", "certbot", "renew", "--dry-run"], check=True)

        print("\nCertificate creation complete!")
        return 0

    except subprocess.CalledProcessError as e:
        print(f"ERROR: certbot failed: {e}")
        return 1


# -----------------------------
# CLI
# -----------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cloudflare management tool for DNS updates and SSL certificates"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup", help="Create log directories")
    sub.add_parser("update-dns", help="Update DNS A records to current IP")
    sub.add_parser("schedule", help="Set up cron job for DNS updates")
    sub.add_parser("create-cert", help="Create SSL certificates with certbot")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    cfg = Config()

    commands = {
        "setup": cmd_setup,
        "update-dns": cmd_update_dns,
        "schedule": cmd_schedule,
        "create-cert": cmd_create_cert,
    }
    return commands[args.command](args, cfg)


if __name__ == "__main__":
    raise SystemExit(main())


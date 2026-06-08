#!/usr/bin/env python3

import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_server_user
from common import ensure_dir
from config import require_config_value
from formatting import print_error, print_header
from logger import init_logger, log

CF_LOG_FILE = "dns.log"
CF_LOG_MAX_LINES = 100
CF_API_BASE = "https://api.cloudflare.com/client/v4"


def _cf_request(
    method: str, path: str, api_key: str, data: dict | None = None
) -> dict:
    body = json.dumps(data).encode() if data else None
    headers = {"Authorization": f"Bearer {api_key}"}
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        f"{CF_API_BASE}{path}", data=body, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())


def _get_public_ipv4() -> str:
    for url in [
        "https://api.ipify.org",
        "https://icanhazip.com",
        "https://ifconfig.me",
    ]:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read().decode().strip()
        except Exception:
            continue


def _get_record_id(zone_id: str, name: str, api_key: str) -> str:
    resp = _cf_request(
        "GET",
        f"/zones/{zone_id}/dns_records?name={name}&type=A",
        api_key,
    )
    results = resp.get("result") or []
    return results[0].get("id", "") if results else ""


def _update_record(
    zone_id: str,
    record_id: str,
    name: str,
    ip: str,
    proxied: bool,
    api_key: str,
) -> bool:
    resp = _cf_request(
        "PUT",
        f"/zones/{zone_id}/dns_records/{record_id}",
        api_key,
        {
            "type": "A",
            "name": name,
            "content": ip,
            "ttl": 1,
            "proxied": proxied,
        },
    )
    return bool(resp.get("success"))


def main():
    print_header("UPDATING DNS")

    require_server_user()

    api_key = require_config_value("CF_API_KEY")
    root_domain = require_config_value("ROOT_DOMAIN")
    wildcard_domain = require_config_value("WILDCARD_DOMAIN")
    cf_log_dir = require_config_value("CF_LOG_DIR")

    ensure_dir(cf_log_dir)
    init_logger(f"{cf_log_dir}/{CF_LOG_FILE}", CF_LOG_MAX_LINES)

    log("Detecting public IPv4 address...")
    public_ip = _get_public_ipv4()
    if not public_ip:
        print_error("Could not determine public IP address")
        sys.exit(1)
    log(f"Current IPv4 address: {public_ip}")

    log(f"Retrieving Zone ID for {root_domain}...")
    zone_resp = _cf_request("GET", f"/zones?name={root_domain}", api_key)
    results = zone_resp.get("result") or []
    zone_id = results[0].get("id", "") if results else ""
    if not zone_id:
        log(f"ERROR: Could not get Zone ID for {root_domain}")
        sys.exit(1)
    log(f"Zone ID: {zone_id}")

    log("Retrieving DNS record IDs...")
    root_record_id = _get_record_id(zone_id, root_domain, api_key)
    wildcard_record_id = _get_record_id(zone_id, wildcard_domain, api_key)

    if not root_record_id:
        log(f"ERROR: Could not get Record ID for {root_domain}")
        sys.exit(1)
    if not wildcard_record_id:
        log(f"ERROR: Could not get Record ID for {wildcard_domain}")
        sys.exit(1)

    log(f"Root Record ID: {root_record_id}")
    log(f"Wildcard Record ID: {wildcard_record_id}")

    log(f"Updating A record for {root_domain} -> {public_ip}")
    if _update_record(
        zone_id, root_record_id, root_domain, public_ip, True, api_key
    ):
        log(f"SUCCESS: Updated {root_domain} to {public_ip}")
    else:
        log(f"ERROR: Failed to update {root_domain}")
        sys.exit(1)

    log(f"Updating A record for {wildcard_domain} -> {public_ip}")
    if _update_record(
        zone_id, wildcard_record_id, wildcard_domain, public_ip, True, api_key
    ):
        log(f"SUCCESS: Updated {wildcard_domain} to {public_ip}")
    else:
        log(f"ERROR: Failed to update {wildcard_domain}")
        sys.exit(1)

    mc_domain = f"mc.{root_domain}"
    log(f"Retrieving DNS record ID for {mc_domain}...")
    mc_record_id = _get_record_id(zone_id, mc_domain, api_key)

    if not mc_record_id:
        log(f"WARNING: Could not get Record ID for {mc_domain} (skipping)")
    else:
        log(f"Updating A record for {mc_domain} -> {public_ip}")
        if _update_record(
            zone_id, mc_record_id, mc_domain, public_ip, False, api_key
        ):
            log(f"SUCCESS: Updated {mc_domain} to {public_ip}")
        else:
            log(f"ERROR: Failed to update {mc_domain}")

    log("DNS Update Complete")


if __name__ == "__main__":
    main()

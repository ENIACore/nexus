#!/usr/bin/env python3

import secrets
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_dir
from common import ensure_dir
from config import DOCKER_NETWORK_NAME, prompt_and_save, require_config_value
from docker import ensure_network, run_container
from formatting import print_header, print_info, print_step

# Server settings
MC_CONTAINER_NAME = "server-mc"
MC_TYPE = "FABRIC"
MC_VERSION = "LATEST"
MC_MEMORY = "3G"
MC_DIFFICULTY = "normal"
MC_MAX_PLAYERS = "10"
MC_VIEW_DISTANCE = "10"
MC_ENFORCE_WHITELIST = "TRUE"
MC_TZ = "America/Chicago"

# Mods (auto-downloaded from Modrinth)
MC_MODRINTH_PROJECTS = "lithium"


def generate_rcon_password(rcon_pass_file: str) -> str:
    password = secrets.token_hex(16)
    from pathlib import Path

    path = Path(rcon_pass_file)
    path.write_text(password + "\n")
    path.chmod(0o600)
    print_info(f"RCON password stored in {rcon_pass_file}")
    return password


def main():
    print_header("SETTING UP MINECRAFT SERVER (FABRIC + LITHIUM)")

    core_path = require_config_value("CORE_SERVICES_PATH")
    require_dir(core_path, "Core services path")

    mc_ops = prompt_and_save(
        "MC_OPS",
        "Enter Minecraft operator usernames (comma-separated) — ops can run server commands",
    )
    mc_whitelist = prompt_and_save(
        "MC_WHITELIST",
        "Enter Minecraft whitelist usernames (comma-separated) — only these players can join",
    )

    mc_path = f"{core_path}/mc-data"
    mc_data_path = f"{mc_path}/data"
    rcon_pass_file = f"{mc_path}/.rcon_password"

    print_step("Creating Minecraft server directories...")
    ensure_dir(mc_data_path)

    rcon_password = generate_rcon_password(rcon_pass_file)

    ensure_network()

    run_container(
        name=MC_CONTAINER_NAME,
        opts=[
            "--network",
            DOCKER_NETWORK_NAME,
            "--restart",
            "unless-stopped",
            "-e",
            "EULA=TRUE",
            "-e",
            f"TYPE={MC_TYPE}",
            "-e",
            f"VERSION={MC_VERSION}",
            "-e",
            f"MEMORY={MC_MEMORY}",
            "-e",
            f"DIFFICULTY={MC_DIFFICULTY}",
            "-e",
            f"MAX_PLAYERS={MC_MAX_PLAYERS}",
            "-e",
            f"VIEW_DISTANCE={MC_VIEW_DISTANCE}",
            "-e",
            f"OPS={mc_ops}",
            "-e",
            f"WHITELIST={mc_whitelist}",
            "-e",
            f"ENFORCE_WHITELIST={MC_ENFORCE_WHITELIST}",
            "-e",
            f"TZ={MC_TZ}",
            "-e",
            "ENABLE_RCON=true",
            "-e",
            f"RCON_PASSWORD={rcon_password}",
            "-e",
            "SERVER_PORT=25565",
            "-e",
            f"MODRINTH_PROJECTS={MC_MODRINTH_PROJECTS}",
            "-v",
            f"{mc_data_path}:/data",
            "itzg/minecraft-server:latest",
        ],
        notes=[
            "Connect via Minecraft client at <server-ip>:25565",
            f"Monitor startup progress: docker logs -f {MC_CONTAINER_NAME}",
            f"World data stored in {mc_data_path}",
            f"RCON password stored in {rcon_pass_file}",
        ],
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import sys
from pathlib import Path
from subprocess import CompletedProcess

sys.path.insert(0, str(Path.home() / "bin" / "_lib"))
from formatting import print_error, print_info, print_step, print_success, print_warning

HOME = Path.home()
USR_BIN = HOME / "bin"
LIB_DIR = USR_BIN / "_lib"
SCRIPTS_DIR = Path(__file__).parent.resolve()


def copy_to_clipboard(text):
    """Copy text to clipboard. Returns the tool used, or empty string if none found."""
    import shutil
    import subprocess

    for tool, args in [
        ("pbcopy", ["pbcopy"]),
        ("xclip", ["xclip", "-selection", "clipboard"]),
        ("xsel", ["xsel", "--clipboard", "--input"]),
        ("wl-copy", ["wl-copy"]),
    ]:
        if shutil.which(tool):
            subprocess.run(args, input=text.encode(), check=True)
            return tool
    return ""


SOURCE_ENV_PATH = Path(f"{USR_BIN}/source-env")


def _ensure_source_env() -> None:
    if not SOURCE_ENV_PATH.exists():
        SOURCE_ENV_PATH.write_text("#!/bin/sh\n")
        SOURCE_ENV_PATH.chmod(0o755)


def add_env_val(env_key: str, env_val: str, description: str) -> None:
    """Append export statements to ~/usr-bin/source-env, creating it if needed."""
    _ensure_source_env()
    export_line = f"# {description}\nexport {env_key}={env_val}"
    with open(SOURCE_ENV_PATH, "a") as f:
        f.write(f"\n{export_line}\n")
    print_info(f"Adding {env_key} to source env")
    print_info(f"Description: {description}")
    print_warning(
        "Make sure current command is ran with `&& source source-env` or run `source source-env` after for changes to take affect in current sesion"
    )


def add_env_cmd(cmd: str, description: str) -> None:
    _ensure_source_env()
    cmd_line = f"# {description}\n{cmd}"
    with open(SOURCE_ENV_PATH, "a") as f:
        f.write(f"\n{cmd_line}\n")
    print_info(f"Adding {cmd} to source env")
    print_info(f"Description: {description}")
    print_warning(
        "Make sure current command is ran with `&& source source-env` or run `source source-env` after for changes to take affect in current sesion"
    )


def clear_env() -> None:
    """Delete the source-env file if it exists."""
    if SOURCE_ENV_PATH.exists():
        SOURCE_ENV_PATH.unlink()


def run_cmd(cmd: str, capture_output: bool = False) -> CompletedProcess:
    """Run a shell command, printing it first. Raises on non-zero exit."""
    import subprocess

    print_step(f"Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture_output,
        text=True,
    )
    if result.returncode == 0:
        if capture_output and result.stdout:
            print_success(result.stdout.strip())
        else:
            print_success("Command completed successfully")
    else:
        err = result.stderr.strip() if capture_output and result.stderr else ""
        print_error(
            f"Command failed (exit {result.returncode}){': ' + err if err else ''}"
        )
        result.check_returncode()  # raises CalledProcessError
    return result

#!/usr/bin/env python3

import sys
from pathlib import Path
from subprocess import CompletedProcess

sys.path.insert(0, "/usr/local/sbin/_lib")
from config import SERVER_ENV_PATH
from formatting import (  # noqa: E402
    print_error,
    print_info,
    print_step,
    print_success,
    print_warning,
)


def copy_to_clipboard(text):
    """Copy text to clipboard.
    Returns the tool used, or empty string if none found."""
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


def _ensure_source_env() -> None:
    if not SERVER_ENV_PATH.exists():
        SERVER_ENV_PATH.write_text("#!/bin/sh\n")
        SERVER_ENV_PATH.chmod(0o755)


def add_env_val(env_key: str, env_val: str, description: str) -> None:
    """Append export statements to ~/usr-bin/source-env,
    creating it if needed."""
    _ensure_source_env()
    export_line = f"# {description}\nexport {env_key}={env_val}"
    with open(SERVER_ENV_PATH, "a") as f:
        f.write(f"\n{export_line}\n")
    print_info(f"Adding {env_key} to source env")
    print_info(f"Description: {description}")
    print_warning(
        """Make sure current command is ran with `&& source source-env`
        or run `source source-env` after
        for changes to take affect in current sesion"""
    )


def add_env_cmd(cmd: str, description: str) -> None:
    _ensure_source_env()
    cmd_line = f"# {description}\n{cmd}"
    with open(SERVER_ENV_PATH, "a") as f:
        f.write(f"\n{cmd_line}\n")
    print_info(f"Adding {cmd} to source env")
    print_info(f"Description: {description}")
    print_warning(
        """Make sure current command is ran with `&& source source-env`
        or run `source source-env` after
        for changes to take affect in current sesion"""
    )


def ensure_dir(path: str) -> Path:
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
            print_success(f"Directory created: {path}")
    except Exception:
        print_error(f"Failed to create directory {path}")
        sys.exit(1)

    return path_obj


def clear_env() -> None:
    """Delete the source-env file if it exists."""
    if SERVER_ENV_PATH.exists():
        SERVER_ENV_PATH.unlink()


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
        err = (
            result.stderr.strip() if capture_output and result.stderr else ""
        )
        print_error(
            f"""Command failed (exit {result.returncode})
            {": " + err if err else ""}"""
        )
        result.check_returncode()  # raises CalledProcessError
    return result


def copy_path(src: str | Path, dest: str | Path) -> None:
    """Recursively copy a file or directory from src to dest.

    Args:
        src:       Source file or directory path.
        dest:      Destination path. For directories,
                   this is the target directory
                   itself (not the parent), mirroring `cp -r src/ dest/`.
    """
    import shutil

    src, dest = Path(src), Path(dest)

    if not src.exists():
        print_error(f"Copy failed: source does not exist: {src}")
        sys.exit(1)

    # Overwrite file/dir if it exists
    if dest.is_dir():
        shutil.rmtree(dest)
    else:
        dest.unlink(missing_ok=True)

    print_step(
        f"Copying {'directory' if src.is_dir() else 'file'}: {src} → {dest}"
    )

    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)

    print_success(f"Copied: {src} → {dest}")


def write_lines(path: str | Path, lines: list[str]) -> None:
    """Write a list of strings to a file, one per line.
    Overwrites the file if it already exists."""
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    if path_obj.exists():
        path_obj.unlink()

    path_obj.write_text("\n".join(lines) + "\n")
    print_success(f"Written: {path}")

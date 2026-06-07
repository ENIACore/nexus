#!/usr/bin/env python3

import os
from pathlib import Path

HOME = Path.home()
USR_BIN = HOME / "bin"
LIB_DIR = USR_BIN / "_lib"
SCRIPTS_DIR = Path("/tmp/server-configs")
SBIN = Path("/usr/local/sbin")
ZSHRC = HOME / ".zshrc"

ZSHRC_BLOCK = """
# Add custom scripts directory to PATH
if [[ ':$PATH:' != *':/usr/local/sbin:'* ]]; then
  export PATH="/usr/local/sbin:$PATH"
fi
"""

BASHRC = HOME / ".bashrc"

BASHRC_BLOCK = """
# Add custom scripts directory to PATH
if [[ ':$PATH:' != *':/usr/local/sbin:'* ]]; then
  export PATH="/usr/local/sbin:$PATH"
fi
"""


def create_dirs():
    SBIN.mkdir(parents=True, exist_ok=True)
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    init = LIB_DIR / "__init__.py"
    if not init.exists():
        init.touch()


def create_symlinks():
    for script in SCRIPTS_DIR.rglob("*.py"):
        link = SBIN / script.stem
        link.unlink(missing_ok=True)
        link.symlink_to(script)
        link.chmod(0o755)


def modify_zshrc():
    zshrc_text = ZSHRC.read_text() if ZSHRC.exists() else ""
    if "/usr/local/sbin" in zshrc_text:
        print("PATH already configured in ~/.zshrc")
        return
    with ZSHRC.open("a") as f:
        f.write(ZSHRC_BLOCK)
    print("Added PATH update to ~/.zshrc")
    os.environ["PATH"] = f"{SBIN}:{os.environ.get('PATH', '')}"


def modify_bashrc():
    bashrc_text = BASHRC.read_text() if BASHRC.exists() else ""
    if "/usr/local/sbin" in bashrc_text:
        print("PATH already configured in ~/.bashrc")
        return
    with BASHRC.open("a") as f:
        f.write(BASHRC_BLOCK)
    print("Added PATH update to ~/.bashrc")
    os.environ["PATH"] = f"{SBIN}:{os.environ.get('PATH', '')}"


def main():
    create_dirs()
    create_symlinks()
    modify_bashrc()


if __name__ == "__main__":
    main()

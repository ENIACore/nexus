#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

HOME = Path.home()
SCRIPTS_DIR = Path("/tmp/server-configs")
SBIN = Path("/usr/local/sbin")
LIB_DIR = SBIN / "_lib"

BASHRC = HOME / ".bashrc"
ZSHRC = HOME / ".zshrc"

PATH_BLOCK = """
# Add custom scripts directory to PATH
if [[ ':$PATH:' != ':/usr/local/sbin:' ]]; then
    export PATH="/usr/local/sbin:$PATH"
fi
"""

IGNORE = {
    # "setup",
    "install",
    # "uninstall",
}


def create_dirs():
    SBIN.mkdir(parents=True, exist_ok=True)
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    init = LIB_DIR / "init.py"
    if not init.exists():
        init.touch()


def move_scripts():
    lib_prefix = SCRIPTS_DIR / "lib"

    for script in SCRIPTS_DIR.rglob("*.py"):
        if script.stem in IGNORE:
            continue

        try:
            script.relative_to(lib_prefix)
            dest = LIB_DIR / script.stem
        except ValueError:
            dest = SBIN / script.stem

        dest.unlink(missing_ok=True)
        shutil.move(str(script), str(dest))
        dest.chmod(0o755)


def add_to_path_config(rc_file: Path):
    rc_text = rc_file.read_text() if rc_file.exists() else ""
    if "/usr/local/sbin" in rc_text:
        return
    with rc_file.open("a") as f:
        f.write(PATH_BLOCK)


def main():
    create_dirs()
    move_scripts()
    add_to_path_config(BASHRC)
    add_to_path_config(ZSHRC)
    os.environ["PATH"] = f"{SBIN}:{os.environ.get('PATH', '')}"


if __name__ == "__main__":
    main()

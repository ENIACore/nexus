#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/ENIACore/server-configs.git"
CLONE_PATH = Path("/tmp/server-configs")
BOOTSTRAP_SCRIPT = Path("/tmp/server-install-scripts.py")
RAW_URL = "https://raw.githubusercontent.com/ENIACore/server-configs/main/lib/install-scripts.py"

print("new SCRIPT!")
subprocess.run(
    ["curl", "-fsSL", RAW_URL, "-o", str(BOOTSTRAP_SCRIPT)], check=True
)
subprocess.run([sys.executable, str(BOOTSTRAP_SCRIPT)], check=True)
BOOTSTRAP_SCRIPT.unlink()

if CLONE_PATH.exists():
    shutil.rmtree(CLONE_PATH)

subprocess.run(["git", "clone", REPO_URL, str(CLONE_PATH)], check=True)
subprocess.run(
    [sys.executable, str(CLONE_PATH / "lib" / "setup.py")], check=True
)

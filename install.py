#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/ENIACore/server-configs.git"
CLONE_PATH = Path("/tmp/server-configs")

if CLONE_PATH.exists():
    shutil.rmtree(CLONE_PATH)

subprocess.run(["git", "clone", REPO_URL, str(CLONE_PATH)], check=True)
subprocess.run(
    [sys.executable, str(CLONE_PATH / "lib" / "install-scripts.py")],
    check=True,
)
subprocess.run(
    [sys.executable, str(CLONE_PATH / "lib" / "setup.py")], check=True
)

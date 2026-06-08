#!/usr/bin/env python3

import shutil
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_dir
from common import copy_path
from config import NGINX_CONFIG_PATH, SERVER_CLONE_PATH
from formatting import print_header, print_info, print_step, print_success

NGINX_SRC_PATH = SERVER_CLONE_PATH / "nginx"
NGINX_SUBDIRS = ["conf", "conf.d", "snippets"]


def main():
    print_header("UPDATING SERVER REVERSE PROXY CONFIGURATION")

    require_dir(str(NGINX_SRC_PATH), "Nginx source directory")

    print_step("Removing old configuration files...")
    for subdir in NGINX_SUBDIRS:
        dest = NGINX_CONFIG_PATH / subdir
        if dest.exists():
            shutil.rmtree(dest)

    print_step("Copying updated nginx configuration...")
    for subdir in NGINX_SUBDIRS:
        copy_path(NGINX_SRC_PATH / subdir, NGINX_CONFIG_PATH / subdir)

    print_success("Configuration files updated successfully")
    print_info("Run nginx-reload to apply changes to the running container")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import subprocess
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import (
    get_input,
    print_error,
    print_header,
    print_info,
    print_step,
    print_warning,
)


def run_ss(args: list[str]) -> str:
    result = subprocess.run(
        ["sudo", "ss"] + args,
        capture_output=True,
        text=True,
    )
    return result.stdout


def show_all_ports() -> None:
    print_step("All Listening Ports (TCP & UDP)")
    print(run_ss(["-tulpn"]))


def show_tcp_ports() -> None:
    print_step("TCP Listening Ports")
    print(run_ss(["-tlpn"]))


def show_udp_ports() -> None:
    print_step("UDP Listening Ports")
    print(run_ss(["-ulpn"]))


def search_port() -> None:
    port = get_input("Enter port number to search for")
    if not port.isdigit():
        print_error("Invalid port number. Please enter a numeric value.")
        return

    print_step(f"Connections on Port {port}")
    output = run_ss(["-tulpn"])
    matches = [line for line in output.splitlines() if f":{port}" in line]

    if matches:
        print("\n".join(matches))
    else:
        print_warning(f"No connections found on port {port}")


def show_listening_processes() -> None:
    print_step("Processes Using Ports")
    output = run_ss(["-tulpn"])
    lines = [line for line in output.splitlines() if "LISTEN" in line]
    print("\n".join(lines) if lines else "No listening processes found")


def show_established() -> None:
    print_step("Established TCP Connections")
    output = run_ss(["-tuln"])
    lines = [line for line in output.splitlines() if "ESTAB" in line]
    print("\n".join(lines) if lines else "No established connections found")


def show_summary() -> None:
    from collections import Counter

    print_step("Port Usage Summary")

    def extract_ports(output: str) -> list[str]:
        ports = []
        for line in output.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 5:
                addr = parts[4]
                port = addr.rsplit(":", 1)[-1]
                if port.isdigit():
                    ports.append(port)
        return ports

    tcp_out = run_ss(["-tlpn"])
    udp_out = run_ss(["-ulpn"])

    tcp_counts = Counter(extract_ports(tcp_out))
    udp_counts = Counter(extract_ports(udp_out))

    print_info("TCP Listening Ports:")
    for port, count in sorted(tcp_counts.items(), key=lambda x: -x[1]):
        print(f"  {count:>4}  {port}")

    print_info("UDP Listening Ports:")
    for port, count in sorted(udp_counts.items(), key=lambda x: -x[1]):
        print(f"  {count:>4}  {port}")


MENU_OPTIONS = {
    "1": ("Show all listening ports (TCP & UDP)", show_all_ports),
    "2": ("Show only TCP listening ports", show_tcp_ports),
    "3": ("Show only UDP listening ports", show_udp_ports),
    "4": ("Search for specific port", search_port),
    "5": ("Show all listening processes", show_listening_processes),
    "6": ("Show established connections", show_established),
    "7": ("Show port summary (count by service)", show_summary),
    "8": ("Exit", None),
}


def show_menu() -> None:
    print_header("Ubuntu Port Monitor Tool")
    for key, (label, _) in MENU_OPTIONS.items():
        print(f"  {key}) {label}")
    print()


def check_ss_available() -> None:
    result = subprocess.run(["which", "ss"], capture_output=True)
    if result.returncode != 0:
        print_error("'ss' command not found. Please install iproute2 package.")
        print_error("sudo apt update && sudo apt install iproute2")
        sys.exit(1)


def main() -> None:
    check_ss_available()

    while True:
        show_menu()
        choice = get_input("Choose an option [1-8]")

        if choice not in MENU_OPTIONS:
            print_error("Invalid option. Please choose 1-8.")
            continue

        _, fn = MENU_OPTIONS[choice]

        if fn is None:
            print_info("Goodbye!")
            sys.exit(0)

        fn()
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

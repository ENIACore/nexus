#!/bin/bash

# Port Monitor Script for Ubuntu
# Shows network ports and processes using them

show_menu() {
    echo "=================================="
    echo "    Ubuntu Port Monitor Tool"
    echo "=================================="
    echo "1) Show all listening ports (TCP & UDP)"
    echo "2) Show only TCP listening ports"
    echo "3) Show only UDP listening ports"
    echo "4) Search for specific port"
    echo "5) Show all listening processes"
    echo "6) Show established connections"
    echo "7) Show port summary (count by service)"
    echo "8) Exit"
    echo "=================================="
}

show_all_ports() {
    echo -e "\n--- All Listening Ports ---"
    sudo ss -tulpn
}

show_tcp_ports() {
    echo -e "\n--- TCP Listening Ports ---"
    sudo ss -tlpn
}

show_udp_ports() {
    echo -e "\n--- UDP Listening Ports ---"
    sudo ss -ulpn
}

search_port() {
    echo -n "Enter port number to search for: "
    read port
    if [[ $port =~ ^[0-9]+$ ]]; then
        echo -e "\n--- Connections on Port $port ---"
        sudo ss -tulpn | grep ":$port"
        if [ $? -ne 0 ]; then
            echo "No connections found on port $port"
        fi
    else
        echo "Invalid port number. Please enter a numeric value."
    fi
}

show_listening_processes() {
    echo -e "\n--- Processes Using Ports ---"
    sudo ss -tulpn | grep LISTEN
}

show_established() {
    echo -e "\n--- Established TCP Connections ---"
    sudo ss -tuln | grep ESTAB
}

show_summary() {
    echo -e "\n--- Port Usage Summary ---"
    echo "TCP Listening Ports:"
    sudo ss -tlpn | awk 'NR>1 {split($4,a,":"); print a[length(a)]}' | sort -n | uniq -c | sort -nr
    echo -e "\nUDP Listening Ports:"
    sudo ss -ulpn | awk 'NR>1 {split($4,a,":"); print a[length(a)]}' | sort -n | uniq -c | sort -nr
    echo -e "\nTop Processes by Port Count:"
    sudo ss -tulpn | grep -o 'users:(([^)]*' | sed 's/users:((//' | cut -d',' -f1 | sort | uniq -c | sort -nr | head -10
}

# Check if ss command exists
if ! command -v ss &> /dev/null; then
    echo "Error: 'ss' command not found. Please install iproute2 package."
    echo "sudo apt update && sudo apt install iproute2"
    exit 1
fi

# Main menu loop
while true; do
    show_menu
    echo -n "Choose an option [1-8]: "
    read choice
    
    case $choice in
        1)
            show_all_ports
            ;;
        2)
            show_tcp_ports
            ;;
        3)
            show_udp_ports
            ;;
        4)
            search_port
            ;;
        5)
            show_listening_processes
            ;;
        6)
            show_established
            ;;
        7)
            show_summary
            ;;
        8)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please choose 1-8."
            ;;
    esac
    
    echo -e "\nPress Enter to continue..."
    read
    clear
done

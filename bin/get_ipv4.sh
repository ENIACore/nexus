#!/bin/bash

PUBLIC_IPV4=$(curl -s4 https://api.ipify.org || curl -s4 https://icanhazip.com || curl -s4 https://ifconfig.me)
echo "Public IPV4 is ${PUBLIC_IPV4}"

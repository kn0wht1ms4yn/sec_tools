#!/bin/bash

if [ $# -le 1 ]; then
    echo "usage $0 <ipAddress> <baseHostName> [filter]"
    exit 1
fi

ip=$1
hostname=$2
shift 2

ffuf -w ~/opt/SecLists/Discovery/DNS/combined_subdomains.txt -u http://$ip -H "Host: FUZZ.$hostname" -mc all "$@"
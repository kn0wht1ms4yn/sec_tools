#!/bin/bash

if [ $# -ne 1 ]; then
    echo "usage: 1_portscan.sh <ipAddress>"
    exit 1
fi

nmap -Pn -n -sT -sV -v $1
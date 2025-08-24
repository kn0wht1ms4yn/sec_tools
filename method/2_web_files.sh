#! /bin/bash
if [ $# -eq 0 ]; then
    echo "usage: $0 <ipAddress> [-caps]"
    exit 1
fi

if [ $2 == "-caps" ]; then
    ffuf -w ~/opt/SecLists/Discovery/Web-Content/raft-large-files.txt -u http://$1/FUZZ -mc all -fc 403,404
else
    ffuf -w ~/opt/SecLists/Discovery/Web-Content/raft-large-files-lowercase.txt -u http://$1/FUZZ -mc all -fc 403,404
fi
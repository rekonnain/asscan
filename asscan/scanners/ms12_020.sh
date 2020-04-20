#!/bin/sh

targets=$*
msfconsole -x "; ; use auxiliary/scanner/rdp/ms12_020_check ; set RHOSTS $targets ; run ; exit" | sed "s/\x1B\[\([0-9]\{1,2\}\(;[0-9]\{1,2\}\)\?\)\?[mGK]//g" | grep -e ^\\[|grep -v complete\)$

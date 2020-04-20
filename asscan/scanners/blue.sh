#!/bin/sh

targets=$*
msfconsole -x "; ; use auxiliary/scanner/rdp/cve_2019_0708_bluekeep ; set CONNECTTIMEOUT 3; set RHOSTS $targets ; run ; exit" | sed "s/\x1B\[\([0-9]\{1,2\}\(;[0-9]\{1,2\}\)\?\)\?[mGK]//g" | grep -e ^\\[|grep -v complete\)$

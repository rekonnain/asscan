#!/bin/sh

targets=$*
msfconsole -x "; ; use auxiliary/scanner/smb/smb_ms17_010 ; set RHOSTS $targets ; run ; exit" | sed "s/\x1B\[\([0-9]\{1,2\}\(;[0-9]\{1,2\}\)\?\)\?[mGK]//g" | grep -e ^\\[|grep -v complete\)$

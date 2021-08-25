#!/bin/sh

domain=$1
user=$2
pass=$3
shift 3
targets=$*
msfconsole -x "; ; use auxiliary/admin/dcerpc/cve_2021_1675_printnightmare ; set DLL_PATH '\\127.0.0.1\dummy' ; set SMBUser $user ; set SMBPass $pass ; set SMBDomain $domain; set RHOSTS $targets ; check ; exit" | sed "s/\x1B\[\([0-9]\{1,2\}\(;[0-9]\{1,2\}\)\?\)\?[mGK]//g" | grep -e ^\\[|grep -v complete\)$

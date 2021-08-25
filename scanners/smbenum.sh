#!/bin/bash

# calls smbmap, smbclient and enum4linux on all targets
# for authenticated queries,
#   ./smbenum.sh -a <domain> <user> <password> target target ... target
# for unauthenticated queries
#   ./smbenum.sh target target ... target

if [ $1 == '-a' ] ; then
    shift 1
    domain=$1
    user=$2
    pass=$3
    shift 3
    targets=$*
else
    domain=''
    user=''
    pass=''
    targets=$*
fi

mkdir -p output
for target in $targets;do
    outfn=output/out.enum.$target
    #enum4linux
    # first, unauth, as authenticated fails if the creds are not valid
    echo Unauthenticated scan: >> $outfn

    enum4linux $target -a -r 2>/dev/null | grep -v 'Working on it' | tee $outfn

    echo >> $outfn
    echo Authenticated scan: >> $outfn
    
    if [ -n "$domain" ] && [ -n "$user" ] && [ -n "$pass" ] ; then
	enum4linux -w $domain -u $domain\\$user -p $pass $target -a -r 2>/dev/null | grep -v 'Working on it'| sed "s/$pass/redacted/g"| tee -a $outfn
    fi

    # smbmap
    if [ -n "$domain" ] && [ -n "$user" ] && [ -n "$pass" ] ; then
	fn=output/out.smbmap.$target
	# smbmap -H $target -u $user -d $domain -p $pass | tee $fn

	# the docker image installs cme via pipx
	cme=`which cme`
	if [ -z "$cme" ] ; then
	    cme=/root/.local/pipx/venvs/crackmapexec/bin/cme
	fi
	
	$cme smb -u $user -d $domain -p $pass --shares --sessions --loggedon-users --pass-pol --sam $target| sed -r "s/[[:cntrl:]]\[[0-9]{1,3}m//g" | sed "s/$pass/redacted/g" | tee $fn
	# copy to the output file
	cat $fn >> $outfn
	disks=`$cme smb -u $user -d $domain -p $pass --shares --sam $target | sed -r "s/[[:cntrl:]]\[[0-9]{1,3}m//g" | sed "s/$pass/redacted/g" | grep -A 500 -- -----------|grep -v -- ----------- | awk '{print $5}' `
	for disk in $disks ; do
	    smbmap -H $target -u $user -d $domain -p $pass -r $disk | sed "s/$pass/redacted/g"| tee -a $outfn
	done
    fi
done
    

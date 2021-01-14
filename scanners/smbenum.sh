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
    if [ -n "$domain" ] && [ -n "$user" ] && [ -n "$pass" ] ; then
	enum4linux -w $domain -u $domain\\$user -p $pass $target -a -r 2>/dev/null | tee $outfn
    else
	enum4linux $target -a -r 2>/dev/null | tee $outfn
    fi

    # smbmap
    if [ -n "$domain" ] && [ -n "$user" ] && [ -n "$pass" ] ; then
	fn=output/out.smbmap.$target
	smbmap -H $target -u $user -d $domain -p $pass | tee $fn
	# copy to the output file
	cat $fn >> $outfn
	disks=`grep -A 10000 Disk $fn |grep -v Disk|grep -v -- ----|awk '{print $1}'`
	for disk in $disks ; do
	    smbmap -H $target -u $user -d $domain -p $pass -r $disk| tee -a $outfn
	done
    fi
done
    

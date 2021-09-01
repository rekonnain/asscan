#!/usr/bin/env python3

import sys
import results

def printhost(hosts, ip):
    try:
        su = results.smbsummary(hosts, ip)
        print('  %16s %16s %16s   %s'%(ip, su['domain'], su['name'], su['osversion']))
    except:
        print('  %s'%ip)

def report(dir):
    r = results.Results()
    r.read_all(dir)
    print("Hosts with readable shares:")
    for key in results.sorted_addresses(results.filter_by_shares(r.hosts, readable=True, writable=False)):
        printhost(r.hosts, key)
    print("\nHosts with writable shares:")
    for key in results.sorted_addresses(results.filter_by_shares(r.hosts, readable=False, writable=True)):
        printhost(r.hosts, key)
    print("\nHosts vulnerable to Bluekeep:")
    for key in results.sorted_addresses(results.sorted_addresses(results.filter_by_bluekeep(r.hosts).keys())):
        printhost(r.hosts, key)
    print('\nHosts vulnerable to MS17-010:')
    for key in results.sorted_addresses(results.sorted_addresses(results.filter_by_ms17010(r.hosts).keys())):
        printhost(r.hosts, key)
    print("\nHosts vulnerable to MS12-020:")
    for key in results.sorted_addresses(results.sorted_addresses(results.filter_by_ms12020(r.hosts).keys())):
        printhost(r.hosts, key)
    print('\nHosts vulnerable to CVE-2021-1675 (printnightmare):')
    for key in results.sorted_addresses(results.sorted_addresses(results.filter_by_cve_2021_1675(r.hosts).keys())):
        printhost(r.hosts, key)


if __name__=='__main__':
    report(sys.argv[1])

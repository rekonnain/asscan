#!/usr/bin/env python3

import sys
import results

def report(dir):
    r = results.Results()
    r.read_all(dir)
    print("Hosts with readable shares:")
    for key in results.filter_by_shares(r.hosts, readable=True, writable=False):
        print('  %s'%key)
    print("\nHosts with writable shares:")
    for key in results.filter_by_shares(r.hosts, readable=False, writable=True):
        print('  %s'%key)
    print("\nHosts vulnerable to Bluekeep:")
    for key in results.sorted_addresses(results.filter_by_bluekeep(r.hosts).keys()):
        print('  %s'%key)
    print('\nHosts vulnerable to MS17-010:')
    for key in results.sorted_addresses(results.filter_by_ms17010(r.hosts).keys()):
        print('  %s'%key)
    print("\nHosts vulnerable to MS12-020:")
    for key in results.sorted_addresses(results.filter_by_ms12020(r.hosts).keys()):
        print('  %s'%key)
    print('\nHosts vulnerable to CVE-2021-1675 (printnightmare):')
    for key in results.sorted_addresses(results.filter_by_cve_2021_1675(r.hosts).keys()):
        print('  %s'%key)


if __name__=='__main__':
    report(sys.argv[1])

#!/usr/bin/env python

""" Pretty prints a dictionary """
def dict2str(d):
    def dictifylist(val):
        if type(val) == list:
            d = {}
            for i in range(len(val)):
                d[str(i)] = val[i]
            return d
        else:
            return val
    def processkeys(d, indent):
        lines = []
        for key, val in d.items():
            if type(val) == list:
                lines.append("%s%s%s ->"%(indent * ' ', key, (18 - indent - len(key)) * ' '))
                lines += processkeys(dictifylist(val), indent + 2)
            elif type(val) == dict:
                lines += processkeys(val, indent + 2)
            else:
                lines.append("%s%s%s : %s"%(indent * ' ', key, (20 - indent - len(key)) * ' ', str(val)))
        return lines
    return '\n'.join(processkeys(d, 0))
    

if __name__=='__main__':
    foo={'a':1, 'b': 2, 'c': {'foo':'bar','asdfasdf':'kikkeli', 'xyz': { 'a':'b'}}, 'd': ['hihi','haha',{'hoho': ['perkele', 'kikkeli']}]}
    print(dict2str(foo))

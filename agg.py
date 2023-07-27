#!/usr/bin/python3
import sys

l_argv = sys.argv
in_file = l_argv[1]
fptr = open(in_file,'r')
lines = fptr.readlines()
num = list()
for l in lines:
    l.strip()
    l = l.replace('\n','')
    num.append(float(l))
avr = sum(num)/len(num)
fptr.close()
print(avr)

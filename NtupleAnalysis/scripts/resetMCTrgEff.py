#!/usr/bin/env python

import sys

def main():

    jsonfile = sys.argv[1]
    newjson = jsonfile.replace(".json",".new")
    fIN = open(jsonfile,"r")
    fOUT = open(newjson,"w")

    mcParamsFound = False
    for line in fIN:

	if "mcParameters" in line:
	    mcParamsFound = True

	if mcParamsFound:
            if "efficiency" in line:
                line = '                    "efficiency"      :1.0,\n'
            if "uncertaintyPlus" in line:
                line = '                    "uncertaintyPlus" :0.0,\n'
            if "uncertaintyMinus" in line:
                line = '                    "uncertaintyMinus" :0.0,\n'

	fOUT.write(line)	
	sys.stdout.write(line)

if __name__ == "__main__":
    main()

#!/usr/bin/env python

"""
Reads a bunch of pa2 (SPAN) files and extracts Option deltas into a CSV.

I believe this will work under py2 or py3.
"""

from __future__ import print_function, unicode_literals

from datetime import datetime
from decimal import Decimal
import fileinput
import glob
import sys

def readfile(inp):
    """Read lines from the file-like object inp, and yield rows
    of a CSV, one row per option delta.
    """
    # Now iterate over the records
    for firstline in inp:
        # New SPAN file, set business date and erase previous data
        if firstline.startswith("0 "):
            BUSDATE = datetime.strptime(firstline[8:16], "%Y%m%d").strftime("%Y-%m-%d")
            EXPIRIES = {}   # Unused!
            STRIKES = {}
        
        # Store the "strike price locator" for P records
        # What we actually store is the divisor (some power of ten)
        elif firstline.startswith("P "):
            if firstline[15:18] != "OOF":
                continue
            commodity = firstline[5:15].strip()
            strike = int(firstline[36:39])
            STRIKES[commodity] = Decimal(10) ** strike
        
        # Store exact expiry dates from B records
        elif firstline.startswith("B "):
            # Filter for option records only
            if firstline[15:18] != "OOF":
                continue
            commodity = firstline[5:15].strip()
            month = firstline[18:24]
            expirydate = datetime.strptime(firstline[91:99], "%Y%m%d")
            EXPIRIES[(commodity, month)] = expirydate
        
        # Process record types 81 and 82 together
        elif firstline.startswith("81"):
            secondline = inp.readline()
            if not secondline.startswith("82"):
                raise ValueError("""Invalid file format, found an 81 record without an 82 record after it.
                    The 81 record was: %s""" % firstline)
            
            # Filter for option records only
            if firstline[25:28] != "OOF":
                continue
            
            # Grab data from the fixed-width records
            commodity = firstline[5:15].strip()
            callput = firstline[28]
            month = firstline[29:35]
            # Scale the strike price according to the P record
            strike = Decimal(firstline[47:54]) / STRIKES[commodity]
            # Scale the delta as 9V9(4)
            delta = Decimal(secondline[101] + secondline[96:101]) / 10**4
            # Scale the implied volatility as 99V9(6)
            impvol = Decimal(secondline[102:110]) / 10**6
            yield ",".join((
                BUSDATE,
                commodity,
                callput,
                str(strike),
                month,
                str(delta),
                str(impvol),
                ))

if __name__ == '__main__':
    if sys.platform == 'win32':
        # Add glob-expansion for Windows
        filelist = []
        for fname in sys.argv[1:]:
            filelist += glob.glob(fname)
    else:
        # Unix systems can do this at the shell
        filelist = sys.argv[1:]
    
    print("Date,Underlying,C/P,Strike,Expiry,Delta,IV")
    for line in readfile(fileinput.input(files=filelist, mode="rU")):
        print(line)

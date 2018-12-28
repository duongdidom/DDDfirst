"""
in designated folder, find a bunch of pa2 files that being after 10:30pm.
find equivalent position file
find equivalent 3 rc cons files
run those combination of files for 21% risk capital calculation
"""

import os
import glob
import datetime

""" input """
parent_dir = r"C:\SPANfiles\201812"
cutoff_time = "22:30:00"
""""""""""""
cutoff_time = datetime.datetime.strptime(cutoff_time,"%H:%M:%S") # convert cut off time from hh:mm:ss to yyyy-mm-dd hh:mm:ss


# 1. find a bunch of pa2 files that their modified time is after predefined cutoff time
def Get_Timestamp():
    all_pa2 = glob.glob(parent_dir + "\\" + "*NZX.*" + "*.s.pa2")   # get list of pa2 files start with NZX... end with .s.pa2

    timestamp_list = []

    for pa2 in all_pa2: 
        mtime = os.path.getmtime(pa2)   # get modified time of pa2 file
        mtime = datetime.datetime.fromtimestamp(mtime)    # convert modified time from float to yyyy-mm-dd hh:mm:ss.ssss
        
        sameday_cutoff = mtime.replace(hour=cutoff_time.time().hour, minute=cutoff_time.time().minute, second=cutoff_time.time().minute, microsecond=0)   # from cut off time, find cut off time of the same day of the modified date & time

        if mtime > sameday_cutoff:  # check if modified time of pa2 file is after cut off time
            timestamp = pa2[(len(parent_dir)+1):35]     # extract time stamp from file name
            timestamp_list.append(timestamp)            # append time stamp to timestamp list

    return timestamp_list


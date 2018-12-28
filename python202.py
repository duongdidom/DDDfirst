"""
in designated folder, find a bunch of pa2 files that being after 10:30pm.
find equivalent position file & 3 rc cons files
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
LOG = []    # create a empty list for logging
LOG.append("start time: " + str(datetime.datetime.now()))   # insert start time to log list

# 1. find a bunch of pa2 files that their modified time is after predefined cut off time
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

# 2. find equivalent original position and rc_cons files at each time stamp
def Get_files(timestamp_list):
    execution_list =[]
    # define an empty execution list. Will be the result of the function
    # in order to store for each timestamp: pa2, position, & 3 rc cons files
    execution_list.append(["date_time","pa2","position","rc_cons_Scan","rc_cons_Interm","rc_cons_Intercomm","rc_cons_House"])   # header for execution list

    for timestamp in timestamp_list:    # loop through list
        # grab position and rc Cons files
            # glob() return result into a list
        posfile = glob.glob(parent_dir + "\\" + timestamp + "_SPANPOS*")
        rcCons_scan = glob.glob(parent_dir + "\\" + timestamp + "_rc_scan.csv")
        rcCons_intermonth = glob.glob(parent_dir + "\\" + timestamp + "_rc_intermonth.csv")
        rcCons_intercomm = glob.glob(parent_dir + "\\" + timestamp + "_rc_intercomm.csv")
        rcCons_house = glob.glob(parent_dir + "\\" + timestamp + "_house.csv")

        # check if those files exist
        if len(posfile) < 1:
            LOG.append("Position file for " + timestamp + " not found")
            posfile = "N/a"
        else:
            posfile = posfile[0]
        if len(rcCons_scan) < 1:
            LOG.append("RC cons Scan file for " + timestamp + " not found")
            rcCons_scan = "N/a"
        else:
            rcCons_scan = rcCons_scan[0]
        if len(rcCons_intermonth) < 1:
            LOG.append("RC cons Intermonth file for " + timestamp + " not found")
            rcCons_intermonth = "N/a"
        else:
            rcCons_intermonth = rcCons_intermonth[0]
        if len(rcCons_intercomm) < 1:
            LOG.append("RC cons Intercomm file for " + timestamp + " not found")
            rcCons_intercomm = "N/a"
        else:
            rcCons_intercomm = rcCons_intercomm[0]
        if len(rcCons_house) < 1:
            LOG.append("RC cons House file for " + timestamp + " not found")
            rcCons_house = "N/a"
        else:
            rcCons_house = rcCons_house[0]

        # find pa2 filename again
        pa2 = glob.glob(parent_dir + "\\" + timestamp + "*NZX*" + "*.s.pa2")
        pa2 = pa2[0]

        # append to execution list
        execution_list.append([timestamp,pa2, posfile,rcCons_scan, rcCons_intermonth,rcCons_intercomm, rcCons_house])

    return execution_list

### MAIN ###
timestamp_list = Get_Timestamp()
Get_files(timestamp_list)
LOG.append("finish time: " + str(datetime.datetime.now()))   # insert finish time to log list
for log in LOG: print (log)
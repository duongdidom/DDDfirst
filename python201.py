# # Breakdown and recreate Risk Capital calculation script

import os   # import os module to change working directory
import glob     # import glob module to file list of filename that match certain criteria
from datetime import datetime, date, timedelta   # import datetime module to convert string to date format
import shutil   # import shutil module to copy file

# define start date and end date
startD = "09/11/2018" 
endD = "10/11/2018"

# define parent directory where input, cons, output folders are stored. This assumes all three folders are under a parent folder, mainly for testing purpose. Might need to modify in real situation
parent_dir = r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital"    # insert r before a string so that python interprete string as raw

#1. Collect input files:
def find_current_files(yyyymmdd,hhmmss):    # variable = date and current execution time
    out_timestamp = yyyymmdd + "-" + hhmmss + "_"

    #1.1. find latest pa2 and position file then copy it to output folder
    os.chdir(parent_dir + r"\in")    # define new working directory = where input files are 

    latest_pa2 = max(glob.iglob("NZX." + yyyymmdd + "*.pa2"), key = os.path.getmtime) # find the latest modified file with specified format

    latest_position = max(glob.iglob("SPANPOS_" + yyyymmdd + "*.txt"), key = os.path.getmtime) # find the latest modified file with specified format
    
    pa2File = parent_dir + r"\\out\\" + out_timestamp + latest_pa2    # define output path for latest pa2 file

    posistionFile = parent_dir + r"\\out\\" + out_timestamp + latest_position   # define output path for latest position file

    shutil.copy(os.getcwd() + "\\" + latest_pa2, pa2File) # copy() function copies from source to destination
    shutil.copy(os.getcwd() + "\\" + latest_position, posistionFile) # copy latest pa2 and position file in input folder to output folder

    #1.2. define a bunch of newly created files

    """latest_pa2 = os.getcwd() + "\\" + latest_pa2     # add directory for latest pa2 file

    latest_position = os.getcwd() + "\\" + latest_position     # add directory for latest position file
    """

############################### MAIN ###############################
# convert start date and end date to date format. strptime = string parse time = retrieve time string
startD = datetime.strptime(startD, "%d/%m/%Y")    # 2nd parameter after comma = how original date was formatted
endD = datetime.strptime(endD, "%d/%m/%Y")  # output would be in date format, not string format
dates = [startD + timedelta(x) for x in range(0, (endD-startD).days)]   # for each x from 0 to number days between start date and end date, convert x from integer to date. Then plus that number to start date. Put that into a list

hhmmss = datetime.now().strftime("%H%M%S")  # define execution time to create time stamp in output files. strftime = string format time = format time string
for date in dates:  # loop for all date in dates list
    #1. Collect input files (cons, input). Define newly created file and path. 
    find_current_files(date.strftime("%Y%m%d"), hhmmss)
    #2. read pa2 file

    #3. read 3 constant files

    #4. calculate new stretched scan range, intermonth, intercomm

    #5. write risk capital pa2 file
    # new pa2 file wouldn't have new risk array calculated, has to be recalculated using whatif file

    #6. write whatif file 

    #7. read position file

    #8. calculate and write position file with sum positions

    #9. calculate and get report for:
    #9.1. margin

    #9.2. risk capital

    #10. calculate delta adjusted net exposure for options

    #11. read cons house file

    #12. read pbreq margin and pbreq risk capital files

    #13. use criteria rule to generate risk capital for each participant

    #14. write final excel file
# # Breakdown and recreate Risk Capital calculation script

import os   # import os module to change working directory
import glob     # import glob module to file list of filename that match certain criteria
from datetime import datetime, date, timedelta   # import datetime module to convert string to date format

# define start date and end date
startD = "09/11/2018" 
endD = "10/11/2018"

# define parent directory where input, cons, output folders are stored. This assumes all three folders are under a parent folder, mainly for testing purpose. Might need to modify in real situation
parent_dir = r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital"    # insert r before a string so that python interprete string as raw

#1. Collect input files:
os.chdir(parent_dir + r"\in")    # define new working directory = where input files are 

# latest_pa2 = max(glob.iglob("NZX." + endD.strf # find the latest modified file with specified format

############################### MAIN ###############################
# convert start date and end date to date format. strptime = string parse time = retrieve time string
startD = datetime.strptime(startD, "%d/%m/%Y")    # 2nd parameter after comma = how original date was formatted
endD = datetime.strptime(endD, "%d/%m/%Y")  # output would be in date format, not string format

dates = [startD + timedelta(x) for x in range(0, (endD-startD).days)]   # for each x from 0 to number days between start date and end date, convert x from integer to date. Then plus that number to start date. Put that into a list
for date in dates:  # loop for all date in dates list
    #1. Collect input files (cons, input). Define newly created file and path. 

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
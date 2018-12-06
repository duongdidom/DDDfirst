# # Breakdown and recreate Risk Capital calculation script

import os   # import os module to change working directory
import glob     # import glob module to file list of filename that match certain criteria
from datetime import datetime, date, timedelta   # import datetime module to convert string to date format
import shutil   # import shutil module to copy file
import sys

# define start date and end date
startD = "09/11/2018" 
endD = "10/11/2018"

# define parent directory where input, cons, output folders are stored. This assumes all three folders are under a parent folder, mainly for testing purpose. Might need to modify in real situation
parent_dir = r"C:\Users\douglas.cao\Documents\Python\RiskCapital"    # insert r before a string so that python interprete string as raw. C:\Users\DDD\Downloads\Test for home

#1. Collect source and new files:
def find_current_files(yyyymmdd,hhmmss):    # variable = date and current execution time
    out_timestamp = yyyymmdd + "-" + hhmmss + "_"

    ### 1.1. find latest pa2 and position file then copy it to output folder
    os.chdir(parent_dir + r"\in")    # define new working directory = where input files are 

    latest_pa2 = max(glob.iglob("NZX." + yyyymmdd + "*.pa2"), key = os.path.getmtime) # find the latest modified file with specified format

    latest_position = max(glob.iglob("SPANPOS_" + yyyymmdd + "*.txt"), key = os.path.getmtime) # find the latest modified file with specified format
    
    pa2_pa2 = parent_dir + r"\\out\\" + out_timestamp + latest_pa2    # define output path for latest pa2 file

    position_txt = parent_dir + r"\\out\\" + out_timestamp + latest_position   # define output path for latest position file
    
    shutil.copy(os.getcwd() + "\\" + latest_pa2, pa2_pa2) # copy() function copies from source to destination
    shutil.copy(os.getcwd() + "\\" + latest_position, position_txt) # copy latest pa2 and position file in input folder to output folder

    ### 1.2. find constant files and copy them to output folder
    # path and filename for cons files
    cons_rc_intercomm_csv =  parent_dir + r"\\cons\\cons_rc_intercomm.csv"
    cons_rc_intermonth_csv =  parent_dir + r"\\cons\\cons_rc_intermonth.csv"
    cons_rc_scan_csv =  parent_dir + r"\\cons\\cons_rc_scan.csv"
    cons_house_csv = parent_dir + r"\\cons\\cons_house.csv"

    # path and filenames for cons files in output folder = original + timestamp
    rc_intercomm_csv =  parent_dir + r"\\out\\" + out_timestamp + r"rc_intercomm.csv"
    rc_intermonth_csv =  parent_dir + r"\\out\\" + out_timestamp + r"rc_intermonth.csv"
    rc_scan_csv =  parent_dir + r"\\out\\" + out_timestamp + r"rc_scan.csv"
    house_csv = parent_dir + r"\\out\\" + out_timestamp + r"house.csv"
    
    # copy from cons folder to output folder
    try:
        shutil.copy(cons_rc_intercomm_csv,rc_intercomm_csv)
        shutil.copy(cons_rc_intermonth_csv,rc_intermonth_csv)
        shutil.copy(cons_rc_scan_csv,rc_scan_csv)
        shutil.copy(cons_house_csv,house_csv)
    except Exception as err:
        print (err)     # try grouping all of copying tasks into one

    ### 1.3. define a bunch of newly created files
    # Modified files
    new_pa2 = out_timestamp + r"new.pa2"
    sum_position_txt =  out_timestamp + r"sum.txt"
    
    # Newly created files
    whatif_xml =  out_timestamp + r"whatif.xml"
    # Leave out file extension to add identifier in write_margin/rc_spanit function
    spanit_txt = out_timestamp + r"spanit_" 
    # Leave out file extension to add identifier in write_margin/rc_spanit function
    span_spn = out_timestamp + r"span_" 
    # Leave out file extension to add identifier in call_span_report function
    pbreq_csv =  out_timestamp + r"pbreq_" 
    final_csv = out_timestamp + r"final.csv"

    return (pa2_pa2, position_txt, rc_intercomm_csv,rc_intermonth_csv, rc_scan_csv, house_csv, new_pa2, sum_position_txt, whatif_xml, spanit_txt, span_spn, pbreq_csv, final_csv)

#2. read pa2 & store data into various lists
### 2.1. read 
def read_pa2(pa2File):
    with open(pa2File,"r") as f: # open pa2 file in read mode and name this file as f
        pa2_list = f.readlines() # read all lines in pa2File and store each line into list
    return (pa2_list)

### 2.2. retrieve and store
def parse_pa2(pa2_list): # from pa2 list, which is from original pa2 file, break down by record type and store them into several dictionaries
    ### 2.2.1. create bunch of dictionary to store data
    price_list = []             # for future prices    
    price_param_list = []       # calculation parameter    
    intermonth_dict = []        # intermonth spread charge
    intermonth_param_dict = []  # intermonth parameter details
    intercomm_dict = []         # intercommodity spread charge
    intercomm_param_dict = []   # intercommodity parameter details
    instrument_dict = []        # instrument type & maturity
    option_dict = []            # option prices and delta
    deltascale_dict = []        # instrument type, maturity & delta scaling factor
    currency_dict = []          # currency    
    
    for line in pa2_list:
        # price_dict = dictionary of futures prices [commodity, type, maturity, price] eg ['WMP','FUT',201801,31200]
        if line.startswith("82") and (str(line[25:28]) == "FUT" or str(line[25:28]) == "PHY"):
            price_list.append({
            'comm':str(line[5:15]).strip(),
            'instype':str(line[25:28]),
            'maturity':int(line[29:35].strip() or 0), 
            'dsp':float(line[110:117].strip() or 0)
            })

        elif line.startswith("P"):
            price_param_list.append({
            'comm':str(line[5:15]).strip(),
            'instype':str(line[15:18]),
            'dspdl':int(line[33:36].strip() or 0),
            'cvf':float(line[41:55].strip() or 0)/10000000,
            'strikedl':int(line[36:39].strip() or 0),
            'curr':str(line[65:68])
            })
        
    print ("PAU")
    ### 2.2.2. add extra details in price_dict from price_param_dict
    

############################### MAIN ###############################
# convert start date and end date to date format. strptime = string parse time = retrieve time string
startD = datetime.strptime(startD, "%d/%m/%Y")    # 2nd parameter after comma = how original date was formatted
endD = datetime.strptime(endD, "%d/%m/%Y")  # output would be in date format, not string format
dates = [startD + timedelta(x) for x in range(0, (endD-startD).days)]   # for each x from 0 to count number days between start date and end date, convert x from integer to date. Then plus that number to start date. Put that into a list

hhmmss = datetime.now().strftime("%H%M%S")  # define execution time to create time stamp in output files. strftime = string format time = format time string
for date in dates:  # loop for all date in dates list
    #1. Collect input files (cons, input). Define newly created file and path. 
    (pa2File, posistionFile, rc_intercomm_csv,rc_intermonth_csv, rc_scan_csv, house_csv, new_pa2, sum_position_txt, whatif_xml, spanit_txt, span_spn, pbreq_csv, final_csv) = find_current_files(date.strftime("%Y%m%d"), hhmmss)
    
    #2. read pa2 file & store data into various lists
    pa2_list = read_pa2(pa2File)
    parse_pa2(pa2_list)
    
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
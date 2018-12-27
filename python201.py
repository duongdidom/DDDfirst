# # Breakdown and recreate Risk Capital calculation script

from __future__ import division     # import division so that / is mapped to __truediv__() and return more decimals figure
import logging  # import logging to log any error
import os   # import os module to change working directory
import glob     # import glob module to file list of filename that match certain criteria
from datetime import datetime, date, timedelta   # import datetime module to convert string to date format
import shutil   # import shutil module to copy file
import csv      # import csv to read csv file
import copy     # import copy to copy from (sum bp account w/o currency) to (sum bp account with currency)
import subprocess   # import subprocess module to call another application

# define start date and end date
# convert start date and end date to date format. strptime = string parse time = retrieve time string
startD = datetime.strptime("16/11/2018", "%d/%m/%Y")    # 2nd parameter after comma = how original date was formatted
endD = datetime.strptime("17/11/2018", "%d/%m/%Y")      # output would be in date format, not string format

# define parent directory where input, cons, output folders are stored. This assumes all three folders are under a parent folder, mainly for testing purpose. Might need to modify in real situation
parent_dir = r"C:\Users\douglas.cao\Documents\Python\RiskCapital"    # insert r before a string so that python interprete string as raw. C:\Users\DDD\Downloads\Test for home

# create a log file
LOGFILE = parent_dir + r"\out\log.log"
logging.basicConfig(filename=LOGFILE.format(datetime.now()), level=logging.INFO)    # tell python to start logging

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
    new_pa2 = parent_dir + r"\\out\\" + out_timestamp + r"new.pa2"
    sum_position_txt =  parent_dir + r"\\out\\" + out_timestamp + r"sum.txt"
    sum_position_rc_txt =  parent_dir + r"\\out\\" + out_timestamp + r"sum_rc.txt"
    
    # Newly created files
    whatif_xml =  parent_dir + r"\\out\\" + out_timestamp + r"whatif.xml"
    # Leave out file extension to add identifier in write_margin/rc_spanit function
    spanit_txt = parent_dir + r"\\out\\" + out_timestamp + r"spanit_" 
    # Leave out file extension to add identifier in write_margin/rc_spanit function
    span_spn = parent_dir + r"\\out\\" + out_timestamp + r"span_" 
    # Leave out file extension to add identifier in call_SPAN_report function
    pbreq_csv =  parent_dir + r"\\out\\" + out_timestamp + r"pbreq_" 
    final_csv = parent_dir + r"\\out\\" + out_timestamp + r"final.csv"

    return (pa2_pa2, position_txt, rc_intercomm_csv,rc_intermonth_csv, rc_scan_csv, house_csv, new_pa2, sum_position_txt,sum_position_rc_txt, whatif_xml, spanit_txt, span_spn, pbreq_csv, final_csv)

#2. read pa2 & store data into various lists
### 2.1. read 
def read_pa2(pa2_pa2):
    with open(pa2_pa2,"r") as f: # open pa2 file in read mode and name this file as f
        pa2_list = f.readlines() # read all lines in pa2 file and store each line into list
    return (pa2_list)

### 2.2. retrieve and store
def parse_pa2(pa2_list): # from pa2 list, which is from original pa2 file, break down by record type and store them into several lists
    ### 2.2.1. create bunch of lists to store data
    price_list = []             # for future prices    
    price_param_list = []       # calculation parameter    
    intermonth_list = []        # intermonth spread charge
    intermonth_param_list = []  # intermonth parameter details
    intercomm_list = []         # intercommodity spread charge
    intercomm_param_list = []   # intercommodity parameter details
    instrument_list = []        # instrument type & maturity
    deltascale_list = []        # instrument type, maturity & delta scaling factor
    option_list = []            # option prices and delta    
    currency_list = []          # currency    
    
    for line in pa2_list:
        # price_list = list of futures prices [commodity, type, maturity, price]
        # eg ['WMP','FUT',201801,31200]
        if line.startswith("82") and (str(line[25:28]) == "FUT" or str(line[25:28]) == "PHY"):
            price_list.append({
            'comm':str(line[5:15]).strip(),    # strip() remove any space character
            'instype':str(line[25:28]),
            'maturity':int(line[29:35].strip() or 0),  # if result is blank string after stripping, will take value 0 to be able to convert to integer
            'dsp':float(line[110:117].strip() or 0)
            })

        # list of all calc parameters [commodity, type, settlement price decimal locator, contract value factor, strike price decimal locator,currency] 
        # eg ['MKP','OOF',2,6000,2,'NZD'] 
        elif line.startswith("P"):
            price_param_list.append({
            'comm':str(line[5:15]).strip(),
            'instype':str(line[15:18]),
            'dspdl':int(line[33:36].strip() or 0),
            'cvf':float(line[41:55].strip() or 0)/10000000,
            'strikedl':int(line[36:39].strip() or 0),
            'curr':str(line[65:68])
            })
        
        # list of intermonth spreads[commodity, tier a, tier b, spread] 
        # eg ['WMP',1,2,130]
        elif line.startswith("C"):
            intermonth_list.append({
            'comm':str(line[2:8]).strip(),
            'tiera':int(line[23:25].strip() or 0),
            'tierb':int(line[30:32].strip() or 0),
            'spread':int(line[14:21].strip() or 0)
            })
        
        # list of intermonth details[commodity, tier number 1, start month, end month...tiers 2,...,3,...,4,...]
        # eg ['WMP',1,201805,201807,2,201808,201905,3,201906,202006,0,0,0]
        elif line.startswith("3"):      
            intermonth_param_list.append({
            'comm':str(line[2:8]).strip(),
            'tier1':int(line[10:12].strip() or 0),
            'tier1start':int(line[12:18].strip() or 0),
            'tier1end':int(line[18:24].strip() or 0),
            'tier2':int(line[24:26].strip() or 0),
            'tier2start':int(line[26:32].strip() or 0),
            'tier2end':int(line[32:38].strip() or 0),
            'tier3':int(line[38:40].strip() or 0),
            'tier3start':int(line[40:46].strip() or 0),
            'tier3end':int(line[46:52].strip() or 0),
            'tier4':int(line[52:54].strip() or 0),
            'tier4start':int(line[54:60].strip() or 0),
            'tier4end':int(line[60:66].strip() or 0)
            })

        # list of intercomm spreads[commodity a, delta a, commodity b, delta b, spread]
        # eg ['WMP',20,'SMP',29,30]
        elif line.startswith("6"):
            intercomm_list.append({
            'comma':str(line[20:26]).strip(),
            'deltaa':int(line[26:29].strip() or 0),
            'commb':str(line[38:44]).strip(),
            'deltab':int(line[44:47].strip() or 0),
            'spread':int(line[9:12].strip() or 0)
            })
            
        # list of intercomm groups and up to ten constituent commodities
        # eg ['CDA', 'WMP','MKP']
        elif line.startswith("5"):
            intercomm_param_list.append({
            'commgroup':str(line[2:5]).strip(),
            'comm1':str(line[12:18]).strip(),
            'comm2':str(line[18:24]).strip(),
            'comm3':str(line[24:30]).strip(),
            'comm4':str(line[30:36]).strip(),
            'comm5':str(line[36:42]).strip(),
            'comm6':str(line[42:48]).strip(),
            'comm7':str(line[48:54]).strip(),
            'comm8':str(line[54:60]).strip(),
            'comm9':str(line[60:66]).strip(),
            'comm10':str(line[66:72]).strip()
            })
            
        # list of instruments by type and maturity, one option record per maturity no individual records for call/put or diff strikes [commodity, type, maturity] 
        # eg ['WMP','OOF',201801]
        elif line.startswith("B") and line[15:18] != "PHY":            
            instrument_list.append({
            'comm':str(line[5:15]).strip(),
            'instype':str(line[15:18]),
            'maturity':int(line[18:24].strip() or 0)
            })
        
        # same as above, incl delta scaling factor
            deltascale_list.append({
            'comm':str(line[5:15]).strip(),
            'instype':str(line[15:18]),
            'maturity':int(line[18:24].strip() or 0),
            'deltasf':int(line[85:91].strip() or 0)
            })

        # list of options prices and deltas [commodity,option on physical or future,call or put, maturity,strike,composite delta,dsp]
        elif line.startswith("82") and (str(line[25:28]) == "OOF" or str(line[25:28]) == "OOP"):
            option_list.append({
            'comm':str(line[5:15]).strip(),
            'instype':str(line[25:28]),
            'callput':str(line[28:29]),
            'maturity':int(line[38:44].strip() or 0),
            'strike':int(line[47:54].strip() or 0),
            'delta':int(line[96:101].strip() or 0) * (-1 if str(line[101:102]) == "-" else 1),    # multiply with -1 in case delta is negative
            'dsp':int(line[110:117].strip() or 0) * (-1 if str(line[117:118]) == "-" else 1),
            })
        
        # list of currency exchange rates [currency converted from, currency converted to, rate]
        # eg ['USD','NZD',1.450537]
        elif line.startswith("T"):            
            currency_list.append({
            'curra':str(line[2:5]),
            'currb':str(line[6:9]),
            'rate':float(line[10:20])/1000000
            })

    # # checking
    # print ("price list")
    # for l in price_list: print (l) 
    # print ("price param")
    # for l in price_param_list: print (l)
    # print ("intermonth list")
    # for l in intermonth_list: print (l)
    # print ("intermonth param")
    # for l in intermonth_param_list: print (l)
    # print ("intercomm list")
    # for l in intercomm_list: print (l)
    # print ("intercom param")
    # for l in intercomm_param_list: print (l)
    # print ("instrument")
    # for l in instrument_list: print (l)
    # print ("delta scal")
    # for l in deltascale_list: print (l)
    # print ("option")
    # for l in option_list: print (l)
    # for l in currency_list : print (l)
    
    ### 2.2.2. add extra details in price_list[] from price_param_list[]
    # new price_list[] = [commodity, type, maturity, price, settlement price decimal locator, contract value factor] 
    # eg ['MKP','FUT',201809,655,2,6000] 
    for price in price_list:
        appended = False    # define appended boolean, default = false
        for price_param in price_param_list:
            if price['comm'] == price_param['comm'] and price['instype'] == price_param['instype']: # condition match comm and instype
                price.update({
                'dspdl':price_param['dspdl'],
                'cvf':price_param['cvf']
                })      # add value from price_param_list[] to price_list[]
                appended = True # change appended boolean to true
                break       # break because there are multiple row matching the if condition
        if not appended:    # case appended boolean = false
            logging.error("Error with original SPAN parameters: this instrument type from record 8 does not"
                " have an equivalent record P: " + str(price['comm']) + str(price['instype']))
            price.update({
            'dspdl':"NA",
            'cvf':"NA"
            })

    # add extra details in instrument_list[] from price_param_list[]
    # now instrument_list is [commodity, type, maturity, settlement price decimal locator, contract value factor]
    # eg ['FBU','OOP',201809,2,100]
    for instrument in instrument_list:
        appended = False
        for price_param in price_param_list:
            if instrument['comm'] == price_param['comm'] and instrument['instype'] == price_param['instype']:
                instrument.update({
                    'dspdl':price_param['dspdl'],
                    'cvf':price_param['cvf']
                    })
                appended = True
                break
        if not appended:
            logging.error("Error with original SPAN parameters: this instrument type from record B does not"
                " have an equivalent record P: " + str(instrument['comm']) + str(instrument['instype']))
            instrument.update({
            'dspdl':"NA",
            'cvf':"NA"
            })

    # # check new list
    # print("revised price list")
    # for l in price_list: print (l) 
    # print ("revised instrument list")
    # for l in instrument_list: print (l) 

    return (price_list, intermonth_list, intermonth_param_list, intercomm_list,
        instrument_list, option_list, deltascale_list,
        price_param_list, currency_list)

#3. read 3 constant files: transfer data from file to list
def read_rcparams (rc_scan_csv,rc_intermonth_csv,rc_intercomm_csv):
    ### 3.1. create bunch of lists to store data
    rc_scan_list = []
    rc_intermonth_list = []
    rc_intercomm_list = []

    ### 3.2. read rc scan. Parse data to rc scan list
    # commodity, maturity, stretch percentage 
    # eg ['MKP',201809,0.02]
    with open (rc_scan_csv, "r") as f:
        rc_scan_reader = csv.reader(f)  # open csv file, read, then store data of each row in a list and each cell as value in that list. If using readlines, whole row data will be one value in a list
        for line in rc_scan_reader:    # append data to rc scan list from rc scan reader
            try:
                rc_scan_list.append({
                    'comm':str(line[0]).strip(),
                    'maturity':(int(line[1]) or 0),
                    'rate':(float(line[2]) or 0)
                    })
            except ValueError:
                logging.error("Format of row = (" 
                    + str('%-2s ' * len(line))[:-1] % tuple(line) 
                    + ") in cons_rc_scan.csv is not as expected and has been ignored. "
                    "It should be commodity, yyyymm, stretch % as decimal, e.g. WMP 201812 0.24")
    
    ### 3.3. read rc intermonth. Parse data to rc intermonth list
    # commodity, tier a, tier b, spread%
    # eg ['WMP',1,2,0.3]
    with open (rc_intermonth_csv,"r") as f:
        rc_intermonth_reader = csv.reader(f)
        for line in rc_intermonth_reader:
            try:
                rc_intermonth_list.append({
                    'comm':str(line[0]).strip(),        
                    'tiera':(int(line[1]) or 0),
                    'tierb':(int(line[2]) or 0),
                    'rate':(float(line[3]) or 0)
                    })
            except ValueError:
                logging.error("Format of row = (" 
                    + str('%-2s ' * len(line))[:-1] % tuple(line) 
                    + ") in cons_rc_intermonth.csv is not as expected and has been ignored. "
                    "It should be commodity, tier a number, tier b number, intermonth % as "
                    "decimal e.g. WMP 1 2 0.02")

    ### 3.4. read rc intercomm. Parse data to rc intercomm list
    # commodity a, delta a, commodity b, delta b, spread% 
    # eg ['WMP',20,'SMP',29,0.4]
    with open (rc_intercomm_csv, "r") as f:
        rc_intercomm_reader = csv.reader(f)
        for line in rc_intercomm_reader:
            try:
                rc_intercomm_list.append({
                    'comma':str(line[0]).strip(),
                    'deltaa':(int(line[1]) or 0),
                    'commb':str(line[2]).strip(),
                    'deltab':(int(line[3]) or 0),
                    'rate':(float(line[4]) or 0)
                    })
            except ValueError:
                logging.error("Format of row = (" 
                    + str('%-2s ' * len(line))[:-1] % tuple(line) 
                    + ") in cons_rc_intercomm is not as expected and has been ignored. "
                    "It should be commodity A, delta A as an integer, commodity B, delta B as "
                    "an integer, intercomm % as decimal e.g. WMP 20 SMP 29 0.3")
    
    ### 3.5. Add blank entries into three rc lists above so no KeyError later (DOUBLE CHECK THIS)
    rc_scan_list.append({'comm':"",'maturity':"",'rate':""})
    rc_intermonth_list.append({'comm':"",'tiera':"",'tierb':"",'rate':""})
    rc_intercomm_list.append({'comma':"",'deltaa':"",'commb':"",'deltab':"",'rate':""})
    
    ### check new list
    # print ("rc scan")
    # for l in rc_scan_list: print (l)
    # print ("rc intermonth")
    # for l in rc_intermonth_list: print (l)
    # print ("rc intercomm")
    # for l in rc_intercomm_list: print (l)

    return rc_scan_list, rc_intermonth_list, rc_intercomm_list
    
#4. calculate new scan range, new intermonth, new intercomm, based on 3 rc cons files. Then re write intermonth list and intercomm list 
"""
anything misspecified or missing is ignored, default for scan stretch is 
0.25, intermonth and intercomm default to what is in original margin pa2
"""
### 4.1. calcuate new scan range
def calc_newscan(price_list, instrument_list,rc_scan_list):
    ###4.1.1. add new column to price list: rc scan rate
    for price in price_list:
        appended = False
        for rc_scan in rc_scan_list:
            if price['comm'] == rc_scan['comm'] and price['maturity'] == rc_scan['maturity']:
                price['rc_scan_rate'] = rc_scan['rate']
                appended = True
                logging.info("Stress scan rate of " + str(price['rc_scan_rate']) + " specified for "
                    + str(price['comm']) + str(price['maturity']))
                break
        if not appended:
            price['rc_scan_rate'] = 0.25 # if instrument is not specified in rc params, given stretch of 25%
    
    # print("new price list")
    # for l in price_list: print (l) 

    # 4.1.2. add new column to instrument list: price, rc scan range 
    # instrument_list is now [commodity,type,maturity,settlement price decimal locator, contract value factor, price, rc scan range]
    for instrument in instrument_list:
        for price in price_list:
            # for futures: append condition on commodity, type, maturity
            if instrument['instype'] == "FUT":
                if instrument['comm'] == price['comm'] and instrument['instype'] == price['instype'] and instrument['maturity'] == price['maturity']:
                    try:
                        instrument['dspconv'] = (price['dsp']/10**price['dspdl'])*instrument['cvf'] # dsp converted = dsp /(10^decimal locator) * contract size
                        instrument['rc_scan_range'] = (price['dsp']/10**price['dspdl'])*instrument['cvf']*price['rc_scan_rate'] # rc scan range = dsp /(10^decimal locator) * contract size * rc scan rate
                        break
                    except (ValueError,KeyError,TypeError):
                        pass
            # for options on futures: append condition on commodity, maturity, type = future instead of matching with price list, no maturity
            elif instrument['instype'] == "OOF":
                if instrument['comm'] == price['comm'] and price['instype'] == "FUT" and instrument['maturity'] == price['maturity']:
                    try:
                        instrument['dspconv'] = (price['dsp']/10**price['dspdl'])*instrument['cvf']
                        instrument['rc_scan_range'] = (price['dsp']/10**price['dspdl'])*instrument['cvf']*price['rc_scan_rate']
                        break
                    except (ValueError,KeyError,TypeError):
                        pass
            # for options on physical: append condition on commodity, type = physical instead of matching with price list, no maturity
            elif instrument['instype'] == "OOP":
                if instrument['comm'] == price['comm'] and price['instype'] == "PHY":
                    try:
                        instrument['dspconv'] = (price['dsp']/10**price['dspdl'])*instrument['cvf']
                        instrument['rc_scan_range'] = (price['dsp']/10**price['dspdl'])*instrument['cvf']*price['rc_scan_rate']
                        break
                    except (ValueError,KeyError,TypeError):
                        pass
            else:
                logging.error("Error with original SPAN parameters: this instrument type from record B does not have an underlying price in record 8"
                    " in record 82: "+str(instrument['comm'])+str(instrument['instype'])+str(instrument['maturity']))
    
    # print("new instrument list")
    # for l in instrument_list: print (l) 

    return price_list, instrument_list

### 4.2. calculate new intermonth
def calc_newintermonth(instrument_list,intermonth_param_list,intermonth_list,rc_intermonth_list):
    tier_list = []  # create empty tier list
    
    # 4.2.1. tier list now become [commodity, month tier]
    # e.g ['WMP', 1]
    for intermonth_param in intermonth_param_list:
        if intermonth_param['tier1'] != 0: 
            tier_list.append({
            'comm':intermonth_param['comm'],
            'tier':intermonth_param['tier1']
            })
        if intermonth_param['tier2'] != 0: 
            tier_list.append({
            'comm':intermonth_param['comm'],
            'tier':intermonth_param['tier2']
            })
        if intermonth_param['tier3'] != 0: 
            tier_list.append({
            'comm':intermonth_param['comm'],
            'tier':intermonth_param['tier3']
            })
        if intermonth_param['tier4'] != 0: 
            tier_list.append({
            'comm':intermonth_param['comm'],
            'tier':intermonth_param['tier4']
            })
    
    # 4.2.2. loop through instrument list, intermonth para; add new column to instrument list: tier = find which tier the instrument belongs to
    # instrument_list is now [commodity,type,maturity,settlement price decimal locator, contract value factor, price, rc scan range, month tier] 
    # eg ['SMP','OOF','201805', 2, 1, price, 465.59999, 1]
    for instrument in instrument_list:
        for intermonth_param in intermonth_param_list:
            if instrument['comm'] == intermonth_param['comm']:
                if intermonth_param['tier1start'] <= instrument['maturity'] <= intermonth_param['tier1end']:
                    # if the instrument's maturity is within tier 1 start date & end date then its in tier 1
                    instrument['tier'] = intermonth_param['tier1']
                    break
                elif intermonth_param['tier2start'] <= instrument['maturity'] <= intermonth_param['tier2end']:
                    # if the instrument's maturity is within tier 2 start date & end date then its in tier 2
                    instrument['tier'] = intermonth_param['tier2']
                    break
                elif intermonth_param['tier3start'] <= instrument['maturity'] <= intermonth_param['tier3end']:
                    # if the instrument's maturity is within tier 3 start date & end date then its in tier 3
                    instrument['tier'] = intermonth_param['tier3']
                    break
                elif intermonth_param['tier4start'] <= instrument['maturity'] <= intermonth_param['tier4end']:
                    # if the instrument's maturity is within tier 4 start date & end date then its in tier 4
                    instrument['tier'] = intermonth_param['tier4']
                    break   
                # on expiry day, expiring contracts will not be included in intermonth DOUBLE CHECK SCRIPT ON EXPIRATION DAY
                else:
                    logging.info(str(instrument['comm']) + str(instrument['maturity']) + 
                        " was not considered in creating or applying intermonth spreads. This is expected on expiry day.")
                    instrument['tier'] = "NA"
    
    # 4.2.3. calculate average dsp and average price scan range per tier. Append it to tier list
    # tier_list is now [commodity, month tier, DSP sum, scan range sum, number of instruments per tier]
    for tier in tier_list:
        pricesum = 0
        scansum = 0
        denominator = 0
        for instrument in instrument_list:           
            if tier['comm'] == instrument['comm'] and tier['tier'] == instrument['tier'] and instrument['instype'] != "OOF":    # excluding option instrument type
                try:
                    pricesum = pricesum + instrument['dspconv']
                    scansum = scansum + instrument['rc_scan_range']
                    denominator = denominator + 1
                except KeyError:
                    pass
        tier.update({
        'pricesum':pricesum,
        'scansum':scansum,
        'denominator':denominator
        })

    # 4.2.4. Loop for every row in rc intermonth list, then for every row tier list. Calculate and update rc intermonth list: append new column: rc tier price = average DSP tier A + average DSP tier B
    for rc_intermonth in rc_intermonth_list:
        tierprice = 0
        for tier in tier_list:
            if tier['denominator'] != 0:
                if rc_intermonth['comm'] == tier['comm'] and rc_intermonth['tiera'] == tier['tier']: # average DSP tier A
                    tierprice += tier['pricesum']/tier['denominator']
                if rc_intermonth['comm'] == tier['comm'] and rc_intermonth['tierb'] == tier['tier']: # average DSP tier B
                    tierprice += tier['pricesum']/tier['denominator']
        rc_intermonth['tierprice'] = tierprice
    
    # print ("tier price per intermonth tier")
    # for l in rc_intermonth_list: print (l) 

    # 4.2.5. loop for every row in "intermonth list", then "RC intermonth list": append new column: rc intermonth spread = rate (from cons file) * avg tier A price + avg tier B price (calculated above)
    for intermonth in intermonth_list: # if inter month percentages not specified in rc inter month file, "NA" added instead of stretched intermonth
        appended = False
        for rc_intermonth in rc_intermonth_list:
            try:
                if intermonth['comm'] == rc_intermonth['comm'] and intermonth['tiera'] == rc_intermonth['tiera'] and intermonth['tierb'] == rc_intermonth['tierb']:
                    intermonth['rc_intermonth_spread'] = rc_intermonth['rate']*rc_intermonth['tierprice']
                    appended = True
                    break
            except KeyError:
                pass
        if not appended:
            intermonth['rc_intermonth_spread'] = "NA"
    
    # print ("Intermonth list with rc intermonth spread")
    # for l in intermonth_list: print (l) 

    return instrument_list, rc_intermonth_list, intermonth_list

### 4.3. calculate new intercom
def calc_newintercomm (rc_intercomm_list,intercomm_list):  # multiply intercomm rate in intercomm cons file by 100. If not defined, take exisint intercomm value

    # intercomm_list is now [commodity a, delta a, commodity b, delta b, spread, rc delta a, rc delta b, rc intercomm spread] 
    # eg ['WMP',20,'SMP',29,30,20,29,40]. If there is no equivalent combo in rc intercomm csv as in original pa2 file, insert "N/A"
    for intercomm in intercomm_list: 
        appended = False
        for rc_intercomm in rc_intercomm_list:
            if intercomm['comma']== rc_intercomm['comma'] and intercomm['commb'] == rc_intercomm['commb']:
                intercomm.update({
                'rc_intercomm_deltaa':rc_intercomm['deltaa'],
                'rc_intercomm_deltab':rc_intercomm['deltab'],
                'rc_intercomm_rate':int(rc_intercomm['rate']*100)
                })
                appended = True
                break
        if not appended:
            intercomm.update({
            'rc_intercomm_deltaa':"NA",
            'rc_intercomm_deltab':"NA",
            'rc_intercomm_rate':"NA"
            })

    # print ("intercomm with RC data")
    # for l in intercomm_list: print (l)

    return intercomm_list

### 4.4. write new intermonth and intercomm list
def write_newinters(intermonth_list,intercomm_list,pa2_list):
    # create new ampty list
    new_intermonth_list = []
    new_intercomm_list = []

    ### 4.4.1. update new intermonth list
    for pa2 in pa2_list:        # loop through pa2 list
        if pa2.startswith("C"):     # record type C
            appendedmonth = False
            for intermonth in intermonth_list:  # loop through intermonth list
                if str(pa2[2:8]).strip() == intermonth['comm'] and int(pa2[23:25].strip() or 0) == intermonth['tiera'] and int(pa2[30:32].strip() or 0) == intermonth['tierb']:     # if matches commodity, tier A & tier B
                    monthstring1 = "Intermonth " + str(intermonth['comm']) + " " + str(intermonth['tiera']) + "v" + str(intermonth['tierb']) + " was " + str(int(pa2[14:21]))       # update value for monthstring1
                    monthstring2 = ""   # empty string for monthstring2
                    if intermonth['rc_intermonth_spread'] == "NA":      # case new rc intermonth spread is N/A
                        new_intermonth_list.append(pa2) # add current pa2 row to new intermonth list
                        appendedmonth = True        # not sure what this boolean is for
                        monthstring2 = ", no change"    # update monthstring2
                        logging.info(monthstring1+monthstring2)
                        break
                    elif intermonth['rc_intermonth_spread'] != "NA":    # case new rc intermonth spread is NOT N/A
                        new_intermonth_list.append(pa2[:14] + str(int(intermonth['rc_intermonth_spread'])).rjust(7,'0') + pa2[21:])     # add current pa2 row to new intermonth list up to character 15th + column rc intermonth spread, add current pa2 row from character 21st
                        # fill with 0 until string has 7 characters
                        appendedmonth = True
                        monthstring2 = ", now " + str(int(intermonth['rc_intermonth_spread']))  # update value for monthstring2
                        logging.info(monthstring1+monthstring2)
                        break
            if not appendedmonth:
            # should have already been taken out by NA condition above, but left here anyway
                new_intermonth_list.append(pa2)   
        
        ### 4.4.2 update new intercomm list. Same methodology as new intermonth
        if pa2.startswith("6"):     # record type 6
            appendedcomm = False
            for intercomm in intercomm_list:
                if str(pa2[20:26]).strip() == intercomm['comma'] and str(pa2[38:44]).strip() == intercomm['commb']:
                    commstring1 = ("Intercomm (" 
                        + str(int(float(pa2[26:33])/10000)) + " " 
                        + str(intercomm['comma']) + " v " 
                        + str(int(float(pa2[44:51])/10000)) + " " 
                        + str(intercomm['commb']) + " = " 
                        + str(int(pa2[9:16])/10000) + ")")
                    commstring2 = ""
                    if intercomm['rc_intercomm_rate'] == "NA":
                        new_intercomm_list.append(pa2)
                        appendedcomm = True
                        commstring2 = ", no change"
                        logging.info(commstring1+commstring2)
                        break
                    elif intercomm['rc_intercomm_rate'] != "NA":
                        new_intercomm_list.append(
                            pa2[:9] 
                            + str(intercomm['rc_intercomm_rate']).rjust(3,'0') 
                            + "0000" 
                            + pa2[16:26] 
                            + str(int(intercomm['rc_intercomm_deltaa'])).rjust(3,'0') 
                            + "0000" 
                            + pa2[33:44] 
                            + str(int(intercomm['rc_intercomm_deltab'])).rjust(3,'0')
                            + "0000" 
                            + pa2[51:])
                        appendedcomm = True
                        commstring2 = (", now (" 
                            + str(int(intercomm['rc_intercomm_deltaa'])) + " " 
                            + str(intercomm['comma']) + " v " 
                            + str(int(intercomm['rc_intercomm_deltab'])) + " " 
                            + str(intercomm['commb']) + " = " 
                            + str(intercomm['rc_intercomm_rate']) + ")")
                        logging.info(commstring1+commstring2)
                        break
            if not appendedcomm:
                # should have already been taken out by NA condition above, but left here anyway
                new_intercomm_list.append(pa2)

    # print ("RC intermonth")
    # for l in new_intermonth_list: print (l)
    # print ("RC intercomm")
    # for l in new_intercomm_list: print (l)

    return new_intermonth_list, new_intercomm_list

# 5. write new pa2 for RC calculation, using current pa2 list (from original pa2 file), new intermonth list + new intercomm list (above), new_pa2 (defined in find current files step)
def write_new_pa2(pa2_list,new_intermonth_list,new_intercomm_list,new_pa2):
    with open(new_pa2, "w") as f:  # open new pa2 file in write mode
        for pa2 in pa2_list:    # for every row in pa2 list
            if not pa2.startswith("C") and not pa2.startswith("6"): # if not record type C and 6
                f.write(pa2)    # write pa2 row in new pa2 file
        # then write new intermonth and new intercomm to the bottom of the file
        f.writelines(new_intermonth_list)   
        f.writelines(new_intercomm_list)

#6. write what if xml file
def write_whatif(instrument_list,whatif_xml):  
    # 6.1. define function write update scan: join together commodity, instrument type, maturity, newscan
    def write_updatescan(commodity,instype,maturity,newscan):
        return ''.join(("<updateRec>\n<ec>NZX</ec>\n<cc>",
            commodity,
            "</cc>\n<exch>NZX</exch>\n<pfCode>",
            commodity,
            "</pfCode>\n<pfType>",
            instype,
            "</pfType>\n<sPe>",
            str(maturity),
            "</sPe>\n<ePe>",
            str(maturity),
            "</ePe>\n<updType>UPD_PRICE_RG</updType>\n<updMethod>UPD_SET</updMethod>\n<value>",
            "{:.2f}".format(newscan),   # new scan range with convert to 2 decimal places
            "</value>\n</updateRec>",
            ))

    # 6.2. append update scan to xml list
    xml_list = []  # define new empty xml list

    for instrument in instrument_list:  # loop through instrument list
        try:    # append to xml list all string info, defined in the write update scan function above
            xml_list.append(write_updatescan(instrument['comm'],instrument['instype'],instrument['maturity'],instrument['rc_scan_range']))
        except KeyError:
        # if there is no scan range available for whatever reason, leave out of whatif
            logging.error("This instrument has not been assigned a new scan range: " 
                + str(instrument['comm'])+str(instrument['instype'])+str(instrument['maturity']))
    
    # 6.3. write xml list to xml file
    with open(whatif_xml, "w") as f:
        f.write("<scenarioFile>\n")   # first add scenarioFile + new line
        for line in xml_list:
            f.write(line)
            f.write("\n")
        f.write("\n</scenarioFile>")  # last add new line + scenarioFile

#7. Read position and break it down into other lists:
### 7.1. read position and store it into a list
def read_position(position_txt):
    position_list = []
    with open(position_txt, "r") as f:  # open as read mode
        position_list = f.readlines()   # readlines and store them in position list
    return position_list  

### 7.2. break down position list to several other lists
def parse_position(position_list):
    # 7.2.1. create new empty lists    
    record5_list = []   # everything in record 5, including position
    bpins_list = []     # every intruments per bp, excluding position
    option_position_list = []   # every option position per bp per ac. This is usefule for delta adjustment net exposure later on
    bpacc_list = []     # every account name per bp, add sum account for each bp
    sum_bpacc_list = []
    omni_acc_list = []  # list of omnibus/client account

    # 7.2.2. if omnibus/client, add accountname to omni_acc_list
    for position in position_list: 
        if position.startswith("2"): 
            accountname = position.strip()[1:11]
            accounttype = position.strip()[24:29]
            if accounttype == 'OCUST':
                omni_acc_list.append(accountname)  

    # 7.2.3. loop through position list and fill in data for those lists above
    for position in position_list:
        if position.startswith("5"):
            # Check if accountname is in the omni_acc_list list. If it is, assign True/False to Boolean variable isOmniAccount
            accountname = position.strip()[1:11]
            isOmniAccount = False
            if accountname in omni_acc_list:
                isOmniAccount = True
                logging.info(accountname + " is OCUST account.") 

            # list of BP+instr,net position [BP+instr chunk,net position]
            record5_list.append({
            'bpins':str(position[1:4])+str(position[24:92]),
            'position':int(position[92:100].strip() or 0),
            'isOmni':bool(isOmniAccount)    # add isOmniAccount boolean variable to record5 list
            })  # record 5 break down to instrument and position per instrument

            # list of BP+instr [BP+instr chunk]
            bpins_list.append({'bpins':str(position[1:4])+str(position[24:92])})

            # list of BP+acc [BP+acc chunk]
            bpacc_list.append({'bpacc':str(position[1:4])+str(position[4:24]).strip()}) # bp+account name
            bpacc_list.append({'bpacc':str(position[1:4])+"Sum"})   # sum account name to bp

            # list of BP,account,commodity,option on future/physical,call/put,maturity,strike,net position
            if str(position[45:48]) == "OOF" or str(position[45:48]) == "OOP":      # case position is option on future/option on physical
                option_position_list.append({
                'bp':str(position[1:4]),
                'acc':str(position[4:24]).strip(),
                'comm':str(position[35:45]).strip(),
                'instype':str(position[45:48]),
                'callput':str(position[48:49]),
                'maturity':int(position[49:57].strip() or 0),
                'strikeconv':float(position[78:92].strip() or 0)/10000000,  # strike price converted
                'position':int(position[92:100].strip() or 0)   # +/- position
                })
    
    # # check each list
    # print ("record 5")
    # for l in record5_list: print (l)
    # print ("bp instrument list")
    # for l in bpins_list: print (l)
    # print ("bp account list")
    # for l in bpacc_list: print (l)
    # print ("option position list")
    # for l in option_position_list: print (l)
    
    # 7.2.4. remove duplicates in bp instrument list & bp account list and insert to sum bp instrument and sum bp account lists. DOUBLE CHECK HOW THIS WORKS
    # this is preparation step for creating sum accounts
    sum_bpins_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in bpins_list)]
    sum_bpacc_list_nocurr = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in bpacc_list)]  # sum bp account, no currency

    # print ("sum bp instrument list")
    # for l in sum_bpins_list: print (l)
    # print ("sum bp account list without currency")
    # for l in sum_bpacc_list_nocurr: print (l)

    # 7.2.5. for each account in summ account list, add currency NZD & USD. I.e. duplicate numbers of rows in the list. 
    for bpacc in sum_bpacc_list_nocurr:
        bpacc['curr'] = "USD"
        sum_bpacc_list.append(copy.deepcopy(bpacc))
        bpacc['curr'] = "NZD"
        sum_bpacc_list.append(copy.deepcopy(bpacc))    

    # print ("sum bp account list with currency")
    # for l in sum_bpacc_list: print (l) 

    # 7.2.6. create sum position per bp
    for bpins in sum_bpins_list:
        # first, add column position in sum position list, & set to 0
        bpins['position'] = 0 

        # loop through record 5 and sum for the same BP and instrument combo. Exclude omnibus client accounts from Sum rule. 
        for record5 in record5_list:            
            if bpins['bpins'] == record5['bpins'] and not record5['isOmni']: 
            ### OLD CODE ### if bpins['bpins'] == record5['bpins']:  # if match bp and instrument
                bpins['position'] = bpins['position'] + record5['position'] # add record 5 position to sum pb position

        # add the whole summed record into the options list too
        if str(bpins['bpins'][24:27]) == "OOF" or str(bpins['bpins'][24:27]) == "OOP":      # if instrument is option
            option_position_list.append({
            'bp':str(bpins['bpins'][0:3]),  # bp name
            'acc':"Sum",                    # account name = Sum
            'comm':str(bpins['bpins'][14:24]).strip(),  # commodity
            'instype':str(bpins['bpins'][24:27]),       # instrument type OOF or OOP
            'callput':str(bpins['bpins'][27:28]),       # call / put
            'maturity':int(bpins['bpins'][48:56].strip() or 0), # maturity
            'strikeconv':float(bpins['bpins'][57:71].strip() or 0)/10000000,    # strike price converted
            'position':bpins['position']    # position per instrument
            })

    # print ("sum bp instrument with position")
    # for l in sum_bpins_list: print (l)
    # print ("option position list, sum account")
    # for l in option_position_list: print (l)

    return sum_bpins_list, option_position_list, sum_bpacc_list

#8. write new position file with additional information for sum account
# copy every row in current position file to new position file, except for some conditions
def write_newposition(position_list,sum_bpins_list,sum_position_txt):
    with open(sum_position_txt, "w") as f:  # open sum position file as f in write mode
        for position in position_list:  # loop through position list, (from original position file)
            f.write(position)   # write every row in position list to sum position file
            if position.startswith("2"):    # for record type 2 = list of accounts
                # accounttype: force OCUST to MHOUS
                accounttype = position.strip()[24:29] 
                if accounttype != 'MHOUS':
                    # REPLACE WITH MHOUS FOR RC (otherwise there will be a duplicate in for bp in PC-SPAN)
                    accounttype = 'MHOUS' 
                f.write(position.strip()[:4]+"Sum".ljust(20," ")+accounttype+position.strip()[29:]+"\n")    # add account named "Sum" and force its type to Net
                
        for bpins in sum_bpins_list:
            f.write("5"+bpins['bpins'][:3]+"Sum".ljust(20," ")+bpins['bpins'][3:]+("-" if bpins['position'] < 0 else "0")+str(abs(bpins['position'])).rjust(7,"0")+"\n")    # add position for sum account

#8.b Write new function to force ALL accounts in position txt file to be M instead of O. So that SPAN calculated stress loss on Net Position basis.
def write_newposition_rc(position_list,sum_bpins_list,sum_position_file):
    with open(sum_position_file, "w") as f:
        for position in position_list:
            if position.startswith("2"):
                # accounttype force OCUST to MHOUS
                accounttype = position.strip()[24:29] 
                if accounttype != 'MHOUS':
                    # REPLACE WITH MHOUS FOR RC (otherwise there will be a duplicate in for bp in PC-SPAN)
                    accounttype = 'MHOUS' 
                # Use string from orig pos file to write BPID and Account number as well as Sum Account lines.
                f.write(position.strip()[:24]+accounttype+position.strip()[29:]+"\n")   # update account type (from string 24-29) to MHOUS
                f.write(position.strip()[:4]+"Sum".ljust(20," ")+accounttype+position.strip()[29:]+"\n")    # add account named "Sum"
            else:
                f.write(position)
        for bpins in sum_bpins_list:
            f.write("5"+bpins['bpins'][:3]+"Sum".ljust(20," ")+bpins['bpins'][3:]+("-" if bpins['position'] < 0 else "0")+str(abs(bpins['position'])).rjust(7,"0")+"\n")

#9. write instruction to tell SPAN calculating margin, then save report.  
### 9.1. write instruction in txt file, for margin calculation purpose. Remove identifier variable as this script only use for margin calculation
def margin_SPAN_instruction(pa2_pa2,position_txt,span_spn,spanit_txt):
    with open(spanit_txt + "margin.txt", "w") as f:  # open SPAN instruction txt file in write mode
        f.write ("Load " + pa2_pa2 + "\n")   # load original pa2
        f.write ("Load " + position_txt + "\n")  # load position file. Since we calculate for Sum account as well, we currently insert Sum position txt file here
        f.write ("Calc" + "\n") # calculate
        f.write ("Save " + span_spn + "margin.spn" + "\n") # save as spn file 
    return spanit_txt

### 9.2. write instruction in txt file, for risk capital calculation purpose. 
def rc_SPAN_instruction(new_pa2,whatif_xml,position_txt,span_spn,spanit_txt):
    with open(spanit_txt + "rc.txt", "w") as f:
        f.write("Load " + new_pa2 + "\n")
        f.write("Load " + position_txt + "\n") 
        f.write("SelectPointInTime" + "\n")
        f.write("ApplyWhatIf " + whatif_xml + "\n")
        f.write("CalcRiskArray" + "\n")
        f.write("Calc" + "\n")
        f.write("Save " + span_spn + "rc.spn\n")    
    return spanit_txt

### 9.A run SPAN, given instruction text file
def call_SPAN(spanit_txt, identifier):
    os.chdir (r"C:\span4\bin")  # os.chdir = change current working directory path
    subprocess.call(["spanitrm.exe", spanit_txt + identifier + ".txt"])

### 9.B generate SPAN report
def call_SPAN_report(span_spn,pbreq_csv,identifier):    # open spn file and generate pbreq.csv file. Add identifier to distinguish margin/rc pbreq
# the input spn file must have already have pa2 and position files combined
# mshta must be given an absolute pathname, not a relative one
# this process does not work with filenames containing spaces " "
    os.chdir(r"C:\span4\Reports")
    subprocess.call(["mshta.exe", r"C:\span4\rptmodule\spanReport.hta", span_spn + identifier + ".spn"])

    # Convert spanReport.hta output (Link AP\C:\span4\Reports\PB Req Delim.txt) to (parent directory + \YYYYMMDD-hhmmss_pbreq_identifier.csv)
    pbreq_txt = r"C:\Span4\Reports\PB Req Delim.txt"
    pbreq_full_csv = pbreq_csv + identifier + ".csv"
    pbreq_reader = csv.reader( open(pbreq_txt,"r"), delimiter = ',')
    with open(pbreq_full_csv , "w") as output:
        output_csv = csv.writer(output)
        output_csv.writerows(pbreq_reader)

#10. calculate delta adjusted net exposure for options
def delta_adjust(option_list, deltascale_list, price_param_list, option_position_list, sum_bpacc_list, instrument_list):
    for option in option_list:  # loop through option list, originaly from pa2 file
        appendeddelta = False
        for deltascale in deltascale_list:  # loop through delta scaling list
            if option['comm'] == deltascale['comm'] and option['instype'] == deltascale['instype'] and option['maturity'] == deltascale['maturity']:    # find matching commodity, type = OOF or OOP, matching maturity
                option['deltasf'] = deltascale['deltasf']   # add another column 'deltasf' to option list
                appendeddelta = True
                break
        if not appendeddelta:   # if delta is not appended
            option['deltasf'] = "N/A"

        appendedparams = False
        for price_param in price_param_list:    # loop through price parameter list
            if option['comm'] == price_param['comm'] and option['instype'] == price_param['instype']:   # find matching commodity, instrument type = OOP or OOF
                option["dspdl"] = price_param["dspdl"]
                option["strikedl"] = price_param["strikedl"]
                option["strikeconv"] = float(option["strike"])/10**price_param["strikedl"]   # converted strike price 
                option["cvf"] = price_param["cvf"]
                option["curr"] = price_param["curr"]
                appendedparams = True
        if not appendedparams:
            option["dspdl"] = "N/A"
            option["strikedl"] = "N/A"
            option["strikeconv"] = "N/A"
            option["cvf"] = "N/A"
            option["curr"] = "N/A"

        appendeddsp = False
        for instrument in instrument_list:  # loop through instrument list
            if option['comm'] == instrument['comm'] and option['instype'] == instrument['instype'] and option['maturity'] == instrument['maturity']:    # find matchin commodity, option type, maturity
                option['underlyingdspconv'] = instrument['dspconv']     # update underlying dsp converted to 
                appendeddsp = True
                break
        if not appendeddsp:
            option['underlyingdspconv'] = "NA"

    # print ("option list with delta scaling factor, dsp decimal locator, strike decimal locator, strike converted, contract size, currency, underlying dsp converted")
    # for l in option_list: print (l)

    for option_position in option_position_list:    # loop through option position list
        appendedposi = False
        for option in option_list:  # loop through option list
            if (option_position['comm'] == option['comm'] and
                option_position['maturity'] == option['maturity'] and
                option_position['instype'] == option['instype'] and
                option_position['strikeconv'] == option['strikeconv'] and
                option_position['callput'] == option['callput']):
            # find matching commodity, maturity, option type, strike price, call or put
                # add columns to option position list
                option_position["delta"] = float(option["delta"])/option["deltasf"]
                option_position["underlyingdspconv"] = option["underlyingdspconv"]
                option_position["deltanetadj"] = option_position["position"]* (float(option["delta"])/option['deltasf'])*option['underlyingdspconv']    # delta net adjusted position = net position * delta * underlying dsp
                option_position["curr"] = option["curr"]
                appendedposi = True
        if not appendedposi:
            option_position.update({
                'delta':"NA",
                'underlyingdspconv':"NA",
                'deltanetadj':"NA",
                'curr':"NA"
                })
    
    # print ("option position with delta net adjusted position")
    # for l in option_position_list: print (l)

    for bpacc in sum_bpacc_list:    # loop sum bp account list
        deltalovsov = float(0)     # delta adjusted long option value minus short option value
        for option_position in option_position_list:    # loop through option postion list finished above
            if bpacc['bpacc'].startswith(option_position['bp']) and bpacc['bpacc'].endswith(option_position['acc']) and bpacc['curr'] == option_position['curr']:   # find matching bp, account, currency
            # Check if 'bpacc', in sum_bpacc_list, starts with value of option_position_list 'bp'  
               deltalovsov = deltalovsov + option_position['deltanetadj']
        bpacc['deltalovsov'] = deltalovsov  # add column delta lov - sov to sum bpacc list
    
    # print ("sum bp account list with delta adj long opt - short opt")
    # for l in sum_bpacc_list: print (l)

    return option_position_list, sum_bpacc_list

#11. read house csv file and store in a list
def read_house(house_csv):
    house_list = [] # create a default empty house list

    with open(house_csv,"r") as f:
        house_reader = list(csv.reader(f))
    for line in house_reader:
        try:
            house_list.append({
            'bp':str(line[0]).strip(),
            'bpid':str(line[1]).strip(),
            'acc':str(line[2]).strip()
            })
        except ValueError:
            logging.error("Format of row = (" 
                + str('%-2s ' * len(line))[:-1] % tuple(line) 
                + ") in cons_house.csv is not as expected and has been ignored. "
                "It should be SPAN BP, BPID, House margin account ref e.g. ADM, ADMU00000, Margin1")
    # print("house list")
    # for l in house_list: print (l)        
    return house_list

#12. read pbreq margin and pbreq rc files. Combine both to pbreq_list
def read_pbreqs(pbreq_csv):
    # open pbreq with identifier margin
    tempfile = pbreq_csv + "margin.csv"
    with open(tempfile, "r") as f:  # open pbreq_margin.csv file in read mode
        pbreq_margin = [{k: v for k,v in row.items()} for row in csv.DictReader(f)] # store every row in pbreq in pbreq_margin dictionary
        # column heading will be key in the dictionary

    # open pbreq with identifier rc
    tempfile = pbreq_csv + "rc.csv"
    with open(tempfile, "r") as f:  # open pbreq_rc.csv file in read mode
        pbreq_rc = [{k: v for k,v in row.items()} for row in csv.DictReader(f)] # store every row in pbreq in pbreq_rc dictionary

    # take row in dictionaries where: node = curReq; ec = NZX; isM = 1 --> use those values in curreq_list. Where: node = curVal; ec = NZX --> use those values in curVal_list
    # use identifier: margin / rc
    curreq_list = []
    curval_list = []
    for pbreq_margin in pbreq_margin:
        if pbreq_margin: # pbreqs have empty rows, so filter out blanks
            if pbreq_margin['node'] == "curReq" and pbreq_margin['ec'] == "NZX" and str(pbreq_margin['isM']) == "1": # Unsure that isM = 1 is any different than 0?
                curreq_list.append({
                'identifier':"margin",
                'bp':pbreq_margin['firm'],
                'acc':pbreq_margin['acct'],
                'curr':pbreq_margin['currency'],
                'span':max(float(pbreq_margin['spanReq'])-float(pbreq_margin['anov']),0)    # span requirement = span req - net option value
                })
            elif pbreq_margin['node'] == "curVal" and pbreq_margin['ec'] == "NZX":
                curval_list.append({
                'identifier':"margin",
                'bp':pbreq_margin['firm'],
                'acc':pbreq_margin['acct'],
                'curr':pbreq_margin['currency'],
                'lfvsfv':float(pbreq_margin['lfv'])-float(pbreq_margin['sfv'])  #long future value - short future value??? 
                }) # [identifier,bp,acc,currency,lfv-sfv]
    
    # print ("curreq Margin")
    # for l in curreq_list: print (l)
    # print ("curval Margin")
    # for l in curval_list: print (l)
    
    for pbreq_rc in pbreq_rc:
        if pbreq_rc:
            if pbreq_rc['node'] == "curReq" and pbreq_rc['ec'] == "NZX" and str(pbreq_rc['isM']) == "1": # Unsure that isM = 1 is any different than 0?
                curreq_list.append({
                'identifier':"rc",
                'bp':pbreq_rc['firm'],
                'acc':pbreq_rc['acct'],
                'curr':pbreq_rc['currency'],
                'span':max(float(pbreq_rc['spanReq'])-float(pbreq_rc['anov']),0)
                })

            elif pbreq_rc['node'] == "curVal" and pbreq_rc['ec'] == "NZX":
                try:        # DOUBLE CHECK: WHY HAVE TO TRY & EXCEPT??
                    curval_list.append({
                    'identifier':"rc",
                    'bp':pbreq_rc['firm'],
                    'acc':pbreq_rc['acct'],
                    'curr':pbreq_rc['currency'],
                    'lfvsfv':(float(pbreq_rc['lfv']) or 0)-float(pbreq_rc['sfv'])
                    })
                except:
                    pass

    # print ("curreq Margin")
    # for l in curreq_list: print (l)
    # print ("curval Margin")
    # for l in curval_list: print (l)

    # Merge curreq and curval
    pbreq_list = []     # define an empty pbreq list
    for curreq in curreq_list:
        pbreq_list.append(copy.deepcopy(curreq)) # copy entire curreq_list to pbreq_list 

    # for l in pbreq_list: print (l)

    for pbreq in pbreq_list:    # loop pbreq list
        for curval in curval_list:  # loop curval list
            if pbreq['identifier'] == curval['identifier'] and pbreq['bp'] == curval['bp'] and pbreq['acc'] == curval['acc'] and pbreq['curr'] == curval['curr']:   # find matching margin/rc identifier, bp, acc, currency. 
                pbreq['lfvsfv'] = curval['lfvsfv']
                # add lfvsfv value for pbreq list from curval list
    # pbreq_list is now [identifier,bp,acc,currency,max(spanreq-anov,0),lfv-sfv]

    # print ("Pb req: margin and rc combine")
    # for l in pbreq_list: print (l)

    return pbreq_list

#13. retrieve from pbreq list, bp account with sum a/c list, house list, currency list. Generate final rc based on our criteria rule
def parse_rc(pbreq_list,sum_bpacc_list,house_list,currency_list):
    bp_list = []        # create empty list first
    bp_unique_list = []  # create empty list first

    for bpacc in sum_bpacc_list:    # loop through account list
        margin = float(0)
        stressl = float(0)  # stress loss
        lfvsfv = float(0)   # long future value - short future value
        # Append all spanreq-anov from pbreq_list to sum_bpacc_list
        # sum_bpacc_list now [bp+acc,curr,delta long opt value-short opt value,lfv-sfv,rc,margin]
        for pbreq in pbreq_list:    # loop thought pbreq list
            if bpacc['bpacc'].startswith(pbreq['bp']) and bpacc['bpacc'].endswith(pbreq['acc']) and bpacc['curr'] == pbreq['curr']: # find matching BP and account and currency
                if pbreq['identifier'] == "rc": # case identifier = rc
                    stressl = pbreq['span']
                    lfvsfv = pbreq['lfvsfv']
                elif pbreq['identifier'] == "margin":   # case identifier = margin
                    margin = pbreq['span']
                    lfvsfv = pbreq['lfvsfv'] 
        bpacc.update({
        'lfvsfv':lfvsfv,
        'stressl':stressl,
        'margin':margin
        })

        # append to sum_bpacc_list whether the account is house or client or Sum account
        # sum_bpacc_list now [bp+acc,curr,delta long opt value-short opt value,lfv-sfv,rc,margin, house/client/sum]
        appended = False
        for house in house_list:
            if bpacc['bpacc'].startswith(house['bp']) and bpacc['bpacc'].endswith(house['acc']):
                bpacc['acctype'] = "House"
                appended = True
                break
            elif bpacc['bpacc'].endswith("Sum"):
                bpacc['acctype'] = "Sum"
                appended = True
                break
        if not appended:
            bpacc['acctype'] = "Client"
        
        # Insert into bplist just the BPs from sum_bpacc_list
        bp_list.append(bpacc['bpacc'][:3])

    # print ("bp list")
    # for l in bp_list: print (l)

    # get USD:NZD fx rate from currency_list
    for curr in currency_list:
        if curr['curra'] == "USD" and curr['currb'] == "NZD":
            usdnzd = curr['rate']

    # do calculation for delta adjusted net exposure, uncovered stress loss, currency conversion in sum bp acc list
    # sum_bpacc_list now [bp+acc,curr,lfo-sfo,lfv-sfv,rc,margin,house/client, delta net exposure unconverted,rc unconverted, delta net exposure converted, rc converted]
    for bpacc in sum_bpacc_list:    # loop through sum bp acc list
        bpacc['deltanetexps'] = bpacc['lfvsfv']+bpacc['deltalovsov']    # Get delta adjusted net exposure by summing (long future value -short future value) + (long opt value-short opt value)
        bpacc['rc'] = max(bpacc['stressl']-bpacc['margin'],0)    # Get rc by taking uncovered losses minus margin. Use 0 if the difference is negative
        # Convert USD to NZD
        if bpacc['curr'] == "USD":
            bpacc.update({
            'deltanetexpsconv':bpacc['deltanetexps'] * usdnzd, # USD delta net exposure converted to NZD
            'rcconv': bpacc['rc'] * usdnzd, # USD rc converted to NZD
            'marginconv': bpacc['margin'] * usdnzd, # margin converted to nzd
            'stresslconv': bpacc['stressl'] * usdnzd # stress loss converted to nzd
            })
        elif bpacc['curr'] == "NZD":
            bpacc.update({
            'deltanetexpsconv':bpacc['deltanetexps'], # = NZD delta net exposure
            'rcconv': bpacc['rc'], # = NZD rc
            'marginconv': bpacc['margin'],
            'stresslconv': bpacc['stressl']
            })
    
    # print ("sum bp account list")
    # for l in sum_bpacc_list: print (l)    

    # Remove duplicates of BPs
    bp_final_strings = list(set(bp_list))   # convert bp list in a set, to remove duplicate data, then convert it back into list.
    for line in bp_final_strings:
        bp_unique_list.append({'bp':line})   # create a dictionary kind of list where bp_unique_list looks like [{'bp': 'OMF'}, {'bp': 'FCS'}]
    
    # filter, modify, risk capital using logic defined by Risk team: gain 
    for bp in bp_unique_list:   # loop through unique list of bp
        longclient = {'deltanetexpsconv':float(0),'rcconv':float(0)}    # create long client dictionary
        shortclient = {'deltanetexpsconv':float(0),'rcconv':float(0)}   # create short client dictionary
        house = {'deltanetexpsconv':float(0),'rcconv':float(0),'marginconv':float(0)}
        houseexist = False
        
        # grab delta net exposure, rc of long client, rc of short client
        for bpacc in sum_bpacc_list:    # loop through sum bp account list
            if bpacc['bpacc'].startswith(bp['bp']) and not bpacc['bpacc'].endswith("Sum"):  # condition on not sum account
                if bpacc['acctype'] == "House" and bpacc['deltanetexpsconv'] > 0:   # house and positive delta adjusted net exposure. DOUBLE CHECK: positive delta adj net exposure means profit? 
                    house['deltanetexpsconv'] += bpacc['deltanetexpsconv'] # delta adjusted net exposure
                    house['rcconv'] += bpacc['rcconv'] # rc
                    house['marginconv'] += bpacc['marginconv'] #margin
                    houseexist = True
                elif bpacc['acctype'] == "Client" and bpacc['deltanetexpsconv'] > 0:    # client account and positive delta net exposure conversion
                    longclient['deltanetexpsconv'] += bpacc['deltanetexpsconv'] # delta adjusted net exposure
                    longclient['rcconv'] += bpacc['rcconv'] # rc
                elif bpacc['acctype'] == "Client" and bpacc['deltanetexpsconv'] < 0:    # client account and negative delta net exposure conversion
                    shortclient['deltanetexpsconv'] += bpacc['deltanetexpsconv'] # delta adjusted net exposure
                    shortclient['rcconv'] += bpacc['rcconv'] # rc
        
        # applying the rule by Risk team
        if not houseexist:
            # if there is no house delta adjusted net exposure, take max of sum rc of(positive delta adjusted net exposure clients) and sum rc of(negative delta adjusted net exposure clients)
            shortrc = shortclient['rcconv']
            longrc = longclient['rcconv']    
        elif house['deltanetexpsconv'] > 0:
            # house and opposing client(s) may be offset using house margin
            shortrc = -house['marginconv'] + shortclient['rcconv']
            longrc = house['rcconv'] + longclient['rcconv']
        elif house['deltanetexpsconv'] < 0:
            # house and opposing client(s) may be offset using house margin
            shortrc = house['rcconv'] + shortclient['rcconv']
            longrc = -house['marginconv'] + longclient['rcconv']
        elif house['deltanetexpsconv'] == 0:
            # unlikely but possible that there is house rc with dane = 0, but if so count on both sides
            shortrc = shortclient['rcconv'] + house['rcconv']
            longrc = longclient['rcconv'] + house['rcconv']
        else: # shouldn't reach here, but just in case
            longrc = shortrc = house['rcconv'] + longclient['rcconv'] + shortclient['rcconv']
        
        # add column rc converted to bp unique list
        bp['rcconv'] = max(shortrc, longrc)
    
    # print ("bp unique list")
    # for l in bp_unique_list: print (l)
    
    # For final rc figure, use higher of rcconv in bp_unique_list vs Sum(rcconv) in sum_bpacc_list
    for bp in bp_unique_list:   # loop through unique list of bp
        finalrc = float(0)
        sumsums = float(0)
        for bpacc in sum_bpacc_list:    # loop through bp account with sum account list
            if bpacc['bpacc'].endswith("Sum") and bpacc['bpacc'].startswith(bp['bp']):  # condition on account is Sum a/c
                sumsums = sumsums + bpacc['rcconv'] # add all rc converted for Sum account together. Have to loop because Sum account would have different currency too
        finalrc = max(bp['rcconv'],sumsums) # final rc = higher of rc converted in unique list vs rc converted in Sum account. We find out that rc converted in unique list would always be used because Sum account is more diversified, therefore lower rc 
        # add rows for each bp: inserting rc converted for rule, and rc final 
        sum_bpacc_list.append({
        'bpacc':bp['bp']+"Rule",
        'curr':"NZD",
        'acctype':"Rule",        
        'rcconv':bp['rcconv']
        })
        sum_bpacc_list.append({
        'bpacc':bp['bp']+"Final",
        'curr':"NZD",
        'acctype':"Final",        
        'rcconv':finalrc
        })
    
    # Add bpid column to sum_bpacc_list, if not specified in cons_house.csv, default to truncated BP
    for bpacc in sum_bpacc_list:
        appendedbpid = False
        for house in house_list:
            if bpacc['bpacc'][:3] == house['bp']:
                bpacc['bpid'] = house['bpid']
                appendedbpid = True
                break
        if not appendedbpid:
            bpacc['bpid'] = bpacc['bpacc']
            logging.error(bpacc['bpacc'][:3] + " BPID is not in cons_house.csv")
    
    # print ("bp accounts with sum a/c final rc")
    # for l in sum_bpacc_list: print (l)

    return pbreq_list, sum_bpacc_list

#14. write final csv file
def write_rc(sum_bpacc_list,final_csv):
    with open(final_csv, "w") as f:
        f.write("BPID,Account,Currency,Delta adjusted net exposure,Stress Losses,Margin,"
            "Intermediate RC,Delta adjusted net exposure (NZD),Stress Losses (NZD),"
            "Margin (NZD),Intermediate RC (NZD)\n")

        # print ("bp accounts with sum a/c final rc")
        # for l in sum_bpacc_list: print (l)
        
        for bpacc in sum_bpacc_list:
            try:
                f.write(bpacc['bpid']+","
                    +bpacc['bpacc'][3:]+","
                    +str(bpacc['curr'])+","
                    +str(bpacc['deltanetexps'])+","
                    +str(bpacc['stressl'])+","
                    +str(bpacc['margin'])+","
                    +str(bpacc['rc'])+","
                    +str(bpacc['deltanetexpsconv'])+","
                    +str(bpacc['stresslconv'])+","
                    +str(bpacc['marginconv'])+","
                    +str(bpacc['rcconv'])+"\n")
            except KeyError:
                f.write(bpacc['bpid']+","
                    +bpacc['bpacc'][3:]+","
                    +str(bpacc['curr'])
                    +",,,,,,,,"
                    +str(bpacc['rcconv'])+"\n")

############################### MAIN ###############################
def main():
    dates = [startD + timedelta(x) for x in range(0, (endD-startD).days)]   # for each x from 0 to count number days between start date and end date, convert x from integer to date. Then plus that number to start date. Put that into a list

    hhmmss = datetime.now().strftime("%H%M%S")  # define execution time to create time stamp in output files. strftime = string format time = format time string

    for date in dates:  # loop for all date in dates list
        #1. Collect input files (cons, input). Define newly created file and path. 
        (pa2_pa2, position_txt, rc_intercomm_csv,rc_intermonth_csv, rc_scan_csv, house_csv, new_pa2, sum_position_txt,sum_position_rc_txt, whatif_xml, spanit_txt, span_spn, pbreq_csv, final_csv) = find_current_files(date.strftime("%Y%m%d"), hhmmss)
        
        #2. read pa2 file & store data into various lists
        pa2_list = read_pa2(pa2_pa2)    # read from file then transfer to pa2 list
        
        (price_list, intermonth_list, intermonth_param_list, intercomm_list,
                instrument_list, option_list, deltascale_list,
                price_param_list, currency_list) = parse_pa2(pa2_list)  # break down from pa2 big list to several smaller list
        
        #3. read 3 constant files. Read from file to list
        (rc_scan_list, rc_intermonth_list, rc_intercomm_list) = read_rcparams(rc_scan_csv,rc_intermonth_csv,rc_intercomm_csv)

        #4. calculate new stretched scan range, intermonth, intercomm. Then write new intermonth, intercomm list
        price_list, instrument_list = calc_newscan(price_list, instrument_list,rc_scan_list)    # calculate new scan range, update them into price list and instrument list

        instrument_list, rc_intermonth_list, intermonth_list = calc_newintermonth(instrument_list, intermonth_param_list, intermonth_list, rc_intermonth_list)   # calculate rc spread charge per intermonth tier 

        intercomm_list = calc_newintercomm(rc_intercomm_list, intercomm_list)   # calculate rc intercomm and insert in intercomm list
            
        new_intermonth_list, new_intercomm_list = write_newinters(intermonth_list,intercomm_list,pa2_list)  

        #5. write risk capital pa2 file
        # new pa2 file wouldn't have new risk array calculated, has to be recalculated using whatif file
        write_new_pa2(pa2_list,new_intermonth_list,new_intercomm_list,new_pa2)

        #6. write whatif file which has scans adjusted
        write_whatif(instrument_list,whatif_xml)

        #7. read position file & break it down into smaller pieces
        position_list = read_position(position_txt)    # read and store it into list
        
        sum_bpins_list, option_position_list, sum_bpacc_list = parse_position(position_list)    # break down into several other lists

        #8. write position file with sum positions
        write_newposition(position_list,sum_bpins_list,sum_position_txt)
        write_newposition_rc(position_list,sum_bpins_list,sum_position_rc_txt)
        
        #9. calculate and get report for:
        #9.1. margin
        margin_SPAN_instruction(pa2_pa2,sum_position_txt,span_spn,spanit_txt) # write txt instruction for SPAN calculation: margin
        # insert sum position txt here to calculate margin for sum account as well
        call_SPAN(spanit_txt, "margin")
        call_SPAN_report(span_spn, pbreq_csv,"margin")

        #9.2. risk capital
        rc_SPAN_instruction(new_pa2,whatif_xml,sum_position_rc_txt,span_spn,spanit_txt)    # write txt instruction for SPAN calculation: risk capital
        call_SPAN(spanit_txt, "rc")
        call_SPAN_report(span_spn, pbreq_csv,"rc")
        
        #10. calculate delta adjusted net exposure for options
        delta_adjust(option_list, deltascale_list, price_param_list, option_position_list, sum_bpacc_list, instrument_list)

        #11. read cons house file
        house_list = read_house(house_csv)

        #12. read pbreq margin and pbreq risk capital files
        pbreq_list = read_pbreqs(pbreq_csv)

        #13. use criteria rule to generate risk capital for each participant
        pbreq_list, sum_bpacc_list = parse_rc(pbreq_list,sum_bpacc_list,house_list,currency_list)
        
        #14. write final excel file
        write_rc(sum_bpacc_list,final_csv)
        print ("\n complete")

# if this python is run directly, run main(); else do not run main()
# before running anything, Python interpreter will define a few variables such as __name__. And if the script is run directly, variable __name__ will take value __main__
if __name__ == "__main__":
    main()
else:
    print ("not run directly")
    
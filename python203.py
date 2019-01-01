"""
re-create Risk Capital calculation script again for 21% stretch
"""
from __future__ import division     # import division so that '/' is mapped to __truediv__() and return more decimals figure
import logging  # import logging to log any error
# import os   # import os module to change working directory
# import glob     # import glob module to file list of filename that match certain criteria
from datetime import datetime, date, timedelta   # import datetime module to convert string to date format
# import shutil   # import shutil module to copy file
import csv      # import csv to read csv file
import copy     # import copy to copy from (sum bp account w/o currency) to (sum bp account with currency)
import subprocess   # import subprocess module to call another application

def input_files(input_dir, out_timestamp, pa2_pa2, position_txt, cons_rc_scan_csv, cons_rc_intermonth_csv, cons_rc_intercomm_csv, cons_house_csv):
    ### skip finding the latest pa2 and position files
    ### skip copying pa2 and position file to another location
    pa2_pa2 = input_dir + pa2_pa2
    position_txt = input_dir + position_txt

    rc_intercomm_csv =  input_dir + cons_rc_intercomm_csv
    rc_intermonth_csv =  input_dir + cons_rc_intermonth_csv
    rc_scan_csv =  input_dir + cons_rc_scan_csv
    house_csv = input_dir + cons_house_csv

    ### 1.1. define a bunch of newly created files
    # modified files
    new_pa2 = input_dir + out_timestamp + r"_new.pa2"
    sum_position_txt = input_dir + out_timestamp + r"_sum.txt"
    sum_position_rc_txt = input_dir + out_timestamp + r"_sum_rc.txt"

    # newly created files
    whatif_xml = input_dir + out_timestamp + r"_whatif.xml"
    spanInstr_margin_txt = input_dir + out_timestamp + r"_spanInstr_margin.txt"  # span instruction for margin
    spanInstr_rc_txt = input_dir + out_timestamp + r"_spanInstr_rc.txt"  # span instruction for rc
    span_margin_spn = input_dir + out_timestamp + r"_span_margin.spn"    # spn files
    span_rc_spn = input_dir + out_timestamp + r"_span_rc.spn"
    pbreq_margin_csv = input_dir + out_timestamp + r"_pbreq_margin.csv"  # pbreq files
    pbreq_rc_csv = input_dir + out_timestamp + r"_pbreq_rc.csv"
    final_csv = input_dir + out_timestamp + r"_final.csv"

    return (pa2_pa2, position_txt, rc_intercomm_csv,rc_intermonth_csv, rc_scan_csv, house_csv, new_pa2, sum_position_txt,sum_position_rc_txt, whatif_xml, spanInstr_margin_txt, spanInstr_rc_txt, span_margin_spn, span_rc_spn, pbreq_margin_csv, pbreq_rc_csv, final_csv)


# 2. read pa2 files and store data into various lists
### 2.1. read and store each line into pa2_list
def read_pa2(pa2_pa2):
    with open (pa2_pa2, "r") as temp:   # open original pa2 in read mode
        original_pa2 = temp.readlines()    # read every lines in pa2 file, and then store in it original pa2 list
    return (original_pa2)

### 2.2. loop through each row in pa2_list, base on each condition, store different information into different list
def parse_pa2(original_pa2):
    # 2.2.1. create a bunch of empty list to store data
    price_list = []             # dsp price, except option price. Record 82
    price_param_list = []       # insrument type, price decimal locator, strike decimal locator, contract size, currency. Record P
    intermonth_list = []        # commodity, tier A, tier B, spread. Record C
    intermonth_param_list = []  # commodity, each tier start + end. Record 3
    intercomm_list = []         # commo A, delta A, commo B, delta B, intercomm spread. Record 6
    intercomm_param_list = []   # commo group, commo 1,2,3,4,... 10. Record 5
    instrument_list = []         # commodity, intrument type, maturity "yyyymm". Record B
    deltascale_list = []       # commodity, instrument type, maturity, delta scaling factor. Record B
    option_list = []            # commodity, call/put, maturity, strike, delta, dsp. Record 82
    currency_list = []          # fx rate. Record T

    # 2.2.2. loop through each row in original_pa2 list, fill up data for each list above
    for line in original_pa2:
        # a. price list = list of prices [commodity, type, maturity, price]
        # eg ['WMP','FUT',201801,31200]
        if line.startswith("82") and (line[25:28] == "FUT" or line[25:28] == "PHY"):
            price_list.append({     # insert into list dictionary style data
                'comm':str(line[5:15]).strip(),    # strip() remove any space character
                'instype':str(line[25:28]),
                'maturity':int(line[29:35].strip() or 0),   # if result is blank string after stripping, will take value 0 to be able to convert to integer
                'dsp':float(line[110:117].strip() or 0)     # if string is blank after stripping, take value of zero. Then convert to float
            })

        # b. list of all calc parameters [commodity, type, settlement price decimal locator, contract value factor, strike price decimal locator,currency] 
        # eg ['MKP','OOF',2,6000,2,'NZD'] 
        elif line.startswith("P"):
            price_param_list.append({
                'comm':str(line[5:15]).strip(),
                'instype':str(line[15:18]),
                'dspdl':int(line[33:36].strip() or 0),
                'cvf':float(line[41:55].strip() or 0)/10000000, # contract size
                'strikedl':int(line[36:39].strip() or 0),
                'curr':str(line[65:68])
            })

        # c. list of intermonth spreads[commodity, tier a, tier b, spread] 
        # eg ['WMP',1,2,130]
        elif line.startswith("C"):
            intermonth_list.append({
                'comm':str(line[2:8]).strip(),
                'tiera':int(line[23:25].strip() or 0),
                'tierb':int(line[30:32].strip() or 0),
                'spread':int(line[14:21].strip() or 0)
            })

        # d. list of intermonth details[commodity, tier number 1, start month, end month...tiers 2,...,3,...,4,...]
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

        # e. list of intercomm spreads[commodity a, delta a, commodity b, delta b, spread]
        # eg ['WMP',20,'SMP',29,30]
        elif line.startswith("6"):
            intercomm_list.append({
                'comma':str(line[20:26]).strip(),
                'deltaa':int(line[26:29].strip() or 0),
                'commb':str(line[38:44]).strip(),
                'deltab':int(line[44:47].strip() or 0),
                'spread':int(line[9:12].strip() or 0)
            })
            
        # f. list of intercomm groups and up to ten constituent commodities
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
            
        # g. list of instruments by type and maturity, one option record per maturity no individual records for call/put or diff strikes [commodity, type, maturity] 
        # eg ['WMP','OOF',201801]
        elif line.startswith("B") and line[15:18] != "PHY":            
            instrument_list.append({
                'comm':str(line[5:15]).strip(),
                'instype':str(line[15:18]),
                'maturity':int(line[18:24].strip() or 0)
            })
        
        # h. same as above, incl delta scaling factor
            deltascale_list.append({
                'comm':str(line[5:15]).strip(),
                'instype':str(line[15:18]),
                'maturity':int(line[18:24].strip() or 0),
                'deltasf':int(line[85:91].strip() or 0)
            })

        # i. list of options prices and deltas [commodity,option on physical or future,call or put, maturity,strike,composite delta,dsp]
        elif line.startswith("82") and (str(line[25:28]) == "OOF" or str(line[25:28]) == "OOP"):
            option_list.append({
                'comm':str(line[5:15]).strip(),
                'instype':str(line[25:28]),
                'callput':str(line[28:29]),
                'maturity':int(line[38:44].strip() or 0),
                'strike':int(line[47:54].strip() or 0),
                'delta':int(line[96:101].strip() or 0) * (-1 if str(line[101:102]) == "-" else 1),    # multiply with -1 in case delta is negative
                'dsp':int(line[110:117].strip() or 0) * (-1 if str(line[117:118]) == "-" else 1)
            })
        
        # j. list of currency exchange rates [currency converted from, currency converted to, rate]
        # eg ['USD','NZD',1.450537]
        elif line.startswith("T"):            
            currency_list.append({
                'curra':str(line[2:5]),
                'currb':str(line[6:9]),
                'rate':float(line[10:20])/1000000
            })
    
    # 2.2.3. consolidate price_list[] and price_param_list[] 
    # new price_list[] = [commodity, type, maturity, price, settlement price decimal locator, contract value factor] 
    # eg ['MKP','FUT',201809,655,2,6000] 
    for price in price_list:
        bAppend = False # default value for append boolean
        for price_param in price_param_list:
            if price['comm'] == price_param['comm'] and price['instype'] == price_param['instype']:    # with matching commodity and instrument type
                price.update({    # update dictionary in price_list row. DO NOT USE append
                    'dspdl':price_param['dspdl'],
                    'cvf':price_param['cvf']
                })
                bAppend = True
                break   # get out of loop price_param. Because there will be multiple row matching criteria
        if not bAppend:
            price.update({
                'dspdl':"N/A",
                'cvf':"N/A"
            })
    
    # 2.2.4. consolidate instrument_list[] and price_param_list[]
    # now instrument_list is [commodity, type, maturity, settlement price decimal locator, contract value factor]
    # eg ['FBU','OOP',201809,2,100]
    for instrument in instrument_list:
        bAppend = False # default value for append boolean
        for price_param in price_param_list:
            if instrument['comm'] == price_param['comm'] and instrument['instype'] == price_param['instype']:    # with matching commodity and instrument type
                instrument.update({  # update dictionary. DO NOT USE append
                    'dspdl':price_param['dspdl'],
                    'cvf':price_param['cvf']
                })
                bAppend = True
                break   # get out of loop price_param. Because there will be multiple row matching criteria
        if not bAppend:
            instrument.update({
                'dspdl':"N/A",
                'cvf':"N/A"
            })

    return (price_list, intermonth_list, intermonth_param_list, intercomm_list,
        instrument_list, option_list, deltascale_list, price_param_list, currency_list)

# 3. read 3 constant files
def read_rcparams (rc_scan_csv,rc_intermonth_csv, rc_intercomm_csv):
    ### 3.1. create empty list
    rc_scan_list = []
    rc_intermonth_list = []
    rc_intercomm_list = []

    ### 3.2. read rc scan. Parse data to rc scan list
    # commodity, maturity, stretch percentage 
    # eg ['MKP',201809,0.02]
    with open (rc_scan_csv, "r") as temp:        
        csv_reader = list(csv.reader(temp))
        for row in csv_reader: 
            rc_scan_list.append({
                'comm':str(row[0]),
                'maturity':int(row[1]),
                'rate':float(row[2])
            })

    ### 3.3. read rc intermonth. Parse data to rc intermonth list
    # commodity, tier a, tier b, spread%
    # eg ['WMP',1,2,0.3]
    with open (rc_intermonth_csv, "r") as temp:
        csv_reader = list(csv.reader(temp))
        for row in csv_reader:
            rc_intercomm_list.append({
                'comm':str(row[0]),
                'tiera':int(row[1]),
                'tierb':int(row[2]),
                'rate':float(row[3])
            })

    ### 3.4. read rc intercomm. Parse data to rc intercomm list
    # commodity a, delta a, commodity b, delta b, spread% 
    # eg ['WMP',20,'SMP',29,0.4]
    with open (rc_intercomm_csv, "r") as temp:
        csv_reader = list(csv.reader(temp))
        for row in csv_reader:
            rc_intercomm_list.append({
                'comma':str(row[0]),
                'deltaa':int(row[1]),
                'commb':str(row[2]),
                'deltab':int(row[3]),
                'rate':float(row[4])
            })
    
    return (rc_scan_list, rc_intermonth_list, rc_intercomm_list)

### MAIN: calculate 21% rc ###
def Calculate_21_rc(input_dir, out_timestamp, pa2_pa2, position_txt, cons_rc_scan_csv, cons_rc_intermonth_csv, cons_rc_intercomm_csv, cons_house_csv):
    (pa2_pa2, position_txt, rc_intercomm_csv,rc_intermonth_csv, rc_scan_csv, house_csv, new_pa2, sum_position_txt,sum_position_rc_txt, whatif_xml, spanInstr_margin_txt, spanInstr_rc_txt, span_margin_spn, span_rc_spn, pbreq_margin_csv, pbreq_rc_csv, final_csv) = input_files(input_dir, out_timestamp, pa2_pa2, position_txt, cons_rc_scan_csv, cons_rc_intermonth_csv, cons_rc_intercomm_csv, cons_house_csv)

    (original_pa2) = read_pa2(pa2_pa2)

    (price_list, intermonth_list, intermonth_param_list, intercomm_list, instrument_list, option_list, deltascale_list, price_param_list, currency_list) = parse_pa2(original_pa2)

    (rc_scan_list, rc_intermonth_list, rc_intercomm_list) = read_rcparams (rc_scan_csv,rc_intermonth_csv, rc_intercomm_csv)
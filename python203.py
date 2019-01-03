"""
re-create Risk Capital calculation script again for 21% stretch
"""
from __future__ import division     # import division so that '/' is mapped to __truediv__() and return more decimals figure
import logging  # import logging to log any error
import os   # import os module to change working directory
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
### 2.1. read and store each line into original_pa2
def read_pa2(pa2_pa2):
    with open (pa2_pa2, "r") as temp:   # open original pa2 in read mode
        original_pa2 = temp.readlines()    # read every lines in pa2 file, and then store in it original pa2 list
    return (original_pa2)

### 2.2. loop through each row in original_pa2, base on each condition, store different information into different list
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
        # Having 2 seperate price list and instrument list because price list doesn't have option instrument. Once calculate price of underlying FUT of options, the script will update rc scan range of underlying instrument of that option in Instrument list
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
            rc_intermonth_list.append({
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

# 4. calculate new scan range, new intermonth, new intercomm, based on 3 rc cons files. Then re write intermonth list and intercomm list 
"""
anything misspecified or missing is ignored, default for scan stretch is 
0.25, intermonth and intercomm default to what is in original margin pa2
"""
### 4.1. calcuate new scan range
# a. append new column to price list
def calc_newscan(price_list, instrument_list, rc_scan_list):
    for price in price_list:
        bUpdate = False # boolean if instrument was specified in rc_scan_csv
        for rc_scan in rc_scan_list:
            if price['comm'] == rc_scan['comm'] and price['maturity'] == rc_scan['maturity']:
                price.update({
                    'rc_scan_rate':rc_scan['rate']
                })
                bUpdate = True
        if not bUpdate:
            price['rc_scan_rate'] = float(0.25) # specify 21% if instrument is not specified in rc_scan parameter

# b. calculate regular price (after consider contract size). Calculate stretch price (after consider contract size and max movement)
    for instru in instrument_list:
        bUpdate = False # boolean variable if price has been calculated and updated?
        for price in price_list:
            if instru['instype'] != 'OOP':   # NOT option on physical
                if instru['comm'] == price['comm'] and instru['maturity'] == price['maturity']:
                    instru.update({
                        'dspconv':price['dsp']/(10**price['dspdl'])*instru['cvf'],  # = price of underlying / (10^decimal locator of underlying) * contract size of instrument itself
                        'rc_scan_range':price['dsp']/(10**price['dspdl'])*instru['cvf']*price['rc_scan_rate']   # = dsp converted * rc_scan_rate
                    })
                    bUpdate = True
            elif instru['instype'] == 'OOP':
                if instru['comm'] == price['comm'] and instru['maturity'] == price['maturity'] and price['instype'] == 'PHY':
                    instru.update({
                        'dspconv':price['dsp']/(10**price['dspdl'])*instru['cvf'],
                        'rc_scan_range':price['dsp']/(10**price['dspdl'])*instru['cvf']*price['rc_scan_rate']
                    })
                    bUpdate = True
        if not bUpdate:
            print (instru['comm'] + " " + instru['instype'] + " not updated")

    return (price_list, instrument_list)

### 4.2. calcuclate new intermonth
def calc_newintermonth(instrument_list, intermonth_param_list, intermonth_list, rc_intermonth_list):
    # 4.2.1. break down intermonth parameter into tier list
    tier_list = []
    for r in intermonth_param_list:
        if r['tier1'] != 0:
            tier_list.append({
                'comm':r['comm'],
                'tier':1
            })
        if r['tier2'] != 0:
            tier_list.append({
                'comm':r['comm'],
                'tier':2
            })
        if r['tier3'] != 0:
            tier_list.append({
                'comm':r['comm'],
                'tier':3
            })
        if r['tier4'] != 0:
            tier_list.append({
                'comm':r['comm'],
                'tier':4
            })
        
    # 4.2.2. In instrument list, assign which tier the instrument belongs to
    for instru in instrument_list:
        for r in intermonth_param_list:
            if instru['comm'] == r['comm'] and r['tier1start'] <= instru['maturity'] <= r['tier1end']:
                instru.update({'tier':1})
            elif instru['comm'] == r['comm'] and r['tier2start'] <= instru['maturity'] <= r['tier2end']:
                instru.update({'tier':2})
            elif instru['comm'] == r['comm'] and r['tier3start'] <= instru['maturity'] <= r['tier3end']:
                instru.update({'tier':3})
            elif instru['comm'] == r['comm'] and r['tier4start'] <= instru['maturity'] <= r['tier4end']:
                instru.update({'tier':4})
    
    # 4.2.3. in Tier list, list all normal & rc_scan prices in the tier. Count how many instrument there are in the tier, in order to calculate average later on
    for tier in tier_list:
        pricesum = 0
        scansum = 0
        denominator = 0
        for instru in instrument_list:
            if tier['comm'] == instru['comm'] and instru['instype'] == 'FUT' and tier['tier'] == instru['tier']:     # matching for FUTURE only
                pricesum += instru['dspconv']
                scansum += instru['rc_scan_range']
                denominator += 1

        # complete loop all instruments. Update tier list
        tier.update({
            'pricesum': pricesum,
            'scansum': scansum,
            'denominator':denominator
        })
        
    # 4.2.4. loop rc_intermonth_list. For each row, calculate average pricesum tierA & average pricesum tierB. Then taking total of those 2 averages.
    # For each row, loop through tier_list to find pricesum of each commodity tier.
    for r in rc_intermonth_list:
        avgPriceA = 0
        avgPriceB = 0
        for tier in tier_list:
            if r['comm'] == tier['comm'] and r['tiera'] == tier['tier'] and tier['denominator'] != 0:
                avgPriceA = tier['pricesum']/tier['denominator']
            if r['comm'] == tier['comm'] and r['tierb'] == tier['tier'] and tier['denominator'] != 0:
                avgPriceB = tier['pricesum']/tier['denominator']
        r['tierprice'] = avgPriceA + avgPriceB
    
    # 4.2.5. update new rc_spread into intermonth list. New rc_intermonth_spread = (rate in rc_intermonth_list) * (tier price in rc_intermonth_list)
    for intermonth in intermonth_list:
        bUpdate = False
        for r in rc_intermonth_list:
            if intermonth['comm'] == r['comm'] and intermonth['tiera'] == r['tiera'] and intermonth['tierb'] == r['tierb']:
                intermonth['rc_intermonth_spread'] = r['rate'] * r['tierprice']
                bUpdate = True
        if not bUpdate: # if row in not updated
            intermonth['rc_intermonth_spread'] = 'N/A'

    return (instrument_list, rc_intermonth_list, intermonth_list)

### 4.3. calculate new intercomm
def calc_newintercomm (rc_intercomm_list, intercomm_list):  # multiply intercomm rate in intercomm cons file by 100. If not defined, take existing intercomm value
    # intercomm_list is now [commodity a, delta a, commodity b, delta b, spread, rc delta a, rc delta b, rc intercomm spread] 
    # eg ['WMP',20,'SMP',29,30,20,29,40]. If there is no equivalent combo in rc intercomm csv as in original pa2 file, insert "N/A"
    for intercomm in intercomm_list:
        bUpdate = False
        for r in rc_intercomm_list:
            if intercomm['comma'] == r['comma'] and intercomm['commb'] == r['commb']:
                intercomm.update({
                    'rc_intercomm_DeltaA':r['deltaa'],
                    'rc_intercomm_DeltaB':r['deltab'],
                    'rc_intercomm_rate':int(r['rate']*100)
                })
                bUpdate = True
        if not bUpdate: # case intercomm row is not updated
            intercomm.update({
                'rc_intercomm_DeltaA':'N/A',
                'rc_intercomm_DeltaB':'N/A',
                'rc_intercomm_rate':'N/A'
            })

    return intercomm_list

### 4.4. write rc data into new pa2 file. In the original pa2 list:
# 4.4.1: check for every row start with C, loop intermonth list to find matching commodity & tierA & tierB. Update character 15th to 21st with rc_intermonth_spread
# 4.4.2: check for every row start with 6, loop intercomm list to find matching commA & commB. Update character 9th with rc_intercomm_rate, 16th-26th with rc_intercomm_DeltaA, 33rd-44th with rc_intercomm_DeltaB
def write_newinters(intermonth_list, intercomm_list, original_pa2):
    new_intermonth_list = []
    new_intercomm_list = []

    # 4.4.1
    for pa2 in original_pa2:
        if pa2.startswith('C'):
            bAmended = False
            for r in intermonth_list:
                if pa2[2:8].strip() == r['comm'] and int(pa2[23:25].strip()) == r['tiera'] and int(pa2[30:32].strip()) == r['tierb']:  # if matches commodity, tier A & tier B
                    if r['rc_intermonth_spread'] == 'N/A':
                        new_intermonth_list.append(pa2)
                        bAmended = True
                    else:
                        new_intermonth_list.append(
                            pa2[:14] +
                            str(int(r['rc_intermonth_spread'])).rjust(7,'0') +   # fill with rc intermonth spread and 0 until enough 7 characters
                            pa2[21:]
                        )
                        bAmended = True
            if not bAmended:
                new_intermonth_list.append(pa2)

    # 4.4.2
        if pa2.startswith('6'):
            bAmended = False
            for r in intercomm_list:
                if pa2[20:26].strip() == r['comma'] and pa2[38:44].strip() == r['commb']:
                    if r['rc_intercomm_rate'] == 'N/A':
                        new_intercomm_list.append(pa2)
                        bAmended = True
                    else:
                        new_intercomm_list.append(
                            pa2[:9] +
                            str(r['rc_intercomm_rate']).rjust(3,'0') + '0000' +
                            pa2[16:26] +
                            str(r['rc_intercomm_DeltaA']).rjust(3,'0') + '0000' +
                            pa2[33:44] +
                            str(r['rc_intercomm_DeltaB']).rjust(3,'0') + '0000' +
                            pa2[51:]
                        )
                        bAmended = True
            if not bAmended:
                new_intercomm_list.append(pa2)

    return (new_intermonth_list, new_intercomm_list)

# 5. write new pa2 for RC calculation. Copying everything from original pa2 list, except for record type C and 6. Using new intermonth list + new intercomm list (above), write every lines in those list to bottom of new pa2 file
def write_new_pa2(original_pa2,new_intermonth_list,new_intercomm_list,new_pa2):
    with open (new_pa2, "w") as temp:
        for origin in original_pa2:
            if not origin.startswith('C') and not origin.startswith('6'):
                temp.write(origin)
        
        # write new intermonth & intercomm in new pa2 file
        temp.writelines(new_intermonth_list)
        temp.writelines(new_intercomm_list)

# 6. write whatif xml file
def write_whatif(instrument_list, whatif_xml):
    # 6.1. define function write update scan: inserting values into what-if.xml file in format that PC SPAN can understand
    def write_updatescan(commodity,instype,maturity,newscan):
        return ''.join((
            "<updateRec>\n<ec>NZX</ec>\n<cc>",
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

    # 6.2. loop through instrument_list, append to xml list all string info being output of write_updatescan() function above
    xml_list = []
    for instru in instrument_list:
        xml_list.append(
            write_updatescan(
                instru['comm'],
                instru['instype'],
                instru['maturity'],
                instru['rc_scan_range']
                )
        )
    
    # 6.3. write xml list to xml file:
    with open (whatif_xml, "w") as temp:
        temp.write('<scenarioFile>\n')  # first: add scenario files statement
        for row in xml_list:
            temp.write(row)
            temp.write('\n')
        temp.write('\n<scenarioFile>')
    
# 7. read position and breakdown to bunch of lists
### 7.1. read position text file and store in position list
def read_position(position_txt):
    with open (position_txt, 'r') as temp:
        position_list = temp.readlines()
    return position_list

### 7.2. breakdown to a bunch of lists
def parse_position(position_list):
    # 7.2.1. create new empty list
    record5_list = []   # everything in record 5
    bpins_list = []     # every instruments per bp
    option_position_list = []   # every option position per bp, per acc. This is for delta adj
    bp_acc_list = []    # every acc name per bp, additional Sum account for each bp
    sum_bpacc_list = [] # list of all accounts per bp, with currency
    omni_acc_list = []  # list of omnibus/client account. Since we want to exclude client position from sum position account

    # 7.2.2. loop through record 2 add any omnibus client account to omni acc list
    for r in position_list:
        if r.startswith('2') and r[24:29] == 'OCUST':
            omni_acc_list.append(
                r[1:24].strip() # e.g. FCSMargin2
            )

    # 7.2.3. loop through record 5, fill up data for record5, bpins, bpacc, option position lists
    for r in position_list:
        if r.startswith('5'):
        # record 5 list
            record5_list.append({
                'bp':r[1:4].strip(),    # e.g. FCS
                'ins':r[27:92].strip(), # e.g. 'BTR   BTR       FUT 201904                      +00000000000000'
                'position':int(r[92:100].strip()),
                'isOmni':False
                })
            if len(record5_list) > 0 and r[1:24].strip() in omni_acc_list:
                record5_list[-1]['isOmni'] = True   # if account is omnibus, update its boolean variable to true            
        
        # bp instrument list
            bpins_list.append({
                'bp':r[1:4].strip(),
                'ins':r[27:92].strip()
                })
            
        # bp account list
            bp_acc_list.append({'bpacc':r[1:24].strip()})    # e.g. FCSMargin2
            bp_acc_list.append({'bpacc':str(r[1:4]+'Sum')})  # e.g. FCSSum

        # option position list
            if r[45:48] == 'OOF' or r[45:48] == 'OOP':  # case option of future or option on physical
                option_position_list.append({
                    'bp':r[1:4],
                    'acc':r[4:24].strip(),
                    'comm':r[35:45].strip(),
                    'instype':r[45:48],
                    'callput':r[48:49],
                    'maturity':int(r[49:57].strip()),
                    'strikeconv':float(r[78:92].strip())/10000000,
                    'position':int(r[92:100].strip())   # include +/- position
                })

    # 7.2.4. remove duplicate in bpins and bpacc lists. To create sum bpins and sum bpacc lists
    # this is preparation step for creating sum accounts
    sum_bpins_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in bpins_list)]
    print (str(len(bpins_list)) + " v.s. " + str(len(sum_bpins_list)))
    
    temp_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in bp_acc_list)]  # sum bp account, no currency
    print (str(len(bpins_list)) + " v.s. " + str(len(temp_list)))
    
    # 7.2.5. for each account in sum account lists, duplicate the account and add currency NZD & USD for each
    for r in temp_list:
        r['curr'] = "USD"   # add usd currency for dictionary
        sum_bpacc_list.append(copy.deepcopy(r))
        r['curr'] = "NZD"   # add nzd currency for dictionary
        sum_bpacc_list.append(copy.deepcopy(r))   

    # 7.2.6. for each account, for each instrument, create position to sum account. 
    for sumR in sum_bpins_list:
        # a. First set the position value to 0
        sumR['position'] = 0

        # b. loop through record 5, find matching bp and instrument, totalling position together
        for rec5 in record5_list:
            if sumR['bp'] == rec5['bp'] and sumR['ins'] == rec5['ins'] and rec5['isOmni'] != True: 
                sumR['position'] += rec5['position']
    
        # c. if the ins record is option, append this record to option_position list as well
        if sumR['ins'][16:19] == 'OOF' or sumR['ins'][16:19] == 'OOP':
            option_position_list.append({
                'bp':sumR['bp'],
                'acc':'Sum',
                'comm':sumR['ins'][0:4].strip(),
                'instype':sumR['ins'][16:19],
                'callput':sumR['ins'][19:20],
                'maturity':int(sumR['ins'][20:29].strip()),
                'strikeconv':float(sumR['ins'][49:63].strip())/10000000,
                'position':sumR['position']
            })

    return sum_bpins_list, option_position_list, sum_bpacc_list

# 8. write position txt files, with sum account
### 8.1. write position txt files for margin. Client account remains OCUST
# but if in record 2 account type is OCUST, its Sum account will be amended to MHOUS
def write_sum_position_txt(position_list,sum_bpins_list,sum_position_txt):
    with open (sum_position_txt, 'w') as temp:
        # write every original row in position file to new sum position txt
        for origin_posi in position_list:
            temp.write(origin_posi)    

            # under every row of record 2, add Sum account underneath it. If account type is OCUST, change to MHOUS
            if origin_posi.startswith('2') and origin_posi[24:29] == 'OCUST':
                temp.write(
                    origin_posi[:4] +
                    'Sum'.ljust(20," ") +   # fill up the next 20 characters by Sum and " "
                    'MHOUS'+                # force sum account to net
                    origin_posi[29:]
                )
            elif origin_posi.startswith('2'):
                temp.write(
                    origin_posi[:4] +
                    'Sum'.ljust(20," ") + # fill up the next 20 characters by Sum and " "
                    origin_posi[24:]
                )
        
        # loop through sum_bpins_list, write record type 5 for position txt
        for sumPos in sum_bpins_list:
            temp.write(
                "5" + 
                sumPos['bp'] + 
                'Sum'.ljust(20," ") + 
                'NZX'.ljust(5," ") +
                sumPos['ins'] + 
                ("-" if sumPos['position'] < 0 else "0") +
                str(abs(sumPos['position'])).rjust(7,"0") + 
                "\n"
            )

### 8.2. write position txt files for rc. Client account becomes MHOUS
def write_sum_rc_position_txt(position_list,sum_bpins_list,sum_position_rc_txt):
    with open (sum_position_rc_txt, 'w') as temp:
        # write every original row in position file to new sum position txt
        for origin_posi in position_list:
            # temp.write(origin_posi)    # don't write every row yet

            # under every row of record 2, add Sum account underneath it. If account type is OCUST, change to MHOUS
            if origin_posi.startswith('2') and origin_posi[24:29] == 'OCUST':
                temp.write(
                    origin_posi[:24] +
                    'MHOUS' +               # force original account to net
                    origin_posi[29:] + 
                    
                    origin_posi[:4] +
                    'Sum'.ljust(20," ") +
                    'MHOUS'+                # force sum account to net
                    origin_posi[29:]
                )
            elif origin_posi.startswith('2'):
                temp.write(
                    origin_posi + 

                    # add new row for Sum account
                    origin_posi[:4] +
                    'Sum'.ljust(20," ") + 
                    origin_posi[24:]
                )
            else:
                temp.write(origin_posi)
        
        # loop through sum_bpins_list, write record type 5 for position txt
        for sumPos in sum_bpins_list:
            temp.write(
                "5" + 
                sumPos['bp'] + 
                'Sum'.ljust(20," ") + 
                'NZX'.ljust(5," ") +
                sumPos['ins'] + 
                ("-" if sumPos['position'] < 0 else "0") +
                str(abs(sumPos['position'])).rjust(7,"0") + 
                "\n"
            )

# 9. write instruction to tell SPAN calculating margin, then save report.  
### 9.1. write instruction in txt file, for margin calculation purpose. Remove identifier variable as this script only use for margin calculation
def margin_SPAN_instruction(pa2_pa2,sum_position_txt, spn ,spanit_txt):
    with open(spanit_txt, "w") as f:  # open SPAN instruction txt file in write mode
        f.write ("Load " + pa2_pa2 + "\n")   # load original pa2
        f.write ("Load " + sum_position_txt + "\n")  # load position file. Since we calculate for Sum account as well, we currently insert Sum position txt file here
        f.write ("Calc" + "\n") # calculate
        f.write ("Save " + spn + "\n") # save as spn file 
    return spanit_txt

### 9.2. write instruction in txt file, for risk capital calculation purpose. 
def rc_SPAN_instruction(new_pa2,whatif_xml,sum_position_rc_txt, spn, spanit_txt):
    with open(spanit_txt, "w") as f:
        f.write("Load " + new_pa2 + "\n")
        f.write("Load " + sum_position_rc_txt + "\n") 
        f.write("SelectPointInTime" + "\n")
        f.write("ApplyWhatIf " + whatif_xml + "\n")
        f.write("CalcRiskArray" + "\n")
        f.write("Calc" + "\n")
        f.write("Save " + spn + "\n")    
    return spanit_txt

### 9.3. run SPAN, given instruction text file
def call_SPAN(spanit_txt):
    os.chdir (r"C:\span4\bin")  # os.chdir = change current working directory
    subprocess.call(["spanitrm.exe",spanit_txt])

### 9.4. generate SPAN report
# open spn file and generate pbreq.csv file
# the input spn file must have already have pa2 and position files combined
# mshta must be given an absolute pathname, not a relative one
# this process does not work with filenames containing spaces " "
def call_SPAN_report(spn,pbreq_csv):
    os.chdir(r"C:\span4\Reports")
    subprocess.call(["mshta.exe", r"C:\span4\rptmodule\spanReport.hta", spn])

    # Convert spanReport.hta output (Link AP\C:\span4\Reports\PB Req Delim.txt) to (parent directory + \YYYYMMDD-hhmmss_pbreq_identifier.csv)
    pbreq_txt = r"C:\Span4\Reports\PB Req Delim.txt"
    pbreq_reader = csv.reader( open(pbreq_txt,"r"), delimiter = ',')
    with open(pbreq_csv , "w") as output:
        output_csv = csv.writer(output)
        output_csv.writerows(pbreq_reader)


### MAIN: calculate 21% rc ###
def Calculate_21_rc(input_dir, out_timestamp, pa2_pa2, position_txt, cons_rc_scan_csv, cons_rc_intermonth_csv, cons_rc_intercomm_csv, cons_house_csv):
    #1. Collect input files (cons, input). Define newly created file and path.
    (pa2_pa2, position_txt, rc_intercomm_csv,rc_intermonth_csv, rc_scan_csv, house_csv, new_pa2, sum_position_txt,sum_position_rc_txt, whatif_xml, spanInstr_margin_txt, spanInstr_rc_txt, span_margin_spn, span_rc_spn, pbreq_margin_csv, pbreq_rc_csv, final_csv) = input_files(input_dir, out_timestamp, pa2_pa2, position_txt, cons_rc_scan_csv, cons_rc_intermonth_csv, cons_rc_intercomm_csv, cons_house_csv)

    #2. read pa2 file & store data into various lists
    (original_pa2) = read_pa2(pa2_pa2)

    (price_list, intermonth_list, intermonth_param_list, intercomm_list, instrument_list, option_list, deltascale_list, price_param_list, currency_list) = parse_pa2(original_pa2)

    #3. read 3 constant files. Read from file to list
    (rc_scan_list, rc_intermonth_list, rc_intercomm_list) = read_rcparams (rc_scan_csv,rc_intermonth_csv, rc_intercomm_csv)

    #4. calculate new stretched scan range, intermonth, intercomm. Then write new intermonth, intercomm list
    price_list, instrument_list = calc_newscan(price_list, instrument_list,rc_scan_list)    # calculate new scan range, update them into price list and instrument list

    instrument_list, rc_intermonth_list, intermonth_list = calc_newintermonth(instrument_list, intermonth_param_list, intermonth_list, rc_intermonth_list)   # calculate rc spread charge per intermonth tier 

    intercomm_list = calc_newintercomm(rc_intercomm_list, intercomm_list)   # calculate rc intercomm and insert in intercomm list

    (new_intermonth_list, new_intercomm_list) = write_newinters(intermonth_list, intercomm_list, original_pa2)

    #5. write risk capital pa2 file
    # new pa2 file would still have old risk array, has to be recalculated using whatif file
    write_new_pa2(original_pa2,new_intermonth_list,new_intercomm_list,new_pa2)

    #6. write what if file
    write_whatif(instrument_list, whatif_xml)

    #7. read position and breakdown to bunch of lists in order to create sum position list
    position_list = read_position(position_txt)

    (sum_bpins_list, option_position_list, sum_bpacc_list) = parse_position(position_list)

    #8. write new position file with sum position. For rc sum position file, for any omnibus client to house account
    write_sum_position_txt(position_list,sum_bpins_list,sum_position_txt)

    write_sum_rc_position_txt(position_list,sum_bpins_list,sum_position_rc_txt)

    #9. calculate and get report for:
    ### margin
    margin_SPAN_instruction(pa2_pa2,sum_position_txt,span_margin_spn,spanInstr_margin_txt) # write txt instruction for SPAN calculation: margin
    call_SPAN(spanInstr_margin_txt)
    call_SPAN_report(span_margin_spn, pbreq_margin_csv)
    
    ### risk capital
    rc_SPAN_instruction(new_pa2,whatif_xml,sum_position_rc_txt,span_rc_spn,spanInstr_rc_txt)    # write txt instruction for SPAN calculation: risk capital
    call_SPAN(spanInstr_rc_txt)
    call_SPAN_report(span_rc_spn, pbreq_rc_csv)

    #10. calculate delta adjusted net exposure for options
#!/usr/bin/env python

"""
Input (filenames are specified within find_current_files() )
-SPUD margin parameters (.pa2)
-BaNCS position file (.txt)
-RISK risk capital parameters (.csv), three files: scan ranges, inter month, inter commodity
-House accounts list (.csv) - will need updating for new participant or change in existing 
 participant account structure!

Intermediate output
-rc parameters with intermonth and intercomm adjusted (.pa2)
-Adjusted position file with instruments netted across accounts for same BP (.txt)
-what-if scenarios to adjust scan ranges(.xml)
-commands to span software to calc risk capital using unadjusted and adjusted position(.txt)
-commands to span software to create csv reports (.txt)
-margins with position unadjusted (.csv)
-margins with position adjusted (.csv)
-rc with position unadjusted(.csv)
-rc with position adjusted (.csv)

Final Output
- uncovered losses/margins/theoretical rc/dane for every BP acc, and final amount per BP according
  to parse_rc logic (.csv)
"""

from __future__ import division #
import copy#
import csv#
import datetime#
import glob#
import logging#
import os#
import shutil
import subprocess#

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.encoders import encode_quopri

# Logging output filename (takes a datetime instance as format() arg)
LOGFILE = r"D:\span\rc\out\{0:%Y%m%d-%H%M%S}_log.log"

# Risk team want the logs emailed to them
# Leave blank if you don't want an email
LOGFILE_EMAIL = '' #risk@nzx.com'
MAILSERVER = '' #'akp-int-services.nzx.com'

# Where's the final directory into which we copy the output CSV
# for consumption by Data Central?
# Leave blank if you don't want to copy anywhere
#OUTPUT_DIR = "E:\\ftp-root\\PRDV7\\riskcapital\\"
OUTPUT_DIR = "C:\\Users\\douglas.cao\\Google Drive\\Python\\RiskCapital"

# don't need to email logfile for 21% RC
def email_logfile(yyyymmdd, hhmmss):
    """Email the logging output to LOGFILE_EMAIL"""
    logdate = datetime.datetime.strptime(yyyymmdd + hhmmss, '%Y%m%d%H%M%S')
    logfile = LOGFILE.format(logdate)
    
    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = 'Log output from riskcapital calcs'
    msg['From'] = 'Risk Capital <securities-it@nzx.com>'
    msg['To'] = LOGFILE_EMAIL
    msg.preamble = 'data from windows'
    msg.epilogue = ''   # Guarantees the message ends in a newline
    msg.attach(MIMEText('Attached is the logging output from riskcapital3.py'))
    
    # Add the attachment
    with open(logfile) as logfileopen:
        # Be very careful here - MIMEText defaults to a 7bit transfer
        # encoding, which will cause lines longer than 990 chars to be
        # wrapped as per RFC2822 (mangling your file).
        # Using quoted-printable encoding avoids this problem.
        submsg = MIMEText(logfileopen.read(), _subtype='plain')
        del submsg['Content-Transfer-Encoding']
        encode_quopri(submsg)
    submsg.add_header("Content-Disposition", "attachment", filename=logfile)
    msg.attach(submsg)
    
    if LOGFILE_EMAIL:
        sock = smtplib.SMTP(MAILSERVER)
        sock.sendmail(msg['From'], msg['To'], msg.as_string())
        sock.close()

# step 1 
def write_log():
    """Configure logging, return YYmmdd and HHMMSS strings for the current date+time"""
    exectime = datetime.datetime.now()
    logging.basicConfig(filename=LOGFILE.format(exectime), level=logging.INFO)
    # return exectime.strftime("%Y%m%d"), exectime.strftime("%H%M%S")   #this return here will define value for yyyymmdd, hhmmss value
    return exectime.strftime("%H%M%S")
    
# step 2
def find_current_files(yyyymmdd,hhmmss):
    # Current date and time
    #yyyymmdd = datetime.date.today().strftime("%Y%m%d")
    #hhmmss = datetime.datetime.now().strftime("%H%M%S")
    
    # Folder where original parameters and position are kept
    os.chdir(r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital\original pa2 and position")     #os.chdir(r"E:\ftp-root\PRDV7\SPAN\Outgoing\target")    
    
    # Find the latest parameter file
    latest_pa2_file = max(glob.iglob('NZX.' + yyyymmdd + '*.pa2'), key=os.path.getmtime)    #find pa2 file with on yyyymmdd date with latest modified time  #max(glob.iglob('NZX.*.pa2'), key=os.path.getmtime)
    latest_pa2_filepath = r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital\original pa2 and position" + "\\" + latest_pa2_file
    
    # Find the latest position file
    latest_position_file = max(glob.iglob('SPANPOS_' + yyyymmdd + '*.txt'), key=os.path.getmtime)   #max(glob.iglob('SPANPOS_*.txt'), key=os.path.getmtime)
    latest_position_filepath = r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital\original pa2 and position" + "\\" + latest_position_file
    
    # Prefix for files created from this script
    prefix_cons = r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital\cons\cons_"    #r"D:\span\rc\cons\cons_"
    prefix_datetime = r"C:\Users\douglas.cao\Google Drive\Python\RiskCapital\out" + "\\" + yyyymmdd + r"_"    #r"D:\span\rc\out" + "\\" + yyyymmdd + r"-" + hhmmss + r"_"
    #prefix_date = r"D:\span\rc" + "\\" + yyyymmdd + r"_"
    
    # Filenames, to be created by other functions
    # Copies of original files
    # Name will be prefix + original, so not consistent with modified/created files below
    pa2_file = prefix_datetime + latest_pa2_file 
    # Name will be prefix + original, so not consistent with modified/created files below
    position_file = prefix_datetime + latest_position_file 
    # Modified files
    new_pa2_file = prefix_datetime + r"new.pa2"
    sum_position_file =  prefix_datetime + r"sum.txt"
    # Constant files
    cons_rc_intercomm_file =  prefix_cons + r"rc_intercomm.csv"
    cons_rc_intermonth_file =  prefix_cons + r"rc_intermonth.csv"
    cons_rc_scan_file =  prefix_cons + r"rc_scan.csv"
    cons_house_file = prefix_cons + r"house.csv"
    # Newly created files
    whatif_file =  prefix_datetime + r"whatif.xml"
    rc_intercomm_file =  prefix_datetime + r"rc_intercomm.csv"
    rc_intermonth_file =  prefix_datetime + r"rc_intermonth.csv"
    rc_scan_file =  prefix_datetime + r"rc_scan.csv"
    house_file = prefix_datetime + r"house.csv"
    # Leave out file extension to add identifier in write_margin/rc_spanit function
    spanit_script = prefix_datetime + r"spanit_" 
    # Leave out file extension to add identifier in write_margin/rc_spanit function
    span_file = prefix_datetime + r"span_" 
    # Leave out file extension to add identifier in call_span_report function
    pbreq_csv_file =  prefix_datetime + r"pbreq_" 
    final_file = prefix_datetime + r"final.csv"
    #log_file = prefix_datetime + r"log.log"
    
    # Copy original files to script folder
    shutil.copy(latest_pa2_filepath, pa2_file)
    shutil.copy(latest_position_filepath, position_file)
    
    # Created dated copy of constant files
    try:
        shutil.copy(cons_rc_intercomm_file, rc_intercomm_file)
    except IOError:
        logging.error(cons_rc_intercomm_file + " not found")
    
    try:
        shutil.copy(cons_rc_intermonth_file, rc_intermonth_file)
    except IOError:
        logging.error(cons_rc_intermonth_file + " not found")
    
    try:
        shutil.copy(cons_rc_scan_file, rc_scan_file)
    except IOError:
        logging.error(cons_rc_scan_file + " not found")
    
    try:
        shutil.copy(cons_house_file, house_file)
    except IOError:
        logging.error(cons_house_file + " not found")   
    
    return (pa2_file, position_file, new_pa2_file, sum_position_file,
        whatif_file, rc_intercomm_file, rc_intermonth_file, rc_scan_file,
        spanit_script, span_file, pbreq_csv_file, house_file, final_file)

# step 3
def read_pa2(pa2_file):
    with open(pa2_file,"r") as f:   #open pa2_file in read mode, name this opened file f
        pa2_list = f.readlines()    #read all lines of the opened pa2_file (f). Put results in pa2_list
    return pa2_list 

# step 4
def parse_pa2(pa2_list):
    price_list = []             # for future prices
    price_param_list = []       # calculation parameter
    intermonth_list = []        # intermonth spread charge
    intermonth_param_list = []  # intermonth parameter details
    intercomm_list = []         # intercommodity spread charge
    intercomm_param_list = []   # intercommodity parameter details
    instrument_list = []        # instrument type & maturity
    option_list = []            # option prices and delta
    deltascale_list = []        # instrument type, maturity & delta scaling factor
    currency_list = []          # currency
    
    # scrap pa2_list based on record type = what each row start with
    for pa2 in pa2_list:
        # list of futures prices [commodity, type, maturity, price] eg ['WMP','FUT',201801,31200]
        if pa2.startswith("82") and (str(pa2[25:28]) == "FUT" or str(pa2[25:28]) == "PHY"):
            price_list.append({
            'comm':str(pa2[5:15]).strip(),
            'instype':str(pa2[25:28]),
            'maturity':int(pa2[29:35].strip() or 0), 
            'dsp':float(pa2[110:117].strip() or 0)
            })
            
        # list of options prices and deltas [commodity,option on physical or future,call or put,
        #       maturity,strike,composite delta,dsp]
        elif pa2.startswith("82") and (str(pa2[25:28]) == "OOF" or str(pa2[25:28]) == "OOP"):
            option_list.append({
            'comm':str(pa2[5:15]).strip(),
            'instype':str(pa2[25:28]),
            'callput':str(pa2[28:29]),
            'maturity':int(pa2[38:44].strip() or 0),
            'strike':int(pa2[47:54].strip() or 0),
            'delta':int(pa2[96:101].strip() or 0) * (-1 if str(pa2[101:102]) == "-" else 1),
            'dsp':int(pa2[110:117].strip() or 0) * (-1 if str(pa2[117:118]) == "-" else 1),
            })
            
        # list of all calc parameters [commodity, type, settlement price decimal locator,
        #   contract value factor, strike price decimal locator,currency] eg ['MKP','OOF',2,6000,2,'NZD'] 
        elif pa2.startswith("P"):
            price_param_list.append({
            'comm':str(pa2[5:15]).strip(),
            'instype':str(pa2[15:18]),
            'dspdl':int(pa2[33:36].strip() or 0),
            'cvf':float(pa2[41:55].strip() or 0)/10000000,
            'strikedl':int(pa2[36:39].strip() or 0),
            'curr':str(pa2[65:68])
            })
            
        # list of intermonth spreads[commodity, tier a, tier b, spread] eg ['WMP',1,2,130]
        elif pa2.startswith("C"):
            intermonth_list.append({
            'comm':str(pa2[2:8]).strip(),
            'tiera':int(pa2[23:25].strip() or 0),
            'tierb':int(pa2[30:32].strip() or 0),
            'spread':int(pa2[14:21].strip() or 0)
            })
            
        # list of intermonth details[commodity, tier number 1, start month, end month...tiers 2,3,4]
        # eg ['WMP',1,201805,201807,2,201808,201905,3,201906,202006,0,0,0]
        elif pa2.startswith("3"):      
            intermonth_param_list.append({
            'comm':str(pa2[2:8]).strip(),
            'tier1':int(pa2[10:12].strip() or 0),
            'tier1start':int(pa2[12:18].strip() or 0),
            'tier1end':int(pa2[18:24].strip() or 0),
            'tier2':int(pa2[24:26].strip() or 0),
            'tier2start':int(pa2[26:32].strip() or 0),
            'tier2end':int(pa2[32:38].strip() or 0),
            'tier3':int(pa2[38:40].strip() or 0),
            'tier3start':int(pa2[40:46].strip() or 0),
            'tier3end':int(pa2[46:52].strip() or 0),
            'tier4':int(pa2[52:54].strip() or 0),
            'tier4start':int(pa2[54:60].strip() or 0),
            'tier4end':int(pa2[60:66].strip() or 0)
            })
            
        # list of intercomm spreads[commodity a, delta a, commodity b, delta b, spread]
        # eg ['WMP',20,'SMP',29,30]
        elif pa2.startswith("6"):
            intercomm_list.append({
            'comma':str(pa2[20:26]).strip(),
            'deltaa':int(pa2[26:29].strip() or 0),
            'commb':str(pa2[38:44]).strip(),
            'deltab':int(pa2[44:47].strip() or 0),
            'spread':int(pa2[9:12].strip() or 0)
            })
            
        # list of intercomm groups and up to ten constituent commodities
        elif pa2.startswith("5"):
            intercomm_param_list.append({
            'commgroup':str(pa2[2:5]).strip(),
            'comm1':str(pa2[12:18]).strip(),
            'comm2':str(pa2[18:24]).strip(),
            'comm3':str(pa2[24:30]).strip(),
            'comm4':str(pa2[30:36]).strip(),
            'comm5':str(pa2[36:42]).strip(),
            'comm6':str(pa2[42:48]).strip(),
            'comm7':str(pa2[48:54]).strip(),
            'comm8':str(pa2[54:60]).strip(),
            'comm9':str(pa2[60:66]).strip(),
            'comm10':str(pa2[66:72]).strip()
            })
            
        elif pa2.startswith("B") and pa2[15:18] != "PHY":
            # list of instruments by type and maturity, one option record per maturity, 
            # no individual records for call/put or diff strikes [commodity, type, maturity] 
            # eg ['WMP','OOF',201801]
            instrument_list.append({
            'comm':str(pa2[5:15]).strip(),
            'instype':str(pa2[15:18]),
            'maturity':int(pa2[18:24].strip() or 0)
            })
            # same as above, incl delta scaling factor
            deltascale_list.append({
            'comm':str(pa2[5:15]).strip(),
            'instype':str(pa2[15:18]),
            'maturity':int(pa2[18:24].strip() or 0),
            'deltasf':int(pa2[85:91].strip() or 0)
            })
            
        elif pa2.startswith("T"):
            # list of currency exchange rates [currency converted from, currency converted to, rate]
            # eg ['USD','NZD',1.450537]
            currency_list.append({
            'curra':str(pa2[2:5]),
            'currb':str(pa2[6:9]),
            'rate':float(pa2[10:20])/1000000
            })

    # add extra details in price_list[] from price_param_list[]
    # new price_list = [commodity, type, maturity, price, settlement price decimal locator,
    # contract value factor] eg ['MKP','FUT',201809,655,2,6000]  
    for price in price_list:
        appended = False
        for price_param in price_param_list:
            if price['comm'] == price_param['comm'] and price['instype'] == price_param['instype']:
                price.update({
                'dspdl':price_param['dspdl'],
                'cvf':price_param['cvf']
                })
                appended = True
                break
        if not appended:
            logging.error("Error with original SPAN parameters: this instrument type from record 8 does not"
                " have an equivalent record P: " + str(price['comm']) + str(price['instype']))
            price.update({
            'dspdl':"NA",
            'cvf':"NA"
            })

    # add extra details in instrument_list[] from price_param_list[]
    # now instrument_list is [commodity, type, maturity, settlement price decimal locator, 
    # contract value factor] eg ['FBU','OOP',201809,2,100]
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

    return (price_list, intermonth_list, intermonth_param_list, intercomm_list,
        intercomm_param_list, instrument_list, option_list, deltascale_list,
        price_param_list, currency_list)

# step 5
def read_rcparams(rc_scan_file,rc_intermonth_file,rc_intercomm_file):
    """
    anything misspecified or missing is ignored, default for scan stretch is 
    0.25, intermonth and intercomm default to what is in original margin pa2
    """
    rc_scan_list = []
    rc_intermonth_list = []
    rc_intercomm_list = []
    # commodity, maturity, stretch percentage eg ['MKP',201809,0.02]
    try:
        with open(rc_scan_file,"r") as f:
            rc_scan_raw_list = list(csv.reader(f))
        for line in rc_scan_raw_list:
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
    except IOError:
        logging.error(rc_scan_file + " was not created")
        
    # commodity, tier a, tier b, spread% eg ['WMP',1,2,0.3]
    try:
        with open(rc_intermonth_file,"r") as f:
            rc_intermonth_raw_list = list(csv.reader(f))
        for line in rc_intermonth_raw_list:
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
    except IOError:
        logging.error(rc_intermonth_file + " was not created")
        
    # commodity a, delta a, commodity b, delta b, spread% eg ['WMP',20,'SMP',29,0.4]
    try:
        with open(rc_intercomm_file,"r") as f:
            rc_intercomm_raw_list = list(csv.reader(f))
        for line in rc_intercomm_raw_list:
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
    except IOError:
        logging.error(rc_intercomm_file + " was not created")
        
    # Add blank entries into three rc lists above so no KeyError later
    rc_scan_list.append({'comm':"",'maturity':"",'rate':""})
    rc_intermonth_list.append({'comm':"",'tiera':"",'tierb':"",'rate':""})
    rc_intercomm_list.append({'comma':"",'deltaa':"",'commb':"",'deltab':"",'rate':""})
        
    return rc_scan_list, rc_intermonth_list, rc_intercomm_list

# step 6
def calc_newscan(price_list,instrument_list,rc_scan_list):
    # append rc scan rate to price_list
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
            price['rc_scan_rate'] = 0.25 # if instrument is not specified in rc params, given stretch of 0.25 
        
    # assign price and rc_scan_range to all instruments incl options
    # instrument_list is now [commodity,type,maturity,settlement price decimal locator, 
    # contract value factor, price, rc scan range]
    for instrument in instrument_list:
        for price in price_list:
            # for futures, assign based on commodity, type, maturity
            if instrument['instype'] == "FUT":
                if instrument['comm'] == price['comm'] and instrument['instype'] == price['instype'] and instrument['maturity'] == price['maturity']:
                    try:
                        instrument['dspconv'] = (price['dsp']/10**price['dspdl'])*instrument['cvf']
                        instrument['rc_scan_range'] = (price['dsp']/10**price['dspdl'])*instrument['cvf']*price['rc_scan_rate']
                        break
                    except (ValueError,KeyError,TypeError):
                        pass
            # for options on futures, assign based on commodity, maturity- take underlying future
            elif instrument['instype'] == "OOF":
                if instrument['comm'] == price['comm'] and price['instype'] == "FUT" and instrument['maturity'] == price['maturity']:
                    try:
                        instrument['dspconv'] = (price['dsp']/10**price['dspdl'])*instrument['cvf']
                        instrument['rc_scan_range'] = (price['dsp']/10**price['dspdl'])*instrument['cvf']*price['rc_scan_rate']
                        break
                    except (ValueError,KeyError,TypeError):
                        pass
            # for options on physical, assign based on commodity- take underlying physical
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
    return price_list, instrument_list

# step 7
def calc_newintermonth(instrument_list,intermonth_param_list,intermonth_list,rc_intermonth_list):
    tier_list = [] #tier_list is [commodity, month tier]
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
        
    # instrument_list is now [commodity,type,maturity,settlement price decimal locator, 
    # contract value factor, price, rc scan range,month tier] 
    # eg ['SMP','OOF','201805',2,1,price, 465.59999,1]
    for instrument in instrument_list:
        for intermonth_param in intermonth_param_list:
            if instrument['comm'] == intermonth_param['comm']:
                if intermonth_param['tier1start'] <= instrument['maturity'] <= intermonth_param['tier1end']:
                    # if the instrument's maturity is within tier 1 months, then its in tier 1
                    instrument['tier'] = intermonth_param['tier1']
                    break
                elif intermonth_param['tier2start'] <= instrument['maturity'] <= intermonth_param['tier2end']:
                    # if the instrument's maturity is within tier 2 months, then its in tier 2
                    instrument['tier'] = intermonth_param['tier2']
                    break
                elif intermonth_param['tier3start'] <= instrument['maturity'] <= intermonth_param['tier3end']:
                    # if the instrument's maturity is within tier 3 months, then its in tier 3
                    instrument['tier'] = intermonth_param['tier3']
                    break
                elif intermonth_param['tier4start'] <= instrument['maturity'] <= intermonth_param['tier4end']:
                    # if the instrument's maturity is within tier 4 months, then its in tier 4
                    instrument['tier'] = intermonth_param['tier4']
                    break   
                # on expiry day, expiring contracts will not be included in intermonth
                else:
                    logging.info(str(instrument['comm']) + str(instrument['maturity']) + 
                        " was not considered in creating or applying intermonth spreads. This is expected on expiry day.")
                    instrument['tier'] = "NA"
    # tier_list is now [commodity, month tier, DSP sum, scan range sum, number of instruments]
    for tier in tier_list:
        pricesum = 0
        scansum = 0
        denominator = 0
        for instrument in instrument_list:           
            if tier['comm'] == instrument['comm'] and tier['tier'] == instrument['tier'] and instrument['instype'] != "OOF":
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

    # rc_intermonth_list is now [commodity, tier a, tier b, spread%, average DSP tier A + average DSP tier B] 
    for rc_intermonth in rc_intermonth_list:
        tierprice = 0
        for tier in tier_list:
            if tier['denominator'] != 0:
                if rc_intermonth['comm'] == tier['comm'] and rc_intermonth['tiera'] == tier['tier']: # average DSP tier A
                    tierprice += tier['pricesum']/tier['denominator']
                if rc_intermonth['comm'] == tier['comm'] and rc_intermonth['tierb'] == tier['tier']: # average DSP tier B
                    tierprice += tier['pricesum']/tier['denominator']
        rc_intermonth['tierprice'] = tierprice
        
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
            
    return tier_list, instrument_list, rc_intermonth_list, intermonth_list
        
# step 8
def calc_newintercomm(rc_intercomm_list,intercomm_list):
    """
    just take whats in rc_intercomm_list times 100. if not defined in rc_intercomm_list,
    take existing in intercomm
    """
    for intercomm in intercomm_list:
        # intercomm_list is now [commodity a, delta a, commodity b, delta b, spread, 
        # rc delta a, rc delta b, rc intercomm spread] 
        # eg ['WMP',20,'SMP',29,30,20,29,40] or if rc_intercomm_list doesn't include 
        # commodity a v b combo in same order then intercomm_list becomes ['WMP',20,'SMP',29,30,'NA']
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
    return intercomm_list
    
# step 9
def write_newinters(intermonth_list,intercomm_list,pa2_list):
    new_intermonth_list = []
    new_intercomm_list = []
    for pa2 in pa2_list:
        if pa2.startswith("C"):
            appendedmonth = False
            for intermonth in intermonth_list:
                if str(pa2[2:8]).strip() == intermonth['comm'] and int(pa2[23:25].strip() or 0) == intermonth['tiera'] and int(pa2[30:32].strip() or 0) == intermonth['tierb']:
                    monthstring1 = "Intermonth " + str(intermonth['comm']) + " " + str(intermonth['tiera']) + "v" + str(intermonth['tierb']) + " was " + str(int(pa2[14:21]))
                    monthstring2 = ""
                    if intermonth['rc_intermonth_spread'] == "NA":
                        new_intermonth_list.append(pa2)
                        appendedmonth = True
                        monthstring2 = ", no change"
                        logging.info(monthstring1+monthstring2)
                        break
                    elif intermonth['rc_intermonth_spread'] != "NA":
                        new_intermonth_list.append(pa2[:14] + str(int(intermonth['rc_intermonth_spread'])).rjust(7,'0') + pa2[21:])
                        appendedmonth = True
                        monthstring2 = ", now " + str(int(intermonth['rc_intermonth_spread']))
                        logging.info(monthstring1+monthstring2)
                        break
            if not appendedmonth:
            # should have already been taken out by NA condition above, but left here anyway
                new_intermonth_list.append(pa2)        
        if pa2.startswith("6"):
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
    return new_intermonth_list, new_intercomm_list

# step 10
def write_new_pa2(pa2_list,new_intermonth_list,new_intercomm_list,new_pa2_file):
    with open(new_pa2_file, "w") as f:
        for pa2 in pa2_list:
            if not pa2.startswith("C") and not pa2.startswith("6"):
                f.write(pa2)
        f.writelines(new_intermonth_list)
        f.writelines(new_intercomm_list)

# step 11
def write_whatif(instrument_list,whatif_file):  
    xml_list = []
    for instrument in instrument_list:
        try:
            xml_list.append(write_updatescan(instrument['comm'],instrument['instype'],instrument['maturity'],instrument['rc_scan_range']))
        except KeyError:
        # if there is no scan range available for whatever reason, leave out of whatif
            logging.error("This instrument has not been assigned a new scan range: " 
                + str(instrument['comm'])+str(instrument['instype'])+str(instrument['maturity']))
    
    with open(whatif_file, "w") as f:
        f.write("<scenarioFile>\n")
        for line in xml_list:
            f.write(line)
            f.write("\n")
        f.write("\n</scenarioFile>")

    def write_updatescan(commodity,scantype,maturity,newscan):
        return ''.join(("<updateRec>\n<ec>NZX</ec>\n<cc>",
            commodity,
            "</cc>\n<exch>NZX</exch>\n<pfCode>",
            commodity,
            "</pfCode>\n<pfType>",
            scantype,
            "</pfType>\n<sPe>",
            str(maturity),
            "</sPe>\n<ePe>",
            str(maturity),
            "</ePe>\n<updType>UPD_PRICE_RG</updType>\n<updMethod>UPD_SET</updMethod>\n<value>",
            "{:.2f}".format(newscan),
            "</value>\n</updateRec>",
            ))

# step 12
def read_position(position_file):
    position_list = []
    with open(position_file, "r") as f:
        position_list = f.readlines()
    return position_list

# step 13
def parse_position(position_list):
    record5_list = []
    bpins_list = []
    option_position_list = []
    bpacc_list = []
    sum_bpacc_list = []
    for position in position_list:
        if position.startswith("5"):
            # list of BP+instr,net position [BP+instr chunk,net position]
            record5_list.append({
            'bpins':str(position[1:4])+str(position[24:92]),
            'position':int(position[92:100].strip() or 0)
            })
            # list of BP+instr [BP+instr chunk]
            bpins_list.append({'bpins':str(position[1:4])+str(position[24:92])})
            # list of BP+acc [BP+acc chunk]
            bpacc_list.append({'bpacc':str(position[1:4])+str(position[4:24]).strip()})
            bpacc_list.append({'bpacc':str(position[1:4])+"Sum"})
            # list of BP,account,commodity,option on future/physical,call/put,maturity,strike,net position
            if str(position[45:48]) == "OOF" or str(position[45:48]) == "OOP":
                option_position_list.append({
                'bp':str(position[1:4]),
                'acc':str(position[4:24]).strip(),
                'comm':str(position[35:45]).strip(),
                'instype':str(position[45:48]),
                'callput':str(position[48:49]),
                'maturity':int(position[49:57].strip() or 0),
                'strikeconv':float(position[78:92].strip() or 0)/10000000,
                'position':int(position[92:100].strip() or 0)
                })
                
    # remove duplicates
    sum_bpins_list = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in bpins_list)]
    sum_bpacc_list_nocurr = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in bpacc_list)]
    
    # add records for NZD and USD in sum_bpacc_list
    for bpacc in sum_bpacc_list_nocurr:
        bpacc['curr'] = "USD"
        sum_bpacc_list.append(copy.deepcopy(bpacc))
        bpacc['curr'] = "NZD"
        sum_bpacc_list.append(copy.deepcopy(bpacc))     
        
    for bpins in sum_bpins_list:
        # add 0 to start with
        bpins['position'] = 0
        for record5 in record5_list:
            # iterate through record 5s and sum for same BP, instr combo
            if bpins['bpins'] == record5['bpins']:
                bpins['position'] = bpins['position'] + record5['position']
        # add the whole summed record into the options list too
        if str(bpins['bpins'][24:27]) == "OOF" or str(bpins['bpins'][24:27]) == "OOP":
            option_position_list.append({
            'bp':str(bpins['bpins'][0:3]),
            'acc':"Sum",
            'comm':str(bpins['bpins'][14:24]).strip(),
            'instype':str(bpins['bpins'][24:27]),
            'callput':str(bpins['bpins'][27:28]),
            'maturity':int(bpins['bpins'][48:56].strip() or 0),
            'strikeconv':float(bpins['bpins'][57:71].strip() or 0)/10000000,
            'position':bpins['position']
            })
    
    return sum_bpins_list, option_position_list, sum_bpacc_list

# step 14
def write_newposition(position_list,sum_bpins_list,sum_position_file):
    with open(sum_position_file, "w") as f:
        for position in position_list:
            f.write(position)
            if position.startswith("2"):
                f.write(position.strip()[:4]+"Sum".ljust(20," ")+position.strip()[24:]+"\n")
        for bpins in sum_bpins_list:
            f.write("5"+bpins['bpins'][:3]+"Sum".ljust(20," ")+bpins['bpins'][3:]+("-" if bpins['position'] < 0 else "0")+str(abs(bpins['position'])).rjust(7,"0")+"\n")
    return

# step 15
def write_margin_spanit(pa2_file,position_file,span_file,spanit_script,identifier):
    """Run this function for margin"""
    with open(spanit_script + identifier + ".txt", "w") as f:
        f.write("Load " + pa2_file + "\n")
        f.write("Load " + position_file + "\n") #position_file here = sum_position_file = position file with sum account for each bp
        f.write("Calc" + "\n")
        f.write("Save " + span_file + identifier + ".spn\n")
    return spanit_script

# step 16, 19
def call_span_calc(spanit_script, identifier):
    """Run this function using outputs from write_rc_spanit and write_margin_spanit"""
    os.chdir(r"C:\span4\bin")   #os.chdir = change current working directory path
    subprocess.call(["spanitrm.exe", spanit_script + identifier + ".txt"])

# step 17, 20
def call_span_report(span_file,pbreq_csv_file,identifier):
    """Run this function twice for margin and rc
    
    The input spn file must include params+positions
    """
    """
    DouglasC 16/08/2018: this function open spn file and generate pbreq.csv file
    """
    # Get reports for margins, rc with original position, rc with sum position
    # mshta must be given an absolute pathname, not a relative one
    # Also this process apparently does not work with filenames containing spaces...
    os.chdir(r"C:\span4\Reports")
    subprocess.call(["mshta.exe", r"C:\span4\rptmodule\spanReport.hta", span_file + identifier + ".spn"])
    
    # Convert spanReport.hta output [Link AP\C:\span4\Reports\PB Req Delim.txt] 
    # to [D:\span\rc\YYYYMMDD-hhmmss_pbreq_margin\rc.csv]
    pbreq_text_file = r"C:\Span4\Reports\PB Req Delim.txt"
    pbreq_csv_file_full = pbreq_csv_file + identifier + ".csv"
    in_text = csv.reader(open(pbreq_text_file,"r"), delimiter = ',')
    with open(pbreq_csv_file_full,"w") as outfile:
        out_csv = csv.writer(outfile)
        out_csv.writerows(in_text)

# step 18
def write_rc_spanit(new_pa2_file,whatif_file,position_file,span_file,spanit_script,identifier):
    """Run this function for rc"""
    with open(spanit_script + identifier + ".txt", "w") as f:
        f.write("Load " + new_pa2_file + "\n")
        f.write("Load " + position_file + "\n") #position_file here = sum_position_file = position file with sum account for each bp
        f.write("SelectPointInTime" + "\n")
        f.write("ApplyWhatIf " + whatif_file + "\n")
        f.write("CalcRiskArray" + "\n")
        f.write("Calc" + "\n")
        f.write("Save " + span_file + identifier + ".spn\n")
    
    return spanit_script

# step 21
def delta_adjust(option_list, deltascale_list, price_param_list, option_position_list, sum_bpacc_list, instrument_list):
    for option in option_list:
        appendeddelta = False
        for deltascale in deltascale_list:
            if option['comm'] == deltascale['comm'] and option['instype'] == deltascale['instype'] and option['maturity'] == deltascale['maturity']:
                # append the delta scaling factor to option_list
                # option_list is now [commodity,oof/oop,c/p,maturity,strike,delta,dsp]
                option['deltasf'] = deltascale['deltasf']
                appendeddelta = True
                break
        if not appendeddelta:
            option['deltasf'] = "NA"
            
        appendedparams = False
        for price_param in price_param_list:
            if option['comm'] == price_param['comm'] and option['instype'] == price_param['instype']:
                option.update({
                'dspdl':price_param['dspdl'], # append the settlement price decimal locator
                'strikedl':price_param['strikedl'], # append the strike price decimal locator
                'strikeconv':float(option['strike'])/10**price_param['strikedl'], # append the converted strike price
                'cvf':price_param['cvf'], # append the contract size
                'curr':price_param['curr'] # append the settlement currency of the contract
                })
                appendedparams = True
                break
        if not appendedparams:
            option.update({
            'dspdl':"NA",
            'strikedl':"NA",
            'strikeconv':"NA",
            'cvf':"NA",
            'curr':"NA",
            })
            
        appendeddsp = False
        for instrument in instrument_list:
            if option['comm'] == instrument['comm'] and option['instype'] == instrument['instype'] and option['maturity'] == instrument['maturity']:
                option['underlyingdspconv'] = instrument['dspconv']
                appendeddsp = True
                break
        if not appendeddsp:
            option['underlyingdspconv'] = "NA"
            
    for option_position in option_position_list:
        appended = False
        for option in option_list:
            if (    option_position['comm'] == option['comm'] and
                    option_position['maturity'] == option['maturity'] and
                    option_position['instype'] == option['instype'] and
                    option_position['strikeconv'] == option['strikeconv'] and
                    option_position['callput'] == option['callput']):
                option_position.update({
                'delta':float(option['delta'])/option['deltasf'], # margin delta. RC delta may be slightly diff. Use margin 
                'underlyingdspconv':option['underlyingdspconv'], # underlying dsp
                'dane':option_position['position']*(float(option['delta'])/option['deltasf'])*option['underlyingdspconv'], # net position * delta * underlying dsp
                'curr':(option['curr']) # append the settlement currency of the option
                })
                appended = True
                break
        if not appended:
            option_position.update({
            'delta':"NA",
            'underlyingdspconv':"NA",
            'dane':"NA",
            'curr':"NA"
            })
     
    for bpacc in sum_bpacc_list:
        dalovsov = float(0)
        for option_position in option_position_list:
            if bpacc['bpacc'].startswith(option_position['bp']) and bpacc['bpacc'].endswith(option_position['acc']) and bpacc['curr'] == option_position['curr']:
                # Sum so that BP and account matches to get delta adjusted net exposure 
                # for options only (delta adjusted long options value minus short options value)
                # per BP/account/currency
                dalovsov = dalovsov + option_position['dane']
        bpacc['dalovsov'] = dalovsov
    # Should print option_position_list to a file so can look back and check dane calcs?
    return option_position_list, sum_bpacc_list 

# step 22
def read_house(house_file):
    house_list = []
    with open(house_file,"r") as f:
        house_raw_list = list(csv.reader(f))
    for line in house_raw_list:
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
            
    return house_list

# step 23
def read_pbreqs(pbreq_csv_file):
    # Open two pbreqs with identifiers margin, rc
    pbreq_csv_file_full = pbreq_csv_file + "margin" + ".csv"
    with open(pbreq_csv_file_full,"r") as f:
        pbreq_margin = [{k: v for k,v in row.items()} for row in csv.DictReader(f)]
    
    pbreq_csv_file_full = pbreq_csv_file + "rc" + ".csv"
    with open(pbreq_csv_file_full,"r") as g:
        pbreq_rc = [{k: v for k,v in row.items()} for row in csv.DictReader(g)]

    # Take rows where (node = curReq and ec = NZX and isM = 1), (node = curVal and ec = NZX)
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
                'span':max(float(pbreq_margin['spanReq'])-float(pbreq_margin['anov']),0)
                })
            elif pbreq_margin['node'] == "curVal" and pbreq_margin['ec'] == "NZX":
                curval_list.append({
                'identifier':"margin",
                'bp':pbreq_margin['firm'],
                'acc':pbreq_margin['acct'],
                'curr':pbreq_margin['currency'],
                'lfvsfv':float(pbreq_margin['lfv'])-float(pbreq_margin['sfv'])
                }) # [identifier,bp,acc,currency,lfv-sfv]
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
                try:
                    curval_list.append({
                    'identifier':"rc",
                    'bp':pbreq_rc['firm'],
                    'acc':pbreq_rc['acct'],
                    'curr':pbreq_rc['currency'],
                    'lfvsfv':(float(pbreq_rc['lfv']) or 0)-float(pbreq_rc['sfv'])
                    })
                except:
                    pass
    # Merge curreq and curval
    pbreq_list = []
    for curreq in curreq_list:
        pbreq_list.append(copy.deepcopy(curreq)) # pbreq_list is curreq_list    

    for pbreq in pbreq_list:
        for curval in curval_list:
            if pbreq['identifier'] == curval['identifier'] and pbreq['bp'] == curval['bp'] and pbreq['acc'] == curval['acc'] and pbreq['curr'] == curval['curr']:
                pbreq['lfvsfv'] = curval['lfvsfv'] # pbreq_list is [identifier,bp,acc,currency,min(spanreq-anov,0),lfv-sfv]
    return pbreq_list

# step 24
def parse_rc(pbreq_list,sum_bpacc_list,house_list,currency_list):
    bp_list = []
    bp_final_list = []
    for bpacc in sum_bpacc_list:
        margin = float(0)
        sl = float(0) # stress losses
        lfvsfv = float(0)
        # Append all spanreq-anov from pbreq_list to sum_bpacc_list
        # sum_bpacc_list now [bp+acc,curr,lfo-sfo,lfv-sfv,rc,margin]
        for pbreq in pbreq_list:
            if bpacc['bpacc'].startswith(pbreq['bp']) and bpacc['bpacc'].endswith(pbreq['acc']) and bpacc['curr'] == pbreq['curr']: # Match BP and account and currency
                if pbreq['identifier'] == "rc":
                    sl = pbreq['span']
                    lfvsfv = pbreq['lfvsfv']
                elif pbreq['identifier'] == "margin":
                    margin = pbreq['span']
                    lfvsfv = pbreq['lfvsfv']
        bpacc.update({
        'lfvsfv':lfvsfv,
        'sl':sl,
        'margin':margin
        })
        # Append whether its a house/client account to sum_bpacc_list
        # sum_bpacc_list now [bp+acc,curr,lfo-sfo,lfv-sfv,rc,margin,house/client]
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
        # Grab just the BPs from sum_bpacc_list
        bp_list.append(bpacc['bpacc'][:3])
      
    # Remove duplicates of BPs
    bp_final_strings = list(set(bp_list))
    for line in bp_final_strings:
        bp_final_list.append({'bp':line})

    # Get USD:NZD from currency_list
    for curr in currency_list:
        if curr['curra'] == "USD" and curr['currb'] == "NZD":
            usdnzd = curr['rate']
            
    for bpacc in sum_bpacc_list:
        # Get dane by summing (lfv-sfv) + (lov-sov)
        bpacc['dane'] = bpacc['lfvsfv']+bpacc['dalovsov']
        # Get rc by taking uncovered losses minus margin
        bpacc['rc'] = max(bpacc['sl']-bpacc['margin'],0)
        # Convert USD to NZD
        if bpacc['curr'] == "USD":
            bpacc.update({
            'daneconv':bpacc['dane'] * usdnzd, # USD dane converted to NZD
            'rcconv': bpacc['rc'] * usdnzd, # USD rc converted to NZD
            'marginconv': bpacc['margin'] * usdnzd,
            'slconv': bpacc['sl'] * usdnzd
            })
        elif bpacc['curr'] == "NZD":
            bpacc.update({
            'daneconv':bpacc['dane'], # NZD dane, duplicate
            'rcconv': bpacc['rc'], # NZD rc, duplicate
            'marginconv': bpacc['margin'],
            'slconv': bpacc['sl']
            })
        # sum_bpacc_list now [bp+acc,curr,lfo-sfo,lfv-sfv,rc,margin,house/client,
        #                     dane unconverted,rc unconverted, dane converted, rc converted]
        
    # Append final rows using logic decided by Risk
    for bp in bp_final_list:
        longclient = {'daneconv':float(0),'rcconv':float(0)}
        shortclient = {'daneconv':float(0),'rcconv':float(0)}
        house = {'daneconv':float(0),'rcconv':float(0),'marginconv':float(0)}
        houseexist = False
        
        for bpacc in sum_bpacc_list:
            if bpacc['bpacc'].startswith(bp['bp']) and not bpacc['bpacc'].endswith("Sum"):
                if bpacc['acctype'] == "House" and bpacc['daneconv'] > 0:
                    house['daneconv'] += bpacc['daneconv'] # dane
                    house['rcconv'] += bpacc['rcconv'] # rc
                    house['marginconv'] += bpacc['marginconv'] #margin
                    houseexist = True
                elif bpacc['acctype'] == "Client" and bpacc['daneconv'] > 0:
                    longclient['daneconv'] += bpacc['daneconv'] # dane
                    longclient['rcconv'] += bpacc['rcconv'] # rc
                elif bpacc['acctype'] == "Client" and bpacc['daneconv'] < 0:
                    shortclient['daneconv'] += bpacc['daneconv'] # dane
                    shortclient['rcconv'] += bpacc['rcconv'] # rc
        
        if not houseexist:
            # if there is no house dane, take max of sum rc(of + dane clients) and sum rc( of - dane clients)
            shortrc = shortclient['rcconv']
            longrc = longclient['rcconv']    
        elif house['daneconv'] > 0:
            # house and opposing client(s) may be offset using house margin
            shortrc = -house['marginconv'] + shortclient['rcconv']
            longrc = house['rcconv'] + longclient['rcconv']
        elif house['daneconv'] < 0:
            # house and opposing client(s) may be offset using house margin
            shortrc = house['rcconv'] + shortclient['rcconv']
            longrc = -house['marginconv'] + longclient['rcconv']
        elif house['daneconv'] == 0:
            # unlikely but possible that there is house rc with dane = 0, but if so count on both sides
            shortrc = shortclient['rcconv'] + house['rcconv']
            longrc = longclient['rcconv'] + house['rcconv']
        else: # shouldn't reach here, but just in case
            longrc = shortrc = house['rcconv'] + longclient['rcconv'] + shortclient['rcconv']
        bp['rcconv'] = max(shortrc, longrc)
    
    # For final rc, take max of final rows in bp_final_list vs Sum in sum_bpacc_list
    for bp in bp_final_list:
        finalrc = float(0)
        sumsums = float(0)
        for bpacc in sum_bpacc_list:
            if bpacc['bpacc'].endswith("Sum") and bpacc['bpacc'].startswith(bp['bp']):
                sumsums = sumsums + bpacc['rcconv']
        finalrc = max(bp['rcconv'],sumsums)
        sum_bpacc_list.append({
        'bpacc':bp['bp']+"Rule",
        'acctype':"Rule",
        'curr':"NZD",
        'rcconv':bp['rcconv']
        })
        sum_bpacc_list.append({
        'bpacc':bp['bp']+"Final",
        'acctype':"Final",
        'curr':"NZD",
        'rcconv':finalrc
        })
    
    # Add BPIDs to sum_bpacc_list, if not specified in cons_house.csv, default to truncated BP
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
    
    return pbreq_list, sum_bpacc_list, bp_final_list

# step 25
def write_rc(sum_bpacc_list,final_file):
    with open(final_file, "w") as f:
        f.write("BPID,Account,Currency,Delta adjusted net exposure,Stress Losses,Margin,"
            "Intermediate RC,Delta adjusted net exposure (NZD),Stress Losses (NZD),"
            "Margin (NZD),Intermediate RC (NZD)\n")
        for bpacc in sum_bpacc_list:
            try:
                f.write(bpacc['bpid']+","
                    +bpacc['bpacc'][3:]+","
                    +str(bpacc['curr'])+","
                    +str(bpacc['dane'])+","
                    +str(bpacc['sl'])+","
                    +str(bpacc['margin'])+","
                    +str(bpacc['rc'])+","
                    +str(bpacc['daneconv'])+","
                    +str(bpacc['slconv'])+","
                    +str(bpacc['marginconv'])+","
                    +str(bpacc['rcconv'])+"\n")
            except KeyError:
                f.write(bpacc['bpid']+","
                    +bpacc['bpacc'][3:]+","
                    +str(bpacc['curr'])
                    +",,,,,,,,"
                    +str(bpacc['rcconv'])+"\n")

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
''' choose startDate and endDate '''
startD = datetime.datetime.strptime("01/07/2018","%d/%m/%Y")
endD = datetime.datetime.strptime("02/07/2018","%d/%m/%Y")
dates = [startD + datetime.timedelta(days=x) for x in range(0, (endD-startD).days)]


def main():
    for date in dates:
        yyyymmdd= date.strftime("%Y%m%d")
        print (yyyymmdd)

        # Make log
        hhmmss = write_log()     # no longer return yyyymmdd, hhmmss variable    # yyyymmdd, hhmmss = write_log()
        # Get filenames for today
        (pa2_file, position_file, new_pa2_file, sum_position_file,
            whatif_file, rc_intercomm_file, rc_intermonth_file, rc_scan_file,
            spanit_script, span_file, pbreq_csv_file, house_file, final_file) = find_current_files(yyyymmdd, hhmmss)
        # Get data from pa2
        pa2_list = read_pa2(pa2_file)
        (price_list, intermonth_list, intermonth_param_list, intercomm_list,
            intercomm_param_list, instrument_list, option_list, deltascale_list,
            price_param_list, currency_list) = parse_pa2(pa2_list)
        # Read rc params: 3 constant files
        rc_scan_list, rc_intermonth_list, rc_intercomm_list = read_rcparams(rc_scan_file,rc_intermonth_file,rc_intercomm_file)
        # Calculate stretched scans, intermonth, intercomm
        price_list, instrument_list = calc_newscan(price_list, instrument_list,rc_scan_list)
        tier_list, instrument_list, rc_intermonth_list, intermonth_list = calc_newintermonth(
            instrument_list, intermonth_param_list, intermonth_list, rc_intermonth_list)
        intercomm_list = calc_newintercomm(rc_intercomm_list, intercomm_list)
        new_intermonth_list, new_intercomm_list = write_newinters(intermonth_list,intercomm_list,pa2_list)
        # Write new pa2 file
        write_new_pa2(pa2_list,new_intermonth_list,new_intercomm_list,new_pa2_file)
        # Write whatif file which has scans adjusted
        write_whatif(instrument_list,whatif_file)
        # Read positions
        position_list = read_position(position_file)
        # Sum positions
        sum_bpins_list, option_position_list, sum_bpacc_list = parse_position(position_list)
        write_newposition(position_list,sum_bpins_list,sum_position_file)
        # Calc and get report for:
        # margin
        write_margin_spanit(pa2_file,sum_position_file,span_file,spanit_script,"margin")
        call_span_calc(spanit_script, "margin")
        call_span_report(span_file,pbreq_csv_file,"margin")
        # rc
        write_rc_spanit(new_pa2_file,whatif_file,sum_position_file,span_file,spanit_script,"rc")
        call_span_calc(spanit_script,"rc")
        call_span_report(span_file,pbreq_csv_file,"rc")
        # Calculate delta adjusted net exposure for options
        option_position_list, sum_bpacc_list = delta_adjust(option_list,
            deltascale_list, price_param_list, option_position_list, sum_bpacc_list, instrument_list)
        # Get list of house accounts
        house_list = read_house(house_file)
        # Grab data from pbreqs
        pbreq_list = read_pbreqs(pbreq_csv_file)
        # Parse pbreqs using dane criteria
        pbreq_list, sum_bpacc_list, bp_final_list = parse_rc(pbreq_list,sum_bpacc_list,house_list,currency_list)
        # Print final file
        write_rc(sum_bpacc_list,final_file)
        # Copy file to somewhere datacentral can see it
        if OUTPUT_DIR:
            shutil.copy(final_file, OUTPUT_DIR)
        # # Maybe email the log file
        # if LOGFILE_EMAIL:
        #     email_logfile(yyyymmdd, hhmmss)

    if __name__ == '__main__':
        main()

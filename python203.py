"""
re-create Risk Capital calculation script again for 21% stretch
"""

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
    intrument_list = []         # commodity, intrument type, maturity "yyyymm". Record B
    delta_scale_list = []       # commodity, instrument type, maturity, delta scaling factor. Record B
    option_list = []            # commodity, call/put, maturity, strike, delta, dsp. Record 82
    currency_list = []          # fx rate. Record T

    # 2.2.2. loop through each row in original_pa2 list, fill up data for each list above
    for line in original_pa2:
        # a. price list = list of prices [commodity, type, maturity, price]
        # eg ['WMP','FUT',201801,31200]
        if line.startswith("82") and (line[25:28] == "FUT" or line[25:28] == "PHY"):

### MAIN: calculate 21% rc ###
def Calculate_21_rc(input_dir, out_timestamp, pa2_pa2, position_txt, cons_rc_scan_csv, cons_rc_intermonth_csv, cons_rc_intercomm_csv, cons_house_csv):
    (pa2_pa2, position_txt, rc_intercomm_csv,rc_intermonth_csv, rc_scan_csv, house_csv, new_pa2, sum_position_txt,sum_position_rc_txt, whatif_xml, spanInstr_margin_txt, spanInstr_rc_txt, span_margin_spn, span_rc_spn, pbreq_margin_csv, pbreq_rc_csv, final_csv) = input_files(input_dir, out_timestamp, pa2_pa2, position_txt, cons_rc_scan_csv, cons_rc_intermonth_csv, cons_rc_intercomm_csv, cons_house_csv)

    (original_pa2) = read_pa2(pa2_pa2)

    parse_pa2(original_pa2)
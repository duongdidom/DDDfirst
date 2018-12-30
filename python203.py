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

    ### 1. define a bunch of newly created files
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


### MAIN ###
def Calculate_21_rc(input_dir, out_timestamp, pa2_pa2, position_txt, cons_rc_scan_csv, cons_rc_intermonth_csv, cons_rc_intercomm_csv, cons_house_csv):
    (pa2_pa2, position_txt, rc_intercomm_csv,rc_intermonth_csv, rc_scan_csv, house_csv, new_pa2, sum_position_txt,sum_position_rc_txt, whatif_xml, spanInstr_margin_txt, spanInstr_rc_txt, span_margin_spn, span_rc_spn, pbreq_margin_csv, pbreq_rc_csv, final_csv) = input_files(input_dir, out_timestamp, pa2_pa2, position_txt, cons_rc_scan_csv, cons_rc_intermonth_csv, cons_rc_intercomm_csv, cons_house_csv)

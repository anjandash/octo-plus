import os,sys,csv 
import pandas as pd 
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--xlfile", "-x", help="path to the excel sheet")
args = parser.parse_args()

df_map = pd.read_excel(args.xlfile, sheet_name=None)
sheets = list(df_map.keys())

df_one = pd.read_excel(args.xlfile, sheet_name=sheets[0]) 
df_ref = []
for i, sheet in enumerate(sheets):
    if i == 0:
        continue
    df_ref.append(pd.read_excel(args.xlfile, sheet_name=sheets[i]))

# df_one
cols = df_one.columns
cols = [item.lower() for item in cols]

if ('base' in cols) and ('rate' in cols) and ('fee' in cols):
    if ('period start' not in cols) and ('period end' not in cols):
        # if len columns is 3
        print("The formula is:")
        print("(base * rate) / 100")
        # demonstrate

    elif ('period start' in cols) and ('period end' in cols):
        print("The formula is:")
        print("(base * rate * get_diff(period end - period start) / 365) / 100")
        # demonstrate

elif ('base' in cols) and ('fee' in cols):
    for ref_sheet in df_ref:
        ref_cols = ref_sheet.columns
        ref_cols = [item.lower() for item in ref_cols]

        if 'rate' in ref_cols:
            # get rate from ref sheet

            if ('period start' in cols) and ('period end' in cols):
                if ('lower limit' in ref_cols) and ('upper limit' in ref_cols):

                    print("The formula is:")
                    print("(base * get_rate(base) * get_diff(period end - period start) / 365) / 100")
                    # demonstrate
                elif 'rate id' in cols:

                    print("The formula is:")
                    print("(base * get_rate(rate id) * get_diff(period end - period start) / 365) / 100")
                    # demonstrate
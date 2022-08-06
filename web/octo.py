import os,sys,csv 
import pandas as pd 
import argparse

from flask import flash, Markup


parser = argparse.ArgumentParser()
parser.add_argument("--xlfile", "-x", help="path to the excel sheet")
args = parser.parse_args()
xlfile = args.xlfile


def octo(xlfile):
    df_map = pd.read_excel(xlfile, sheet_name=None)
    sheets = list(df_map.keys())

    df_one = pd.read_excel(xlfile, sheet_name=sheets[0]) 
    df_ref = []

    m = []
    for i, sheet in enumerate(sheets):
        if i == 0:
            continue
        df_ref.append(pd.read_excel(xlfile, sheet_name=sheets[i]))

    # df_one
    cols = [item.lower() for item in df_one.columns]
    df_one.columns = cols

    if ('base' in cols) and ('rate' in cols) and ('fee' in cols):
        if ('period start' not in cols) and ('period end' not in cols):

            # ####################
            # checking all entries
            # ####################
            base_list = df_one["base"].tolist()
            rate_list = df_one["rate"].tolist()
            fee_list  = df_one["fee"].tolist()

            flash("Checking all data entries ... ")
            correct=0
            for base, rate, fee in zip(base_list, rate_list, fee_list):
                pred_fee = round(((float(base) * float(rate)) / 100), 2)
                orig_fee = float(fee)

                if orig_fee == pred_fee:
                    correct +=1
                elif (round(abs(orig_fee - pred_fee), 2)) < 0.02:
                    correct += 1
                
            if correct == len(fee_list):
                flash(Markup(f"<p class='mini'>100% of entries match!</p>"))
                flash(Markup("<p class='mini'>The formula is:</p>"))
                flash(Markup("<p class='formula'>(base * rate) / 100</p>"))
            else:
                flash(Markup(f"Only {correct / (len(fee_list))}% of entries matched!"))
                flash(Markup("Formula could not be generated: Try Octo+"))
            # ####################
            # ####################


        elif ('period start' in cols) and ('period end' in cols):

            # ####################
            # checking all entries
            # ####################
            base_list = df_one["base"].tolist()
            rate_list = df_one["rate"].tolist()
            fee_list  = df_one["fee"].tolist()

            df_one[['period start','period end']] = df_one[['period start','period end']].apply(pd.to_datetime) 
            df_one['days'] = (df_one['period end'] - df_one['period start']).dt.days
            days_list = df_one["days"].tolist()

            flash("Checking all data entries ... ")
            correct=0
            for base, rate, fee, days in zip(base_list, rate_list, fee_list, days_list):
                pred_fee = round(((float(base) * float(rate) * float(days) / 365) / 100), 2)
                orig_fee = float(fee)        

                if orig_fee == pred_fee:
                    correct +=1
                elif (round(abs(orig_fee - pred_fee), 2)) < 0.02:
                    correct += 1
                
            if correct == len(fee_list):
                flash(Markup(f"<p class='mini'>{100}% of entries match!</p>"))
                flash(Markup("<p class='mini'>The formula is:</p>"))
                flash(Markup("<p class='formula'>(base * rate * get_diff(period end - period start) / 365) / 100</p>"))
            else:
                flash(Markup(f"<p class='mini'>Only {correct / (len(fee_list))}% of entries matched!</p>"))
                flash(Markup("<p class='mini'>Formula could not be generated: Try Octo+</p>"))
            # ####################
            # ####################
            


    elif ('base' in cols) and ('fee' in cols):
        for ref_sheet in df_ref:
            ref_cols = [item.lower() for item in ref_sheet.columns]
            ref_sheet.columns = ref_cols

            if 'rate' in ref_cols:
                # get rate from ref sheet

                if ('period start' in cols) and ('period end' in cols):
                    if ('lower limit' in ref_cols) and ('upper limit' in ref_cols):

                        # ####################
                        # checking all entries
                        # ####################
                        base_list = df_one["base"].tolist()
                        fee_list  = df_one["fee"].tolist()

                        df_one["minbound"] = df_one['base'].apply(lambda row: (int(row) - int(row)%1000))   
                        rate_list = [(ref_sheet[ref_sheet["lower limit"] == item]).iloc[0]["rate"] for item in df_one["minbound"].tolist()]    

                        df_one[['period start','period end']] = df_one[['period start','period end']].apply(pd.to_datetime) 
                        df_one['days'] = (df_one['period end'] - df_one['period start']).dt.days
                        days_list = df_one["days"].tolist()       

                        flash("Checking all data entries ... ")
                        correct=0
                        for base, rate, fee, days in zip(base_list, rate_list, fee_list, days_list):
                            pred_fee = round(((float(base) * float(rate) * float(days) / 365) / 100), 2)
                            orig_fee = float(fee)        

                            if orig_fee == pred_fee:
                                correct +=1
                            elif (round(abs(orig_fee - pred_fee), 2)) < 0.02:
                                correct += 1
                            
                        if correct == len(fee_list):
                            flash(Markup(f"<p class='mini'>{100}% of entries match!</p>"))
                            flash(Markup("<p class='mini'>The formula is:</p>"))
                            flash(Markup("<p class='formula'>(base * get_rate(base) * get_diff(period end - period start) / 365) / 100</p>"))  
                        else:
                            flash(Markup(f"<p class='mini'>Only {correct / (len(fee_list))}% of entries matched!</p>"))
                            flash(Markup("<p class='mini'>Formula could not be generated: Try Octo+</p>"))
                        # ####################
                        # ####################                  

                    elif 'rate id' in cols:
                        
                        # ####################
                        # checking all entries
                        # ####################
                        base_list = df_one["base"].tolist()
                        rate_list = [(ref_sheet[ref_sheet["id"] == rate_id]).iloc[0]["rate"] for rate_id in df_one["rate id"].tolist()]
                        fee_list  = df_one["fee"].tolist()

                        df_one[['period start','period end']] = df_one[['period start','period end']].apply(pd.to_datetime) 
                        df_one['days'] = (df_one['period end'] - df_one['period start']).dt.days
                        days_list = df_one["days"].tolist()       

                        flash("Checking all data entries ... ")
                        correct=0
                        for base, rate, fee, days in zip(base_list, rate_list, fee_list, days_list):
                            pred_fee = round(((float(base) * float(rate) * float(days) / 365) / 100), 2)
                            orig_fee = float(fee)        

                            if orig_fee == pred_fee:
                                correct +=1
                            elif (round(abs(orig_fee - pred_fee), 2)) < 0.02:
                                correct += 1
                            
                        if correct == len(fee_list):
                            flash(Markup(f"<p class='mini'>{100}% of entries match!</p>"))
                            flash(Markup("<p class='mini'>The formula is:</p>"))
                            flash(Markup("<p class='formula'>(base * get_rate(rate id) * get_diff(period end - period start) / 365) / 100</p>"))
                        else:
                            flash(Markup(f"<p class='mini'>Only {correct / (len(fee_list))}% of entries matched!</p>"))
                            flash(Markup("<p class='mini'>Formula could not be generated: Try Octo+</p>"))
                        # ####################
                        # ####################     
    return "\n".join(m)

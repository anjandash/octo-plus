import os,sys,csv 
import pandas as pd 
import numpy as np
import argparse
import matplotlib.pyplot as plt

from flask import flash, Markup
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LassoCV, Lasso, LinearRegression, RidgeCV, Ridge
from joblib import parallel_backend


parser = argparse.ArgumentParser()
parser.add_argument("--xlfile", "-x", help="path to the excel sheet")
args = parser.parse_args()
xlfile = args.xlfile

simple_path = sys.path[0] + "/../csv/simple.xlsx_Data.csv"
period_path = sys.path[0] + "/../csv/period.xlsx_Data.DIFF.csv"
lookup_path = sys.path[0] + "/../csv/reference.xlxs_Data.DIFF.csv"
reference_path = sys.path[0] + "/../csv/reference.xlxs_Data.DIFF.csv"

def get_coeff(csv_path):
    s=pd.read_csv(csv_path, header=0)
    y=s['fee']
    X=s[['base','rate','days']] if 'days' in s.columns else s[['base','rate']]

    pol = PolynomialFeatures(degree=3)
    X_pol = pol.fit_transform(X)
    lassocv1 = LassoCV(cv=5, random_state=0, normalize=True).fit(X_pol, y)
    lasso1 = Lasso(alpha=lassocv1.alpha_, normalize=True)
    lasso1.fit(X_pol, y)
    coeffs1 = lasso1.coef_

    index_list=[]
    for i in range(len(lasso1.coef_)):
        if abs(lasso1.coef_[i])!=0:
            index_list.append(i)

    coeffs_arr = [coeffs1[index] for index in index_list]
    coeffs_arr = [float(item) for item in coeffs_arr]
    coeffs = np.prod(coeffs_arr)

    flash_value = f"Coeff: {round(coeffs, 5)}"
    flash(flash_value)
    return coeffs


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

    # #######################
    # rule-based verification
    # #######################
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
            coeff_simple = get_coeff(simple_path)
            for base, rate, fee in zip(base_list, rate_list, fee_list):
                pred_fee = round(((float(base) * float(rate)) / 100), 2) # * coeff_simple
                #pred_fee = round(((float(base) * float(rate)) * coeff_simple), 2) # * coeff_simple
                orig_fee = float(fee)

                if orig_fee == pred_fee:
                    correct +=1
                elif (round(abs(orig_fee - pred_fee), 2)) < 0.02:
                    correct += 1
                
            if correct == len(fee_list):
                flash(Markup(f"<p class='mini1'>Validated!</p>"))
                flash(Markup("<p class='mini2'>The formula is:</p>"))
                flash(Markup("<p class='formula'>(base * rate) / 100</p>"))
            else:
                flash(Markup(f"<p class='mini1'>Only {correct / (len(fee_list))}% of entries matched!</p>"))
                flash(Markup("<p class='mini2'>Formula could not be generated: Try Octo+</p>"))
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
            coeff_period = get_coeff(period_path)
            for base, rate, fee, days in zip(base_list, rate_list, fee_list, days_list):
                pred_fee = round(((float(base) * float(rate) * float(days) / 365) / 100), 2) # * coeff_period
                #pred_fee = round(((float(base) * float(rate) * float(days) * coeff_period) ), 2) # * coeff_period
                orig_fee = float(fee)        

                if orig_fee == pred_fee:
                    correct +=1
                elif (round(abs(orig_fee - pred_fee), 2)) < 0.02:
                    correct += 1
                
            if correct == len(fee_list):
                flash(Markup(f"<p class='mini1'>Validated!</p>"))
                flash(Markup("<p class='mini2'>The formula is:</p>"))
                flash(Markup("<p class='formula'>(base * rate * get_diff(period end - period start) / 365) / 100</p>"))
            else:
                flash(Markup(f"<p class='mini1'>Only {correct / (len(fee_list))}% of entries matched!</p>"))
                flash(Markup("<p class='mini2'>Formula could not be generated: Try Octo+</p>"))
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
                        coeff_lookup = get_coeff(lookup_path)
                        for base, rate, fee, days in zip(base_list, rate_list, fee_list, days_list):
                            pred_fee = round(((float(base) * float(rate) * float(days) / 365) / 100), 2) # * coeff_lookup
                            #pred_fee = round(((float(base) * float(rate) * float(days) * coeff_lookup) ), 2) # * coeff_lookup
                            orig_fee = float(fee)        

                            if orig_fee == pred_fee:
                                correct +=1
                            elif (round(abs(orig_fee - pred_fee), 2)) < 0.02:
                                correct += 1
                            
                        if correct == len(fee_list):
                            flash(Markup(f"<p class='mini1'>Validated!</p>"))
                            flash(Markup("<p class='mini2'>The formula is:</p>"))
                            flash(Markup("<p class='formula'>(base * get_rate(base) * get_diff(period end - period start) / 365) / 100</p>"))  
                        else:
                            flash(Markup(f"<p class='mini1'>Only {correct / (len(fee_list))}% of entries matched!</p>"))
                            flash(Markup("<p class='mini2'>Formula could not be generated: Try Octo+</p>"))
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
                        coeff_reference = get_coeff(reference_path)
                        for base, rate, fee, days in zip(base_list, rate_list, fee_list, days_list):
                            pred_fee = round(((float(base) * float(rate) * float(days) / 365) / 100), 2) # * coeff_reference
                            #pred_fee = round(((float(base) * float(rate) * float(days) * coeff_reference) ), 2) # * coeff_reference
                            orig_fee = float(fee)        

                            if orig_fee == pred_fee:
                                correct +=1
                            elif (round(abs(orig_fee - pred_fee), 2)) < 0.02:
                                correct += 1
                            
                        if correct == len(fee_list):
                            flash(Markup(f"<p class='mini1'>Validated!</p>"))
                            flash(Markup("<p class='mini2'>The formula is:</p>"))
                            flash(Markup("<p class='formula'>(base * get_rate(rate id) * get_diff(period end - period start) / 365) / 100</p>"))
                        else:
                            flash(Markup(f"<p class='mini1'>Only {correct / (len(fee_list))}% of entries matched!</p>"))
                            flash(Markup("<p class='mini2'>Formula could not be generated: Try Octo+</p>"))
                        # ####################
                        # ####################     
    return "\n".join(m)

# from modalsplit import modalsplit
# from nationstatemodalsplit import nationstatemodalsplit

import pandas as pd
import os
from datetime import datetime
import numpy as np

year_int = datetime.now().year - 2
##
# BUILD DIRECTORIES ON Z TO HOLD CSV FILES
##
'''print('  Building directory structure on Z:\...'),  # add a line to handle exceptions?
#acs_year = str(year_int - 4) + 'to' + str(year_int)[-2:]
base_dir = "Z:/fullerm/CMP/" + datetime.now().strftime('%Y%m%d%H%M') + '\\' + str(year_int)
# Create base directory if it doesn't exist
if not os.path.exists(base_dir):
    os.makedirs(base_dir)'''

def nationstatemodalsplittoexcel(base_dir,df, writer):


    # df = pd.DataFrame()
    # df = df.append(nationstatemodalsplit())
    #df = df.append(mi_sd())
    df.set_index('NAME',inplace=True)
    df = df.apply(pd.to_numeric, errors='ignore') # why this?
    #df['Drive Alone Percent'] = df['B08301_001E']




    #df = df.append(df.sum(numeric_only=True), ignore_index=True)

    # row_sum = df[df.columns.values.tolist()].sum()
    # print(row_sum)
    # row_sum = row_sum.rename(columns={'0':'Number of Trips'}) # Number of Trips might actually be number of people
    # row_sum_t = pd.DataFrame(data=row_sum).T
    # row_sum_t = row_sum_t.rename(index={0: "Number of Trips"})
    # new data frame with only relevant columns for modal split data
    new_df = df[['B08301_001E','B08301_003E','B08301_004E','B08301_011E','B08301_016E','B08301_017E','B08301_018E',
    'B08301_019E','B08301_020E','B08301_021E']]

    # df = df.append(row_sum_t)



    # writer = pd.ExcelWriter(os.path.join(base_dir, 'modalsplit.xlsx'), engine= 'xlsxwriter')
    #csv_path =
    #df.to_excel()
    new_df = new_df.T.rename(index={'B08301_001E':'All Modes','B08301_003E':'Drive Alone','B08301_004E':'Carpool','B08301_011E':'Bus',
                           'B08301_016E':'Taxi','B08301_017E':'Motorcycle','B08301_018E':'Bicycle','B08301_019E':'Walk',
                           'B08301_020E':'Other','B08301_021E':'Work at Home'})
    new_df['National Percent'] = new_df['United States']/new_df.loc['All Modes','United States']
    new_df['State Percent'] = new_df['Ohio']/new_df.loc['All Modes','Ohio']
    # new_df = new_df.round({'National Percent':2, 'State Percent':2})
    new_df.index.name = 'Commuting to Work'
    # new_df.sort_values('Number of Trips',ascending=False,inplace=True)

    # this line includes only the columns listed and slices off the row containing 'All Modes' 100% to match
    # the format of the table in the most recent report
    new_df[['State Percent','National Percent']][1:].to_excel(writer, 'Sheet2')
    wrkbk = writer.book
    wrksht = writer.sheets['Sheet2']
    percent_fmt = wrkbk.add_format({'align': 'right', 'num_format': '0.0%'})
    wrksht.set_column('B:C', 12, percent_fmt)
    # chrt = wrkbk.add_chart({'type':'pie'})
    '''chrt.add_series({'categories':['Sheet1',2,0, len(new_df),0],
                     'values': ['Sheet1',2,2,len(new_df),2],
                     'data_labels': {'percentage':True},
                     })'''
    # chrt.set_title({'name':'2015 5-year ACS Means of Transportation to Work for Ohio and U.S.'})
    # wrksht.insert_chart('E2',chrt)
    #new_df
    # writer.save()
if __name__ == '__main__':
    nationstatemodalsplittoexcel("Z:/fullerm/CMP/" + datetime.now().strftime('%Y%m%d%H%M') + '\\' + str(year_int))
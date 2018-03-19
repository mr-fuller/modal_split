from traveltimebymode import traveltimebymode
from mi_sd import mi_sd
import pandas as pd
import os
from datetime import datetime
import numpy as np

def traveltimetoexcel():

    year_int = datetime.now().year - 2
    ##
    # BUILD DIRECTORIES ON Z TO HOLD CSV FILES
    ##
    print('  Building directory structure on Z:\...'),  # add a line to handle exceptions?
    #acs_year = str(year_int - 4) + 'to' + str(year_int)[-2:]
    base_dir = "Z:/fullerm/CMP/" + datetime.now().strftime('%Y%m%d%H%M') + '\\' + str(year_int)
    # Create base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    df = pd.DataFrame()
    df = df.append(traveltimebymode())
    #df = df.append(mi_sd())
    df.set_index('NAME',inplace=True)
    #print(df)
    df = df.apply(pd.to_numeric, errors='ignore') # why this? data written as strings, so sums were just concatenations
    #df['Drive Alone Percent'] = df['B08301_001E']




    #df = df.append(df.sum(numeric_only=True), ignore_index=True)

    row_sum = df[df.columns.values.tolist()].sum()
    print(row_sum)
    row_sum = row_sum.rename(columns={'0':'Number of Trips'}) # Number of Trips might actually be number of people
    row_sum_t = pd.DataFrame(data=row_sum).T
    row_sum_t = row_sum_t.rename(index={0: "Number of Trips"})
    # new data frame with only relevant columns for modal split data
    new_df = row_sum_t[['S0802_C01_090E',  # total/all modes
                        'S0802_C02_090E',  # drive alone
                        'S0802_C03_090E',  # carpool
                        'S0802_C04_090E'  # public transportation
                        # 2015 ACS doesn't appear to have data for other modes
                        ]]

    df = df.append(row_sum_t)
    #print(df)


    writer = pd.ExcelWriter(os.path.join(base_dir, 'traveltime.xlsx'), engine= 'xlsxwriter')
    #csv_path =
    #df.to_excel()
    new_df = new_df.T.rename(index={'S0802_C01_090E':'All Modes','S0802_C02_090E':'Drove Alone','S0802_C03_090E':'Carpooled',
                                    'S0802_C04_090E':'Public Transportation',
                           })
    # new_df['Percent of Total'] = new_df['Number of Trips']/new_df.loc['All Modes','Number of Trips']
    # new_df = new_df.round({'Percent of Total':2})
    new_df.index.name = 'Mode'
    new_df.sort_values('Number of Trips',ascending=False,inplace=True)
    new_df.to_excel(writer, 'Sheet1')
    df=df[['S0802_C01_090E',  # total/all modes
                        'S0802_C02_090E','S0802_C02_001E',  # drive alone
                        'S0802_C03_090E', 'S0802_C03_001E',  # carpool
                        'S0802_C04_090E',  'S0802_C04_001E'# public transportation
                        # 2015 ACS doesn't appear to have data for other modes
                        ]]
    df = df.rename(columns={'S0802_C01_090E':'All Modes',
                            'S0802_C02_001E': 'Drove Alone People',
                            'S0802_C02_090E':'Drove Alone Time',
                            'S0802_C03_001E': 'People Carpooled',
                            'S0802_C03_090E':'Carpooled',
                            'S0802_C04_001E':'People Public Transportation',
                            'S0802_C04_090E':'Public Transportation',
                           })
    df.index.name = "Mean Travel Time (minutes)"
    df.to_excel(writer,'Sheet2')
    wrkbk = writer.book
    wrksht = writer.sheets['Sheet1']
    percent_fmt = wrkbk.add_format({'align': 'right', 'num_format': '0.00%'})
    wrksht.set_column('C:C', 12, percent_fmt)
    chrt = wrkbk.add_chart({'type':'column'})
    chrt.add_series({'categories':['Sheet1',1,0, len(new_df),0],
                     'values': ['Sheet1',1,1,len(new_df),1],
                     # 'data_labels': {'percentage':True},
                     })
    chrt.set_title({'name':str(year_int) + ' 5-year ACS Average Travel Time by Mode'})
    chrt.set_x_axis({'name':'Mode of Transportation'})
    chrt.set_y_axis({'name':'Time(Minutes)'})
    wrksht.insert_chart('E2',chrt)
    #new_df
    writer.save()

if __name__ == '__main__':
    traveltimetoexcel()
# this script will grab average travel time by mode for all modes, drive alone, carpool, public transportation, and
# taxi/motorcycle/bicycle/other means

import requests
import pandas
import os
import pandas as pd


from datetime import datetime
start_time = datetime.now()
api_key = 'b7da053b9e664586b9e559dba9e73780602f0aab'  # CGR's API key

fips = {
    #'Fulton': '39051',
    #'Hancock': '39063',
    #'Henry': '39069',
    'Lucas': '39095',
    #'Ottawa': '39123',
    #'Putnam': '3937',
    #'Sandusky': '39143',
    #'Seneca': '39147',
    'Wood': '39173',
    #'Lenawee': '26091',
    #'Monroe': '26115'
    'Bedford': '06740',
    'Erie':'26320',
    'Luna Pier':'49700',
    'Whiteford':'86740'
}
mi_fips = {
    'Bedford': '06740',
    'Erie':'26320',
    'Luna Pier':'49700',
    'Whiteford':'86740'
}


variable_list = ['S0802'  # The table number for means of transportation to work data
     #'S0802_C01_090E',  # total/all modes
     #'S0802_C02_090E',  # drive alone
     #'S0802_C03_090E',  # carpool
     #'S0802_C04_090E',
  ]


counties = ['Lucas', 'Wood'
            ,'Bedford','Erie','Luna Pier','Whiteford'
]
api_pull = {}
for x in range(0, len(counties)):
    api_pull[counties[x]] = variable_list

def traveltimebymode():
    # this function pulls a ACS 5-year data from Census API, formats it, and creates a chart of modal split data for
    # counties in OH portion of TMACOG
    year_int = int(datetime.now().year) - 2
    print(year_int)
    ##
    # BUILD DIRECTORIES ON Z TO HOLD CSV FILES
    ##
    print('  Building directory structure on Z:\...'),  # add a line to handle exceptions?
    #acs_year = str(year_int - 4) + 'to' + str(year_int)[-2:]
    base_dir = "Z:/fullerm/CMP/" + str(year_int)
    # Create base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    # Create subdirectories if they don't exist
    '''for geo in api_pull:
        directory = base_dir + '\\' + geo
        if not os.path.exists(directory):
            os.makedirs(directory)
    print('\bDone')'''

    ##
    # PULLING THE VARIABLE LIST FROM API
    ##

    # Now that we know what year of data the user wants we need to pull the
    # variable list.

    print('  Pulling JSON variable list...'),
    # Build the API URL
    variables_url = 'http://api.census.gov/data/' + str(year_int) + '/acs/acs5/subject/variables.json'
    # Read in the data
    data = requests.get(url=variables_url)
    # Check to make sure we could pull variables
    if data.status_code == 404:

        print('\bFailed')
        import sys
        sys.exit('You entered an invalid ACS year.  Please try again.')
    else:
        data = data.json()
        print('\bDone')

    ##
    # BUILDING ACS TABLE VARIABLE LIST DICTIONARY
    ##

    # We now will iterate through the data and build a dictionary that has all
    # the variables associated with the table.

    print('  Building table list...'),
    table_list = list()  # This will hold all the tables. also, []
    acs_dict = dict()  # This will hold the variables by table. also, {}
    # Iterate through the variables
    for variable in data['variables']:
        s = variable.split('_')  # Break the string apart by the underscore.
        table = s[0]  # This is the table name.

        if not table in table_list:
            table_list.append(table)  # Add it to the table list
            var_list = list()  # Create an empty list for the acs_dict
            var_list.append(variable)  # Put the variable name in the list
            acs_dict[table] = var_list  # Add the variable list to the dictionary
        else:
            var_list = acs_dict[table]  # Pull the existing variable list
            var_list.append(variable)  # Add in the new variable
            var_list.sort()  # Sort it (so the estimates are followed by the MOE)
            acs_dict[table] = var_list  # Replace the list with the updated one
    print('\bDone')

    # Now that this has been complete we can call acs_dict['B10001'] to get all
    # the variables in the table

    ##
    # DOWNLOAD ACS DATA
    ##

    def download_and_save_data(acs_dict, fips, location, api_key, api_url_base, base_dir, table):
        # Since there is a 50 variable maximum we need to see how many calls
        # to the API we need to make to get all the variables.
        api_calls_needed = (len(acs_dict[table]) // 49) + 1
        api_calls_done = 0
        variable_range = 49
        while api_calls_done < api_calls_needed:
            get_string = ''
            print('        API Call Set ' + str(api_calls_done + 1) + ' of ' + str(api_calls_needed))
            variable_range_start = variable_range * api_calls_done
            variable_range_end = variable_range_start + variable_range
            for variable in acs_dict[table][variable_range_start:variable_range_end]:
                get_string = get_string + ',' + variable
            # can I just handle the different geography levels/types with and if statement?
            if location == 'Lucas' or location == 'Wood':
                api_url = api_url_base + get_string + '&for=county:' + fips[location][2:]+'&in=state:' + fips[location][:2]\
                      + '&key=' + api_key
            else:
                api_url = api_url_base + get_string + '&for=county+subdivision:' + fips[location] + \
                          '&in=state:26&in=county:115&key=' + api_key
            data = pandas.io.json.read_json(api_url)
            #print(data)
            data.columns = data[:1].values.tolist()  # Rename columns based on first row
            #county_data['Geocode'] = county_data['state'] + county_data['county'] + tract_data['tract']
            data = data[1:]  # Drop first row

            data = data.drop(['state','county'], axis=1) # drop this column to fix valueError('Plan shapes are not aligned')? Yes!
            if location == 'Bedford' or location == 'Whiteford' or location == 'Luna Pier' or location == 'Erie':
                data = data.drop(['county subdivision'],axis=1) # drop this column to fix valueError('Plan shapes are not aligned')? Yes!
            #print(data)
            temp_t = data
            # Add columns if the final data frame is created
            if api_calls_done == 0:
                data_t = temp_t

            else:
                data_t = pandas.concat([data_t, temp_t], axis=1,)
            #print(data_t)
            api_calls_done += 1
        #data = pandas.concat([geocode_t, name_t, data_t], axis=1)
        name_t = data_t['NAME']
        if isinstance(name_t, pd.Series):
            name_t = pandas.DataFrame(name_t, columns=['NAME'])
        else:
            name_t = name_t.iloc[:, 0]  # this should return the first column
        data_t = data_t.drop(['NAME'], axis=1)
        data_t = pd.concat([name_t,data_t], axis=1)
        # print(len(data_t['NAME']), data_t['NAME'])
        return data_t


    api_url_base = 'https://api.census.gov/data/' + str(year_int) + '/acs/acs5/subject?get=NAME'
    df = pandas.DataFrame()
    for location in api_pull:
        for table in api_pull[location]:
            df = df.append(download_and_save_data(acs_dict, fips, location, api_key, api_url_base, base_dir, table))
        #mi = download_and_save_data(acs_dict, mi_fips, location, api_key, api_url_base, base_dir, table)

    '''writer = pd.ExcelWriter(os.path.join(base_dir, 'cmp.xlsx'))
    #csv_path =
    #df.to_excel()
    df.to_excel(writer, 'Sheet1', index= False)
    writer.save()'''
    return df
if __name__ == "__main__":
    traveltimebymode()
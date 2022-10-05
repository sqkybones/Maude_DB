# ~Inputs for the Query~
# Product Code = ['results']['device']['device_report_product_code']
    # EX: search=device.device_report_product_code:"FOO+BAR" (searches for if FOO or BAR appear)
# Date Range = date_received:[20130101+TO+20141231] (Jan 01, 2013 and Dec 31, 2014)
# manufacuter = ['results']['device']['manufacturer_d_name'] device.manufacturer_d_name:"FOO+BAR"

# ~Required Outputs~
# Date Report Recieved by FDA = 'date_received'
# Model number = ['results']['device']['model_number']
# Report Number = ['results']['report_number']
# Event Type = ['results']['event_type']
# Manufacturer = 
# Event Text


#Just getting the stuff that I need
from dataclasses import dataclass
from IPython.display import display
import json
import requests
import csv
import pandas as pd
import math
import datetime

#Temporarily dispable user input for dubugging purposes
# start_date = input("Please enter in your start date formatted as year-month-day i.e. Dec 31, 2014 would be 2014-12-31 ")
# end_date = input("Now enter your end date following the same formatat: i.e. Dec 31, 2014 would be 2014-12-31 ")

start_date = '2009-01-01'
end_date = '2022-09-29'

# making dataframe for user input
df = pd.read_csv('data.csv')

# Turning pd columns into lists. Note that these column headers need to stay constant.
prodc = df['product_code'].tolist()
mfr = df['manufacturer'].tolist()

# Creating function 'isnan' to determine if there are nan values.. for some reason using nan from math directly did not work. 
def isnan(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False

# Taking out the NaNs
prodc_clean = [x for x in prodc if isnan(x) == False]
mfr_clean = [x for x in mfr if isnan(x) == False]
print(prodc_clean)
print(mfr_clean)

# laying out strings to build our query list
prodc_string_1 = 'device.device_report_product_code:"'
prodc_string_2 = '"'
mfr_string_1 = 'device.manufacturer_d_name:"'
mfr_string_2 = '"'

# creating the query list
prodc_qry_list = [prodc_string_1 + s + prodc_string_2 for s in prodc_clean]
mfr_qry_list = [mfr_string_1 + s + mfr_string_2 for s in mfr_clean]

# Turning the Query lists into strings
def convert_list_to_string(org_list, seperator=' '):
    """ Convert list to string, by joining all item in list with given separator.
        Returns the concatenated string """
    return seperator.join(org_list)

# Join all the strings in list
prodc_qry = convert_list_to_string(prodc_qry_list, '+')
# print(prodc_qry)
mfr_qry = convert_list_to_string(mfr_qry_list, '+')
# print(mfr_qry)
final_qry = f"https://api.fda.gov/device/event.json?search=({prodc_qry})+AND+({mfr_qry})+AND+date_received:[{start_date}+TO+{end_date}]&limit=1000"
print(final_qry)

# Calling the FDA API
response = requests.get(final_qry)

#Did I get a good response? If so I should print "200"
print(response.status_code)

#Converting to dict
maude_data = response.json()

# Creating a dictionary specifically for results
result = maude_data['results'][0]

#Initiating the report list
reportid_list = []

#Iterating through the subsection in maude 'results' to grab the information I need
for result in maude_data['results']:
    reportid_list.append([result.get('report_number', "x"), result.get('date_received', "x"), result['device'][0].get('manufacturer_d_name', "x"), result['device'][0].get('device_report_product_code', "x"), result.get('product_problems', "x")])

# Turning the info from the sliced json into a viewable df
reportid_df = pd.DataFrame(data=reportid_list, columns=['Report Number', 'Date Received', 'Manufacturer Name', 'Device Product Code', 'Product Problem'])
df2 = reportid_df.explode('Product Problem')

#Seperating out the List into new rows for every instance of a list item in 'Product Problem'
df2['Product Problem'] = df2['Product Problem'].apply(lambda x: [x])

#Getting rid of the brackets in the list column (grabbing the first element in the list and making it a string?)
df2['Product Problem'] = df2['Product Problem'].str[0]

print(df2)

# if I wanted to split the list into seperate columns with nans
# split_df = pd.DataFrame(reportid_df['Product Problem'].tolist())
# If I ever wanted to combine by columns
# combinded_df = pd.concat([reportid_df, split_df], axis=1)

#Adding the current date and time to the file 
now = datetime.datetime.now()
now_formatted = now.strftime("%Y-%m-%d %H.%M.%S")
file_name = f"report{now_formatted}.csv"

# Save the df to a csv
df2.to_csv(file_name)
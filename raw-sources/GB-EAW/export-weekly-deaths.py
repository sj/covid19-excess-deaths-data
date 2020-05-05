#!/usr/bin/python3
import pandas as pd
import datetime
import os
import sys
import string

metadata_data_source = "Office of National Statistics under Open Government License (https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/datasets/weeklyprovisionalfiguresondeathsregisteredinenglandandwales)"
scriptname = os.path.basename(__file__)
scriptdir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

# There's an XLSX file for every year. The one for 2020 will be updated regularly.

xlsx_file_2020 = ""
for direntry in os.listdir(os.path.dirname(os.path.abspath(__file__))):
    if os.path.isfile(direntry) and direntry.startswith("publishedweek") and direntry.endswith("2020.xlsx") and direntry > xlsx_file_2020:
        xlsx_file_2020 = direntry

if xlsx_file_2020 == "":
    print("Error: cannot find data file for 2020")
    sys.exit(1)

## XLS file for 2020 has many tabs. Only the "Weekly figures 2020" is interesting.
excel_columns = list(string.ascii_uppercase)
for letter in string.ascii_uppercase: excel_columns.append('A' + letter)
for letter in string.ascii_uppercase: excel_columns.append('B' + letter)

df_xlsx = pd.read_excel(xlsx_file_2020, sheet_name = "Weekly figures 2020", header = None)
df_xlsx.columns = excel_columns[:len(df_xlsx.columns)]

## The layout of the sheet will probably change over time. We can't be sure in which row/col the relevant data is located. But let's assume
## that the data for January 2020 won't change any more. We know that in the week ending 3 January 2020, there were 12254 deaths. From there
## we can work out the other columns and rows. Note that rows are 0-indexed in Pandas. So C8 in Excel would be column C, row index 7.
first_column = None
data_row = None

deaths_week_3_jan = 12254
for col_i in range(0,10):
    col = excel_columns[col_i]
    for row in range(1, 20):
        if df_xlsx.at[row, col] == deaths_week_3_jan:
            first_column_i = col_i
            first_column = col
            data_row = row

if first_column is None:
    print(f"Error: couldn't identify row/column that holds weekly data deaths (looking for: {deaths_week_3_jan})")
    sys.exit(1)

deaths_week_10_jan = 14058
col2 = excel_columns[first_column_i+1]
if df_xlsx.at[data_row, col2] != deaths_week_10_jan:
    print(f"Error: was expecting {deaths_week_10_jan} in cell {col2}" + str(data_row+1) +", but found " + str(df_xlsx.at[data_row, col2]))
    sys.exit(1)

print(first_column + str(data_row))
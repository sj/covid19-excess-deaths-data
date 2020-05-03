#!/usr/bin/python3
import pandas as pd
import datetime
import os

data_source = "https://opendata.cbs.nl/statline/#/CBS/nl/dataset/70895ned/table"
scriptname = os.path.basename(__file__)
scriptdir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

# Columns: 
#  ID: auto-incrementing key
#  Geslacht: gender. Category keys: 1100 = total for all genders, 3000 = men, 4000 = women
#  LeeftijdOp31December: age on the 31 December of the year of death. Category keys: 10000 = total for all ages, 21700 = 80+ years, 41700 = 0-65 years (exclusive), 53950 = 65-80 years
#  Perioden: particular year or week in time. E.g. "1995W103" = week 3 of 1995, "1995JJ00" = whole of 1995.
#  Overledenen_1: number of deaths in that category
#
# This data is based on death certificates issued in The Netherlands

df = pd.read_csv("weekly-deaths-70895ned.csv", sep=';')

# Filter on gender = sum of all genders (1100)
df2 = df[(df['Geslacht'] == 1100) & (df['LeeftijdOp31December'] == 10000)]


# Print out data with following columns:
# - country (NL)
# - first day of the week (e.g. 2019-08-19 = the Monday)
# - last day of the week (e.g. 2019-08-25 = the Sunday)
# - filters (always empty)
# - number of deaths
# - notes

skipped_previous_week_note = None
deathcount_cuml = 0

for index, row in df2.iterrows():
    year_week_raw = row['Perioden']

    # Week numbers in the Dutch data are ISO weeks (ISO8601). A week
    # starts on Monday, and ends on Sunday.
    # But weeks are weirdly split to straddle years. For example:
    #  - week 53 of 2019 = week 1 of 2020: Mon 30 Dec 2019 - Sun 5 January 2020
    #  - data labelled 2019-W153 is only for 30-31 Dec (2 days)
    #  - data labelled 2020-W101 is only for 1-5 Dec (5 days)
    #  - ISO8601 specifies that this week should be called 2020-W1
    #
    # To do this properly, we'd have to combine two different data
    # entries in the raw data into a single data entry in the
    # exported output data. But I expect that many other countries
    # will struggle with this too, so for now we'll just ignore
    # the first and last week of the year.

    if "JJ" in year_week_raw: continue      # period "2019JJ00" indicates data for that entire year
    if "X" in year_week_raw: 
        # "1995X000" indicates deaths in last days of 1994
        skipped_previous_week_note = f"Previous week straddled two years and was skipped to avoid data inconsistencies (see {scriptdir}/{scriptname} for explanation)"
        continue
    
    # Get rid of leading '1' in week numbers, add dash: 2019W133 becomes 2019-W33
    weekno = int(year_week_raw[6:])
    year = int(year_week_raw[0:4])
    year_week = str(year) + "-W" + str(weekno)

    # Determine first day (Mon) and last day (Sun) of this week
    # using ISO8601 (see note above)
    first_day = datetime.datetime.strptime(year_week + "-1", "%G-W%V-%u")
    last_day = datetime.datetime.strptime(year_week + "-7", "%G-W%V-%u")

    if first_day.year != last_day.year:
        # This week straddles to years. Skip it to avoid complications, and add note to next week.
        skipped_previous_week_note = f"Previous week ({year_week}) straddles two years and was skipped to avoid data inconsistencies (see {scriptdir}/{scriptname} for explanation)"
        continue

    notes = ""
    if skipped_previous_week_note:
        notes = skipped_previous_week_note

    if deathcount_cuml > 0:
        # Only print source once to save space
        data_source = ""

    deathcount = int(row['Overledenen_1'].strip())
    deathcount_cuml = deathcount_cuml + deathcount

    print(f"NL;{first_day:%Y-%m-%d};{last_day:%Y-%m-%d};;{deathcount};{data_source};{notes}")
    skipped_previous_week_note = None
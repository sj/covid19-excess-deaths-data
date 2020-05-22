#!/usr/bin/python3

import numpy as np
import os
import pandas as pd


data_source = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/" \
              "demo_r_mweek3.tsv.gz&unzip=true"
scriptname = os.path.basename(__file__)
scriptdir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

# Input file:
# Columns are separated by either a tab (\t) or a comma:
# - unit: all values are 'NR' (no clue what this column represents)
# - sex: F (female), M (male), T (total; both male and female)
# - age: different age categories, split in 5 year intervals, next to 'TOTAL' and 'UNK' (unknown)
# - geo\time: country codes and sub-country codes (regions) following the NUTS classifications
# - a lot of columns representing a week per column; a 'p' added in this value represents an estimated number


# /-----------------------------------------------------------------------------------------------------------------\ #
# |                          Read the data, rename the columns and select the relevant rows                         | #
# \-----------------------------------------------------------------------------------------------------------------/ #

# Read the data from the tab separated file
# Note: the parsing will fall back to the 'python' engine, as the 'c' engine does not support regex separators
df_raw = pd.read_csv('demo_r_mweek3.tsv', sep='\t|,')

# Only select the rows where both sexes and all ages are considered
df_raw = df_raw[(df_raw['sex'] == 'T') & (df_raw['age'] == 'TOTAL')]

# Drop the columns which are no longer required
df_raw.drop(['unit', 'sex', 'age'], axis=1, inplace=True)

# Rename the 'geo\time' column to 'country'
df_raw.rename({'geo\\time': 'country'}, axis=1, inplace=True)

# Only select the rows considering the entire country and not any (sub)regions
mask = df_raw['country'].str.len() == 2
df_raw = df_raw.loc[mask]


# /-----------------------------------------------------------------------------------------------------------------\ #
# |                                         Clean the values in the dataframe                                       | #
# \-----------------------------------------------------------------------------------------------------------------/ #

# Replace all ': ' and ':' values in the dataframe with np.nan values
df_raw.replace(':\s?', np.nan, regex=True, inplace=True)

# Remove all ' p' parts from the number of deaths (provisional numbers) Note: ' p' is removed from _all_ columns
df_raw.replace(' p', '', regex=True, inplace=True)


# /-----------------------------------------------------------------------------------------------------------------\ #
# |                     Pivot the dataframe such that the weeks become rows rather than columns                     | #
# \-----------------------------------------------------------------------------------------------------------------/ #

# Create a separate country dataframe to merge later with the stacked week values
countries = df_raw[['country']]
df_raw.drop('country', axis=1, inplace=True)

# Stack the week values and make a dataframe with a single index from this
df = df_raw.stack(dropna=False)
df = df.reset_index(level=[0, 1])

# Add the counties back to the dataframe
df = df.merge(countries, left_on='level_0', right_index=True)

# Rename the week column and the deaths column
df.rename({'level_1': 'week', 0: 'deaths'}, axis=1, inplace=True)

# Drop the level_0 column (the original index)
df.drop('level_0', axis=1, inplace=True)


# /-----------------------------------------------------------------------------------------------------------------\ #
# |           Further clean up the dataframe and prepare it so it's similar to other parts of the dataset           | #
# \-----------------------------------------------------------------------------------------------------------------/ #

# Add source column and add the source to all rows
df['source'] = 'https://data.europa.eu/euodp/en/data/dataset/WHum2Ir8F4KYmrrkj1sRQ'

# Add filter and notes columns and leave them empty
df['filter'] = ''
df['notes'] = ''

# Remove all spaces from the 'week' column (some of the values end with a space, some don't)
df['week'].replace(' ', '', regex=True, inplace=True)

# Make sure the deaths column is of type float (to keep the np.NaN it cannot be int)
df.deaths = df.deaths.astype(float)

# Add the first day of the week as a column
df['first_day'] = pd.to_datetime(df['week'] + '-1', format="%GW%V-%u")  # The -1 is for the first day of the week

# Add the last day of the week as a column
df['last_day'] = pd.to_datetime(df['week'] + '-7', format="%GW%V-%u")  # The -7 is for the first day of the week

# Remove the week column
df.drop('week', axis=1, inplace=True)

# Remove the rows where the first_day and the last_day are not in the same year (in order to keep the data clean)
df = df[df['first_day'].dt.year == df['last_day'].dt.year]


# /-----------------------------------------------------------------------------------------------------------------\ #
# |                                    Write the resulting dataframe to csv file                                    | #
# \-----------------------------------------------------------------------------------------------------------------/ #
df.to_csv("./weekly-deaths-eu.csv")

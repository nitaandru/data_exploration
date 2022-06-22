import pandas as pd
import glob
import numpy as np
import matplotlib as plt

# get data file names
path ='C:/Nita/UGAL/ECA_non-blended_custom/'
filenames = glob.glob(path + 'TG_*')

# append all the columns into a single dataframe 
li = []
for m in filenames:
    df = pd.read_table(m, index_col=None, header=0, skiprows = 19, na_values = -9999, delimiter = ',')
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)

# check the column names
frame.columns.tolist() 

# change the names
frame.columns = ['STAID', 'SOUID', 'DATE', 'TG', 'Q_TG'] 

# convert the date column in DATE format 
frame['DATE'] = pd.to_datetime(frame['DATE'], format = "%Y%m%d")
frame = frame.set_index('DATE', drop = False)

# count the number of stations
frame.nunique()

# see general statistics
frame.describe()

# divide the TG to 10
frame.TG = frame.TG/10
frame.TG.describe()

# subset the data for 1961-2020 interval
frame = frame.loc[frame["DATE"].between("1961-01-01", "2020-12-31")]

# read the metadata for stations
meta = pd.read_csv("C:/Nita/UGAL/ECA_non-blended_custom/sources.txt", skiprows = 23)
meta.head(5)

# select only the name and coordinates then name the columns
meta = meta.iloc[:,[1,2,4,5,6]]
meta.columns = ['SOUID', 'SOUNAME', 'LAT', 'LON', 'HEIGHT']

# join temperature data with stations names
new_data = pd.merge(frame, meta.iloc[:,[0,1]], how = 'inner') 

# count the number of missing data for each weather station
new_data.TG.isnull().sum()
misses = new_data.TG.isnull().groupby([new_data['SOUNAME']]).sum().astype(int).reset_index(False)
misses['PERCENT'] = misses['TG'] / len(pd.date_range(start="1961-01-01",end="2020-12-31")) * 100

# let's check the missing interval for each station
new_data = new_data.set_index('DATE')
new_data['YEAR'] = pd.to_datetime(new_data.index).strftime('%Y')
misses_year = new_data.TG.isnull().groupby([new_data['SOUNAME'],new_data['YEAR']]).sum().astype(int).reset_index(name = 'Count')

# let's plot the actual missing data
sns.set_style("darkgrid")
ax = sns.barplot(x="PERCENT", y="SOUNAME", data = misses)
misses.plot.line( y='Temperature', figsize=( 12 , 8 ))

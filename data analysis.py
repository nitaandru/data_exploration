import pandas as pd
import glob
import numpy as np

# get data file names
path ='/home/nitaandru/Desktop/ugal/'
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

# count the number of stations
frame.nunique()

# see general statistics
frame.describe()

# divide the TG to 10
frame.TG = frame.TG/10
frame.TG.describe()

# read the metadata for stations
meta = pd.read_csv("/home/nitaandru/Desktop/ugal/sources.txt", skiprows = 23)
meta.head(5)

# select only the name and coordinates then name the columns
meta = meta.iloc[:,[1,2,4,5,6]]
meta.columns = ['SOUID', 'SOUNAME', 'LAT', 'LON', 'HEIGHT']

# join temperature data with stations names
new_data = pd.merge(frame, meta.iloc[:,[0,1]], how = 'inner') 

# count the number of missing data for each weather station
new_data.TG.isnull().sum()
misses = new_data.TG.isnull().groupby([new_data['SOUNAME']]).sum().astype(int)

# let's check the missing interval for each station


# media multianuala pe statii
multianuala = new_data.groupby('SOUNAME').agg('mean')
suspect = new_data[new_data['Q_TG'] == 9]

new_data.isnull().sum()

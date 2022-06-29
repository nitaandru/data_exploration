import pandas as pd
import glob
import numpy as np
import seaborn as sns

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

# Plot annual missings – check https://www.python-graph-gallery.com/242-area-chart-and-faceting 
# for more info about seaborn
misses_year['YEAR'] =  misses_year['YEAR'].astype(int)

g = sns.FacetGrid(misses_year, col='SOUNAME', hue='SOUNAME', col_wrap=8)

# Add the line over the area with the plot function
g = g.map(plt.plot, 'YEAR', 'Count')
 
# Fill the area with fill_between
g = g.map(plt.fill_between, 'YEAR', 'Count', alpha=0.2).set_titles("{col_name} station")
 
# Control the title of each facet
g = g.set_titles("{col_name}")
 
# Add a title for the whole plot
plt.subplots_adjust(top=0.92)
# g = g.fig.suptitle('Evolution of the value of stuff in 16 countries')

# Show the graph
plt.show()

# toate statiile au lipsa informatii pentru 2020.

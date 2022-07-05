import pandas as pd
import glob
import numpy as np
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt

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

# convert the date column in DATE format 
frame['DATE'] = pd.to_datetime(frame['DATE'], format = "%Y%m%d")
frame = frame.set_index('DATE', drop = False)

# count the number of stations
frame.nunique()

# see general statistics
frame.describe()

# divide the TG to 10
frame.TG = frame.TG/10

# subset the data for 1961-2019 interval
frame = frame.loc[frame["DATE"].between("1961-01-01", "2019-12-31")]

# read the metadata for stations
meta = pd.read_table("/home/nitaandru/Desktop/ugal/sources.txt", skiprows = 23, sep = ',')
meta.head(5)

# select only the name and coordinates then name the columns
meta = meta.iloc[:,[1,2,4,5,6]]
meta.columns = ['SOUID', 'SOUNAME', 'LAT', 'LON', 'HEIGHT']
meta.SOUNAME = meta.SOUNAME.replace(r'\s+', ' ', regex=True) # remove extra whitespaces in the stations name

# join temperature data with stations names
new_data = pd.merge(frame, meta.iloc[:,[0,1]], how = 'inner') 

# count the number of missing data for each weather station
new_data.TG.isnull().sum()
misses = new_data.TG.isnull().groupby([new_data['SOUNAME']]).sum().astype(int).reset_index(False)
misses['PERCENT'] = misses['TG'] / len(pd.date_range(start="1961-01-01",end="2019-12-31")) * 100

# let's check the missing interval for each station
new_data = new_data.set_index('DATE', drop = False)
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
# Show the graph
plt.show()

# toate statiile au lipsa informatii pentru 2020.
# unele statii au informatii lipsa random (Bacau), altele non-aleatoriu (Baia Mare, Turnu Magurele sau Ocna-Sugatag)
## Exemplul 1: inlocuim valorile lipsa cu media sirului (ex: Ocna Sugatag).
ex1 = new_data[new_data["SOUNAME"] == "OCNA SUGATAG "]

# aggregate to annual mean
ex1_an = ex1['TG'].resample('A').mean()
round(ex1_an.mean(),2) # get the multianual mean

# calculeaza panta cu lipsuri
x = ex1_an.dropna() # drop the missing to calculate the Sen slope
y = range(1960, 2018)

res = stats.theilslopes(x, y, 0.95)
round(res[0] * 60,2) # panta medie a schimbarii pe deceniu

# calculeaza panta fara lipsuri
x = ex1_an.fillna(ex1_an.mean()) # replace the missing with multiannual mean
y = range(1960, 2019)

res = stats.theilslopes(x, y, 0.95)
round(res[0] * 60,2) 

# Exclude missings data
new_data = new_data[~new_data['SOUNAME'].isin(['BAIA MARE ', 'TURNU MAGURELE ', 'TG JIU '])] # exclude stations with too many NAs

# boxplots for temp
sns.set(style="darkgrid")
sns.boxplot(x=new_data["TG"], y=new_data["SOUNAME"])
plt.show()

## Calculate basic statistics: 
multiannual = new_data.groupby('SOUNAME').TG.aggregate([np.mean, np.min, np.max])

## Extract the hottest and coldest day
multiannual = pd.merge(multiannual, new_data[['SOUNAME', 'DATE', 'TG']],  how='left', left_on=['SOUNAME','amin'], right_on = ['SOUNAME','TG'])
multiannual = pd.merge(multiannual, new_data[['SOUNAME', 'DATE', 'TG']],  how='left', left_on=['SOUNAME','amax'], right_on = ['SOUNAME','TG'])
multiannual = multiannual.rename(columns = {'DATE_x': 'DATE_MN', 'DATE_y': 'DATE_MX'})
multiannual = multiannual.drop(['TG_x', 'TG_y'], axis = 1)

## Calculate annual means; adjust to anomalies
anuale = new_data.groupby(['SOUNAME', 'YEAR'])['TG'].aggregate('mean')
anuale = anuale.to_frame()
anuale = anuale.reset_index()
anuale['ABATERE'] = ''

for m in pd.unique(anuale['SOUNAME']):
    print(m)
    sub = anuale[anuale['SOUNAME'] == m]    
    sub['TG'] = sub.TG - sub.TG.mean()
    anuale.loc[anuale.SOUNAME == m, 'ABATERE'] = sub.TG;

anuale.YEAR = anuale['YEAR'].astype(int)
anuale.ABATERE = anuale.ABATERE.astype('float')

# Plot annual anomalies
g = sns.FacetGrid(anuale, col='SOUNAME', hue='SOUNAME', col_wrap=8)
# Add the line over the area with the plot function
g = g.map(plt.plot, 'YEAR', 'ABATERE')
# Control the title/labels of each facet
g = g.set_titles("{col_name}")
g.set(xlabel='An',
       ylabel='Abatere [°C]')
# Add a title for the whole plot
plt.subplots_adjust(top=0.92)
# Show the graph
plt.show()

## Calculate multiannual monthly means
new_data['MONTH'] = pd.to_datetime(new_data.index).strftime('%m')
lunare = new_data.groupby(['SOUNAME', 'MONTH'])['TG'].aggregate('mean')
lunare = lunare.reset_index()

## Visualize the monthly data
g = sns.catplot(x="MONTH", y = 'TG', col="SOUNAME", col_wrap=8,
                data=lunare,
                kind="bar", height=2.5, aspect=.8)
g = g.set_titles("{col_name}")


## Discretization: Group stations by altitude
meta['AREA'] = pd.cut(x = meta['HEIGHT'], bins = [0, 300, 800, 2600], 
                      labels = ['campie', 'deal', 'munte'])
env = pd.merge(new_data[['SOUID', 'DATE', 'TG', 'YEAR']], meta[['SOUID', 'AREA']])
env = env.groupby(['YEAR', 'AREA'])['TG'].aggregate('mean')
env = env.reset_index()
env.YEAR = env.YEAR.astype(int)

## Calculate the slope for each altitude category
for y in pd.unique(env['AREA']) :
    x = env[env['AREA'] ==y].YEAR
    z = env[env['AREA'] ==y].TG
    res = stats.theilslopes(z, x, 0.95)
    print(y + ": " + str(round(res[0] * 60,2) ))

    
## Export to spreadsheets
multiannual.to_excel("/home/nitaandru/Desktop/ugal/export/medii_multianuale.xlsx") # a single file

## or multiple sheets inside the same excel file
with pd.ExcelWriter('/home/nitaandru/Desktop/ugal/export/climate_data_RO.xlsx') as writer:  
    anuale.to_excel(writer, sheet_name='medii_anuale')
    lunare.to_excel(writer, sheet_name='lunare')
    misses.to_excel(writer, sheet_name = 'missing')
    
## Pentru KDE plots   
# getting necessary libraries
sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

temp = pd.read_csv('/home/nitaandru/Desktop/ugal/TG_SOUID107510.txt', skiprows = 19, header = 0,  na_values = -9999)
temp.columns = ['STAID', 'SOUID', 'DATE', 'TG', 'Q_TG'] 
temp['DATE'] = pd.to_datetime(temp['DATE'], format = "%Y%m%d")
temp = temp.set_index('DATE', drop = False)
temp.TG = temp.TG/ 10

temp['month'] = pd.to_datetime(temp['DATE']).dt.month
temp['b'] =  pd.to_datetime(temp.index).strftime('%m')

# we define a dictionnary with months that we'll use later
month_dict = {1: 'january',
              2: 'february',
              3: 'march',
              4: 'april',
              5: 'may',
              6: 'june',
              7: 'july',
              8: 'august',
              9: 'september',
              10: 'october',
              11: 'november',
              12: 'december'}

# we create a 'month' column
temp['month'] = temp['month'].map(month_dict)

# we generate a pd.Serie with the mean temperature for each month (used later for colors in the FacetGrid plot), and we create a new column in temp dataframe
month_mean_serie = temp.groupby('month')['TG'].mean()
temp['mean_month'] = temp['month'].map(month_mean_serie)

# we generate a color palette with Seaborn.color_palette()
pal = sns.color_palette(palette='coolwarm', n_colors=12)

# in the sns.FacetGrid class, the 'hue' argument is the one that is the one that will be represented by colors with 'palette'
g = sns.FacetGrid(temp, row='month', hue='mean_month', aspect=15, height=0.75, palette=pal)

# then we add the densities kdeplots for each month
g.map(sns.kdeplot, 'TG',
      bw_adjust=1, clip_on=False,
      fill=True, alpha=1, linewidth=1.5)

# here we add a white line that represents the contour of each kdeplot
g.map(sns.kdeplot, 'TG', 
      bw_adjust=1, clip_on=False, 
      color="w", lw=2)

# here we add a horizontal line for each plot
g.map(plt.axhline, y=0,
      lw=2, clip_on=False)

# we loop over the FacetGrid figure axes (g.axes.flat) and add the month as text with the right color
# notice how ax.lines[-1].get_color() enables you to access the last line's color in each matplotlib.Axes
for i, ax in enumerate(g.axes.flat):
    ax.text(-15, 0.02, month_dict[i+1],
            fontweight='bold', fontsize=15,
            color=ax.lines[-1].get_color())
    
# we use matplotlib.Figure.subplots_adjust() function to get the subplots to overlap
g.fig.subplots_adjust(hspace=-0.3)

# eventually we remove axes titles, yticks and spines
g.set_titles("")
g.set(yticks=[])
g.despine(bottom=True, left=True)

g.set(ylabel='')

plt.setp(ax.get_xticklabels(), fontsize=15, fontweight='bold')
plt.xlabel('Temperatura in grade Celsius', fontweight='bold', fontsize=15)
g.fig.suptitle('Media zilnica lunara a temperaturii in Galati',
               ha='right',
               fontsize=20,
               fontweight=20)

plt.show()


#All code taken from https://www.datacamp.com/community/tutorials/web-scraping-using-python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from pylab import rcParams

from urllib.request import urlopen
from bs4 import BeautifulSoup

url = "http://www.hubertiming.com/results/2017GPTR10K" #this sets the url where we are going to get the data from
html = urlopen(url) #will open the url specified

#You can use the find_all() method of soup to extract useful html tags within a webpage.
soup = BeautifulSoup(html, 'lxml')  #creates a beautiful soup object from teh HTML of the webpage

#To print out table rows only, pass the 'tr' argument in soup.find_all().
rows = soup.find_all('tr')


list_rows = []
for row in rows:
    cells = row.find_all('td')
    str_cells = str(cells)
    clean = re.compile('<.*?>')
    clean2 = (re.sub(clean, '',str_cells))
    list_rows.append(clean2)

#The next step is to convert the list into a dataframe and get a quick view of the first 10 rows using Pandas.
df = pd.DataFrame(list_rows)
df.head(10)

#The dataframe is not in the format we want. To clean it up, you should split the "0" column into multiple columns at the comma position. This is accomplished by using the str.split() method.
df1 = df[0].str.split(',', expand=True)
df1.head(10)

#You can use the strip() method to remove the opening square bracket on column "0."
df1[0] = df1[0].str.strip('[')
df1.head(10)

#The table is missing table headers. You can use the find_all() method to get the table headers.
col_labels = soup.find_all('th')

#Similar to table rows, you can use Beautiful Soup to extract text in between html tags for table headers.
all_header = []
col_str = str(col_labels)
cleantext2 = BeautifulSoup(col_str, "lxml").get_text()
all_header.append(cleantext2)


#You can then convert the list of headers into a pandas dataframe.
df2 = pd.DataFrame(all_header)
df2.head()

#Similarly, you can split column "0" into multiple columns at the comma position for all rows.
df3 = df2[0].str.split(',', expand=True)
df3.head()

#The two dataframes can be concatenated into one using the concat() method as illustrated below.
frames = [df3, df1]
df4 = pd.concat(frames)
df4.head(10)

#Below shows how to assign the first row to be the table header.
df5 = df4.rename(columns=df4.iloc[0])
df5.head()

#At this point, the table is almost properly formatted. For analysis, you can start by getting an overview of the data as shown below.
df5.info()
df5.shape

#The table has 597 rows and 14 columns. You can drop all rows with any missing values.
df6 = df5.dropna(axis=0, how='any')

#Also, notice how the table header is replicated as the first row in df5. It can be dropped using the following line of code.
df7 = df6.drop(df6.index[0])
df7.head()

#You can perform more data cleaning by renaming the '[Place' and ' Team]' columns.
df7.rename(columns={'[Place': 'Place'},inplace=True)
df7.rename(columns={' Team]': 'Team'},inplace=True)
df7.head()

#The final data cleaning step involves removing the closing bracket for cells in the "Team" column.
df7['Team'] = df7['Team'].str.strip(']')
df7.head()

time_list = df7[' Chip Time'].tolist()


# You can use a for loop to convert 'Chip Time' to minutes
# Error in the format of the code will be missing elements when splitting the string
time_mins = []
temp = "00:"
for i in time_list:
    if len(i) < 7:
        i = temp + i
    h, m, s = i.split(':')
    m = str(m)
    m = m.strip()
    math = (int(h) * 3600 + int(m) * 60 + int(s))/60
    time_mins.append(math)


#The next step is to convert the list back into a dataframe and make a new column ("Runner_mins") for runner chip times expressed in just minutes
df7['Runner_mins'] = time_mins
df7.head()
#The code below shows how to calculate statistics for numeric columns only in the dataframe.
df7.describe(include=[np.number])

#For data visualization, it is convenient to first import parameters from the pylab module that comes with matplotlib and set the same size for all figures to avoid doing it for each figure.
rcParams['figure.figsize'] = 15, 5
df7.boxplot(column='Runner_mins')
plt.grid(True, axis='y')
plt.ylabel('Chip Time')
plt.xticks([1], ['Runners'])

#This is an missing parameter on the website
plt.show()

#Below is a distribution plot of runners' chip times plotted using the seaborn library. The distribution looks almost normal.
x = df7['Runner_mins']
ax = sns.distplot(x, hist=True, kde=True, rug=False, color='m', bins=25, hist_kws={'edgecolor':'black'})
plt.show()

#The third question deals with whether there were any performance differences between males and females of various age groups. Below is a distribution plot of chip times for males and females.
f_fuko = df7.loc[df7[' Gender']==' F']['Runner_mins']
m_fuko = df7.loc[df7[' Gender']==' M']['Runner_mins']
sns.distplot(f_fuko, hist=True, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Female')
sns.distplot(m_fuko, hist=False, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Male')
plt.legend()

#missing function on the website code
plt.show()

#The distribution indicates that females were slower than males on average. You can use the groupby() method to compute summary statistics for males and females separately as shown below.
df7.boxplot(column='Runner_mins', by=' Gender')
plt.ylabel('Chip Time')
plt.suptitle("")
plt.show()
# --------------
import datetime
import numpy as np
import pandas as pd

# import matplotlib as mpl
from matplotlib.dates import DateFormatter
from matplotlib.dates import date2num
from matplotlib.dates import drange
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

CSV_FILE_NAME = "./DrunkSenpai.csv"
FIG_FILE_NAME = "./DrunkSenpai.png"

df = pd.read_csv(CSV_FILE_NAME, index_col='date')[['amount_ml']]

plt.close(1)
fig = plt.figure(1, figsize=(12, 8))
axes = fig.add_subplot(111)

axes.plot(date2num(df.index), np.array(df.values.transpose()[0]), 'o-')
axes.xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M'))
plt.xticks(rotation=45)

plt.savefig(FIG_FILE_NAME)

# --------------
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

CSV_FILE_NAME = "./DrunkSenpai.csv"
FIG_FILE_NAME = "./DrunkSenpai.png"

df = pd.read_csv(CSV_FILE_NAME, index_col='date')[['amount_ml']]
df.plot()
plt.xticks(rotation=90)

plt.savefig(FIG_FILE_NAME)

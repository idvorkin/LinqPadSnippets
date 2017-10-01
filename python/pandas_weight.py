# this uses ipython so:
# > ipython --TerminalInteractiveShell.editing_mode=vi
# %load pandas_weight.py

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

%matplotlib



matplotlib.style.use("ggplot")
# Export Data from healthkit - unzip it then run:
# https://github.com/tdda/applehealthdata
# data goes to

weight_label = "Weight in lbs"
date_group_label = "Date" 
EXPORTED_AND_TRANDFORMED_CSV = "c:/temp/apple_health_export/BodyMass.csv"
df = pd.read_csv(EXPORTED_AND_TRANDFORMED_CSV)
df["startDate"] = pd.to_datetime(df["startDate"])
df[weight_label] = df["value"]

# grouping is weird so switch to strings 
df[date_group_label]=df["startDate"].apply(lambda t:f"{t.month}-{t.year-2000}")
ax = sns.boxplot(x=date_group_label, y=weight_label, data=df)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.set_title("Weight over time")

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


#############################################################################
# Prepare data and import into a dataframe
#############################################################################
# 1) Export Data from healthkit (search internet) - unzip to a directory.
# 2) Run code from - https://github.com/tdda/applehealthdata
# 3) Update the script to point to your file name.

exported_and_trandformed_csv_file = "c:/temp/apple_health_export/BodyMass.csv"
df = pd.read_csv(exported_and_trandformed_csv_file)

#############################################################################
# Clean up the data.
#############################################################################

# make startDate a datetime.
df["startDate"] = pd.to_datetime(df["startDate"])

# and then apply stats to reasonable time period.
date_group_column_name = "month_year" 
df[date_group_column_name]=df["startDate"].apply(lambda t:f"{t.month}-{t.year-2000}")

# Normalize weight into lbs.
weight_lbs_column_name = "weight_in_lbs"
df[weight_lbs_column_name] = df.apply(lambda row: row.value * 2.2 if row.unit == "kg" else row.value, axis="columns")

#############################################################################
# Make pretty pictures.
#############################################################################
ax = sns.boxplot(x=date_group_column_name, y=weight_lbs_column_name, data=df)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.set_title("Weight over time")
ax.set_xlabel("date")
ax.set_ylabel("lbs")

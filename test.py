import pandas as pd
import math
import datetime
import csv
import sqlite3
import time
import psycopg2
import re
import os
import glob
import os.path, time



folderdir = r"M:\DXD Log Files"
mylist = glob.glob(folderdir + '/*') # * means all if need specific format then *.csv
r_nmr = re.compile(".*NMR")
nmrlist = list(filter(r_nmr.match, mylist)) # Read Note
latestnmr = max(nmrlist, key=os.path.getctime)

#temp = r"M:\DXD Log Files\VindumPumpLog (Pump1NMR) 6-8 1240pm.csv"
df_vinnmr = pd.read_csv(latestnmr, index_col=False,  error_bad_lines=False)
df_vinnmr = df_vinnmr[['Date', 'Time', 'P1 Press', 'P1 Rate', 'P2 Press', 'P2 Rate']]
df_vinnmr.columns = ['Date', 'Time', 'P1NMRPres', 'P1NMRRate', 'P2NMRPres', 'P2NMRRate']
# df_vinnmr = df_vinnmr[:-1]
# df_vinnmr['DateTime'] = pd.to_datetime(df_vinnmr['Date'].astype(str) + ' ' + df_vinnmr['Time'].astype(str))
# df_vinnmr['DateTime'] = pd.to_datetime(df_vinnmr['DateTime'])

# df_vinnmr['DateTime'] = df_vinnmr['DateTime'].dt.round('30s') 
# df_vinnmr = df_vinnmr.drop_duplicates(subset='DateTime', keep="first")
# df_vinnmr = df_vinnmr.drop(['Date', 'Time'], axis=1) 
# df_vinnmr = df_vinnmr.dropna()
# df_vinnmr = df_vinnmr.sort_values(by='DateTime')

print(df_vinnmr.head())

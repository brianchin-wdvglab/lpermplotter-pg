import pandas as pd
import math
import datetime
import csv
import sqlite3
import time
import psycopg2

df_dxd = pd.read_csv(r"M:\DXD Log Files\DXD_Log_9_4_1009am.csv", skiprows=7, error_bad_lines=False)
df_dxd.drop(df_dxd.columns[[3, 4, 6, 7, 9, 10, 12, 13, 15, 16,
                18, 19, 21, 22, 24, 25, 27, 28, 30, 31, 33, 34, 36, 37, 39, 40, 42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61]], axis=1, inplace=True)
df_dxd.to_csv("test.csv")
print(df_dxd.head)
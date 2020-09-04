import pandas as pd
import math
import datetime
import csv
import sqlite3
import time
import psycopg2
from sqlalchemy import create_engine

dxd = r"M:\New folder\DXD_Log_8_28_444pm.csv"

df_dxd = pd.read_csv(dxd, skiprows=7, error_bad_lines=False)
df_dxd.drop(df_dxd.columns[[3, 4, 6, 7, 9, 10, 12, 13, 15, 16,
                        18, 19, 21, 22, 24, 25, 27, 28, 30, 31, 33, 34, 36, 37, 39, 40, 42,43,44,45,46,47,48,49,50,51,52,53,54,55]], axis=1, inplace=True)
df_dxd.to_csv('test.csv')
print("done")
# print(df_dxd.head)
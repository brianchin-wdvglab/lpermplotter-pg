import pandas as pd
import math
import datetime
import csv
import sqlite3
import time
import psycopg2
from sqlalchemy import create_engine


class logLoader:
    def __init__(self, dxd, isco, vindum, vindumNMR, EOR):
        self.dxd = dxd
        self.isco = isco
        self.vindum = vindum
        self.vindumNMR = vindumNMR
        self.EOR = EOR
        self.conn = create_engine('postgresql://liquidperm:vglab224@localhost:5432/lpermdb')
        #print(self.conn.table_names())
        #print('test2')
        #self.conn = psycopg2.connect("dbname=lpermdb user=liquidperm password=vglab224")

    def test(self):
        return("hello world")

    def dxdLoader(self):
        df_dxd = pd.read_csv(self.dxd, skiprows=7, error_bad_lines=False)
        df_dxd.drop(df_dxd.columns[[3, 4, 6, 7, 9, 10, 12, 13, 15, 16,
                18, 19, 21, 22, 24, 25, 27, 28, 30, 31, 33, 34, 36, 37, 
                39, 40, 42,43,45,46,48,49,51,52,54,55,57,58,60,61]], axis=1, inplace=True)
        df_dxd.columns = ['Date', 'Time','SS1Conf', 'SS1Up', 'SS1Down', 
                'SS2Conf', 'SS2Up', 'SS2Down', 'Ext3Conf', 'Ext3Up', 'Ext3Down', 
                'Ext4Conf', 'Ext4Up', 'Ext4Down', 'DeadulusUp', 'DeadulusDown', 
                'EOR5Conf', 'EOR6Conf','EOR6Up', 'EOR6Down','EOR5Up', 'EOR5Down']
        df_dxd['DateTime'] = pd.to_datetime(df_dxd['Date'] + " " + df_dxd['Time'])
        df_dxd['DateTime'] = df_dxd['DateTime'].dt.round('30s')  
        df_dxd = df_dxd.dropna()
        df_dxd = df_dxd.sort_values(by='DateTime')
        df_dxd.drop(df_dxd.columns[[0,1]], axis=1, inplace=True)
        df_temp = pd.read_sql_query("SELECT * from dxd", self.conn)
        #df_dxd = pd.concat([df_dxd, df_temp])
        #df_dxd.to_csv('text.csv')
        cond = df_dxd['DateTime'].isin(df_temp['DateTime'])
        df_dxd.drop(df_dxd[cond].index, inplace = True)
        #df_dxd['DateTime'] = pd.to_datetime(df_dxd['DateTime'] ,errors='coerce')
        #df_dxd = df_dxd.sort_values(by='DateTime')
        #df_dxd = df_dxd.drop_duplicates(subset='DateTime', keep="first")
        df_dxd.to_sql('dxd', self.conn, if_exists='append', index = False)

    def iscoLoader(self):
        df_isco = pd.read_csv(self.isco)
        df_isco.columns = df_isco.columns.str.replace('/', '')
        df_isco['DateTime'] = df_isco['DateTime'].str.replace('=', '')
        df_isco['DateTime'] = df_isco['DateTime'].str.replace('"', '')
        df_isco[pd.to_numeric(df_isco['DateTime'], errors='coerce').notnull()]
        isco_list = ["Pressure AB", "Flow Rate AB", "DateTime"]
        df_isco = df_isco[isco_list]
        df_isco['DateTime'] = pd.to_datetime(df_isco['DateTime'], errors='coerce') 
        df_isco.columns = ['ISCOPres', 'ISCORate', 'DateTime']
        df_isco['DateTime'] = pd.to_datetime(df_isco['DateTime'])
        df_isco['DateTime'] = df_isco['DateTime'].dt.round('30s')
        df_isco = df_isco.dropna(subset=['DateTime'])
        df_temp = pd.read_sql_query("SELECT * from isco", self.conn)
        cond = df_isco['DateTime'].isin(df_temp['DateTime'])
        df_isco.drop(df_isco[cond].index, inplace = True)
        df_isco.to_sql('isco', self.conn, if_exists='append', index = False)

    def vindumLoader(self):
        df_vin = pd.read_csv(self.vindum, index_col=False)
        mainlist = ['Date', 'Time', 'P1 Press', 'P1 Rate', 'P2 Press',
            'P2 Rate', 'P3 Press', 'P3 Rate', 'P4 Press', 'P4 Rate', 'P1 Cum Vol', 'P2 Cum Vol', 'P3 Cum Vol', 'P4 Cum Vol']
        df_vin = df_vin[[c for c in df_vin.columns if c in mainlist]]
        
        df_vin = df_vin[:-1]
        df_vin['DateTime'] = pd.to_datetime(df_vin['Date'] + " " + df_vin['Time'])
        df_vin['DateTime'] = pd.to_datetime(df_vin['DateTime'])
        df_vin['DateTime'] = df_vin['DateTime'].dt.round('30s')
        df_vin = df_vin.drop_duplicates(subset='DateTime', keep="first")
        df_vin = df_vin.drop(['Date', 'Time'], axis=1)
        df_vin.columns = ['P1Pres', 'P1Rate', 'P1Cum', 'P2Pres','P2Rate', 'P2Cum', 'P3Pres', 'P3Rate', 'P3Cum', 'P4Pres', 'P4Rate', 'P4Cum', 'DateTime']
        df_vin = df_vin.dropna(subset = ['DateTime'])
        df_vin = df_vin.sort_values(by='DateTime')

        df_temp = pd.read_sql_query("SELECT * from vin", self.conn)
        cond = df_vin['DateTime'].isin(df_temp['DateTime'])
        df_vin.drop(df_vin[cond].index, inplace = True)
        df_vin.to_sql('vin', self.conn, if_exists='append', index = False)

    def vindumnmrLoader(self):
        #temp = r"M:\DXD Log Files\VindumPumpLog (Pump1NMR) 6-8 1240pm.csv"
        df_vinnmr = pd.read_csv(self.vindumNMR, index_col=False,  error_bad_lines=False)
        #df_vinnmr = pd.read_csv(temp, index_col=False,  error_bad_lines=False)
        df_vinnmr = df_vinnmr[['Date', 'Time', 'P1 Press', 'P1 Rate', 'P2 Press', 'P2 Rate', 'P1 Cum Vol', 'P2 Cum Vol']]
        df_vinnmr.columns = ['Date', 'Time', 'P1NMRPres', 'P1NMRRate', 'P2NMRPres', 'P2NMRRate', 'P1NMRCum', 'P2NMRCum']
        df_vinnmr = df_vinnmr[:-1]
        df_vinnmr['DateTime'] = pd.to_datetime(df_vinnmr['Date'].astype(str) + ' ' + df_vinnmr['Time'].astype(str))
        df_vinnmr['DateTime'] = pd.to_datetime(df_vinnmr['DateTime'])
        
        df_vinnmr['DateTime'] = df_vinnmr['DateTime'].dt.round('30s') 
        df_vinnmr = df_vinnmr.drop_duplicates(subset='DateTime', keep="first")
        df_vinnmr = df_vinnmr.drop(['Date', 'Time'], axis=1) 
        df_vinnmr = df_vinnmr.dropna()
        df_vinnmr = df_vinnmr.sort_values(by='DateTime')
        
        df_temp = pd.read_sql_query("SELECT * from vinnmr", self.conn)
        cond = df_vinnmr['DateTime'].isin(df_temp['DateTime'])
        df_vinnmr.drop(df_vinnmr[cond].index, inplace = True)
        df_vinnmr.to_sql('vinnmr', self.conn, if_exists='append', index = False)

    def EORLoader(self):
        df_eor = pd.read_csv(self.EOR, skiprows=46,encoding='latin1', header = None)
        df_eor = df_eor.drop(df_eor.columns[[1, 3, 4, 5, 6, 7, 8, 9, 12, 13 ,16 ,17, 19, 21, 22, 23, 24,
                                            25, 26, 27 ,28, 29, 30, 34, 36, 37, 38, 39, 40, 41, 42, 
                                            43, 44, 45]], axis=1)
        
        df_eor.columns = ['DateTime', 'EORPConf', 'P1_injV', 'P1_injQ', 'P2_injV', 'P2_ingQ', 'EORUP',
                            'EORDOWN', 'EORVol', 'EORRate', 'EORDP', 'EORHES']
        df_eor.drop_duplicates('DateTime', inplace=True)
        df_eor = df_eor.set_index('DateTime')
        df_eor.index = pd.to_datetime(df_eor.index)
        df_eor = df_eor.resample('30s').pad()
        df_eor = df_eor.reset_index()
        df_eor = df_eor.dropna()
        df_eor = df_eor.sort_values(by='DateTime')
        df_eor['DateTime'] = pd.to_datetime(df_eor['DateTime'] ,errors='coerce')

        df_temp = pd.read_sql_query("SELECT * from eor", self.conn)
        cond = df_eor['DateTime'].isin(df_temp['DateTime'])
        df_eor.drop(df_eor[cond].index, inplace = True)
        df_eor.to_sql('eor', self.conn, if_exists='append', index = False)

    def accesspg(self):
        cur = self.conn.cursor()
        df_temp = pd.read_sql_query("SELECT * from dxd", self.conn)
        print(df_temp.head())

    def combined(self):
        #merge logs
        df_dxd_temp = pd.read_sql_query("SELECT * from dxd", self.conn)
        df_dxd_temp['DateTime'] = pd.to_datetime(df_dxd_temp['DateTime'] ,errors='coerce')
        
        df_vin_temp = pd.read_sql_query("SELECT * from vin", self.conn)
        df_vin_temp['DateTime'] = pd.to_datetime(df_vin_temp['DateTime'] ,errors='coerce')
        df_vinnmr_temp = pd.read_sql_query("SELECT * from vinnmr", self.conn)
        df_vinnmr_temp['DateTime'] = pd.to_datetime(df_vinnmr_temp['DateTime'] ,errors='coerce')
        df_isco_temp = pd.read_sql_query("SELECT * from isco", self.conn)
        df_isco_temp['DateTime'] = pd.to_datetime(df_isco_temp['DateTime'] ,errors='coerce')
        df_eor_temp = pd.read_sql_query("SELECT * from EOR", self.conn)
        df_eor_temp['DateTime'] = pd.to_datetime(df_eor_temp['DateTime'] ,errors='coerce')
        df_dxd_temp = df_dxd_temp.sort_values('DateTime')
        df_dxd_temp = df_dxd_temp.drop_duplicates(subset='DateTime', keep="first")
        # df_dxd_temp.to_csv('out.csv')
        df_com = pd.merge_asof(df_dxd_temp, df_vin_temp.sort_values('DateTime'), on='DateTime')
        df_com = pd.merge_asof(df_com, df_vinnmr_temp.sort_values('DateTime'), on='DateTime')
        df_com = pd.merge_asof(df_com, df_isco_temp.sort_values('DateTime'), on='DateTime')
        df_temp = pd.read_sql_query("SELECT * from combined", self.conn)
        
        cond = df_com['DateTime'].isin(df_temp['DateTime'])
        df_com.drop(df_com[cond].index, inplace = True)
        df_com = df_com.drop_duplicates(subset='DateTime', keep="first")
        df_com.to_sql('combined', self.conn, if_exists='append', index = False)

        df_com_eor = pd.merge_asof(df_eor_temp, df_isco_temp.sort_values('DateTime'), on='DateTime')
        df_temp = pd.read_sql_query("SELECT * from combined_eor", self.conn)
        cond = df_com_eor['DateTime'].isin(df_temp['DateTime'])
        df_com_eor.drop(df_com_eor[cond].index, inplace = True)
        df_com_eor = df_com_eor.drop_duplicates(subset='DateTime', keep="first")
        df_com_eor.to_sql('combined_eor', self.conn, if_exists='append', index = False)

# loglocations = pd.read_excel(r"M:\Team Chaos Liquid Perm Initialization v5.xlsx", sheet_name="Initialize")
# df_ll = loglocations.set_index("log").to_dict()
# dxd = df_ll['address']['dxd']
# isco = df_ll['address']['isco']
# vindum = df_ll['address']['vindum']
# vindumNMR = df_ll['address']['vindumNMR']
# eor = df_ll['address']['eor']

# x = logLoader(dxd, isco, vindum, vindumNMR, eor)
# print(x.test())
# x.dxdLoader()
# x.iscoLoader()
# x.vindumLoader()
# x.vindumnmrLoader()
# x.EORLoader()
# x.combined()
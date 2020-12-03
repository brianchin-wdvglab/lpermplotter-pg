from sampleparser import sample
import sqlite3
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
from visc import visc, visc_dead
import math
import psycopg2
from sqlalchemy import create_engine

def sample_data_dec(current_sample):
    conn = create_engine('postgresql://liquidperm:vglab224@localhost:5432/lpermdb') 
    #get start and end time for sql query
    sample_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][0])
    sample_end = current_sample['End Time'][-1]
    if pd.isnull(sample_end):
        sample_end = datetime.datetime.utcnow()
    else :
        sample_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][-1])

    params = [sample_start.strftime('%Y-%m-%d %H:%M:%S'), sample_end.strftime('%Y-%m-%d %H:%M:%S')]
    df_sample_raw = pd.read_sql_query("SELECT * from combined_temp_dec WHERE public.combined_temp_dec.\"DateTime\" BETWEEN %s AND %s", params = params, con=conn)
    df_sample_raw['DateTime'] = df_sample_raw['DateTime'].astype('datetime64[ns]')
    df_sample = pd.DataFrame()
    #print(df_sample)
    for i in range(len(current_sample['Start Time'])):
        #get time intervals
        interval_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][i])
        interval_end = current_sample['End Time'][i]
        if pd.isnull(interval_end):
            interval_end = datetime.datetime.utcnow()
        else :
            interval_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][i])

        mask = (df_sample_raw['DateTime'] > interval_start) & (df_sample_raw['DateTime'] <= interval_end)
        df_sample.loc[mask, 'DateTime'] = df_sample_raw['DateTime']
        df_sample.loc[mask, 'Confining Pressure'] = df_sample_raw[current_sample['vessel']+'Conf']
        df_sample.loc[mask, 'Upstream Pressure'] = df_sample_raw[current_sample['vessel']+'Up']
        df_sample.loc[mask, 'Downstream Pressure'] = df_sample_raw[current_sample['vessel']+'Down']
        # df_sample.loc[mask, 'Cumulative Volume'] = df_sample_raw[current_sample['vessel']+'Cum']

        if current_sample['Pump'][i] == 'None':
            df_sample.loc[mask, 'Rate'] = 0
            df_sample.loc[mask, 'Cumulative Volume'] = 0
        else:
            df_sample.loc[mask, 'Rate'] = df_sample_raw[current_sample['Pump'][i]+'Rate']
            df_sample.loc[mask, 'Cumulative Volume'] = df_sample_raw[current_sample['Pump'][i]+'Cum']
        
        #df_sample.loc[mask, 'Rate'] = df_sample_raw[current_sample['Pump'][i]+'Rate']
        df_sample.loc[mask, 'Comment'] = current_sample['Instance Comment'][i]
    #temp values for viscosity params
    a, b = visc(current_sample['fluid'], current_sample['temperature'])
    # a = 8.365010181414292e-06
    # b = 0.0732989622362088
    df_sample['Rate'] = df_sample['Rate'].fillna(0)
    df_sample = df_sample.dropna()
    df_sample['dp'] = df_sample['Upstream Pressure'].astype(int) - df_sample['Downstream Pressure'].astype(int)
    df_sample['absdp'] = abs(df_sample['Upstream Pressure'].astype(int) - df_sample['Downstream Pressure'].astype(int))
    df_sample['Rate'] = df_sample['Rate'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['dp'] = df_sample['dp'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['qdp'] = df_sample['Rate'].astype(float)/df_sample['dp'].astype(float)
    df_sample['Viscosity'] = (a*df_sample['Upstream Pressure'].astype(int)+b)*current_sample['visc_mult']
    area = math.pi*(current_sample['diameter']/2)**2
    df_sample['Permeability'] = (df_sample['Rate']/60*df_sample['Viscosity']*current_sample['length']*1000) / (area*(df_sample['dp']/14.696))*1000000
    df_sample.sort_values(by=['DateTime'], inplace=True, ascending=True)

    return df_sample

def sample_data_dead_dec(current_sample):
    conn = create_engine('postgresql://liquidperm:vglab224@10.0.100.140:5432/lpermdb') 
    #get start and end time for sql query
    sample_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][0])
    sample_end = current_sample['End Time'][-1]
    if pd.isnull(sample_end):
        sample_end = datetime.datetime.utcnow()
    else :
        sample_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][-1])

    params = [sample_start.strftime('%Y-%m-%d %H:%M:%S'), sample_end.strftime('%Y-%m-%d %H:%M:%S')]
    df_sample_raw = pd.read_sql_query("SELECT * from combined_temp_dec WHERE public.combined_temp_dec.\"DateTime\" BETWEEN %s AND %s", params = params, con=conn)
    df_sample_raw['DateTime'] = df_sample_raw['DateTime'].astype('datetime64[ns]')
    df_sample = pd.DataFrame()
    visc_df = pd.DataFrame(list(dict.fromkeys(current_sample['Instance Comment'])), columns = ['fn'])
    visc_df['a'], visc_df['b'] = zip(*visc_df.apply( lambda x: visc_dead(x['fn']), axis =1 ))

    for i in range(len(current_sample['Start Time'])):
        #get time intervals
        interval_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][i])
        interval_end = current_sample['End Time'][i]
        if pd.isnull(interval_end):
            interval_end = datetime.datetime.utcnow()
        else :
            interval_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][i])
        mask = (df_sample_raw['DateTime'] > interval_start) & (df_sample_raw['DateTime'] <= interval_end)
        df_sample.loc[mask, 'DateTime'] = df_sample_raw['DateTime']
        # df_sample.loc[mask, 'Confining Pressure'] = current_sample['Confining Pressure'][i]
        if type(current_sample['Confining Pressure'][i]) == int:
            df_sample.loc[mask, 'Confining Pressure'] = current_sample['Confining Pressure'][i]
        else:
            df_sample.loc[mask, 'Confining Pressure'] = df_sample_raw[current_sample['Confining Pressure'][i]+'Pres']
        df_sample.loc[mask, 'Upstream Pressure'] = df_sample_raw[current_sample['vessel']+'Up']
        df_sample.loc[mask, 'Downstream Pressure'] = df_sample_raw[current_sample['vessel']+'Down']
        if current_sample['Pump'][i] == 'None':
            df_sample.loc[mask, 'Rate'] = 0
        else:
            df_sample.loc[mask, 'Rate'] = df_sample_raw[current_sample['Pump'][i]+'Rate']
        #df_sample.loc[mask, 'Rate'] = df_sample_raw[current_sample['Pump'][i]+'Rate']
        df_sample.loc[mask, 'Comment'] = current_sample['Instance Comment'][i]
        df_sample.loc[mask, 'visc_a'] = visc_df.loc[visc_df['fn'] == current_sample['Instance Comment'][i], 'a'].iloc[0]
        df_sample.loc[mask, 'visc_b'] = visc_df.loc[visc_df['fn'] == current_sample['Instance Comment'][i], 'b'].iloc[0]
    #temp values for viscosity params
    # a = 8.365010181414292e-06
    # b = 0.0732989622362088
    df_sample['Rate'] = df_sample['Rate'].fillna(0)
    df_sample = df_sample.dropna()
    df_sample['dp'] = df_sample['Upstream Pressure'].astype(int) - df_sample['Downstream Pressure'].astype(int)
    df_sample['absdp'] = abs(df_sample['Upstream Pressure'].astype(int) - df_sample['Downstream Pressure'].astype(int))
    df_sample['Rate'] = df_sample['Rate'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['dp'] = df_sample['dp'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['qdp'] = df_sample['Rate'].astype(float)/df_sample['dp'].astype(float)
    df_sample['Viscosity'] = (df_sample['visc_a']*df_sample['Upstream Pressure'].astype(int)+df_sample['visc_b'])*current_sample['visc_mult']
    df_sample.drop(columns=['visc_a', 'visc_b'], inplace = True)
    area = math.pi*(current_sample['diameter']/2)**2
    df_sample['Permeability'] = (df_sample['Rate']/60*df_sample['Viscosity']*current_sample['length']*1000) / (area*(df_sample['dp']/14.696))*1000000
    df_sample.sort_values(by=['DateTime'], inplace=True, ascending=True)
    return df_sample

def sample_data(current_sample):
    conn = create_engine('postgresql://liquidperm:vglab224@localhost:5432/lpermdb') 
    #get start and end time for sql query
    sample_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][0])
    sample_end = current_sample['End Time'][-1]
    if pd.isnull(sample_end):
        sample_end = datetime.datetime.utcnow()
    else :
        sample_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][-1])

    params = [sample_start.strftime('%Y-%m-%d %H:%M:%S'), sample_end.strftime('%Y-%m-%d %H:%M:%S')]
    df_sample_raw = pd.read_sql_query("SELECT * from combined WHERE public.combined.\"DateTime\" BETWEEN %s AND %s", params = params, con=conn)
    df_sample_raw['DateTime'] = df_sample_raw['DateTime'].astype('datetime64[ns]')
    df_sample = pd.DataFrame()
    #print(df_sample)
    for i in range(len(current_sample['Start Time'])):
        #get time intervals
        interval_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][i])
        interval_end = current_sample['End Time'][i]
        if pd.isnull(interval_end):
            interval_end = datetime.datetime.utcnow()
        else :
            interval_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][i])

        mask = (df_sample_raw['DateTime'] > interval_start) & (df_sample_raw['DateTime'] <= interval_end)
        df_sample.loc[mask, 'DateTime'] = df_sample_raw['DateTime']
        df_sample.loc[mask, 'Confining Pressure'] = df_sample_raw[current_sample['vessel']+'Conf']
        df_sample.loc[mask, 'Upstream Pressure'] = df_sample_raw[current_sample['vessel']+'Up']
        df_sample.loc[mask, 'Downstream Pressure'] = df_sample_raw[current_sample['vessel']+'Down']
        # df_sample.loc[mask, 'Cumulative Volume'] = df_sample_raw[current_sample['vessel']+'Cum']

        if current_sample['Pump'][i] == 'None':
            df_sample.loc[mask, 'Rate'] = 0
            df_sample.loc[mask, 'Cumulative Volume'] = 0
        else:
            df_sample.loc[mask, 'Rate'] = df_sample_raw[current_sample['Pump'][i]+'Rate']
            df_sample.loc[mask, 'Cumulative Volume'] = df_sample_raw[current_sample['Pump'][i]+'Cum']
        
        #df_sample.loc[mask, 'Rate'] = df_sample_raw[current_sample['Pump'][i]+'Rate']
        df_sample.loc[mask, 'Comment'] = current_sample['Instance Comment'][i]
    #temp values for viscosity params
    a, b = visc(current_sample['fluid'], current_sample['temperature'])
    # a = 8.365010181414292e-06
    # b = 0.0732989622362088
    df_sample['Rate'] = df_sample['Rate'].fillna(0)
    df_sample = df_sample.dropna()
    df_sample['dp'] = df_sample['Upstream Pressure'].astype(int) - df_sample['Downstream Pressure'].astype(int)
    df_sample['absdp'] = abs(df_sample['Upstream Pressure'].astype(int) - df_sample['Downstream Pressure'].astype(int))
    df_sample['Rate'] = df_sample['Rate'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['dp'] = df_sample['dp'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['qdp'] = df_sample['Rate'].astype(float)/df_sample['dp'].astype(float)
    df_sample['Viscosity'] = (a*df_sample['Upstream Pressure'].astype(int)+b)*current_sample['visc_mult']
    area = math.pi*(current_sample['diameter']/2)**2
    df_sample['Permeability'] = (df_sample['Rate']/60*df_sample['Viscosity']*current_sample['length']*1000) / (area*(df_sample['dp']/14.696))*1000000
    df_sample.sort_values(by=['DateTime'], inplace=True, ascending=True)

    return df_sample

def sample_data_dead(current_sample):
    conn = create_engine('postgresql://liquidperm:vglab224@10.0.100.140:5432/lpermdb') 
    #get start and end time for sql query
    sample_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][0])
    sample_end = current_sample['End Time'][-1]
    if pd.isnull(sample_end):
        sample_end = datetime.datetime.utcnow()
    else :
        sample_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][-1])

    params = [sample_start.strftime('%Y-%m-%d %H:%M:%S'), sample_end.strftime('%Y-%m-%d %H:%M:%S')]
    df_sample_raw = pd.read_sql_query("SELECT * from combined WHERE public.combined.\"DateTime\" BETWEEN %s AND %s", params = params, con=conn)
    df_sample_raw['DateTime'] = df_sample_raw['DateTime'].astype('datetime64[ns]')
    df_sample = pd.DataFrame()
    visc_df = pd.DataFrame(list(dict.fromkeys(current_sample['Instance Comment'])), columns = ['fn'])
    visc_df['a'], visc_df['b'] = zip(*visc_df.apply( lambda x: visc_dead(x['fn']), axis =1 ))

    for i in range(len(current_sample['Start Time'])):
        #get time intervals
        interval_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][i])
        interval_end = current_sample['End Time'][i]
        if pd.isnull(interval_end):
            interval_end = datetime.datetime.utcnow()
        else :
            interval_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][i])
        mask = (df_sample_raw['DateTime'] > interval_start) & (df_sample_raw['DateTime'] <= interval_end)
        df_sample.loc[mask, 'DateTime'] = df_sample_raw['DateTime']
        # df_sample.loc[mask, 'Confining Pressure'] = current_sample['Confining Pressure'][i]
        if type(current_sample['Confining Pressure'][i]) == int:
            df_sample.loc[mask, 'Confining Pressure'] = current_sample['Confining Pressure'][i]
        else:
            df_sample.loc[mask, 'Confining Pressure'] = df_sample_raw[current_sample['Confining Pressure'][i]+'Pres']
        df_sample.loc[mask, 'Upstream Pressure'] = df_sample_raw[current_sample['vessel']+'Up']
        df_sample.loc[mask, 'Downstream Pressure'] = df_sample_raw[current_sample['vessel']+'Down']
        if current_sample['Pump'][i] == 'None':
            df_sample.loc[mask, 'Rate'] = 0
        else:
            df_sample.loc[mask, 'Rate'] = df_sample_raw[current_sample['Pump'][i]+'Rate']
        #df_sample.loc[mask, 'Rate'] = df_sample_raw[current_sample['Pump'][i]+'Rate']
        df_sample.loc[mask, 'Comment'] = current_sample['Instance Comment'][i]
        df_sample.loc[mask, 'visc_a'] = visc_df.loc[visc_df['fn'] == current_sample['Instance Comment'][i], 'a'].iloc[0]
        df_sample.loc[mask, 'visc_b'] = visc_df.loc[visc_df['fn'] == current_sample['Instance Comment'][i], 'b'].iloc[0]
    #temp values for viscosity params
    # a = 8.365010181414292e-06
    # b = 0.0732989622362088
    df_sample['Rate'] = df_sample['Rate'].fillna(0)
    df_sample = df_sample.dropna()
    df_sample['dp'] = df_sample['Upstream Pressure'].astype(int) - df_sample['Downstream Pressure'].astype(int)
    df_sample['absdp'] = abs(df_sample['Upstream Pressure'].astype(int) - df_sample['Downstream Pressure'].astype(int))
    df_sample['Rate'] = df_sample['Rate'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['dp'] = df_sample['dp'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['qdp'] = df_sample['Rate'].astype(float)/df_sample['dp'].astype(float)
    df_sample['Viscosity'] = (df_sample['visc_a']*df_sample['Upstream Pressure'].astype(int)+df_sample['visc_b'])*current_sample['visc_mult']
    df_sample.drop(columns=['visc_a', 'visc_b'], inplace = True)
    area = math.pi*(current_sample['diameter']/2)**2
    df_sample['Permeability'] = (df_sample['Rate']/60*df_sample['Viscosity']*current_sample['length']*1000) / (area*(df_sample['dp']/14.696))*1000000
    df_sample.sort_values(by=['DateTime'], inplace=True, ascending=True)
    return df_sample

def sample_data_eor(current_sample):
    conn = create_engine('postgresql://liquidperm:vglab224@localhost:5432/lpermdb') 

    sample_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][0])
    sample_end = current_sample['End Time'][-1]
    if pd.isnull(sample_end):
        sample_end = datetime.datetime.utcnow()
    else :
        sample_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][-1])

    params = [sample_start, sample_end]
    df_sample_raw = pd.read_sql_query("SELECT * from combined_eor WHERE DateTime BETWEEN ? and ?", params = params, con=conn)
    df_sample_raw['DateTime'] = df_sample_raw['DateTime'].astype('datetime64[ns]')
    df_sample = pd.DataFrame()
    for i in range(len(current_sample['Start Time'])):
        #get time intervals
        interval_start = pd.Timestamp.to_pydatetime(current_sample['Start Time'][i])
        interval_end = current_sample['End Time'][i]

        if pd.isnull(interval_end):
            interval_end = datetime.datetime.utcnow()
        else :
            interval_end = pd.Timestamp.to_pydatetime(current_sample['End Time'][i])

        mask = (df_sample_raw['DateTime'] > interval_start) & (df_sample_raw['DateTime'] <= interval_end)
        df_sample.loc[mask, 'DateTime'] = df_sample_raw['DateTime']
        df_sample.loc[mask, 'Confining Pressure'] = df_sample_raw['EORPConf']
        df_sample.loc[mask, 'Upstream Pressure'] = df_sample_raw['EORUP']
        df_sample.loc[mask, 'Downstream Pressure'] = df_sample_raw['EORDOWN']
        if current_sample['Pump'][i] == 'ISCO':
            df_sample.loc[mask, 'Rate'] = df_sample_raw['ISCORate']
        else:
            df_sample.loc[mask, 'Rate'] = ((df_sample_raw['EORVol'].diff())/0.5)
        df_sample.loc[mask, 'Comment'] = current_sample['Instance Comment'][i]
    #temp values for viscosity params
    df_sample.to_csv('text.csv')
    a, b = visc(current_sample['fluid'], current_sample['temperature'])
    #df_sample['Upstream Pressure'] = df_sample['Upstream Pressure'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    #df_sample['Downstream Pressure'] = df_sample['Downstream Pressure'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample = df_sample.iloc[1:]
    df_sample['dp'] = df_sample['Upstream Pressure'] - df_sample['Downstream Pressure']
    df_sample['absdp'] = abs(df_sample['Upstream Pressure'].astype(int) - df_sample['Downstream Pressure'].astype(int))
    df_sample['qdp'] = df_sample['Rate']/df_sample['dp']
    df_sample['Rate'] = df_sample['Rate'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['dp'] = df_sample['dp'].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
    df_sample['Viscosity'] = (a*df_sample['Upstream Pressure']+b)*current_sample['visc_mult']
    area = math.pi*(current_sample['diameter']/2)**2
    df_sample['Permeability'] = (df_sample['Rate']/60*df_sample['Viscosity']*current_sample['length']*1000) / (area*(df_sample['dp']/14.696))*1000000
    #time_window = current_sample['length']
    time_window = 60
    df_sample['Permeability'] = df_sample['Permeability'].rolling(window=time_window).mean()
    df_sample.sort_values(by=['DateTime'], inplace=True, ascending=True)
    return df_sample

# #get sample info
# samplesheet = r"M:\Team Chaos Liquid Perm Initialization v5.xlsx"
# current_sample = sample(samplesheet, 1).sampleprop()
# df_current = sample_data(current_sample)
# print(df_current)
# fig = go.Figure([go.Scatter(x=df_current['DateTime'], y=df_current['Rate'])])
# fig.update_xaxes(rangeslider_visible=True)

# fig.show()

#print(df_temp.head(5))
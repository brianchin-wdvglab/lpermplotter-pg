import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import math
import plotly
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import datetime
import numpy as np
import os.path
import csv
from sklearn import datasets, linear_model
from visc import visc
from sampledata import sample_data
from sampleparser import sample
import dash_bootstrap_components as dbc
import logloader
import time


samplesheet = r"M:\Team Chaos Liquid Perm Initialization v5.xlsx"
outputfolder = r"C:\Users\Brian.Chin\learning\lpermplotter_db_postgres\temp"
def csv_output(df_current, current_sample):
    df_current_output = pd.DataFrame()
    df_current_output['DateTime'] = df_current['DateTime']
    df_current_output['Upstream Pressure (psi)'] = df_current['Upstream Pressure']
    df_current_output['Downstream Pressure (psi)'] = df_current['Downstream Pressure']
    df_current_output['dp'] = df_current['dp']
    df_current_output['absdp'] = df_current['absdp']
    df_current_output['Rate (cc/min)'] = df_current['Rate']
    df_current_output['Confining Pressure (psi)'] = df_current['Confining Pressure']
    df_current_output['Comments'] = df_current['Comment']
    df_current_output['qdp'] = df_current['qdp']
    df_current_output['Viscosity'] = df_current['Viscosity']
    df_current_output['Permeability'] = df_current['Permeability']
    df_current_output['Time (Min)'] = df_current.index*0.5
    df_current_output['Average Permeability (nD)'] = ""
    df_current_output = df_current_output.reset_index()
    csv_title = current_sample['client'] + ' ' + current_sample['sample ID']
    csv_path = outputfolder + "\\" + csv_title + ".csv"
    df_params = pd.DataFrame.from_dict(current_sample)
    df_params['sample ID'] = df_params['client'] + " " + df_params['sample ID']
    df_params['area'] = math.pi*(df_params['diameter']/2)**2
    df_params = df_params.iloc[[-1]]
    df_params = df_params.reset_index()
    df_params = df_params.drop(['client', 'Start Time', 'End Time', 'Instance Comment'], axis = 1)
    reorder = ['area', 'sample ID', 'diameter', 'length','vessel', 'perm_min', 'perm_max', 'comment', 'Pump', 'time scale', 'temperature', 'fluid']
    df_params = df_params[reorder]
    df_concat = pd.concat([df_current_output, df_params], axis = 1)
    df_concat = df_concat.drop(['index'], axis = 1)
    df_concat.to_csv(csv_path)
    
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SIMPLEX])
app.layout = html.Div(
    html.Div([
        html.H4('LPerm Plotter V5 - Update interval: 2 minutes'),
        html.Div(id='live-update-text'),

        #dcc.Graph(id='live-update-graph5'),
        dcc.Interval(
            id='interval-component',
            interval=600*1000,  # in milliseconds
            n_intervals=0
        ),
        dcc.Interval(
            id='interval-component-2',
            interval=120*1000,  # in milliseconds
            n_intervals=0
        )
    ])
)


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component-2', 'n_intervals')])
def timenow(n): 
    print('db update started, do not pause script')
    loglocations = pd.read_excel(r"M:\Team Chaos Liquid Perm Initialization v5.xlsx", sheet_name="Initialize")
    df_ll = loglocations.set_index("log").to_dict()
    dxd = df_ll['address']['dxd']
    isco = df_ll['address']['isco']
    vindum = df_ll['address']['vindum']
    vindumNMR = df_ll['address']['vindumNMR']
    eor = df_ll['address']['eor']

    x = logloader.logLoader(dxd, isco, vindum, vindumNMR, eor)
    start = time.time()
    x.dxdLoader()
    print('dxd complete')
    x.iscoLoader()
    print('isco complete')
    x.vindumLoader()
    print('vindum complete')
    x.vindumnmrLoader()
    print('vindumnmr complete')
    x.EORLoader()
    print('eor complete')
    x.combined()
    print('combine complete')
    print('db update ended, safe to pause script')
    end = time.time()
    print(end - start)
    return("last updated: " + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

if __name__ == '__main__':
    app.run_server(debug=True)
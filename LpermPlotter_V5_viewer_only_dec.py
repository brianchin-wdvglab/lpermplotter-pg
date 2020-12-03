import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import math
import plotly
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import datetime
import os.path
import csv
from sklearn import datasets, linear_model
from visc import visc
from sampledata import sample_data, sample_data_dead, sample_data_dec, sample_data_dead_dec
from sampleparser import sample
import dash_bootstrap_components as dbc
import logloader
import time
from json import JSONEncoder
import json

VALID_USERNAME_PASSWORD_PAIRS = {
    'safdar': 'ali',
    'colton': 'barnes',
    'ashish': 'mathur',
    'chad': 'belanger',
    'evan': 'kias'
}


samplesheet = r"M:\Team Chaos Liquid Perm Initialization v5.xlsx"
outputfolder = r"M:\Lpermplotter output"
outputfolder_json = r"M:\Lpermplotter json output"
def csv_output(df_current, current_sample):

    sample_JSONData = json.dumps(current_sample, indent=4, cls=DateTimeEncoder)
    output_fn = current_sample['client'] + " " + current_sample['sample ID'] + ".json"
    csv_path_json = outputfolder_json + "\\" + output_fn + ".csv"
    with open(csv_path_json, "w") as outfile:  
        json.dump(sample_JSONData, outfile)
    
    df_current_output = pd.DataFrame()
    df_current_output['DateTime'] = df_current['DateTime']
    df_current_output['Upstream Pressure (psi)'] = df_current['Upstream Pressure']
    df_current_output['Downstream Pressure (psi)'] = df_current['Downstream Pressure']
    df_current_output['Cumulative Volume (cc)'] = df_current['Cumulative Volume']
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
def csv_output_dead(df_current, current_sample):

    sample_JSONData = json.dumps(current_sample, indent=4, cls=DateTimeEncoder)
    output_fn = current_sample['client'] + " " + current_sample['sample ID'] + ".json"
    csv_path_json = outputfolder_json + "\\" + output_fn + ".csv"
    with open(csv_path_json, "w") as outfile:  
        json.dump(sample_JSONData, outfile)
    
    df_current_output = pd.DataFrame()
    df_current_output['DateTime'] = df_current['DateTime']
    df_current_output['Upstream Pressure (psi)'] = df_current['Upstream Pressure']
    df_current_output['Downstream Pressure (psi)'] = df_current['Downstream Pressure']
    # df_current_output['Cumulative Volume (cc)'] = df_current['Cumulative Volume']
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

class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SIMPLEX])
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

app.layout = html.Div(
    html.Div([
        html.H4('LPerm Plotter V5 - Update interval: 5 minutes'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph0'),
        dcc.Graph(id='live-update-graph1'),
        dcc.Graph(id='live-update-graph2'),
        dcc.Graph(id='live-update-graph3'),
        dcc.Graph(id='live-update-graph4'),
        dcc.Graph(id='live-update-graph5'),
        dcc.Graph(id='live-update-graph6'),

        #dcc.Graph(id='live-update-graph5'),
        dcc.Interval(
            id='interval-component',
            interval=300*1000,  # in milliseconds
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
    return("last updated: " + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

@app.callback(Output('live-update-graph0', 'figure'),
              [Input('interval-component', 'n_intervals')])
# m is the sheet name
def plot0(n):
    current_sample = sample(samplesheet, 1).sampleprop()
    df_current = sample_data_dec(current_sample)
    csv_output(df_current, current_sample)
    xax=df_current.DateTime
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig = go.Figure([go.Scatter(x=df_current['DateTime'], y=df_current['Rate'])])
    fig.update_xaxes(rangeslider_visible=True)
    #print(df_current.head())
    fig.add_trace(go.Scatter(x=xax, y=df_current.Permeability,
                            name="Permeability", line_color='Blue', opacity=.5, hovertext=df_current.Comment))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Upstream Pressure'],
                            name="Upstream", line_color='red', yaxis="y2"))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Downstream Pressure'],
                            name="Downstream", line_color='purple', yaxis="y2"))
    #fig.add_trace(go.Scatter(x=xax, y=df_current['rollingq'],
    fig.add_trace(go.Scatter(x=xax, y=df_current.Rate,
                            name="Flow Rate", line_color='Green', yaxis="y3", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current.qdp,
                            name="q over dp", line_color='Black', yaxis="y4", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Confining Pressure'],
                            name="confining pressure", line_color='Orange', yaxis="y5", opacity=1))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Cumulative Volume'],
                            name="Cumulative Volume", line_color='Magenta', yaxis="y6", opacity=1))
    title = '| Sample ID: ' + current_sample['client'] + ' ' +  current_sample['sample ID'] + ' | Vessel: ' + \
        current_sample['vessel'] + ' | Pump: ' + current_sample['Pump'][-1] + ' | Temperature: '+ \
            str(current_sample['temperature']) + ' <br> | Comments: '+current_sample['comment'] + ' | Visc: '+str(current_sample['fluid'])
    fig.update_layout(plot_bgcolor = "#f3f7fd", paper_bgcolor = "#f3f7fd", title_text=title, title_font_color = "#5c0325", xaxis_rangeslider_visible=True, xaxis=dict(domain=[0, 0.8]), hovermode='x',
                    yaxis=dict(title="Permeability - nD", titlefont=dict(color="Blue"), anchor="free",
                                tickfont=dict(color="Blue"), range=[current_sample['perm_min'], current_sample['perm_max']]),
                    yaxis2=dict(title="Pressure - psia", titlefont=dict(color="Red"), tickfont=dict(
                        color="Red"), anchor="free", overlaying="y", side="right", position=0.8, range=[0, 10000]),
                    yaxis3=dict(title="Flow rate - cc/min", titlefont=dict(color="Green"), tickfont=dict(
                        color="Green"), anchor="free", overlaying="y", side="right", position=0.84, range=[0, .0005]),
                    yaxis4=dict(title="q over dp", titlefont=dict(color="Black"), tickfont=dict(
                        color="Black"), anchor="free", overlaying="y", side="right", position=0.88, range=[0, .000001]),
                    yaxis5=dict(title="confining pressure", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.92, range=[0, 10000]),
                    yaxis6=dict(title="Cumulative Volume", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.96, range=[0, 5]))
    return fig

@app.callback(Output('live-update-graph1', 'figure'),
              [Input('interval-component', 'n_intervals')])
# m is the sheet name
def plot1(n):
    current_sample = sample(samplesheet, 2).sampleprop()
    df_current = sample_data_dec(current_sample)
    csv_output(df_current, current_sample)
    xax=df_current.DateTime
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig = go.Figure([go.Scatter(x=df_current['DateTime'], y=df_current['Rate'])])
    fig.update_xaxes(rangeslider_visible=True)
    #print(df_current.head())
    fig.add_trace(go.Scatter(x=xax, y=df_current.Permeability,
                            name="Permeability", line_color='Blue', opacity=.5, hovertext=df_current.Comment))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Upstream Pressure'],
                            name="Upstream", line_color='red', yaxis="y2"))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Downstream Pressure'],
                            name="Downstream", line_color='purple', yaxis="y2"))
    #fig.add_trace(go.Scatter(x=xax, y=df_current['rollingq'],
    fig.add_trace(go.Scatter(x=xax, y=df_current.Rate,
                            name="Flow Rate", line_color='Green', yaxis="y3", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current.qdp,
                            name="q over dp", line_color='Black', yaxis="y4", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Confining Pressure'],
                            name="confining pressure", line_color='Orange', yaxis="y5", opacity=1))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Cumulative Volume'],
                            name="Cumulative Volume", line_color='Magenta', yaxis="y6", opacity=1))
    title = '| Sample ID: ' + current_sample['client'] + ' ' +  current_sample['sample ID'] + ' | Vessel: ' + \
        current_sample['vessel'] + ' | Pump: ' + current_sample['Pump'][-1] + ' | Temperature: '+ \
            str(current_sample['temperature']) + ' <br> | Comments: '+current_sample['comment'] + ' | Visc: '+str(current_sample['fluid'])
    fig.update_layout(plot_bgcolor = "#f3f7fd", paper_bgcolor = "#f3f7fd", title_text=title, title_font_color = "#5c0325", xaxis_rangeslider_visible=True, xaxis=dict(domain=[0, 0.8]), hovermode='x',
                    yaxis=dict(title="Permeability - nD", titlefont=dict(color="Blue"), anchor="free",
                                tickfont=dict(color="Blue"), range=[current_sample['perm_min'], current_sample['perm_max']]),
                    yaxis2=dict(title="Pressure - psia", titlefont=dict(color="Red"), tickfont=dict(
                        color="Red"), anchor="free", overlaying="y", side="right", position=0.8, range=[0, 10000]),
                    yaxis3=dict(title="Flow rate - cc/min", titlefont=dict(color="Green"), tickfont=dict(
                        color="Green"), anchor="free", overlaying="y", side="right", position=0.84, range=[0, .0005]),
                    yaxis4=dict(title="q over dp", titlefont=dict(color="Black"), tickfont=dict(
                        color="Black"), anchor="free", overlaying="y", side="right", position=0.88, range=[0, .000001]),
                    yaxis5=dict(title="confining pressure", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.92, range=[0, 10000]),
                    yaxis6=dict(title="Cumulative Volume", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.96, range=[0, 5]))
    return fig

@app.callback(Output('live-update-graph2', 'figure'),
              [Input('interval-component', 'n_intervals')])
# m is the sheet name
def plot2(n):
    current_sample = sample(samplesheet, 3).sampleprop()
    df_current = sample_data_dec(current_sample)
    csv_output(df_current, current_sample)
    xax=df_current.DateTime
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig = go.Figure([go.Scatter(x=df_current['DateTime'], y=df_current['Rate'])])
    fig.update_xaxes(rangeslider_visible=True)
    #print(df_current.head())
    fig.add_trace(go.Scatter(x=xax, y=df_current.Permeability,
                            name="Permeability", line_color='Blue', opacity=.5, hovertext=df_current.Comment))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Upstream Pressure'],
                            name="Upstream", line_color='red', yaxis="y2"))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Downstream Pressure'],
                            name="Downstream", line_color='purple', yaxis="y2"))
    #fig.add_trace(go.Scatter(x=xax, y=df_current['rollingq'],
    fig.add_trace(go.Scatter(x=xax, y=df_current.Rate,
                            name="Flow Rate", line_color='Green', yaxis="y3", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current.qdp,
                            name="q over dp", line_color='Black', yaxis="y4", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Confining Pressure'],
                            name="confining pressure", line_color='Orange', yaxis="y5", opacity=1))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Cumulative Volume'],
                            name="Cumulative Volume", line_color='Magenta', yaxis="y6", opacity=1))
    title = '| Sample ID: ' + current_sample['client'] + ' ' +  current_sample['sample ID'] + ' | Vessel: ' + \
        current_sample['vessel'] + ' | Pump: ' + current_sample['Pump'][-1] + ' | Temperature: '+ \
            str(current_sample['temperature']) + ' <br> | Comments: '+current_sample['comment'] + ' | Visc: '+str(current_sample['fluid'])
    fig.update_layout(plot_bgcolor = "#f3f7fd", paper_bgcolor = "#f3f7fd", title_text=title, title_font_color = "#5c0325", xaxis_rangeslider_visible=True, xaxis=dict(domain=[0, 0.8]), hovermode='x',
                    yaxis=dict(title="Permeability - nD", titlefont=dict(color="Blue"), anchor="free",
                                tickfont=dict(color="Blue"), range=[current_sample['perm_min'], current_sample['perm_max']]),
                    yaxis2=dict(title="Pressure - psia", titlefont=dict(color="Red"), tickfont=dict(
                        color="Red"), anchor="free", overlaying="y", side="right", position=0.8, range=[0, 10000]),
                    yaxis3=dict(title="Flow rate - cc/min", titlefont=dict(color="Green"), tickfont=dict(
                        color="Green"), anchor="free", overlaying="y", side="right", position=0.84, range=[0, .0005]),
                    yaxis4=dict(title="q over dp", titlefont=dict(color="Black"), tickfont=dict(
                        color="Black"), anchor="free", overlaying="y", side="right", position=0.88, range=[0, .000001]),
                    yaxis5=dict(title="confining pressure", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.92, range=[0, 10000]),
                    yaxis6=dict(title="Cumulative Volume", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.96, range=[0, 5]))
    return fig

@app.callback(Output('live-update-graph3', 'figure'),
              [Input('interval-component', 'n_intervals')])
# m is the sheet name
def plot3(n):
    current_sample = sample(samplesheet, 4).sampleprop()
    df_current = sample_data_dec(current_sample)
    csv_output(df_current, current_sample)
    xax=df_current.DateTime
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig = go.Figure([go.Scatter(x=df_current['DateTime'], y=df_current['Rate'])])
    fig.update_xaxes(rangeslider_visible=True)
    #print(df_current.head())
    fig.add_trace(go.Scatter(x=xax, y=df_current.Permeability,
                            name="Permeability", line_color='Blue', opacity=.5, hovertext=df_current.Comment))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Upstream Pressure'],
                            name="Upstream", line_color='red', yaxis="y2"))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Downstream Pressure'],
                            name="Downstream", line_color='purple', yaxis="y2"))
    #fig.add_trace(go.Scatter(x=xax, y=df_current['rollingq'],
    fig.add_trace(go.Scatter(x=xax, y=df_current.Rate,
                            name="Flow Rate", line_color='Green', yaxis="y3", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current.qdp,
                            name="q over dp", line_color='Black', yaxis="y4", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Confining Pressure'],
                            name="confining pressure", line_color='Orange', yaxis="y5", opacity=1))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Cumulative Volume'],
                            name="Cumulative Volume", line_color='Magenta', yaxis="y6", opacity=1))
    title = '| Sample ID: ' + current_sample['client'] + ' ' +  current_sample['sample ID'] + ' | Vessel: ' + \
        current_sample['vessel'] + ' | Pump: ' + current_sample['Pump'][-1] + ' | Temperature: '+ \
            str(current_sample['temperature']) + ' <br> | Comments: '+current_sample['comment'] + ' | Visc: '+str(current_sample['fluid'])
    fig.update_layout(plot_bgcolor = "#f3f7fd", paper_bgcolor = "#f3f7fd", title_text=title, title_font_color = "#5c0325", xaxis_rangeslider_visible=True, xaxis=dict(domain=[0, 0.8]), hovermode='x',
                    yaxis=dict(title="Permeability - nD", titlefont=dict(color="Blue"), anchor="free",
                                tickfont=dict(color="Blue"), range=[current_sample['perm_min'], current_sample['perm_max']]),
                    yaxis2=dict(title="Pressure - psia", titlefont=dict(color="Red"), tickfont=dict(
                        color="Red"), anchor="free", overlaying="y", side="right", position=0.8, range=[0, 10000]),
                    yaxis3=dict(title="Flow rate - cc/min", titlefont=dict(color="Green"), tickfont=dict(
                        color="Green"), anchor="free", overlaying="y", side="right", position=0.84, range=[0, .0005]),
                    yaxis4=dict(title="q over dp", titlefont=dict(color="Black"), tickfont=dict(
                        color="Black"), anchor="free", overlaying="y", side="right", position=0.88, range=[0, .000001]),
                    yaxis5=dict(title="confining pressure", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.92, range=[0, 10000]),
                    yaxis6=dict(title="Cumulative Volume", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.96, range=[0, 5]))
    return fig

@app.callback(Output('live-update-graph4', 'figure'),
              [Input('interval-component', 'n_intervals')])
# m is the sheet name
def plot4(n):
    current_sample = sample(samplesheet, 5).sampleprop()
    df_current = sample_data_dead_dec(current_sample)
    csv_output_dead(df_current, current_sample)
    xax=df_current.DateTime
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig = go.Figure([go.Scatter(x=df_current['DateTime'], y=df_current['Rate'])])
    fig.update_xaxes(rangeslider_visible=True)
    #print(df_current.head())
    fig.add_trace(go.Scatter(x=xax, y=df_current.Permeability,
                            name="Permeability", line_color='Blue', opacity=.5, hovertext=df_current.Comment))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Upstream Pressure'],
                            name="Upstream", line_color='red', yaxis="y2"))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Downstream Pressure'],
                            name="Downstream", line_color='purple', yaxis="y2"))
    #fig.add_trace(go.Scatter(x=xax, y=df_current['rollingq'],
    fig.add_trace(go.Scatter(x=xax, y=df_current.Rate,
                            name="Flow Rate", line_color='Green', yaxis="y3", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current.qdp,
                            name="q over dp", line_color='Black', yaxis="y4", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Confining Pressure'],
                            name="confining pressure", line_color='Orange', yaxis="y5", opacity=1))
    title = '| Sample ID: ' + current_sample['client'] + ' ' +  current_sample['sample ID'] + ' | Vessel: ' + \
        current_sample['vessel'] + ' | Pump: ' + current_sample['Pump'][-1] + ' | Temperature: '+ \
            str(current_sample['temperature']) + ' <br> | Comments: '+current_sample['comment'] + ' | Visc: '+str(current_sample['fluid'])
    fig.update_layout(plot_bgcolor = "#f3f7fd", paper_bgcolor = "#f3f7fd", title_text=title, title_font_color = "#5c0325", xaxis_rangeslider_visible=True, xaxis=dict(domain=[0, 0.85]), hovermode='x',
                    yaxis=dict(title="Permeability - nD", titlefont=dict(color="Blue"), anchor="free",
                                tickfont=dict(color="Blue"), range=[current_sample['perm_min'], current_sample['perm_max']]),
                    yaxis2=dict(title="Pressure - psia", titlefont=dict(color="Red"), tickfont=dict(
                        color="Red"), anchor="free", overlaying="y", side="right", position=0.85, range=[0, 10000]),
                    yaxis3=dict(title="Flow rate - cc/min", titlefont=dict(color="Green"), tickfont=dict(
                        color="Green"), anchor="free", overlaying="y", side="right", position=0.89, range=[0, .0005]),
                    yaxis4=dict(title="q over dp", titlefont=dict(color="Black"), tickfont=dict(
                        color="Black"), anchor="free", overlaying="y", side="right", position=0.93, range=[0, .000001]),
                    yaxis5=dict(title="confining pressure", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.97, range=[0, 10000]))
    return fig

@app.callback(Output('live-update-graph5', 'figure'),
              [Input('interval-component', 'n_intervals')])
# m is the sheet name
def plot5(n):
    current_sample = sample(samplesheet, 'EOR5').sampleprop()
    df_current = sample_data_dec(current_sample)
    csv_output(df_current, current_sample)
    xax=df_current.DateTime
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig = go.Figure([go.Scatter(x=df_current['DateTime'], y=df_current['Rate'])])
    fig.update_xaxes(rangeslider_visible=True)
    #print(df_current.head())
    fig.add_trace(go.Scatter(x=xax, y=df_current.Permeability,
                            name="Permeability", line_color='Blue', opacity=.5, hovertext=df_current.Comment))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Upstream Pressure'],
                            name="Upstream", line_color='red', yaxis="y2"))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Downstream Pressure'],
                            name="Downstream", line_color='purple', yaxis="y2"))
    #fig.add_trace(go.Scatter(x=xax, y=df_current['rollingq'],
    fig.add_trace(go.Scatter(x=xax, y=df_current.Rate,
                            name="Flow Rate", line_color='Green', yaxis="y3", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current.qdp,
                            name="q over dp", line_color='Black', yaxis="y4", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Confining Pressure'],
                            name="confining pressure", line_color='Orange', yaxis="y5", opacity=1))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Cumulative Volume'],
                            name="Cumulative Volume", line_color='Magenta', yaxis="y6", opacity=1))
    title = '| Sample ID: ' + current_sample['client'] + ' ' +  current_sample['sample ID'] + ' | Vessel: ' + \
        current_sample['vessel'] + ' | Pump: ' + current_sample['Pump'][-1] + ' | Temperature: '+ \
            str(current_sample['temperature']) + ' <br> | Comments: '+current_sample['comment'] + ' | Visc: '+str(current_sample['fluid'])
    fig.update_layout(plot_bgcolor = "#f3f7fd", paper_bgcolor = "#f3f7fd", title_text=title, title_font_color = "#5c0325", xaxis_rangeslider_visible=True, xaxis=dict(domain=[0, 0.8]), hovermode='x',
                    yaxis=dict(title="Permeability - nD", titlefont=dict(color="Blue"), anchor="free",
                                tickfont=dict(color="Blue"), range=[current_sample['perm_min'], current_sample['perm_max']]),
                    yaxis2=dict(title="Pressure - psia", titlefont=dict(color="Red"), tickfont=dict(
                        color="Red"), anchor="free", overlaying="y", side="right", position=0.8, range=[0, 10000]),
                    yaxis3=dict(title="Flow rate - cc/min", titlefont=dict(color="Green"), tickfont=dict(
                        color="Green"), anchor="free", overlaying="y", side="right", position=0.84, range=[0, .0005]),
                    yaxis4=dict(title="q over dp", titlefont=dict(color="Black"), tickfont=dict(
                        color="Black"), anchor="free", overlaying="y", side="right", position=0.88, range=[0, .000001]),
                    yaxis5=dict(title="confining pressure", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.92, range=[0, 10000]),
                    yaxis6=dict(title="Cumulative Volume", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.96, range=[0, 5]))
    return fig

@app.callback(Output('live-update-graph6', 'figure'),
              [Input('interval-component', 'n_intervals')])
# m is the sheet name
def plot6(n):
    current_sample = sample(samplesheet, 'EOR6').sampleprop()
    df_current = sample_data_dec(current_sample)
    csv_output(df_current, current_sample)
    xax=df_current.DateTime
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig = go.Figure([go.Scatter(x=df_current['DateTime'], y=df_current['Rate'])])
    fig.update_xaxes(rangeslider_visible=True)
    #print(df_current.head())
    fig.add_trace(go.Scatter(x=xax, y=df_current.Permeability,
                            name="Permeability", line_color='Blue', opacity=.5, hovertext=df_current.Comment))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Upstream Pressure'],
                            name="Upstream", line_color='red', yaxis="y2"))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Downstream Pressure'],
                            name="Downstream", line_color='purple', yaxis="y2"))
    #fig.add_trace(go.Scatter(x=xax, y=df_current['rollingq'],
    fig.add_trace(go.Scatter(x=xax, y=df_current.Rate,
                            name="Flow Rate", line_color='Green', yaxis="y3", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current.qdp,
                            name="q over dp", line_color='Black', yaxis="y4", opacity=.5))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Confining Pressure'],
                            name="confining pressure", line_color='Orange', yaxis="y5", opacity=1))
    fig.add_trace(go.Scatter(x=xax, y=df_current['Cumulative Volume'],
                            name="Cumulative Volume", line_color='Magenta', yaxis="y6", opacity=1))
    title = '| Sample ID: ' + current_sample['client'] + ' ' +  current_sample['sample ID'] + ' | Vessel: ' + \
        current_sample['vessel'] + ' | Pump: ' + current_sample['Pump'][-1] + ' | Temperature: '+ \
            str(current_sample['temperature']) + ' <br> | Comments: '+current_sample['comment'] + ' | Visc: '+str(current_sample['fluid'])
    fig.update_layout(plot_bgcolor = "#f3f7fd", paper_bgcolor = "#f3f7fd", title_text=title, title_font_color = "#5c0325", xaxis_rangeslider_visible=True, xaxis=dict(domain=[0, 0.8]), hovermode='x',
                    yaxis=dict(title="Permeability - nD", titlefont=dict(color="Blue"), anchor="free",
                                tickfont=dict(color="Blue"), range=[current_sample['perm_min'], current_sample['perm_max']]),
                    yaxis2=dict(title="Pressure - psia", titlefont=dict(color="Red"), tickfont=dict(
                        color="Red"), anchor="free", overlaying="y", side="right", position=0.8, range=[0, 10000]),
                    yaxis3=dict(title="Flow rate - cc/min", titlefont=dict(color="Green"), tickfont=dict(
                        color="Green"), anchor="free", overlaying="y", side="right", position=0.84, range=[0, .0005]),
                    yaxis4=dict(title="q over dp", titlefont=dict(color="Black"), tickfont=dict(
                        color="Black"), anchor="free", overlaying="y", side="right", position=0.88, range=[0, .000001]),
                    yaxis5=dict(title="confining pressure", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.92, range=[0, 10000]),
                    yaxis6=dict(title="Cumulative Volume", titlefont=dict(color="Orange"), tickfont=dict(
                        color="Orange"), anchor="free", overlaying="y", side="right", position=0.96, range=[0, 5]))
    return fig
if __name__ == '__main__':
    app.run_server(debug=True,port=8081,host='10.0.100.140')
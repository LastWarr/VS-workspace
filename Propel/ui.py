# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 08:16:30 2022

@author: dwaradi
"""
from logic import *
import plotly.express as px
import plotly.graph_objects as go
import warnings

# warnings.filterwarnings("ignore")

def getModelList(data):
    return data['Model'].drop_duplicates()

def getModelYearList(data):
    return data['Model_year'].drop_duplicates()

def update_hover_text(trace, points, state):
    global hover_text
    if points.point_inds:
        hover_text = points.trace.text[points.point_inds[0]]
    else:
        hover_text = ''
    return hover_text
"""
==========
Function to create the profit and retail cube 
==========

"""

def plotCube(plotType,data): 

    HoverTemplate = "<br>".join([
        'PromoAmt:%{customdata[4]}',
        'Start Date:%{customdata[3]}',
        'Duration:%{customdata[5]}',
        'Profitability:%{customdata[2]:$.5s}',
        'Profit variance:%{customdata[7]:$.5s}',
        "Retail: %{customdata[0]:0.0f}",
        "Retail variance:%{customdata[6]:0.0f}",
        # "%Retail var2: %{customdata[8]:0.2%}",
        "%Retail var: %{customdata[1]:0.2%}",
        
    ]) 
  #RETAIL CUBE SETTINGS
    if plotType=="retail":
        plotdata = promoGraph(data=data, dataType='retail')
        # graphTitle = "Retail Cube"
        zaxisTitle = "Retail Cube"


    # PROFIT CUBE SETTINGS
    else:
        plotdata = promoGraph(data=data, dataType='profit')
        # graphTitle = "Profitability Cube"
        zaxisTitle = "Profit Cube"

    fig = go.Figure(data=plotdata)
    fig.update_layout(scene = dict(
                      xaxis_title='Duration',
                      yaxis_title='Weeks',
                      zaxis_title=zaxisTitle),
                      legend_title_text = 'Promo Amount',
                      template='plotly_dark', 
                      # title=graphTitle,
                      height = 500,
                      margin=dict(r=20, b=10, l=10))
    fig.update_traces(
      showlegend=True,
      hovertemplate= HoverTemplate,
      
    )
    # hover_text = fig.data[0].on_hover(update_hover_text)
    # print(hover_text)
    # fig.write_html(plotType+'_cube_dark_n.html')
    # fig.show()
    return fig

def plot_Forecast(baseline_date,selected_data,graph_type):
    dt = baseline_with_forecast(baseline_date,selected_data)
    # create a line graph with two y-axes
    if (graph_type == 'cum'):
        fig_forecast = px.line(dt, x='Date', y=['cum_Forecast', 'cum_Adj_Forecast'], title='Cumulative Forecast vs Promo Adj Forecast')
        # fig_forecast.update_layout(yaxis=dict(title='Forecast'), yaxis2=dict(title='Promo Adjusted Forecast', side='right', overlaying='y'))
        fig_forecast.update_traces(mode="lines", hovertemplate ='%{y:.2f}')
    # fig_forecast.show()
    else:
        fig_forecast = px.line(dt, x='Date', y=['Forecast', 'Adj_Forecast'], title='Forecast vs Promo Adj Forecast')
        fig_forecast.update_traces(mode="markers+lines", hovertemplate ='%{y:.2f}')
    fig_forecast.update_layout(yaxis=dict(title='Forecast Units'), yaxis2=dict(title='Promo Adjusted Forecast', side='right', overlaying='y'))
    # fig_forecast.update_traces(mode="markers+lines", hovertemplate ='%{y:.2f}')
    fig_forecast.update_layout(hovermode="x unified")

    return fig_forecast
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 08:16:30 2022

@author: dwaradi
"""
from logic import promoGraph
import plotly.graph_objects as go

def getModelList(data):
    return data['Model'].drop_duplicates()

def getModelYearList(data):
    return data['Model_year'].drop_duplicates()

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
        zaxisTitle = "Retail"


    # PROFIT CUBE SETTINGS
    else:
        plotdata = promoGraph(data=data, dataType='profit')
        # graphTitle = "Profitability Cube"
        zaxisTitle = "Profit"

    fig_profit1 = go.Figure(data=plotdata)
    fig_profit1.update_layout(scene = dict(
                      xaxis_title='Duration',
                      yaxis_title='Weeks',
                      zaxis_title=zaxisTitle),
                      legend_title_text = 'Promo Amount',
                      template='plotly_dark', 
                      # title=graphTitle,
                      margin=dict(r=20, b=10, l=10))
    fig_profit1.update_traces(
      showlegend=True,
      hovertemplate= HoverTemplate
    )
    
    fig_profit1.write_html(plotType+'_cube_dark_n.html')
    # fig_profit1.show()
    return fig_profit1

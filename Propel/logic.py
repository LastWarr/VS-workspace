# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 04:58:02 2022

@author: dwaradi
"""
import pandas as pd
import numpy as np
from data_transformation import * 
import plotly.graph_objects as go
# import warnings

# warnings.filterwarnings("ignore")
##############################################################################
# Aggregate the daily data to weekly ( Not required after we receive forecast at weekly granularity)
def getWeeklyDataWithCYNCY(data,grp_col):
    if 'CY_NCY' in grp_col:
        data_agg = data.groupby(grp_col).agg(
                                    Retail = ('Serial_number','count'),
                                    MSRP_Avg = ('MSRP','mean'),
                                    DealerPrice_Avg = ('DealerPrice','mean'),
                                    Margin = ('Margin','mean')
                                ).reset_index().sort_values(['Model','Date'])
    else:
        data_agg = data.groupby(grp_col).agg( DealerPrice_Avg = ('DealerPrice_Avg','mean'),
                                                         Retail = ('Retail','sum'),
                                                         Margin = ('Margin','mean')).reset_index().sort_values(['Model','Date'])

    return data_agg

################################################################################

def getModelData(df):
    # Assign dummy margin 
    # Outlander 1000 - .3 , Outlander 850 - .25, Outlander 450 - .18
    df = assignMargin(df,'OUTLANDER 450',0.18)
    df = assignMargin(df,'OUTLANDER 850',0.25)
    df = assignMargin(df,'OUTLANDER 1000',0.30)

    # Aggregate the SKU level data to Weekly data grouped by Model, CY_NCY
    grp_col = ['Model','CY_NCY','Date'] 
    data_agg = getWeeklyDataWithCYNCY(df,grp_col)

    # Dummy data code
    # Delete code once forecast is obtained
    # Separating the CY and NCY units in Retail
    df_pivot = pd.pivot_table(data_agg, index=['Model', 'Date'],
                              columns=['CY_NCY'],  
                              aggfunc={'Retail': np.sum},
                              fill_value=0)

    df_pivot.columns = ['_'.join(map(str, c)).strip('_') for c in df_pivot] # Name the pivoted columns
    df_pivot.reset_index(inplace=True)

    # Granularity at weekly level per model  - Each date has 1 row for a model
    grp_col = ['Model','Date']
    data_agg1 = getWeeklyDataWithCYNCY(data_agg,grp_col)


    model_data = data_agg1.merge(df_pivot,on=['Model','Date']) # Merge to get the data used for scenario modelling
    model_data['cumForecast']=model_data.groupby(['Model'])['Retail'].cumsum()
    model_data.rename(columns={'Retail':'Forecast','Retail_CY':'Forecast_CY',
                  'Retail_NCY':'Forecast_NCY'},inplace=True)
    return model_data

def promo_uplift(dealer_price,coe,promo_amt):
    return coe * promo_amt/dealer_price

def adj_Forecast(forecast,promo_uplift,penalty):
    return round(forecast*(1+promo_uplift*penalty),2)

def profit(units,margin,dealer_price):
    return round(units*margin*dealer_price,2)

def profit_calculations(model_input,promo_amt,duration,dealer_price,coe,ncypenalty):

    # create an empty dataframe
    df_calc = pd.DataFrame()
    # loop through each date
    for index,row in model_input.iterrows():
        dprice = dealer_price[row['Model']]['Dealer_price']
        margin = dealer_price[row['Model']]['Margin']
        model = row['Model']
        # Checking the index for the last 15 weeks
        # if index <= model_input.shape[0]-len(duration):
        # Loop through all the promo amount values 
        for value in range(len(promo_amt)):
            
            adj_ForecastCY = 0
            adj_ForecastNCY = 0
            original_F = 0
            f_CY = 0
            f_NCY = 0
            f = []
            adj_F = []
            profit_promo = 0
            profit_nopromo = 0
            promo_cost = 0                         

            promoamt = promo_amt[value]
            
            duration_flag = 1
            #Loop through for a duration 
        
            for inner_index, inner_row in model_input[index:index+len(duration)].iterrows():
                # print(promoamt,row['Date'],model,duration_flag,promo_amt[value])               
                # Adjusted forecast for CY and NCY            
                p_uplift = promo_uplift(dprice,coe,promo_amt[value])
                forecast_CY = inner_row['Forecast_CY']
                forecast_NCY = inner_row['Forecast_NCY']
                f_CY = f_CY + forecast_CY
                f_NCY = f_NCY + forecast_NCY
                adj_FCY =  adj_Forecast(forecast_CY,p_uplift,1)
                adj_NCY = adj_Forecast(forecast_NCY,p_uplift,ncypenalty)
                adj_ForecastCY = adj_ForecastCY +adj_FCY
                adj_ForecastNCY = adj_ForecastNCY + adj_NCY

                # Profit for both with Promo and without Promo
                profit_promo = profit(adj_ForecastCY,margin,dprice) + profit(adj_ForecastNCY,(margin-ncypenalty),dprice)
                profit_nopromo = profit(f_CY,margin,dprice) + profit(f_NCY,(margin-ncypenalty),dprice)

                # Adjusted forecast after promotional uplift            
                original_F = f_CY + f_NCY
                new_F = adj_ForecastCY + adj_ForecastNCY

                f.append(forecast_CY+forecast_NCY)
                a_f = adj_FCY+adj_NCY
                adj_F.append(round(a_f,2))

                # Create the row for output dataframe
                promo_row = pd.DataFrame([[row['Date'],model,duration_flag,promo_amt[value],original_F,new_F,adj_ForecastCY,adj_ForecastNCY,profit_promo,profit_nopromo,f.copy(),adj_F.copy()]],
                                            columns=['Date','Model','Duration','PromoAmt','Forecast','Adj_Forecast','Adj_ForecastCY','Adj_ForecastNCY','Profit_Promo','Profit_NoPromo','Weekly_Forecast','Weekly_Adj_Forecast'])
                # add the new dataframe to the original dataframe
                # df_calc = df_calc.append(promo_row)
                df_calc = pd.concat([df_calc, promo_row])
                # print(df_calc)
                duration_flag += 1

    df_calc['incremental_Retail'] = df_calc.Adj_Forecast - df_calc.Forecast
    df_calc['PromoCost'] = round(df_calc.PromoAmt * df_calc.Adj_Forecast,2)
    df_calc['incremental_Profit'] = df_calc.Profit_Promo - df_calc.Profit_NoPromo - df_calc.PromoCost

    initial_profit = df_calc[(df_calc.Duration == 1) & (df_calc.PromoAmt == 0)]
    Total_P = initial_profit.Profit_NoPromo.sum()
    Total_R = initial_profit.Forecast.sum()
    df_calc['Profitability'] = Total_P + df_calc.incremental_Profit
    df_calc['Retail'] = Total_R + df_calc.incremental_Retail
    df_calc['Retail_var1'] = df_calc.Retail/Total_R
    df_calc['Retail_var'] = df_calc.incremental_Retail/Total_R
    # print(df_calc)

    return df_calc

"""
===========
Function to create graph coordinates for each promo discount value
===========
"""

def promoGraph(data, dataType):
  
  plotData = []
  promoDiscount = [x for x in range(0, 3250, 250)] #list of promo discount values from 0 to 3000 ) 
  colorList = [ [[0, 'rgb(194,197,204)'], [1, 'rgb(194,197,204)']], [[0, 'rgb(25,25,112)'], [1, 'rgb(25,25,112)']],
   [[0, 'rgb(221,160,221)'], [1, 'rgb(221,160,221)']], [[0, 'rgb(178,34,34)'], [1, 'rgb(178,34,34)']], [[0, 'rgb(107,142,35)'], [1, 'rgb(107,142,35)']],
   [[0, 'rgb(255,127,80)'], [1, 'rgb(255,127,80)']],[[0, 'rgb(255,192,203)'], [1, 'rgb(255,192,203)']],[[0, 'rgb(230,190,138)'], [1, 'rgb(230,190,138)']],
   [[0, 'rgb(0,128,128)'], [1,'rgb(0,128,128)']],[[0, 'rgb(135,206,250)'], [1, 'rgb(135,206,250)']],[[0, 'rgb(224,255,255)'], [1, 'rgb(224,255,255)']],
   [[0, 'rgb(255,239,213)'], [1, 'rgb(255,239,213)']],[[0, 'rgb(144,238,144)'], [1, 'rgb(144,238,144)']]]#list of colour values for the graph 
  
  cols = ['Retail', 'Retail_var','Profitability','Date','PromoAmt','Duration','incremental_Retail','incremental_Profit','Retail_var1']
  x = [x for x in range(1, 16, 1)] 

  if dataType=="profit":
    for i in range(len(promoDiscount)): 
      promo = data[data.PromoAmt == promoDiscount[i]] #segments the data by promo amount 
      promo['cdata'] = [[e for e in row if e==e] for row in promo[cols].values.tolist()] #List the values to display in tooltip        
      plotpromo = promo.groupby(['Duration'],group_keys='True')['Profitability'].apply(list).reset_index()
      z = pd.DataFrame(plotpromo.Profitability.values.tolist()).transpose().to_numpy()
      custdata = promo.groupby(['Duration'],group_keys='True')['cdata'].apply(list).reset_index()
      
      plotData.append(go.Surface(z=z,
                                      colorscale=colorList[i],
                                      showscale=False,
                                      customdata = custdata.cdata.values,
                                      name='Promo' + str(promoDiscount[i]))) #return the coordinates for the graph
      
  else:
    for i in range(len(promoDiscount)): 
      promo = data[data.PromoAmt == promoDiscount[i]]
      promo['cdata'] = [[e for e in row if e==e] for row in promo[cols].values.tolist()] #List the values to display in tooltip        
      plotpromo = promo.groupby(['Duration'],group_keys='False')['Retail'].apply(list).reset_index()
      z = pd.DataFrame(plotpromo.Retail.values.tolist()).transpose().to_numpy()
      custdata = promo.groupby(['Duration'],group_keys='False')['cdata'].apply(list).reset_index()
      
      plotData.append(go.Surface(z=z,
                                 colorscale=colorList[i],
                                 showscale=False,
                                 customdata = custdata.cdata.values,
                                 name='Promo' + str(promoDiscount[i])))
  
  return plotData



def baseline_with_forecast(forecast_baseline,forecast_df):
    forecast_df.reset_index(drop=True,inplace=True)
    forecast_baseline.reset_index(drop=True,inplace=True)
    # Get index of the date choosen and the duration
    row_index = forecast_baseline.loc[forecast_baseline['Date'] == forecast_df.Date[0]].index[0]
    # update the values in the selected rows
    forecast_baseline.loc[row_index:row_index+forecast_df.Duration[0]-1, 'Adj_Forecast'] = forecast_df['Weekly_Adj_Forecast'][0]
    # convert single value lists to values
#     forecast_baseline.loc[:,'Weekly_Adj_Forecast'] = forecast_baseline['Weekly_Adj_Forecast'].apply(lambda x: x[0] if isinstance(x, list) else x)
    forecast_baseline.loc[:,'cum_Forecast'] = forecast_baseline['Forecast'].cumsum()
    forecast_baseline.loc[:,'cum_Adj_Forecast'] = forecast_baseline['Adj_Forecast'].cumsum()
    return forecast_baseline
import pandas as pd
from logic import *
from data_transformation import *
from dateutil.relativedelta import relativedelta
from ui import plot_Forecast
import warnings
import streamlit as st

warnings.filterwarnings("ignore")
# from pathlib import Path

# base_path = Path(__file__).parent
# datafile = (base_path / "Static_files/Prototype_dt18-21.csv").resolve()
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


def getStateData(df,state_choice):
    df = df[df.State.isin(state_choice)]
    df = df.groupby(['Model','Date','Country']).agg(Forecast_CY = ('Forecast_CY','sum'),
                                                                                Forecast_NCY = ('Forecast_NCY','sum'),
                                                                                Forecast = ('Forecast','sum')).reset_index()
    # df['State'] = state_list
    df['Country'] = 'US'
    df['cumForecast'] = df.groupby(['Model'])['Forecast'].cumsum()

    return df

@st.cache_data(show_spinner="Please wait while we load the model...")
def get_profitability_data(m_data,promo_amt,duration,dealer_price,coe,ncypenalty):
    # define the start date
    # start_date = m_data.Date.min()
    # add 2 years and 15 weeks to the start date
    # end_date = start_date + relativedelta(years=2, weeks=15)

    # generate the dates for 2 years and 15 weeks
    # dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')

    model_input = m_data[['Model', 'Date','Forecast_CY','Forecast_NCY']]

    # model_input = model_input[(model_input.Date >= start_date) & (model_input.Date <= end_date)]
    model_input = model_input.reset_index()

    data = profit_calculations(model_input,promo_amt,duration,dealer_price,coe,ncypenalty)
    
    
    return data

@st.cache_data()
def load_country_data(url):
  
    
    df = pd.read_csv(url,low_memory=False)
        # Modify data
    df['Date'] = df.apply(lambda x: getWeeklyStartDate(x.Registration_date), axis=1) # Get weekly start date
    df['Year'] = pd.DatetimeIndex(df['Registration_date']).year
    df = df.assign(CY_NCY=df.apply(getCYNCY, axis=1)) # Assign Current, Non current flag for ORV

    model_data = getModelData(df) 
    
    return model_data

# @st.cache_data()
def load_state_data(url):
    df = pd.read_csv(url,low_memory=False)
        
    return df
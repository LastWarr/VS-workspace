import streamlit as st
import pandas as pd
from ui import *

with st.container():
    if 'plotData' not in st.session_state:
        st.write("Please choose the model and coefficient of elasticity and run the calculations in Home page to choose a scenario for deep dive. Thank you!")
        
    else:               
        data = st.session_state["plotData"]
        data.loc[:,'Date'] = pd.to_datetime(data['Date'])
        data.loc[:,'Date'] = data['Date'].dt.date
        data = data.sort_values(['Date','PromoAmt','Duration'], ascending=True)
        datecol, modelcol,durationcol, promoamtcol = st.columns([1,1,1,1])
        cumforecast_graph,weeklyforecast_graph = st.columns([1,1])
        model = data.Model.unique()
        date = data.Date.unique()
        # # Convert the 'date_time' column to a datetime data type
        # date = pd.to_datetime(date)
        # date = date.dt.date
        duration = data.Duration.unique()
        promoamt = data.PromoAmt.unique()

        forecast_graph = data.loc[:,['Date', 'Model', 'Duration', 'PromoAmt', 'Forecast','Adj_Forecast','Weekly_Forecast','Weekly_Adj_Forecast']]
        forecast_baseline = forecast_graph[(forecast_graph['PromoAmt'] == 0) & (forecast_graph['Duration'] == 1)]
        forecast_baseline = forecast_baseline.loc[:,['Date', 'Model','Forecast','Adj_Forecast']]


        with st.container():
            with datecol:
                # Choose the start date to show the 2D graph
                start_date_choice = st.selectbox('Date',date)
                
            with modelcol:
                # streamlit code for choosing model
                models_choice = st.selectbox("Model", model)
                

            with durationcol:
                # Choose the start date to show the 2D graph
                duration_choice = st.selectbox('Duration',duration)
                
            with promoamtcol:
                # streamlit code for choosing model
                promo_choice = st.selectbox("Promo Amount", promoamt)
            
        with st.container():
            forecast_df = forecast_graph[(forecast_graph['PromoAmt'] == promo_choice ) & (forecast_graph['Duration'] == duration_choice) & 
                                        (forecast_graph['Date'] == start_date_choice) & (forecast_graph['Model'] == models_choice)]
            st.dataframe(forecast_df)
            
        with st.container():
            # st.dataframe(forecast_baseline)
            if st.button('Create Forecast Graph'):
                with cumforecast_graph:
                    forecastplot_data = plot_Forecast(forecast_baseline,forecast_df,'cum')
                    st.plotly_chart(forecastplot_data, use_container_width=True)
                with weeklyforecast_graph:
                    forecastplot_data = plot_Forecast(forecast_baseline,forecast_df,'weekly')
                    st.plotly_chart(forecastplot_data, use_container_width=True)
            else:
                st.write('Choose the Promotion scenario to run and click the button')
            
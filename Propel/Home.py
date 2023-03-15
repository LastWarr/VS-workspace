
import pandas as pd
from data import *
from ui import *
import time
import streamlit as st
import warnings

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide")
edit_footer = """
<style>
footer{
    visibility : hidden;
}
footer:before{
    content: 'version 2.4';
    display:block;
    position:relative;
}
</style>
"""
# Load data

#Retail filter
# print(model_data.head())
# model_data

# print(plot_data.head())
# plot_data.to_csv('plotdata.csv',index=False)
# Add header and a subheader
# st.header("Propel: Programs & Promotions ")

####################################################################    
    # Use columns to display the three dataframes side-by-side along with their headers
   
if __name__ == "__main__":
    # session = create_session_object()
    st.title('Prototype v2.6')
    st.markdown(edit_footer,unsafe_allow_html=True)
    datafile = 'Propel/Static_files/Prototype_dt18-21.csv'
    model_data = load_country_data(datafile)

    state_forecast_file = 'Propel/Static_files/forecast_state.csv'
    state_forecast = load_state_data(state_forecast_file)

    # Intitializing Promo amount from $250 to $3000  
    promo_amt = [x for x in range(0, 3250, 250)] # Promo range 0 - 3000 with increment of 250

    # Add penalty/Bonus based on Duration (Using static data)
    # This is a score that is derived based on - Market share, Forward cannabalization, Marketing spend
    duration = pd.read_csv('Propel/Static_files/Promo_penalty_bonus.csv')
    duration = dict(duration.values) # Penalty/bonus due to duration

    # Dictonary of dealer price by Model
    dealer_price = model_data.groupby(['Model']).agg(Dealer_price = ('DealerPrice_Avg','mean'),Margin = ('Margin','mean'))
    dealer_price.Dealer_price = dealer_price.Dealer_price.round(2)
    dealer_price = dealer_price.to_dict(orient="index")  # Dealer price dictionary
    # print(dealer_price)
    ###############################################################################
    data_input = st.radio("Choose Granularity",('Country','State wise'))
    if data_input == 'Country':
        # country_input_data = st.checkbox('Country Data',value=True)
        country_input_data = True
        state_input_data = False
    else:
        # state_input_data = st.checkbox('State wise dummy data')
        country_input_data = False
        state_input_data = True

    # List models in the data
    # models = model_data['Model'].drop_duplicates()
    if country_input_data:
        models = model_data['Model'].drop_duplicates()
        # models_choice = st.sidebar.selectbox("Choose Model", models)
    if state_input_data:
        models = state_forecast['Model'].unique().tolist()
        state_list = state_forecast['State'].unique().tolist()
        # state_list.insert(0, "All")
        country = state_forecast['Country'].drop_duplicates()
    #  Static values 
    behind_forecast = 0.8
    ncypenalty = .075

    minRetail = 0
    maxRetail = 1000

    coecol, modelcol,countrycol,statecol2 = st.columns([1, 1, 1, 1])
    statecol,allstatecol = st.columns([2,.3])
    minretailcol,placeholdercol1,maxretailcol,placeholdercol2,minprofitcol,placeholdercol3,maxprofitcol,placeholdercol4 = st.columns([1,.1,1,1.5,1,0.1,1,1.5])
    # minretailcol, maxretailcol,dummycol = st.columns([1,1,6])
    profitcol, retailcol = st.columns(2)

    # fig.data[0].on_hover(update_hover_text)


    with st.container():
        with coecol:
            # Choose the coefficient of elasticity - Currently an option later will be integrated to the calculation
            # coe = 5
            coe = st.number_input('Elasticity coeffiecient',0.0,15.0,value=5.0)
            coe = abs(coe)
        
        with modelcol:
            # streamlit code for choosing model
            models_choice = st.selectbox("Model", models)
            # models_choice = 'OUTLANDER 1000'
            if country_input_data:
                m_data = model_data[model_data['Model'].values == models_choice]
            elif state_input_data:
                m_data = state_forecast[state_forecast['Model'].values == models_choice]

        with  countrycol:
            # country = ['NA','US','CA']
            if state_input_data:
                country_choice = st.selectbox("Country",country)
                
                m_data = m_data[m_data['Country'].values == country_choice]
    with st.container():
        if state_input_data: 
            with allstatecol: 
                    all = st.checkbox("Select All",True)
            with statecol:         
                    if all:
                        state_choice = st.multiselect("State",state_list,state_list)
                        m_data = getStateData(m_data,state_choice)
                    else:
                        state_choice = st.multiselect("State",state_list)
                        if len(state_choice) >= 1:
                            m_data = getStateData(m_data,state_choice)
                        else:
                            m_data = getStateData(m_data,state_list)
            
    with st.container():
        if st.button('Load Cube'):
            plot_data = get_profitability_data(m_data=m_data,promo_amt=promo_amt,duration=duration,dealer_price=dealer_price,coe=coe,ncypenalty=ncypenalty)

            with st.container():
                retail_min = int(plot_data.Retail.min())
                retail_max = int(plot_data.Retail.max())

                with minretailcol:
                    n_retail_min = st.number_input("Retail min", value=retail_min,min_value = retail_min,max_value=retail_max-1,step=5)
                    
                with maxretailcol:
                    n_retail_max = st.number_input("Retail max", value=retail_max,min_value =retail_min+1,max_value=retail_max,step=5)

                plot_data = plot_data[(plot_data.Retail >= n_retail_min-.99) & (plot_data.Retail <= n_retail_max+.99)]

                profit_min = int(plot_data.Profitability.min())
                profit_max = int(plot_data.Profitability.max())


                with minprofitcol:
                    n_profit_min = st.number_input("Profitability min", value=profit_min,min_value = profit_min,max_value=profit_max-1,step=5)
                    
                with maxprofitcol:
                    n_profit_max = st.number_input("Profitability max", value=profit_max,min_value = profit_min+1,max_value=profit_max,step=5)

                plot_data = plot_data[(plot_data.Profitability >= n_profit_min-.99) & (plot_data.Profitability <= n_profit_max+.99)]

                n_retail_min = int(plot_data.Retail.min())
                n_retail_max = int(plot_data.Retail.max())
                n_profit_min = int(plot_data.Profitability.min())
                n_profit_max = int(plot_data.Profitability.max())
        
            with st.container():
                with profitcol:
                    st.subheader('Profit cube')
                    profit_graph = plotCube('profit',plot_data)

                    minRetail = plot_data.Retail.min().astype(int)
                    maxRetail = plot_data.Retail.max().astype(int)

                    st.plotly_chart(profit_graph, use_container_width=True)
                    # profit_graph.data[0].on_hover(update_hover_text)
                    # print(hover_text)

                with retailcol:
                    st.subheader('Retail cube')
                    retail_graph = plotCube('retail',plot_data)
                    minProfit = plot_data.Profitability.min().astype(int)
                    maxProfit = plot_data.Profitability.max().astype(int)

                    st.plotly_chart(retail_graph, use_container_width=True)
                    
            
            st.session_state['plotData'] = plot_data
        

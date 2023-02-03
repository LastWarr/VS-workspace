
import pandas as pd
from data import *
from ui import *
import streamlit as st

# Load data

datafile = 'Propel/Static_files/Prototype_dt18-21.csv'
df = pd.read_csv(datafile,low_memory=False)

# Modify data
df['Date'] = df.apply(lambda x: getWeeklyStartDate(x.Registration_date), axis=1) # Get weekly start date
df['Year'] = pd.DatetimeIndex(df['Registration_date']).year
df = df.assign(CY_NCY=df.apply(getCYNCY, axis=1)) # Assign Current, Non current flag for ORV

model_data = getModelData(df) # All the model and forecast data

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

###############################################################################

# Choose the coefficient of elasticity - Currently an option later will be integrated to the calculation
# coe = 5
coe = st.sidebar.number_input('Coefficient of elasticity',-10.0,10.0,value=-3.0)
coe = abs(coe)
# List models in the data
models = model_data['Model'].drop_duplicates()

# streamlit code for choosing model
models_choice = st.sidebar.selectbox("Choose Model", models)
# models_choice = 'OUTLANDER 1000'
m_data = model_data[model_data['Model'].values == models_choice]



# models_choice = st.sidebar.selectbox("Choose Model", models)

#  Static values 
behind_forecast = 0.8
ncypenalty = .075

plot_data = get_profitability_data(m_data=m_data,promo_amt=promo_amt,duration=duration,dealer_price=dealer_price,coe=coe,ncypenalty=ncypenalty)

retail = [int(plot_data.Retail.min()),int(plot_data.Retail.max())]
#Retail filter
# print(model_data.head())
# model_data
retail = st.sidebar.slider("Retail", int(retail[0]), int(retail[1]), (int(retail[0]),(int(retail[1]))))
print(retail)
plot_data = plot_data[(plot_data.Retail >= retail[0]) & (plot_data.Retail <= retail[1])]
print(plot_data.head())
# plot_data.to_csv('plotdata.csv',index=False)
# Add header and a subheader
st.header("Propel: Programs & Promotions ")

  

####################################################################    
    # Use columns to display the three dataframes side-by-side along with their headers
def load_page():
    minRetail = 0
    maxRetail = 1000
    col1, col2 = st.columns(2)
    with st.container():
        with col1:
            st.subheader('Profit cube')
            profit_graph = plotCube('profit',plot_data)

            minRetail = plot_data.Retail.min().astype(int)
            maxRetail = plot_data.Retail.max().astype(int)
            print(minRetail," ",maxRetail)
            # retail_range = st.slider('Choose Retail range',minRetail, maxRetail, (minRetail, maxRetail))
            # retail_range = st.slider('Enter Retail range',min_value= minRetail,max_value=maxRetail

            st.plotly_chart(profit_graph, use_container_width=True)
        with col2:
            st.subheader('Retail cube')
            retail_graph = plotCube('retail',plot_data)
            minProfit = plot_data.Profitability.min().astype(int)
            maxProfit = plot_data.Profitability.max().astype(int)
            # profit_range = st.slider('Choose Profit range', minProfit,maxProfit,(minProfit,maxProfit))

            st.plotly_chart(retail_graph, use_container_width=True)
            
   
if __name__ == "__main__":
    # session = create_session_object()
    load_page()
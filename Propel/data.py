import pandas as pd
from logic import *
from data_transformation import *
from dateutil.relativedelta import relativedelta
from ui import plot_Forecast
import warnings

warnings.filterwarnings("ignore")
# from pathlib import Path

# base_path = Path(__file__).parent
# datafile = (base_path / "Static_files/Prototype_dt18-21.csv").resolve()

def get_profitability_data(m_data,promo_amt,duration,dealer_price,coe,ncypenalty):
    # define the start date
    start_date = m_data.Date.min()
    # add 2 years and 15 weeks to the start date
    end_date = start_date + relativedelta(years=2, weeks=15)

    # generate the dates for 2 years and 15 weeks
    # dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')

    model_input = m_data[['Model', 'Date','Forecast_CY','Forecast_NCY']]

    model_input = model_input[(model_input.Date >= start_date) & (model_input.Date <= end_date)]
    model_input = model_input.reset_index()

    data = profit_calculations(model_input,promo_amt,duration,dealer_price,coe,ncypenalty)
    
    
    return data
# Library Requirements 
# import os
import pandas as pd
# import numpy as np
from datetime import datetime, timedelta
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
import random
import warnings
warnings.filterwarnings(action='once')


##############################################################################
# Temporary code to Read data - this should be replaced with database query
def read_data(filename,filetype):
    if filetype == 'csv':
        return pd.read_csv(filename)
    elif filetype == 'xlsx':
        return pd.read_excel(filename)
    else:
        print('Unsupported filetype')

##############################################################################
# Get the start day of the week 
# Eg: 2022-11-17 is a Thru, the function return start day is 11-13-2022 i.e Sun
def getWeeklyStartDate(day):
    dt = datetime.strptime(day, '%Y-%m-%d')
    start = dt - timedelta(days=dt.weekday()+1)
    return start

# Assign current year - CY and non current year NCY for ORV (current scope)
# ORV Season Jul 1 - Jun 30 
# Need to add other product lines
def getCYNCY(x):
    if ((x.Month > 6) and (x.Model_Year == (x.Year+1))) | ((x.Month <= 6) and (x.Model_Year == x.Year)):
        return 'CY'
    else: 
        return 'NCY'
 
##############################################################################    
# Can delete this code when we integrate with database - This is used to create dummy data
# Function to generate random numbers and append them
# start = starting range,
# end = ending range
# num = number of elements needs to be appended
def getRand(start, end, num):
    res = []
    for j in range(num):
        res.append(random.randint(start, end))
 
    return res

##############################################################################
# Returns data for the range specified

def getCustomRange(*args):
    s = slice(*args)
    start, stop, step = s.start, s.stop, s.step
    if 0 == step:
        raise ValueError("range() arg 3 must not be zero")
    i = start
    while i < stop if step > 0 else i > stop:
        yield i
        i += step
        
##############################################################################

#This input will be provided by finance
# create dummy margin data
def assignMargin(data,model,margin):
    data.loc[data['Model'] == model, 'Margin'] = margin
    return data
    
##############################################################################
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 19:00:50 2022

@author: Tomasz
"""

#Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import pandas_datareader.data as pdr
from datetime import datetime, timedelta
import plotly.graph_objects as go
from scipy.stats import linregress
from scipy.ndimage.filters import gaussian_filter1d
from scipy.signal import argrelextrema

#Layout settings
st.set_page_config(layout="wide")

#Define functions
#Function to calculate trend
def calculate_trend(data, start, end):
    '''
    Calculate the trend for specific period
    
    Input:
    - data - dataframe time series data including Close price and Number which indicates row number
    - start - integer indicating period starting row number
    - end - integer indicating period end row number
    Output:
    - data - dataframe
    '''
    
    #Filter period data
    data_high = data.loc[start:end].copy()
    data_low = data.loc[start:end].copy()
    
    #Identify high
    while len(data_high)>2:
        slope_high, intercept_high, _, _, _ = linregress(x=data_high.index, y=data_high['Close'])
        data_high = data_high.loc[data_high['Close'] > slope_high * data_high.index + intercept_high]
    #Identify low    
    while len(data_low)>2:   
        slope_low, intercept_low, _, _, _ = linregress(x=data_low.index, y=data_low['Close'])
        data_low = data_low.loc[data_low['Close'] < slope_low * data_low.index + intercept_low]
    
    try:
        if (slope_high < 0) & (slope_low < 0):
            data.loc[start:end-1, 'Uptrend'] = slope_high * data.loc[start:end-1].index + intercept_high
        elif (slope_high > 0) & (slope_low > 0):
            data.loc[start:end-1, 'Downtrend'] = slope_low * data.loc[start:end-1].index + intercept_low
        else:
            data.loc[start:end-1, 'Uptrend'] = slope_high * data.loc[start:end-1].index + intercept_high
            data.loc[start:end-1, 'Downtrend'] = slope_low * data.loc[start:end-1].index + intercept_low
    except:
        pass
    
    return stock


def plot_stock(stock):
    '''
    Print stock graph with trendlines and moving average
    
    Parameters
    ----------
    stock : DataFrame

    Returns
    -------
    Plotly graph
    '''
    
   
    trace1 = go.Scatter(
        x = stock.Date,
        y = stock.Close,
        mode = 'lines',
        name = 'Stock',
        line_color = 'rgb(204,229,255)',
        line_width = 3
        )

    trace2 = go.Scatter(
        x = stock.Date,
        y = stock.Downtrend,
        mode = 'lines',
        name = 'Upward Trend',
        line_color = 'rgb(0,255,0)'
        )
 
    trace3 = go.Scatter(
        x = stock.Date,
        y = stock.Uptrend,
        mode = 'lines',
        name = 'Downward Trend',
        line_color = 'rgb(255,0,0)'
        )

    
    trace4 = go.Scatter(
        x = stock.Date,
        y = stock.sma,
        mode = 'lines',
        name = '50-day Moving Average',
        line_color = 'rgb(173,216,230)'
        )
    
    layout = go.Layout(
        title = security,
        xaxis = {'title' : "Date"},
        yaxis = {'title' : "Close"},
        plot_bgcolor='rgb(14,17,23)'
        )
    fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)
    fig.update_layout(autosize=False, width=1200)
    fig.update_xaxes(showgrid=True, gridwidth=0.3, gridcolor='rgb(71,81,91)',
                     dtick="M1", tickformat="%b\n%Y",
                     rangebreaks=[dict(bounds=["sat", "mon"]), dict(values=[date_start, date_end])])
    fig.update_yaxes(showgrid=True, gridwidth=0.3, gridcolor='rgb(71,81,91)')
    return fig


#Body
st.title('Stock Analysis')
st.markdown("""
Highlight stock trends
""")

#Sidebar
st.sidebar.header('Select stock')

#Download SP500 companies
@st.cache
def download_SP500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    return html[0][['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry']]
sp500 = download_SP500()

# Sidebar - Sector selection
sectors = sorted( sp500['GICS Sector'].unique() )
select_sector = st.sidebar.multiselect('Sector', sectors, sectors)

# Sidebar - Industry selection
#industries = sorted( sp500['GICS Sub-Industry'].unique() )
#select_industry = st.sidebar.multiselect('Industry', industries, industries)

# Filtering data
sp500_sector = sp500[sp500['GICS Sector'].isin(select_sector)]['Symbol']
symbol = st.sidebar.selectbox('Symbol', list(sp500_sector))
security = sp500[sp500['Symbol'] == symbol]['Security'].item()

#Download stock historical data
date_end = datetime.today().date()
date_start = date_end - timedelta(days = 600)

stock = pdr.get_data_stooq('{}.US'.format(symbol), start=date_start, end=date_end)
#Sort by ascending date
stock = stock.sort_index(ascending=True)
#Move dates to column
stock['Date'] = stock.index
#Calculate 50day moving average
stock['sma'] = gaussian_filter1d(stock['Close'].rolling(60).mean(), 6)
stock = stock.dropna()
stock.reset_index(drop=True, inplace=True)
#Calculate SMA gradient to identify gradient change
stock['sma_gradient'] = np.gradient(stock['sma'])

#Find extrema
maxima = np.array(argrelextrema(stock['sma_gradient'].values, np.greater, order=20)).reshape(-1)
minima = np.array(argrelextrema(stock['sma_gradient'].values, np.less, order=20)).reshape(-1)
extrema = np.sort(np.append((np.append(minima, maxima)), np.array([0, len(stock)-1])))
extrema_values = stock.filter(items = extrema, axis=0)['sma_gradient']
extrema_values = extrema_values.apply(lambda x: 1 if x>0 else 0)
pivot = np.abs(extrema_values.diff(1)).shift(-1)
extrema = np.sort(np.append(pivot[pivot == 1].index, np.array([0, len(stock)-1])))

for x in range(len(extrema)-1):
    stock = calculate_trend(stock, extrema[x], extrema[x+1]-1)
if 'Uptrend' not in stock.columns:
    stock['Uptrend'] = np.nan
if 'Downtrend' not in stock.columns:
    stock['Downtrend'] = np.nan


st.plotly_chart(plot_stock(stock))
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 23:39:14 2016

Assesses a Stock portfolio. Taken from Georgia Tech's Machine Learning for Trading

Description from wiki: Create a function called assess_portfolio() that takes 
as input a description of a portfolio and computes important statistics about it.

http://quantsoftware.gatech.edu/MC1-Project-1

@author: Kenneth Dopp
"""

import datetime as dt
import pandas as pd

def symbol_to_path(symbol):
    """Return CSV file path given ticker symbol."""
    return "data/{}.csv".format(str(symbol))
    
def get_data(symbols, dates):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df = pd.DataFrame(index=dates)
    for symbol in symbols: #uses data in data directory, if you want to see a stock not there add it
        df_sym = pd.read_csv(symbol_to_path(symbol), index_col = "Date", 
                        parse_dates = True, usecols = ['Date', 'Adj Close'],
                        na_values=['nan'])
        df_sym = df_sym.rename(columns = {'Adj Close':symbol})
        df = df.join(df_sym)
    df = df.dropna()
    return df

def normalize_data(df):
    """normalizes the data"""
    return df/ df.ix[0,:]
    
def compute_daily_returns(df):
    """Compute and return the daily return values."""
    daily_returns = (df/df.shift(1)) -1
    daily_returns.ix[0] = 0 #has some issues, only works with one column as is
    return daily_returns
    
def assess_portfolio(sd, ed, syms, allocs, sv, rfr, sf, gen_plot):
    #sd = start date, ed = end date, syms = stock symbols, allocs = allocation
    #sv = start value, rfr = daily risk free rate (usually zero), sf = sampling frequency
    #gen_plot = whether or not you want to plot
    """Process the data to make it possible to get the statistics"""   
    dates = pd.date_range(sd, ed) #turns the given dates into a range for indexing
    prices = get_data(syms, dates= dates) #makes the dataframe using symbols and dates
    normed = normalize_data(prices)
    alloced = normed*allocs 
    pos_vals = alloced*sv #the amount of money in each stock
    port_val = pos_vals.sum(axis=1) #the portfolio value on a given date
    daily_returns = compute_daily_returns(port_val)
    
    """Compute the Statistics cr, adr, sddr"""    
    cr = (port_val[-1]/port_val[0])-1 #the cumulative return for the portfolio
    adr = daily_returns.mean() #the average daily return
    sddr = daily_returns.std() #standard deviation of daily returns
    
    """Compute Sharpe Ratio"""
    #formula is mean(daily port returns - daily risk free rate)/ std (potfolio returns)
    dailyrfr = ((1.0 + rfr)**(1./sf))-1. #the daily risk free rate
    #daily sharpe is that * k or sampling so sqrt(252)
    sr = ((daily_returns - dailyrfr).mean()/sddr)*(sf**(1./2)) #sharpe ratio is Rp - Rf / stdp
    
    """End value of the Portfolio"""
    ev = (1+cr) * sv #the cumulative return times the start value equals end value
    
    """Plot the data"""
    if gen_plot == True:
        #Plot the normalized portolio value, normalized for comparison vs. S&P500 (SPY)
        ax = normalize_data(port_val).plot(title = "Daily Portfolio Value vs. S&P 500", label='Portfolio')
        #Plot the normalized value of the S&P 500 
        SPY = get_data(['SPY'], dates=dates)
        normed_SPY = normalize_data(SPY)
        normed_SPY.plot(label="SPY", ax=ax)
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend(loc='upper left')
    #the following print statements are for easy reading of the output
    print "Start Date:", sd
    print "End Date:", ed
    print "Symbols:", syms
    print "Allocations:", allocs
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr
    print "Starting Portfolio Value:", sv
    print "Ending Portfolio Value:", ev
    return cr, adr, sddr, sr, ev #return so they can be accessed and worked with if necessary

def test_run():
    assess_portfolio(sd=dt.datetime(2010,1,1), ed=dt.datetime(2010,12,31), \
                                syms=['GOOG','AAPL','GLD','XOM'], \
                                allocs=[0.2,0.3,0.4,0.1], \
                                sv=1000000, rfr=0.0, sf=252.0, \
                                gen_plot=True)
    
if __name__ == "__main__":
    test_run()
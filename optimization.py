# -*- coding: utf-8 -*-
"""
Created on Fri Apr 01 02:44:58 2016
Optimizes a portfolio for Return, Risk, or (ideally) Sharpe Ratio
Taken from Georgia Tech's Machine Learning for Trading. Wiki for the project:
http://quantsoftware.gatech.edu/MC1-Project-2
@author: Kenneth
"""

import datetime as dt
import pandas as pd
import numpy as np
import scipy.optimize as spo

"""
The following functions are from analysis.py
The project instructions specifically forbid importing them
"""
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
    prices = get_data(syms, dates= dates) #makes the dataframe using symbol2s and dates
    normed = normalize_data(prices)
    alloced = normed*allocs 
    pos_vals = alloced*sv #the amount of money in each stock
    port_val = pos_vals.sum(axis=1) #the portfolio value on a given date
    daily_returns = compute_daily_returns(port_val)
    
    """Compute the Statistics cr, adr, sddr"""    
    cr = (port_val[-1]/port_val[0])-1 #the cumulative return for the portfolio, 
    adr = daily_returns.mean() #the average daily return
    sddr = daily_returns.std() #standard deviation of daily returns
    
    """Compute Sharpe Ratio"""
    #formula is mean(daily port returns - daily risk free rate)/ std (potfolio returns)
    dailyrfr = ((1.0 + rfr)**(1./sf))-1. #the daily risk free rate
    #daily sharpe is that * k or sampling so sqrt(252)
    sr = ((daily_returns - dailyrfr).mean()/sddr)*(sf**(1./2)) #sharpe ratio is Rp - Rf / stdp
    
    """End value of the Portfolio"""
    er = (1+cr) * sv #the cumulative return times the start value
    
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
    #print statements in portfolioassessor.py not necessary here
    return cr, adr, sddr, sr, er #return so they can be accessed and worked with if necessary
"""End Functions from PortfolioAssessor.py"""

#We need a function to minimize, that being negative sharpe ratio
def sharpe_ratio(allocs, normed): 
    """
    We use allocations and df with relevant stock data to find sharpe ratio, 
    this is the function to minimize
    We'll a assume daily sampling and rfr of 0
    Further, the df should be of normalized price returns for the symbols
    """
    alloced = normed*allocs
    port_val = alloced.sum(axis=1) #gets total normalized returns for the portfolio as a whole
    daily_returns = compute_daily_returns(port_val)
    sddr = daily_returns.std()
    sr = ((daily_returns).mean()/sddr)*(252.**(1./2)) #computes sr
    return sr*-1 #multiply by negative 1 because we actually want to maximize sr


#Now we run the optimization and find optimal allocations
def optimize_portfolio(sd, ed, syms, gen_plot):
    #reads in necessary data for minimize, i.e. normalized price data    
    dates = pd.date_range(sd, ed) #turns the given dates into a range for indexing
    prices = get_data(syms, dates= dates) #makes the dataframe using symbols and dates
    normed = normalize_data(prices)
    
    """Prep for the minimize function"""
    guess_allocs = [(1./len(syms))] *len(syms) #just guess all the same allocations for initial guess
    bnds = ((0.,1.),) * len(syms) #make sure all allocations are between 0 and 1
    
    """Run the minimize function"""
    allocs = spo.minimize(sharpe_ratio, guess_allocs, args = (normed,), \
        method='SLSQP', options = {'disp':True}, bounds = bnds, \
        constraints = ({ 'type': 'eq', 'fun': lambda allocs: 1.0 - np.sum(allocs) })) #make sure allocations sum up to 1
    
    #run these allocations through assess_portfolio to get info 
    cr,adr,sddr,sr,er = assess_portfolio(sd, ed, syms, allocs.x,1,0,252,gen_plot )   #use 1 as startvalue, 0 as rfr, and 252 as sampling frequency
    
    #print out the results    
    print "Start Date:", sd
    print "End Date:", ed
    print "Symbols:", syms
    print "Optimal Allocations:", allocs.x
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr    
    return allocs.x,cr,adr,sddr,sr
    
def test_run():
    allocs, cr, adr, sddr, sr = \
    optimize_portfolio(sd=dt.datetime(2010,1,1), ed=dt.datetime(2010,12,31), \
    syms=['GOOG', 'AAPL', 'GLD', 'XOM'], gen_plot=True)

if __name__ == "__main__":
    test_run()
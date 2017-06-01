This project uses Python libraries such as Numpy, Pandas, and Scipy to make, analyze, and optimize a Pandas dataframe contatining price information on various stocks (you can choose any stock and any date range to put in the portfolio so long as it is in the data folder).

Once you know what portfolio of stocks you want to analyze as well as the dates and allocations, you can put their information
into the analysis.py test_run() function and you'll get an output giving important statistics on the portfolio such as
Sharpe ratio, Volatility, Average Daily Return, and Cumulative Return. If you want the function can also produce a nice graph of the
normalized return of the portfolio versus the S&P 500.

If you know what stocks you're interested in but not sure on how to allocate them, optimization.py may be of more interest to you. 
It takes in a date range and stock symbols and using Scipy's minimization function is able to find the allocations that will maximize
the portfolio's Sharpe ratio. This function can then, like analysis.py, graph the normalized returns of the function vs. the S&P500.

If you compare the graphs from analysis.py versus those from optimization.py and hold everything else constant but allocations 
you can really notice how much optimizing for Sharpe Ratio improves the Portfolio.


The relevant instruction for this project as well as the data folder is taken from Georgia Tech's (hosted on Udacity) course
Machine Learning for Trading

analysis.py: http://quantsoftware.gatech.edu/MC1-Project-1

optimization.py: http://quantsoftware.gatech.edu/MC1-Project-2

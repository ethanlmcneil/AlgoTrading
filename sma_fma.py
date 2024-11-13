


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf





class stock_data:

    def __init__(self, ticker, fma, sma, interval, start_date, end_date):

        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        
        data = data['Close']
        data.columns = ['close']
    
        data[f'{interval} change'] = data.close.pct_change(periods=1).fillna(0)

        data["slow_ma"] = data.close.rolling(sma).mean()
        data["fast_ma"] = data.close.rolling(fma).mean()
        data = data.dropna() 

        data = data.assign(
            signal=lambda x: np.where(x.fast_ma > x.slow_ma, 1, 0)
        )

        data['signal'] = data['signal'].shift(1, fill_value=0)
        data['strategy'] = data[f'{interval} change'] * data['signal']
    

        self.df = data

   
    



        

    
class optimize:

    def __init__(self, ticker, interval, start_date, end_date):


        self.ticker = ticker
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date

        results = []
    
        for fast_ma in range(5,50,5):
            for slow_ma in range(30, 300, 5):
            

                if fast_ma >= slow_ma:
                    continue
                
                else:

                    ticker_data_obj = stock_data(ticker,fast_ma, slow_ma,  interval, start_date, end_date)
                    ticker_data = ticker_data_obj.df
                
                    ticker_data['strategy'] = ticker_data[f'{interval} change'] * ticker_data['signal']

                    cumprod_strategy = (1 + ticker_data['strategy']).cumprod()
                    annualized_returns = (1 + (ticker_data[[f'{interval} change', 'strategy']]).mean())**252 - 1
                    annualized_std_deviation = ticker_data[[f'{interval} change', 'strategy']].std() * np.sqrt(252)
                    sharpe_ratio = annualized_returns / annualized_std_deviation

                    result_dict = {
                        'fast_ma': fast_ma,
                        'slow_ma': slow_ma,
                        'annualized_returns': annualized_returns['strategy'],
                        'annualized_std_deviation': annualized_std_deviation['strategy'],
                        'sharpe_ratio': sharpe_ratio['strategy']
                    }

                    results.append(result_dict)

        results = pd.DataFrame(results)

        optimal = results.loc[results['sharpe_ratio'].idxmax()]   
       
        optimal_fma = int(optimal['fast_ma'])
        optimal_sma = int(optimal['slow_ma'])
        


        optimal_strat = stock_data(ticker, optimal_fma, optimal_sma, interval,start_date, end_date)
        
        self.optimal_ma = optimal_fma, optimal_sma
        self.data = optimal_strat.df
        self.optimal_results = optimal
        
        return 



    

        
            
    







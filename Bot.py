from operator import pos
import pandas as pd  
import requests
import itertools
import random
import statistics as stats
from Keys import AV_API_KEY # API use API key = 'demo' and symbol ' IBM' for demo results


#Function returns unparsed JSON market data
def api_caller(symbol: str, key: str):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol={symbol}&apikey={key}"
    response = requests.get(url).json()
    try:
        raw_data = response['Weekly Adjusted Time Series']
        return raw_data
    except:
        print(response)
        return 0

#Function
def purchase_calculator(price_list, results_df, column_dictionary: dict, position_size: float):
    momentum_list = []
    proportion_list = []
    mean_dictionary = {}
    proportion_dictionary = {}
    purchase_dictionary = {}
    for row in results_df.index:
        for column_name in column_dictionary:
            momentum_list.append(results_df.loc[row,f'{column_name}'])
        mean_dictionary.update({stats.mean(momentum_list)+1: 0})
    results_df['Biased Average Momentum'] = mean_dictionary
    total_momentum = results_df.sum(numeric_only=True)['Biased Average Momentum']
    for value in results_df['Biased Average Momentum']:
        proportion = (value/total_momentum)
        proportion_dictionary.update({proportion*100: 0})
        proportion_list.append(proportion)
    if len(price_list) == 5:
        for i in range(0,5):
            ammount_purchased = (float(position_size)*float(proportion_list[i]))/float(price_list[i])
            purchase_dictionary.update({ammount_purchased: 0})
    if len(purchase_dictionary) == 5:
        results_df['Shares to Purchase'] = purchase_dictionary
        results_df['Propotions'] = proportion_dictionary

#Function returns latest weekly adjusted closing cost
def stock_price(raw_data: dict):
    for dict_key in raw_data:
        price = raw_data[dict_key]['5. adjusted close']
        break
    return price

# function returns stock momentum
# Momentum is = (Cost_now - Cost_before)/Cost_before
def stock_momentum(time_interval, raw_data: dict):
    if time_interval== '1 Week Momentum':
        week_ammount = 2
    elif time_interval== '3 Months Momentum':
        week_ammount = 13
    elif time_interval== '6 Months Momentum':
        week_ammount = 26
    elif time_interval== '1 Year Momentum':
        week_ammount = 52
    parsed_data = {}
    i = 0
    for dict_key in raw_data:
        i += 1
        parsed_data.update({i: raw_data[f'{dict_key}']['5. adjusted close']})
    parsed_truncated=dict(itertools.islice(parsed_data.items(),week_ammount))
    momentum_sum = 0
    for i in range(1, week_ammount):
        closed_new = parsed_truncated[i+1]
        closed_old = parsed_truncated[i]
        momentum_partial = (float(closed_new) - float(closed_old))/float(closed_old)
        momentum_sum = momentum_sum + momentum_partial
    return (((momentum_sum/week_ammount)*100)+1)


def main():
    key = AV_API_KEY
    stocks = pd.read_csv('sp_500_stocks.csv')
    stocklist={}
    price_dictionary={}
    price_list = []
    # Change the number of stocks
    for i in range(0, 5):
        random_index = random.randint(0, 505)
        stocklist.update({i: stocks['Ticker'][random_index]})
    
    # SET UP RESULTS
    position_size: float = input("Input Position size in dollars:")
    column_dictionary={'1 Year Momentum','6 Months Momentum','3 Months Momentum','1 Week Momentum'}
    results_df = pd.DataFrame(index=[f'{stocklist[i]}'],columns=column_dictionary)
    for i in range(0, len(stocklist)):
        raw_data = api_caller(stocklist[i],key)
        if raw_data == 0:
            return 0
        for column_name in column_dictionary:
            momentum = stock_momentum(f'{column_name}',raw_data)
            results_df.at[f'{stocklist[i]}',f'{column_name}']= momentum
        price = stock_price(raw_data)
        price_dictionary.update({price: 0})
        price_list.append(price)
        purchase_calculator(price_list, results_df, column_dictionary, position_size)
    results_df['Share Price'] = price_dictionary
    results_df.to_excel(file_path)
    print(results_df)


file_path: str = r'input desired result path here'
main()


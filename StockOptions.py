from yahoo_fin import options as op
import yfinance as yf
from datetime import datetime
import pandas as pd
import math
from tqdm import tqdm
import threading


def get_option_data(ticker, daysOut, strikePercentage):
    stock = yf.Ticker(ticker)

    #pull current stock price
    historical_data = stock.history(period="1y")
    lastClose = historical_data['Close'].iloc[-1]

    # print(lastClose)

    #get all contract dates
    expirationDates = op.get_expiration_dates(ticker)

    #get the date that is closest to *daysOut* days out, typically 30 days out
    bestDate = ""
    bestDiff = 1000000

    # print(expirationDates)

    for date in expirationDates:
        diff = math.fabs(daysOut - (datetime.strptime(date, "%B %d, %Y") - datetime.now()).days)
        if diff < bestDiff:
            bestDiff = diff
            bestDate = date
    
    #pulls all the call data for the best date
    callData = op.get_calls(ticker, bestDate)

    key = lastClose * strikePercentage
    bestIndex = -1
    bestDiff = 100000

    #gets the call contract best suited for the percentage you want above the current stock price
    for i in range(len(callData['Strike'])):
        diff = math.fabs(key - callData['Strike'][i])
        if diff < bestDiff and callData['Strike'][i] > lastClose:
            bestDiff = diff
            bestIndex = i
    
    return bestDate, callData['Strike'][bestIndex], callData['Bid'][bestIndex], callData['Implied Volatility'][bestIndex]

def get_sp500_tickers():
    sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return sp500_tickers['Symbol'].tolist()
    
class Option:
    def __init__(self, ticker, strike, bid, closePrice, date, volatility, implied_volatility):
        self.ticker = ticker
        self.strike = strike
        self.bid = bid
        self.closePrice = closePrice
        self.date = date
        self.volatility = volatility
        self.implied_volatility = implied_volatility

        self.odds = (float(self.implied_volatility.strip('%')) + ((datetime.strptime(self.date, "%B %d, %Y") - datetime.now()).days / 30) + ((self.closePrice - self.strike) / self.closePrice)) / 3

        self.ratio = bid/closePrice

    def __cmp__(self, other):
        return cmp(other.ratio, self.ratio)

    def print(self):
        print(f"{self.ticker}, Last Close: {round(self.closePrice, 2)}, Date: {self.date}, Strike: {self.strike}, Bid: {self.bid}, Ratio: {round(self.ratio * 100, 3)}%, Volatility: {round(self.volatility, 5)}, Implied Volatility: {self.implied_volatility}, Odds to Excersize: {round(self.odds, 2)}%")
    
    def export(self):
        return f"{self.ticker};{self.strike};{self.bid};{self.closePrice};{self.date};{self.volatility};{self.implied_volatility}"

def export(options_data):
    f = open("C:\\Personal Projects\\StockOptions\\Exports\\" + datetime.now().strftime("%m%d%Y%H%M%S") + ".txt", "w")
    for data in options_data:
        f.write(data.export() + "\n")

def insertion_sort_reverse(array):
    for i in range(1, len(array)):
        key_item = array[i]

        j = i - 1

        while j >= 0 and array[j].ratio < key_item.ratio:
            array[j + 1] = array[j]
            j -= 1

        array[j + 1] = key_item

    return array

def parse_option_data_to_list(symbol, addToList):
    try:
        stock = yf.Ticker(symbol)

        historical_data = stock.history(period="1y")
        lastClose = historical_data['Close'].iloc[-1]

        #volatility of the stock itself
        volatility = historical_data['Close'].pct_change().std() * (252 ** 0.5)

        date, strike, bid, implied_volatility = get_option_data(symbol, 30, 1.05)

        obj = Option(symbol, strike, bid, lastClose, date, volatility, implied_volatility)

        addToList.append(obj)
    except Exception as e:
        print(f"Failed to get option data for {symbol} {e}")
        failCount = failCount + 1
    

startTime = datetime.now()

sp500_symbols = get_sp500_tickers()

days_out = 30
percentileAbove = 1.05


optionData = []
index = 0
for i in tqdm(range(len(sp500_symbols))):
    try:
        parse_option_data_to_list(sp500_symbols[index], optionData)

        # optionData[len(optionData) - 1].print()
    except Exception as e:
        print(f"Failed to get option data for {sp500_symbols[index]} {e}")

    index = index + 1

insertion_sort_reverse(optionData)

auto_export = True
filterVolatilityInSort = .25
moneyThreshold = 50000
export_data = []

print("\nBest Ratios:")
for i in range(0, len(optionData)):
    optionData[i].print()

    if auto_export and optionData[i].volatility < filterVolatilityInSort and optionData[i].closePrice * 100 <= moneyThreshold:
        export_data.append(optionData[i])
        moneyThreshold = moneyThreshold - (optionData[i].closePrice * 100)

if auto_export:
    export(export_data)


endTime = datetime.now()

print("Duration: " + str(endTime - startTime))
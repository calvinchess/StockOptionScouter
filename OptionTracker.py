from yahoo_fin import options as op
import yfinance as yf
from datetime import datetime
import pandas as pd
import math
from tqdm import tqdm
from colorama import Fore


def get_option_data(ticker, daysOut, strikePercentage):
    stock = yf.Ticker(ticker)

    #pull current stock price
    historical_data = stock.history(period="1y")
    lastClose = historical_data['Close'].iloc[-1]

    #get all contract dates
    expirationDates = op.get_expiration_dates(ticker)

    #get the date that is closest to *daysOut* days out, typically 30 days out
    bestDate = ""
    bestDiff = 1000000
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

        self.closePriceOverride = "-1000000"
        self.highStatusOverride = ""

        self.odds = (float(self.implied_volatility.strip('%')) + ((datetime.strptime(self.date, "%B %d, %Y") - datetime.now()).days / 30) + ((self.closePrice - self.strike) / self.closePrice)) / 3

        self.ratio = bid/closePrice

    def __cmp__(self, other):
        return cmp(other.ratio, self.ratio)

    def print(self):
        print(f"{self.ticker}, Last Close: {round(self.closePrice, 2)}, Date: {self.date}, Strike: {self.strike}, Bid: {self.bid}, Ratio: {round(self.ratio * 100, 3)}%, Volatility: {round(self.volatility, 5)}, Implied Volatility: {self.implied_volatility}, Odds to Excersize: {round(self.odds, 2)}%")
    
    def export(self):
        return f"{self.ticker};{self.strike};{self.bid};{self.closePrice};{self.date};{self.volatility};{self.implied_volatility};{self.closePriceOverride};{self.highStatusOverride}"

def insertion_sort_reverse(array):
    for i in range(1, len(array)):
        key_item = array[i]

        j = i - 1

        while j >= 0 and array[j].ratio < key_item.ratio:
            array[j + 1] = array[j]
            j -= 1

        array[j + 1] = key_item

    return array

def export(options_data):
    file_time = datetime.now().strftime("%m%d%Y%H%M%S")

    f = open("C:\\Personal Projects\\StockOptions\\Exports\\" + file_time + ".txt", "w")
    for data in options_data:
        f.write(data.export() + "\n")

    f.close()

    f = open("C:\\Personal Projects\\StockOptions\\Exports\\hash.txt", "r")

    lines = f.read()

    f.close()

    f = open("C:\\Personal Projects\\StockOptions\\Exports\\hash.txt", "w")

    f.write(lines + "\n" + datetime.now().strftime("%B %d, %Y") + ";" + "C:\\Personal Projects\\StockOptions\\Exports\\" + file_time + ".txt")

    f.close()

    load_file_hashes()


def reExport(file, options_data):
    f = open(file, "w")
    for data in options_data:
        f.write(data.export() + "\n")

def import_option_data(option_line):
    components = option_line.split(';')

    obj = Option(components[0], float(components[1]), float(components[2]), float(components[3]), components[4], float(components[5]), components[6])
    
    if(len(components) == 9):
        obj.closePriceOverride = components[7]
        obj.highStatusOverride = components[8]

    return obj

def compare_price_to_option(option, price):
    if price < (option.closePrice - option.bid):
        return f"Red"
    elif price < option.closePrice:
        color_code = f"\033[38;2;{255};{140};{0}m"
        return f"Orange"
    elif price < (option.strike):
        return f"Yellow"
    elif price < (option.strike + option.bid):
        color_code = f"\033[38;2;{0};{255};{255}m"
        return f"Blue"
    else:
        return f"Green"

def return_option_tracking(file, start_date):

    # print("Start Date: " + start_date)

    f = open(file, "r")

    lines = f.read().split('\n')
    optionData = []

    for line in lines:
        if line == "":
            continue
        optionData.append(import_option_data(line))

    f.close()

    #  optionData[len(optionData) - 1].print()

    daysBack = (datetime.now() - datetime.strptime(start_date, "%B %d, %Y")).days
    startingBal = 50000


    profit = 0
    profitDueToHighs = 0
    totalLoss = 0
    premium = 0
    optionArray = []
    for option in optionData:
        stock = yf.Ticker(option.ticker)

        #pull current stock price
        historical_data = stock.history(period="1y")

        high = 0

        lastDay = (datetime.now() - datetime.strptime(option.date, "%B %d, %Y")).days

        # print(option.date + " " + str(lastDay))

        lastClose = historical_data['Close'].iloc[-1]

        for i in range(daysBack):
            daysHigh = historical_data['High'].iloc[-1 * (i + 1)]
            if daysHigh > high:
                high = daysHigh
        # print(lastDay)

        if option.closePriceOverride != "-1000000":
            lastClose = float(option.closePriceOverride)

        priceCap = lastClose

        if priceCap > option.strike:
            priceCap = option.strike

        profit = profit + option.bid * 100 + (priceCap - option.closePrice) * 100

        if "Green" in compare_price_to_option(option, high):
            profitDueToHighs = profitDueToHighs + option.bid * 100 + (option.strike - option.closePrice) * 100
        else:
            profitDueToHighs = profitDueToHighs + option.bid * 100 + (priceCap - option.closePrice) * 100

        premium = premium + option.bid * 100

        currentProfit = option.bid * 100 + (priceCap - option.closePrice) * 100

        if lastClose - option.closePrice < 0:
            totalLoss = totalLoss + (lastClose - option.closePrice) * -100

        finalString = ""
        if lastDay > 0 and option.closePriceOverride == "-1000000":
            option.closePriceOverride = lastClose
            option.highStatusOverride = compare_price_to_option(option, high)

            reExport(file, optionData)


        # print(f"{option.ticker} Buy Price: {option.closePrice}, Strike: {option.strike}, Bid: {option.bid}, Current Price: {lastClose}, High Since Purchace: {high}")

        highStatus = compare_price_to_option(option, high)
        if option.highStatusOverride != "":
            highStatus = option.highStatusOverride

        optionArray.append([option.ticker, compare_price_to_option(option, lastClose), highStatus, round(currentProfit, 2), round(option.bid * 100, 2), round(option.bid * 100 + (option.strike - option.closePrice) * 100, 2), option.date, lastDay > 0])

        # print(f"{Fore.WHITE}{option.ticker} Current Status: {finalString}{compare_price_to_option(option, lastClose)}{Fore.WHITE}, Status due to High: {compare_price_to_option(option, high)}{Fore.WHITE}, Profit: ${round(currentProfit, 2)}, Premium: ${round(option.bid * 100, 2)}, Target Profit: ${round(option.bid * 100 + (option.strike - option.closePrice) * 100, 2)}")

    # print(f"Premium: ${round(premium, 2)} ({round(premium/startingBal * 100, 2)}%)")
    # print(f"Total Profit: ${round(profit, 2)} ({round(profit/startingBal * 100, 2)}%)")
    # print(f"Optimal Profit: ${round(profitDueToHighs, 2)} ({round(profitDueToHighs/startingBal * 100, 2)}%)")
    # print(f"Total Loss: ${round(totalLoss, 2)}")

    returnArray = [optionArray, round(premium, 2), round(profit, 2), round(profitDueToHighs, 2), round(totalLoss, 2)]

    return returnArray


def load_file_hashes():
    f = open("C:\\Personal Projects\\StockOptions\\Exports\\hash.txt", "r")

    lines = f.read().split('\n')

    for line in lines:
        components = line.split(';')
        files[components[0]] = components[1]

    f.close()


files = {}

load_file_hashes()

def get_option_tracking_data(date):
    return return_option_tracking(files[date], date)

    
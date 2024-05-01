from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import subprocess
import yfinance as yf
import OptionTracker

app = Flask(__name__)
CORS(app)

@app.route('/date', methods=['GET'])
def get_date():
    date = datetime.strftime(datetime.now(), "%m %d, %Y")
    return jsonify({'date': date})

@app.route('/tracking', methods=['GET'])
def get_tracking_data():
    date = request.args.get('date')
    return jsonify({'data': OptionTracker.get_option_tracking_data(date)})

@app.route('/smp500', methods=['GET'])
def get_smp500_data():
    return jsonify({'data': OptionTracker.get_sp500_tickers()})

@app.route('/option_data', methods=['GET'])
def get_single_option_data():
    symbol = request.args.get('symbol')
    daysOut = int(request.args.get('daysOut'))
    strikePercentage = float(request.args.get('strikePercentage'))

    stock = yf.Ticker(symbol)

    historical_data = stock.history(period="1y")
    lastClose = historical_data['Close'].iloc[-1]

    #volatility of the stock itself
    volatility = historical_data['Close'].pct_change().std() * (252 ** 0.5)

    date, strike, bid, implied_volatility = OptionTracker.get_option_data(symbol, daysOut, strikePercentage)

    obj = OptionTracker.Option(symbol, strike, bid, lastClose, date, volatility, implied_volatility)

    returnList = [symbol, strike, bid, lastClose, date, volatility, implied_volatility, obj.ratio, obj.odds]

    print(returnList)

    return jsonify({'data': returnList})

@app.route('/create_new_data_set', methods=['GET'])
def create_new_data_set():
    delimiter = ';'
    tickers = request.args.get('tickers').split(delimiter)
    strikes = request.args.get('strikes').split(delimiter)
    bids = request.args.get('bids').split(delimiter)
    closePrices = request.args.get('closePrices').split(delimiter)
    dates = request.args.get('dates').split(delimiter)
    volatilities = request.args.get('volatilities').split(delimiter)
    implied_volatilities = request.args.get('implied_volatilities').split(delimiter)

    option_list = []

    for i in range(len(tickers)):
        option_list.append(OptionTracker.Option(tickers[i], float(strikes[i]), float(bids[i]), float(closePrices[i]), dates[i], volatilities[i], implied_volatilities[i]))

    OptionTracker.export(option_list)

    return jsonify({'data': ""})


if __name__ == '__main__':
    app.run()
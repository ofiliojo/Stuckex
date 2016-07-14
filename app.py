#!/usr/bin/env python

# Author: Ofiliojo Ichaba
# Date: 07/11/2016
# File Name: app.py

import urllib.request
import json
from flask import Flask, session, render_template, url_for, request, redirect
from flask_session import Session

app = Flask(__name__)
#app.secret_key = 'jdhfsk.jdfnskdnjk.snclkamdnvjdn;lmj'
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)
ticker = {}
portfolioOfCompanies = []
quantityOwned = 0
cashBalance = 100000.0
theSymbol = ""
numberOfStocksToBuy = ""
numberOfStocksToSell = ""


@app.route("/")
def index():
    return render_template('index.html' , cashBalance = cashBalance, portfolioOfCompanies = portfolioOfCompanies)

@app.route("/search" , methods=['POST'])
def searchForTicker():
    global quantityOwned
    global cashBalance
    global theSymbol
    global ticker
    global portfolioOfCompanies
    theSymbol = request.form["symbol"]
    url = "http://data.benzinga.com/rest/richquoteDelayed?symbols="+theSymbol
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        data = json.loads(the_page.decode('utf-8'))
    ticker = {'name': data.get(theSymbol).get('name'),
                'bidPrice': data.get(theSymbol).get('bidPrice'),
                    'askPrice': data.get(theSymbol).get('askPrice'),
                        'quantityOwned' : quantityOwned}
    return render_template('result.html', ticker = ticker, cashBalance = cashBalance, portfolioOfCompanies = portfolioOfCompanies)
@app.route("/buy", methods=['POST'])
def buy():
    global ticker
    global quantityOwned
    global cashBalance
    global theSymbol
    global portfolioOfCompanies
    numberOfStocksToBuy = request.form["numberOfStocksToBuy"]
    numberToBuy = int(numberOfStocksToBuy)
    costOfStocks = int(ticker.get('askPrice')) * numberToBuy
    if costOfStocks <= cashBalance:
        if not any(stock.get('name', None) == ticker.get('name') for stock in portfolioOfCompanies):
            ticker['quantityOwned'] = numberToBuy
            cashBalance = cashBalance - costOfStocks
            portfolioOfCompanies.append(ticker)
        else:
            for stock in portfolioOfCompanies:
                if stock['name'] == ticker['name']:
                    stock['quantityOwned'] = stock['quantityOwned']+numberToBuy
            cashBalance = cashBalance - costOfStocks
    return render_template('result.html', ticker = ticker, cashBalance = cashBalance, portfolioOfCompanies = portfolioOfCompanies)

@app.route("/sell", methods=['POST'])
def sell():
    global cashBalance
    global quantityOwned
    global ticker
    global theSymbol
    global portfolioOfCompanies
    numberOfStocksToSell = request.form["numberOfStocksToSell"]
    numberToSell = int(numberOfStocksToSell)
    costOfStocks = int(ticker.get('bidPrice')) * numberToSell
    for stock in portfolioOfCompanies:
        if stock['name'] == ticker['name']:
            if numberToSell <= stock['quantityOwned']:
                stock['quantityOwned'] = stock['quantityOwned']-numberToSell
                cashBalance = cashBalance + costOfStocks
                if stock['quantityOwned'] == 0:
                    portfolioOfCompanies[:] = [stock for stock in portfolioOfCompanies if stock.get('name') != ticker.get('name')]
    return render_template('result.html', ticker = ticker, cashBalance = cashBalance, portfolioOfCompanies = portfolioOfCompanies, session = session)



if __name__ == "__main__":
    app.debug = True
    app.run()

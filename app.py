#!/usr/bin/env python

# Author: Ofiliojo Ichaba
# Date: 07/11/2016
# File Name: app.py

import urllib.request
import json
from flask import Flask, session, render_template, url_for, request, redirect

app = Flask(__name__)
app.secret_key = 'jdhfsk.jdfnskdnjk.snclkamdnvjdn;lmj'
ticker = {}
portfolioOfCompanies = []
quantityOwned = 0
cashBalance = 100000.00
theSymbol = ""
numberOfStocksToBuy = ""
numberOfStocksToSell = ""


@app.route("/")
def index():
    return render_template('index.html' , cashBalance = cashBalance, portfolioOfCompanies = portfolioOfCompanies, session = session)

@app.route("/search" , methods=['POST'])
def searchForTicker():
    global quantityOwned
    global cashBalance
    global theSymbol
    global ticker
    global portfolioOfCompanies
    session[theSymbol] = request.form["symbol"]
    url = "http://data.benzinga.com/rest/richquoteDelayed?symbols="+session[theSymbol]
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        data = json.loads(the_page.decode('utf-8'))
    ticker = {'name': data.get(session[theSymbol]).get('name'),
                'bidPrice': data.get(session[theSymbol]).get('bidPrice'),
                    'askPrice': data.get(session[theSymbol]).get('askPrice'),
                        'quantityOwned' : quantityOwned}
    return render_template('result.html', ticker = ticker, cashBalance = cashBalance, portfolioOfCompanies = portfolioOfCompanies, session = session)
@app.route("/buy", methods=['POST'])
def buy():
    global ticker
    global quantityOwned
    global cashBalance
    global theSymbol
    global portfolioOfCompanies
    session[numberOfStocksToBuy] = request.form["numberOfStocksToBuy"]
    numberToBuy = int(session[numberOfStocksToBuy])
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
    return render_template('result.html', ticker = ticker, cashBalance = cashBalance, portfolioOfCompanies = portfolioOfCompanies, session = session)

@app.route("/sell", methods=['POST'])
def sell():
    global cashBalance
    global quantityOwned
    global ticker
    global theSymbol
    global portfolioOfCompanies
    session[numberOfStocksToSell] = request.form["numberOfStocksToSell"]
    numberToSell = int(session[numberOfStocksToSell])
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

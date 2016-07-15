#!/usr/bin/env python

# Author: Ofiliojo Ichaba
# Date: 07/11/2016
# File Name: app.py

import urllib.request
import json
import random
from flask import Flask, session, render_template, url_for, request, redirect


app = Flask(__name__)
app.secret_key = 'jdhfsk.jdfnskdnjk.snclkamdnvjdn;lmj'
ticker = {}
portfolioOfCompanies = []
quantityOwned = 0
theSymbol = ""
numberOfStocksToBuy = ""
numberOfStocksToSell = ""


@app.route("/")
def index():
    session['cashBalance'] = 1000000.00
    return render_template('index.html', cash = session['cashBalance'], portfolioOfCompanies = portfolioOfCompanies)

@app.route("/search" , methods=['POST'])
def searchForTicker():
    global quantityOwned
    global theSymbol
    global ticker
    ticker = {}
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
    return render_template('result.html', ticker = ticker, cash = session['cashBalance'], portfolioOfCompanies = portfolioOfCompanies)
@app.route("/buy", methods=['POST'])
def buy():
    global ticker
    global quantityOwned
    global theSymbol
    global portfolioOfCompanies
    numberOfStocksToBuy = request.form["numberOfStocksToBuy"]
    numberToBuy = int(numberOfStocksToBuy)
    costOfStocks = int(ticker.get('askPrice')) * numberToBuy
    if costOfStocks <= session['cashBalance']:
        if not any(stock.get('name', None) == ticker.get('name') for stock in portfolioOfCompanies):
            ticker['quantityOwned'] = numberToBuy
            session['cashBalance'] = session['cashBalance'] - costOfStocks
            portfolioOfCompanies.append(ticker)
        else:
            for stock in portfolioOfCompanies:
                if stock['name'] == ticker['name']:
                    stock['quantityOwned'] = stock['quantityOwned']+numberToBuy
                session['cashBalance'] = session['cashBalance'] - costOfStocks
    return render_template('result.html', ticker = ticker, cash = session['cashBalance'], portfolioOfCompanies = portfolioOfCompanies)

@app.route("/sell", methods=['POST'])
def sell():
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
                session['cashBalance'] = session['cashBalance'] + costOfStocks
                if stock['quantityOwned'] == 0:
                    portfolioOfCompanies[:] = [stock for stock in portfolioOfCompanies if stock.get('name') != ticker.get('name')]
    return render_template('result.html', ticker = ticker, cash = session['cashBalance'], portfolioOfCompanies = portfolioOfCompanies)



if __name__ == "__main__":
    app.debug = True
    app.run()

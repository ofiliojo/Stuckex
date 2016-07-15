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


@app.route("/")
def index():
    session['cashBalance'] = 1000000.00
    session['portfolioOfCompanies'] = []
    return render_template('index.html', cash = session['cashBalance'], portfolio = session['portfolioOfCompanies'])

@app.route("/search" , methods=['POST'])
def searchForTicker():
    global quantityOwned
    session['ticker'] = {}
    session['theSymbol'] = request.form["symbol"]
    url = "http://data.benzinga.com/rest/richquoteDelayed?symbols="+session['theSymbol']
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        data = json.loads(the_page.decode('utf-8'))
    session['ticker'] = {'name': data.get(session['theSymbol']).get('name'),
                            'bidPrice': data.get(session['theSymbol']).get('bidPrice'),
                                'askPrice': data.get(session['theSymbol']).get('askPrice'),
                                    'quantityOwned' : 0}
    return render_template('result.html', ticker = session['ticker'], cash = session['cashBalance'], portfolio = session['portfolioOfCompanies'])
@app.route("/buy", methods=['POST'])
def buy():
    session['numberOfStocksToBuy'] = request.form["numberOfStocksToBuy"]
    numberToBuy = int(session['numberOfStocksToBuy'])
    costOfStocks = int(session['ticker'].get('askPrice')) * numberToBuy
    if costOfStocks <= session['cashBalance']:
        if not any(stock.get('name', None) == session['ticker'].get('name') for stock in session['portfolioOfCompanies']):
            session['ticker']['quantityOwned'] = numberToBuy
            session['cashBalance'] = session['cashBalance'] - costOfStocks
            session['portfolioOfCompanies'].append(session['ticker'])
        else:
            for stock in session['portfolioOfCompanies']:
                if stock['name'] == session['ticker']['name']:
                    stock['quantityOwned'] = stock['quantityOwned']+numberToBuy
                session['cashBalance'] = session['cashBalance'] - costOfStocks
    return render_template('result.html', ticker = session['ticker'], cash = session['cashBalance'], portfolio = session['portfolioOfCompanies'])

@app.route("/sell", methods=['POST'])
def sell():
    session['numberOfStocksToSell'] = request.form["numberOfStocksToSell"]
    numberToSell = int(session['numberOfStocksToSell'])
    costOfStocks = int(session['ticker'].get('bidPrice')) * numberToSell
    for stock in session['portfolioOfCompanies']:
        if stock['name'] == session['ticker']['name']:
            if numberToSell <= stock['quantityOwned']:
                stock['quantityOwned'] = stock['quantityOwned']-numberToSell
                session['cashBalance'] = session['cashBalance'] + costOfStocks
                if stock['quantityOwned'] == 0:
                    session['portfolioOfCompanies'][:] = [stock for stock in session['portfolioOfCompanies'] if stock.get('name') != session['ticker'].get('name')]
    return render_template('result.html', ticker = session['ticker'], cash = session['cashBalance'], portfolio = session['portfolioOfCompanies'])



if __name__ == "__main__":
    app.debug = True
    app.run()

#!/usr/bin/env python

# Author: Ofiliojo Ichaba
# Date: 07/11/2016
# File Name: app.py

import urllib.request
import json
import random
from flask import Flask, session, render_template, url_for, request, redirect


app = Flask(__name__)
#Secret key for the sessions
app.secret_key = 'jdhfsk.jdfnskdnjk.snclkamdnvjdn;lmj'


@app.route("/")
def index():
    # session stores the session variables of each unique variable
    session['cashBalance'] = 1000000.00
    session['portfolioOfCompanies'] = []
    #Renders index.html page
    return render_template('index.html', cash = session['cashBalance'], portfolio = session['portfolioOfCompanies'])

#When the search button is clicked
@app.route("/search" , methods=['POST'])
def searchForTicker():
    session['ticker'] = {}
    session['theSymbol'] = request.form["symbol"]
    url = "http://data.benzinga.com/rest/richquoteDelayed?symbols="+session['theSymbol']
    #Makes request to URL
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        #Loads the file as json
        data = json.loads(the_page.decode('utf-8'))
    #Error Handling: incorrect searches
    if data.get("null") or data == {}:
        session['searchError'] = "Please Enter a Valid Ticker"
        return render_template('index.html', searchError = session['searchError'], cash = session['cashBalance'], portfolio = session['portfolioOfCompanies'])
    else:
        session['searchError'] = ""
        #Data of a particular ticker
        session['ticker'] = {'name': data.get(session['theSymbol']).get('name'),
                                'bidPrice': data.get(session['theSymbol']).get('bidPrice'),
                                    'askPrice': data.get(session['theSymbol']).get('askPrice'),
                                        'quantityOwned' : 0}
        return render_template('result.html', searchError = session['searchError'], ticker = session['ticker'], cash = session['cashBalance'], portfolio = session['portfolioOfCompanies'])

#When the buy button is pressed
@app.route("/buy", methods=['POST'])
def buy():
    session['numberOfStocksToBuy'] = request.form["numberOfStocksToBuy"]
    #Error Handling: Makes sure the amount is a digit
    if session['numberOfStocksToBuy'].isdigit():
        numberToBuy = int(session['numberOfStocksToBuy'])
        session['buyError'] = ""
        costOfStocks = int(session['ticker'].get('askPrice')) * numberToBuy
        #Check if user has enough cash to buy
        if costOfStocks <= session['cashBalance']:
            #Checks if stock already exists in portfolio
            if not any(stock.get('name', None) == session['ticker'].get('name') for stock in session['portfolioOfCompanies']):
                session['ticker']['quantityOwned'] = numberToBuy
                session['cashBalance'] = session['cashBalance'] - costOfStocks
                session['portfolioOfCompanies'].append(session['ticker'])
            else:
                for stock in session['portfolioOfCompanies']:
                    if stock['name'] == session['ticker']['name']:
                        stock['quantityOwned'] = stock['quantityOwned']+numberToBuy
                    session['cashBalance'] = session['cashBalance'] - costOfStocks
        else:
            session['buyError'] = "Not Enough Buy"

    else:
        session['buyError'] = "Enter Valid Amount"
    return render_template('result.html', buyError = session['buyError'], ticker = session['ticker'], cash = session['cashBalance'], portfolio = session['portfolioOfCompanies'])

#When the sell button is pressed
@app.route("/sell", methods=['POST'])
def sell():
    session['numberOfStocksToSell'] = request.form["numberOfStocksToSell"]
    #Error Handling: Makes sure the amount is a digit
    if session['numberOfStocksToSell'].isdigit():
        session['sellError'] = ""
        numberToSell = int(session['numberOfStocksToSell'])
        costOfStocks = int(session['ticker'].get('bidPrice')) * numberToSell
        for stock in session['portfolioOfCompanies']:
            if stock['name'] == session['ticker']['name']:
                #Makes sure you have enough stocks to sell
                if numberToSell <= stock['quantityOwned']:
                    stock['quantityOwned'] = stock['quantityOwned']-numberToSell
                    session['cashBalance'] = session['cashBalance'] + costOfStocks
                    #Deletes company from portfolio if stocks is 0
                    if stock['quantityOwned'] == 0:
                        session['portfolioOfCompanies'][:] = [stock for stock in session['portfolioOfCompanies'] if stock.get('name') != session['ticker'].get('name')]
                else:
                    session['sellError'] = "Not Enough Stock"
    else:
        session['sellError'] = "Enter Valid Amount"
    return render_template('result.html', sellError = session['sellError'], ticker = session['ticker'], cash = session['cashBalance'], portfolio = session['portfolioOfCompanies'])



if __name__ == "__main__":
    #Debugs the website
    app.debug = True
    app.run()

#!/usr/bin/env python3

import asyncio
import websockets
import json
import time

from datetime import datetime

import pandas as pd
import numpy as np

import time

uri = "wss://services.thinkorswim.com/Services/WsJson"

#ADD TOKEN
token = ""

sessionPayload = {"ver":  "25.*.*", "fmt": "json-patches", "heartbeat": "2s"}
loginPayload = {"payload": [{"service":"login",
					 "id":"login",
					 "ver":0,
					 "domain":"TOS",
					 "platform":"PROD",
					 "token":token,
					 "accessToken":"",
					 "tag":"TOSWeb",
					 "client":{"platform":"MacIntel",
							   "vendor":"",
							   "locale":"en-US",
							   "timezone":"America/Chicago",
							   "deviceModel":"Firefox",
							   "arch":"",
							   "osVersion":"10.15"}}]}

def getSymbolData(*symbols):
	return {"payload":[{"service":"quotes_charts",
						"id":"tradequotes",
						"account":"COMBINED ACCOUNT",
						"symbols":symbols,
						"fields":["MARK","MARK_CHANGE","MARK_PERCENT_CHANGE","BID","BID_EXCHANGE","ASK","ASK_EXCHANGE","BID_SIZE","ASK_SIZE","VOLUME","OPEN","HIGH52","LOW52","HIGH","LOW","VWAP","VOLATILITY_INDEX","IMPLIED_VOLATILITY","MARKET_MAKER_MOVE","PERCENTILE_IV","HISTORICAL_VOLATILITY_30_DAYS","MARKET_CAP","BETA","PE","INITIAL_MARGIN","LAST","LAST_SIZE","LAST_EXCHANGE","RHO"],
						"ver":0}]}

def getOptionData(*symbols):
	return {"payload":[{"service":"quotes_charts",
							"id":"draftOrderQuotes",
							"account":"COMBINED ACCOUNT",
							"symbols":symbols,
							"fields":["MARK","MARK_CHANGE","MARK_PERCENT_CHANGE","BID","BID_EXCHANGE","ASK","ASK_EXCHANGE","BID_SIZE","ASK_SIZE","VOLUME","OPEN","HIGH52","LOW52","HIGH","LOW","VWAP","VOLATILITY_INDEX","IMPLIED_VOLATILITY","MARKET_MAKER_MOVE","PERCENTILE_IV","HISTORICAL_VOLATILITY_30_DAYS","MARKET_CAP","BETA","PE","INITIAL_MARGIN","LAST","LAST_SIZE","LAST_EXCHANGE","RHO"],
							"ver":0}]}

def getOptionDataForExp(symbol, exp, strikeQuantity=2147483647):
	return {"payload":[{"service":"option_chain",
				 "id":"option_chain",
				 "ver":0,
				 "accountCode":"COMBINED ACCOUNT",
				 "exchange":"BEST",
				 "underlyingSymbol":symbol,
				 "strikeQuantity":strikeQuantity,
				 "seriesNames":[exp],
				 "fields":["BID","ASK","PROBABILITY_ITM","PROBABILITY_OTM","IMPLIED_VOLATILITY","EXTRINSIC","INTRINSIC","OPEN_INT","VOLUME","THEO_PRICE","DELTA","GAMMA","THETA","VEGA","RHO"]}]}


# period // aggregationPeriod
#
# TODAY => MIN1, MIN5, MIN10, MIN15, MIN30, HOUR1
# DAY1 => MIN1, MIN5, MIN10, MIN15, MIN30, HOUR1
# DAY5 => HOUR1, HOUR2, HOUR4
# DAY10 => HOUR1, HOUR2, HOUR4
# DAY20 => HOUR1, HOUR2, HOUR4
# MONTH3 => DAY, WEEK
# MONTH6 => DAY, WEEK
# YTD => DAY, WEEK, MONTH
# YEAR1 => DAY, WEEK, MONTH
# YEAR5 => WEEK, MONTH
# YEAR15 => MONTH
#
# Get price history.
def getChart(symbol, aggregationPeriod, period):
	return {"payload":[{"service":"chart",
						   "id":"chart",
						   "ver":0,
						   "symbol":symbol,
						   "aggregationPeriod":aggregationPeriod,
						   "studies":[],
						   "range":period}]}

def getOptionSeriesQuotes(symbol):
	return {"payload":[{"service":"optionSeries/quotes",
						"id":"optionSeriesQuotes",
						"ver":0,
						"underlying":symbol,
						"exchange":"BEST",
						"fields":["IMPLIED_VOLATILITY","SERIES_EXPECTED_MOVE"]}]}

def getOptionSeries(symbol):
	return {"payload":[{"id":"517729721228393",
						"service":"optionSeries",
						"ver":0,
						"underlying":symbol}]}

def getInstrumentDetails(symbol):
	return {"payload":[{"service":"instrument_details",
				 "ver":0,
				 "id":"instrument/{}".format(symbol),
				 "symbol":symbol,
				 "fields":["DIV_AMOUNT","EPS","EXD_DIV_DATE","PRICE_TICK","PRICE_TICK_VALUE","YIELD"]}]}

def getVolumeData(*symbols):
	return {"payload":[{"service":"study/subscribe",
				 "id":"studyRequest",
				 "ver":0,
				 "symbols":symbols,
				 "account":"COMBINED ACCOUNT",
				 "type":"STUDY",
				 "studies":[{"name":"VolumeAvg",
							 "plot":"VolAvg",
							 "aggregationPeriod":"DAY",
							 "parameters":{"length":"50"}}]}]}

#getOptionChart(".SPY200515C280", "DAY", "YEAR1")
# futures: /ES:XCME

# , '18 MAY 20 100 (Weeklys)', '20 MAY 20 100 (Weeklys)', '22 MAY 20 100 (Weeklys)', '26 MAY 20 100', '27 MAY 20 100 (Weeklys)', '29 MAY 20 100 (Weeklys)', '1 JUN 20 100 (Weeklys)', '3 JUN 20 100 (Weeklys)', '5 JUN 20 100 (Weeklys)', '8 JUN 20 100 (Weeklys)', '10 JUN 20 100 (Weeklys)', '12 JUN 20 100 (Weeklys)', '15 JUN 20 100 (Weeklys)', '17 JUN 20 100 (Weeklys)', '19 JUN 20 100', '26 JUN 20 100 (Weeklys)', '30 JUN 20 100 (Quarterlys)', '17 JUL 20 100', '21 AUG 20 100', '18 SEP 20 100', '30 SEP 20 100 (Quarterlys)', '16 OCT 20 100', '20 NOV 20 100', '18 DEC 20 100', '31 DEC 20 100 (Quarterlys)', '15 JAN 21 100', '19 MAR 21 100', '31 MAR 21 100 (Quarterlys)', '18 JUN 21 100', '17 SEP 21 100', '17 DEC 21 100', '21 JAN 22 100', '18 MAR 22 100', '16 DEC 22 100'

'''
sample = {"payload":[{"service":"option_chain",
				 "id":"option_chain",
				 "ver":0,
				 "accountCode":"COMBINED ACCOUNT",
				 "exchange":"BEST",
				 "underlyingSymbol":"SPY",
				 "strikeQuantity":25,
				 "seriesNames":['15 MAY 20 100' , '18 MAY 20 100 (Weeklys)', '20 MAY 20 100 (Weeklys)', '22 MAY 20 100 (Weeklys)', '26 MAY 20 100', '27 MAY 20 100 (Weeklys)', '29 MAY 20 100 (Weeklys)', '1 JUN 20 100 (Weeklys)', '3 JUN 20 100 (Weeklys)', '5 JUN 20 100 (Weeklys)', '8 JUN 20 100 (Weeklys)', '10 JUN 20 100 (Weeklys)', '12 JUN 20 100 (Weeklys)', '15 JUN 20 100 (Weeklys)'],
				 "fields":["BID","ASK","PROBABILITY_ITM","PROBABILITY_OTM","IMPLIED_VOLATILITY","EXTRINSIC","INTRINSIC","OPEN_INT","VOLUME","THEO_PRICE","DELTA","GAMMA","THETA","VEGA","RHO"]}]}
'''

async def getDataHelper(payload):  
	async with websockets.connect(uri) as websocket:

		for pl in [sessionPayload, loginPayload]:

			await websocket.send(json.dumps(pl))
			await websocket.recv()

		await websocket.send(json.dumps(payload))
		result = await websocket.recv()
		await websocket.close()
		return result

def getData(payload):
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

	try:
		result = loop.run_until_complete(getDataHelper(payload))
	finally:
		asyncio.set_event_loop(None)
		loop.close()

	return result

def getJson(data):

	jsonData = json.loads(data)
	if "payloadPatches" not in jsonData.keys(): return
	else: return jsonData["payloadPatches"][0]["patches"][0]["value"]

def getDfForChart(jsonData):
	df = pd.DataFrame()

	for col in ['timestamps', 'open', 'high', 'low', 'close', 'volume']: 
		df[col] = jsonData[col]

	return df

# this takes so long so its stupid
def getAllOptionData(ticker):

	allOpts = []

	exps = [x["name"] for x in getJson(getData(getOptionSeries(ticker)))["series"]]
	print(exps)
	for exp in exps:
		jsonData = getJson(getData(getOptionDataForExp(ticker, exp)))["expirationSpreadPairs"][0]
		expiration = jsonData["expiration"]
		spreadPairs = jsonData["spreadPairs"]

		print(expiration)

		for spreadPair in spreadPairs:

			'''
			allOpts.append({"strike": float(spreadPair["spreadPair"]["strikeName"]),
							"expiration": expiration,
							"expirationString": spreadPair["spreadPair"]["expirationString"],
							"symbol": spreadPair["spreadPair"]["callSymbol"],
							"values": spreadPair["callValues"]})

			allOpts.append({"strike": float(spreadPair["spreadPair"]["strikeName"]),
							"expiration": expiration,
							"expirationString": spreadPair["spreadPair"]["expirationString"],
							"symbol": spreadPair["spreadPair"]["putSymbol"],
							"values": spreadPair["putValues"]})
			'''

			#print(expiration, float(spreadPair["spreadPair"]["strikeName"]), spreadPair["spreadPair"]["callSymbol"])

def getChartDf(ticker, aggregationPeriod, period):

	start_time = time.time()
	data = getData(getChart(ticker, aggregationPeriod, period))
	jsonData = getJson(data)

	if jsonData is None: return

	df = pd.DataFrame()

	for col in ['timestamps', 'open', 'high', 'low', 'close', 'volume']: 
		df[col] = jsonData[col]

	df["date"] = df.apply(lambda x: datetime.fromtimestamp(x["timestamps"] / 1000).strftime("%Y-%m-%d"), axis=1)

	return df

if __name__ == "__main__":

	df = getChartDf(".INTC200221C67.5", "DAY", "YEAR1")

	#print(df.head())




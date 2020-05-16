#!/usr/bin/env python3

import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from dateutil import tz
import dateutil.parser

import json

def convert_iso_to_dt(iso_time):
	return dateutil.parser.isoparse(iso_time).replace(tzinfo=tz.gettz('America/New_York'))

def convert_date_to_dt(date):
	
	if len(date) == 10 and "-" in date:
		return datetime.strptime(date, "%Y-%m-%d").replace(hour=16, minute=0).replace(tzinfo=tz.gettz('America/New_York'))
	elif "/" in date:
		if len(date) == 8:
			return datetime.strptime("20"+date, "%Y/%m/%d").replace(hour=16, minute=0).replace(tzinfo=tz.gettz('America/New_York'))
		elif len(date) == 10:
			return datetime.strptime(date, "%Y/%m/%d").replace(hour=16, minute=0).replace(tzinfo=tz.gettz('America/New_York'))
	
	return datetime(2030, 1, 1, 16, 0).replace(tzinfo=tz.gettz('America/New_York'))

def get_dte(order_date, expiry_date):
	
	if expiry_date.year == 2030: return -1
	return (expiry_date - order_date).days	

def column_to_float(data, *column, feedback=True):
	fdata = data.copy()
	
	for col in column:
		fdata[col] = fdata[col].astype(str).apply(lambda x: x.replace(',','')).astype(np.float32)
			
		if feedback: print("Converted column \"{}\" to float".format(col))  
			
	return fdata

def get_moneyness(call_put, strike, spot):
	if call_put == "CALLS": return (strike/spot) - 1
	else: return 1 - (strike/spot)

class flowAlgo():

	def __init__(self, fileDir):
		self.fileDir = fileDir

		f = open(fileDir, "r")
		self.rawData = pd.json_normalize(json.loads(f.read()))

		self.data = self.rawData.copy()
	
		self.data = self.data[["date",
					"slug",
					"status",
					"type",
					"ticker",
					"title.rendered",
					"acf.flow_type",
					"acf.option_bet_size",
					"acf.option_call_or_put",
					"acf.option_contract_amount",
					"acf.option_contract_price",
					"acf.option_expiration",
					"acf.option_order_type",
					"acf.option_reference_price",
					"acf.option_strike",
					"acf.option_open_interest",
					"acf.option_volume",
					"acf.flow_ticker",
					"acf.flow_order_time",
					"acf.option_delta",
					"acf.ivol_change",
					"acf.sector",
					"acf.underlying_avg_daily_volume",
					"acf.order_status"]]
		
		self.data = column_to_float(self.data, "acf.option_bet_size",
								"acf.option_contract_amount",
								"acf.option_contract_price",
								"acf.option_reference_price",
								"acf.option_strike",
								"acf.option_open_interest",
								"acf.option_volume",
								"acf.option_delta",
								"acf.ivol_change")
		
		self.data["date"] = self.data.apply(lambda x: convert_iso_to_dt(x["date"]), axis=1)
		print("Converted dates to datetime objs.")
		
		self.data["acf.option_expiration"] = self.data.apply(lambda x: convert_date_to_dt(x["acf.option_expiration"]), axis=1)
		print("Converted expiration dates to datetime objs.")
		
		self.data["acf.dte"] = self.data.apply(lambda x: get_dte(x["date"], x["acf.option_expiration"]), axis=1)
		print("Created \"acf.dte\" column.")
		
		self.data["acf.moneyness"] = self.data.apply(lambda x: get_moneyness(x["acf.option_call_or_put"], x["acf.option_strike"], x["acf.option_reference_price"]), axis=1)
		print("Created \"acf.moneyness\" column.")

	def getData(self):
		return self.data

if __name__ == "__main__":

	fa = flowAlgo("merged_2020_04.json")


		
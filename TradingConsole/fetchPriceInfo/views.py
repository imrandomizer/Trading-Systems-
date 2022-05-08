from django.shortcuts import render
from django.http import HttpResponse
from nsetools import Nse
from django.http import JsonResponse 
import html
import json
from time import localtime, strftime

#this is a part of fetchPriceInfo app for TradingConsole Server 
#this will fetch the current price info from NSE site

nse = Nse()

def fetchPreMarketInfo():
	
	globalJsonForPremarket = nse.downloadUrlNewSite("https://www.nseindia.com/api/market-data-pre-open?key=ALL")
	jsData = json.loads(globalJsonForPremarket)
	processedJson = dict()

	for x in jsData["data"]:
		symbol = x["metadata"]["symbol"]
		data = dict()
		data["pChange"]           = str(x["metadata"]["pChange"])
		if(len(data["pChange"])>3):
			data["pChange"] = float(data["pChange"][:3])

		data["lastPrice"]         = x["metadata"]["lastPrice"]
		data["totalTradedVolume"] = x["detail"]["preOpenMarket"]["totalTradedVolume"]
		data["purpose"]           = x["metadata"]["purpose"]
		if(data["purpose"]==None):data["purpose"] = ""
		data["totalBuyQuantity"]  = x["detail"]["preOpenMarket"]["totalBuyQuantity"]
		data["totalSellQuantity"] = x["detail"]["preOpenMarket"]["totalSellQuantity"]
		processedJson[symbol] = data

	#print(processedJson)
	return processedJson

def index(request):
	response = "NULL"
	symbol = "None"
	preMarket = "No"

	try:
		symbol = request.GET["SYMBOL"]
	except:
		print("NO SYMBOL PROVIDED")

	try:
	
		preMarket = request.GET["PREMARKET"]
		
	except:
		pass
	#print(preMarket)
	try:
		if("Yes" in preMarket and len(preMarket)==3):
			response = fetchPreMarketInfo()
			#print(response)
		else:
			symbol = html.unescape(symbol)
			response = nse.get_quote(symbol)
		#print(response)
	except Exception as e:
		print(e)
	return JsonResponse(response)
from optionChain import *
import downloadCashMarketActivityData
import json
from datetime import datetime
import random



symbolFileName = "/home/pi/Feynman-Server/staticContentHelper/FOSYMBOLS"
allSymbolList  = []
from nsetools import Nse
nse = Nse()

scriptCapturesIndexData = True

def fetchDataSymbol(symbolName):
	global scriptCapturesIndexData
	if(scriptCapturesIndexData == True):
		if("NIFTY" not in symbolName):
			return
	print("Invoked for Symbol :",symbolName," @ ",str(datetime.now()))
	d = optionChainAnalysis(symbolName)
	d.analyzeOptionChain(refresh=True)

def readAllSymbolNames():

	handle = open(symbolFileName)
	data   = handle.read()
	handle.close()

	data = data.split("\n")
	for x in data:
		allSymbolList.append(x)

def isMarketOpen():
	#override for debugging
	#return True

	try:
		statusData = nse.downloadUrlNewSite("https://www.nseindia.com/api/marketStatus")
		statusData = json.loads(statusData)
	except:
		return False

	for x in statusData["marketState"]:

		if("Capital Market" in x["market"]):
			if("Close" in x["marketStatus"]):
				return  False
			else:
				return True

	#TODO if reached here we have to rely on the timestamp will take care later 



def main():

	readAllSymbolNames()

	marketOpen = True

	while(1):
		if(isMarketOpen()):
			for x in allSymbolList:
				print("COLLECTING DATA FOR ",x)
				try:
					fetchDataSymbol(x)
				except Exception as e:
					print(e)

			marketOpen = True


				
			print("Fetched All Symbols Sleeping for 600 Secs")
			#print("Fetching Cash MArket Activity")

			#downloadCashMarketActivityData.getData()

			time.sleep(600)
		else:
			if(marketOpen):
				#collect data one last time before setting this variable as false
				marketOpen = False
				for x in allSymbolList:
					print("COLLECTING DATA FOR ",x)
					try:
						fetchDataSymbol(x)
					except Exception as e:
						print(e)

				print("Post market collection Done")

				print("Fetching Cash MArket Activity")

				downloadCashMarketActivityData.getData()

			x = random.randint(0,5)
			if(x==4):
				#every so often even if the market is closed try to get this data
				print("Fetching Cash MArket Activity")

				downloadCashMarketActivityData.getData()

			print("Market Closed Sleeping for 600 Secs")
			time.sleep(600)

main()

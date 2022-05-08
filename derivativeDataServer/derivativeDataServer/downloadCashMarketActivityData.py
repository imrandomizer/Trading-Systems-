import html
import json
import time
import os.path
from nsetools import Nse
from time import localtime, strftime 
from datetime import datetime, timedelta
import pprint
from dateutil.tz import *


cashMarketActivityDBLocation = "/home/pi/Feynman-Server/DATA/CASHMARKETACTIVITY/"

"""
DATE
	DII - > net value
			total volume
	FII - > net value
			total volume

"""

def loadJSON():
	
	ret = dict()
	try:
		file = open(cashMarketActivityDBLocation+"activity.json")
		data = file.read()
		file.close()
		ret = json.loads(data)
	except Exception as e:
		print (e)

	return ret

def saveJSON(fileJSONStructure):

	fileName = cashMarketActivityDBLocation+"activity.json"

	with open(fileName, 'w') as f:
            json.dump(fileJSONStructure, f)



def getData():
	nse = Nse()
	url = "https://www.nseindia.com/api/fiidiiTradeReact"
	
	for x in range(0,10):
		try:
			data = nse.downloadUrlNewSite(url)
			print(data)
			structure = json.loads(data)
			existingJSON = loadJSON()
			print("existingJSON ",existingJSON)

			activityData = dict()
			
			date = ""

			for s in structure:
				activityData[s["category"]] = s
				date = s["date"]

			existingJSON[date] = activityData

			saveJSON(existingJSON)
			break
		except Exception as e:
			print(e)
			print("RETRY COUNT ",x)
			time.sleep(4)



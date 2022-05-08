import os
import sys
import subprocess
import time
from datetime import datetime
import random

varMargins = dict()
symbolNameDict = dict()
priceBand      = dict()


debugFlag = True
#debugFlag = False

def debug(message):
	if(debugFlag):
		print(message)

def checkIfReqToDownloadBhavDataFile():

	try:
		outp = subprocess.check_output(["ls","-lart","out.csv"])
		outs = str(outp).split("\n")
		for x in outs:
			timestamp = datetime.today().strftime('%m-%d')
			allchr = x.split(" ")
			timestamp = timestamp.split("-")

			month  = None
			monthLis = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
			month = str(monthLis[int(timestamp[0])-1])

			day = timestamp[1]
			timeIn = allchr[7].split(":")
			#print(timeIn)
			hr = int(timeIn[0])

			if(allchr[5] in month and allchr[6] in day):
				if(hr>20):
					print("Using Previous File")
					return None
			else:
				break
	except Exception as e:
		print(e)
		print("Importing for First time")
		pass
	print("EXECUTING")
	try:
		os.system("curl -k  https://archives.nseindia.com/content/equities/sec_list.csv -o /home/pi/Feynman-Server/staticContentHelper/priceBand.csv > /dev/null 2>&1")

	except:
		print("Unable to download priceband data")

	os.system("curl -k https://www1.nseindia.com/products/content/sec_bhavdata_full.csv -o out.csv > /dev/null 2>&1")


def loadLatestBhavDataFile():
	checkIfReqToDownloadBhavDataFile()
	file = open("out.csv","r")
	data = file.read().split("\n")
	file.close()
	bhavData= data[1:]
	return bhavData

def loadVARFile():
	fileDef = "https://www1.nseindia.com/archives/nsccl/volt/CMVOLT_10082020.CSV"
	os.system("curl -k "+fileDef+" -o varMargins.csv > /dev/null 2>&1")
	file = open("varMargins.csv")
	data = file.read().split("\n")
	data = data[1:]
	for x in data:
		allD = x.split(",")
		try:
			varMargins[allD[1]] = float(allD[7])
		except:
			try:
				varMargins[allD[1]] = 1
			except:
				pass

loadVARFile()
#print(varMargins)


def readSymbolNameDict():
	file = open("/home/pi/Feynman-Server/staticContentHelper/EQUITY_L.csv")
	data = file.read().split("\n")
	data = data[1:]
	for x in data:
		d = x.split(",")
		try:
			symbolNameDict[d[0]]=d[1]
		except:
			pass

readSymbolNameDict()


#try to only keep shares which have a possibility to move >10 percent in a day
def readSymbolPriceBand():
	fl = open("/home/pi/Feynman-Server/staticContentHelper/priceBand.csv")
	da = fl.read().split("\n")[1:]
	for x in da:
		allRows = x.split(",")
		band = 10
		try:
			band = allRows[3]
		except:
			print("allRows >> ",allRows)
			continue
		try:
			band = int(band)
		except:
			band = 10

		if("EQ" in allRows[1]):
			priceBand[allRows[0]] = band


readSymbolPriceBand()
#print(priceBand)


def processBhavDataFile():
	lis = []

	colName = ["SYMBOL", "SERIES", "DATE1", "PREV_CLOSE", "OPEN_PRICE", "HIGH_PRICE", "LOW_PRICE", "LAST_PRICE", "CLOSE_PRICE", "AVG_PRICE", "TTL_TRD_QNTY", "TURNOVER_LACS", "NO_OF_TRADES", "DELIV_QTY", "DELIV_PER"]

	lim = 250000
	data = loadLatestBhavDataFile()
	#print("LENGTH ::: ", len(data))

	for x in data:
		cols = x.split(",")
		symb = dict()
		i = 0
		for y in cols:
			symb[colName[i]] = y
			i += 1

		lis.append(symb)

		lim -= 1
		if(lim<0):
			break

	array = []

	date = ""



	print("READ ",len(lis)," SYMBOLS")
	#print("ORIGLIST",lis)


	lisTrades     = []
	lisTurnOver   = []

	for x in lis:
		try:
			tOver = float(x["TURNOVER_LACS"].strip())
			tradeCnt = float(x["TTL_TRD_QNTY"].strip())
			if(tOver>50):
				lisTurnOver.append(tOver)
			if(tradeCnt>500):
				lisTrades.append(tradeCnt)
		except:
			print("DDEBUG ", x)

	lisTrades.sort()
	lisTurnOver.sort()

	print("MEDIAN Trades   : ",lisTrades[int(len(lisTrades)/2)])
	print("MEDIAN TurnOver : ",lisTurnOver[int(len(lisTurnOver)/2)])




	debug(lis)
	for x in lis:
		TURNOVER_LACS = 0
		NO_OF_TRADES = 0
		try:
			date = x["DATE1"]
		except:
			pass

		try:
			TURNOVER_LACS = float(x["TURNOVER_LACS"].strip())
			NO_OF_TRADES  = float(x["TTL_TRD_QNTY"].strip())
		except:
			pass

		if(len(x["SYMBOL"])<1):
			continue
		try:
			volatility = 1
			try:
				volatility = varMargins[x["SYMBOL"]]
			except:
				pass

			#print(volatility)
			volatilityCheck = volatility>=0.6 and volatility <=1.5

			priceBandCheck = True
			band = 10

			try:
				band = priceBand[x["SYMBOL"]]
			except:
				debug("BAND info not found for "+x["SYMBOL"])

			#only include stocks which can move more than 5 percent in a day
			if(band>5):
				priceBandCheck = True
			else:
				debug("PRICE BAND CHECK SET TO FALSE for "+x["SYMBOL"])
				priceBandCheck = False

			if(volatilityCheck==False):
				debug("VOLATILITY CHECK SET TO FALSE FOR "+x["SYMBOL"])

			noOfTradesCheck = NO_OF_TRADES>6000

			if(noOfTradesCheck==False):
				debug("NO OF TRADES CHECK SET TO FALSE FOR "+x["SYMBOL"])

			turnOverMedian = 700

			turnOverMedian = lisTurnOver[int(len(lisTurnOver)/2)-10]
			debug("TURNOVER CUTOFF "+str(turnOverMedian))


			turnoverCheck = int(TURNOVER_LACS)>int(turnOverMedian)

			if(turnoverCheck==False):
				debug("Turnover CHECK SET TO FALSE FOR "+x["SYMBOL"])

			deleverableCheck = True

			#if there are more than 95 percent develeries share is mos likely an ETF.
			try:
				if(float(x["DELIV_PER"])>=95):
					deleverableCheck = False
			except:
				pass




			
			#print(volatilityCheck)
			if("-" not in x["DELIV_PER"] and float(x["OPEN_PRICE"].strip())>30 and deleverableCheck and turnoverCheck and noOfTradesCheck and "EQ" in x["SERIES"] and volatilityCheck and priceBandCheck):
				array.append([float(x["DELIV_PER"].strip()),x["SYMBOL"]])
				debug("ADDING "+x["SYMBOL"])
			else:
				debug("REJECTED : SYMBOL "+x["SYMBOL"]+"deleverableCheck :"+str(deleverableCheck)+" turnoverCheck : "+str(turnoverCheck)+" noOfTradesCheck :"+str(noOfTradesCheck)+" volatilityCheck : "+str(volatilityCheck)+" priceBandCheck : "+str(priceBandCheck))
			"""else:
				print(x,TURNOVER_LACS,x["SERIES"])
				if(float(x["OPEN_PRICE"].strip())>50):
					os.exit()
	"""
			#if("NESCO" in x["SYMBOL"]):
			#		print("sds",x)

		except Exception as e:
			print("256",e) 
			#os.exit()
			pass

	debug("RETURNED ARRAY")
	debug(array)
	return date,array
	#print(array)

def formatDistance(already,dist):
	alr = len(already)
	dist = dist - alr
	strs = ""
	for x in range(0,dist):strs += " "
	return strs



def deliverablePattern(arg):
	


	loadLatestBhavDataFile()
	date, array  = processBhavDataFile()
	print("No of scripts in comparison : ",len(array))
	if(arg!=None):
		for x in range(0,len(array)):
			try:
				if(arg in symbolNameDict.get(array[x][1],"") or arg in array[x][1]):
					message = array[x][1]
					message += formatDistance(message,25)
					try:
						message += symbolNameDict[array[x][1]]
					except:
						continue
					message += formatDistance(message,80)
					message += str(array[x][0])
					print(message)
			except:
				print(array[x])
				os.exit()

		return None



	array.sort(reverse=True)

	finalList = [[]]
	for x in range(0,35):
		try:
			lis = []
			message = array[x][1]
			lis.append(array[x][1])

			message += formatDistance(message,25)
			try:
				lis.append(symbolNameDict[array[x][1]])
				
			except:
				lis.append(array[x][1])
			lis.append(str(array[x][0]))

			#appending these 4 things to put a null place holder in place of col current price / pChange and others (currently 4 cols) 
			lis.append(0)
			lis.append(0)
			lis.append(0)
			lis.append(0)
			finalList.append(lis)
		except:
			print(array[x])
			os.exit()
	highestDeliv =  finalList


	array.sort(reverse=False)
	#print(array)
	finalList = [[]]
	for x in range(0,35):
		try:
			lis = []
			message = array[x][1]
			lis.append(array[x][1])

			message += formatDistance(message,25)
			try:
				lis.append(symbolNameDict[array[x][1]])
				
			except:
				lis.append(array[x][1])
			lis.append(str(array[x][0]))
			#appending these 4 things to put a null place holder in place of col current price / pChange and others (currently 4 cols) 
			lis.append(0)
			lis.append(0)
			lis.append(0)
			lis.append(0)
			finalList.append(lis)
		except:
			print(array[x])
			os.exit()

	lowestDeliv = finalList
	return highestDeliv,lowestDeliv,date 
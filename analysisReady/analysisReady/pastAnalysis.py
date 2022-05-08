import os
from time import localtime, strftime 
from datetime import datetime, timedelta
import time
import pprint
from nsetools import Nse
import random
import inspect
import json
from candlestick import candlestick

#production code

#symbols under blacklist

blacklist = ["GOLDBEES","SETFGOLD","LIQUIDBEES","SETFNIFBK","KOTAKBKETF","N100","HDFCMFGETF"]

#required to be made manually
databaseFileName = "./Database/"
cashMarketReportFile = "/home/pi/Feynman-Server/DATA/CASHMARKETACTIVITY/activity.json"

#keep files as old as 15 days for analysis.
#buffer of 4 days for saturdays and sundays
fileDaysLimit    = 15 + 4 

#fileDaysLimit = 5

nse = Nse()

#for fetch Historical Price
debugFlag = False

#for past datastructure
debug2 = False

#TODO still have to handle holidays

def debug(string):
	#only callable  from within classes

	global debugFlag
	global debug2

	try:
		callerName = inspect.stack()[1][0].f_locals["self"].__class__.__name__
		
		if(debugFlag == True and "fetchHistoricalData" in callerName):
			pprint.pprint(string)
		if(debug2 == True and "pastDataStructure" in callerName):
			pprint.pprint(string)
	except:
		pprint.pprint(String)


class fetchParticipantData:

	participantDataObject = None
	global cashMarketReportFile

	def extractRowData(self,rowData):
		rowData = rowData.split(",")

		rowDataDict = dict()

		rowDataDict["Client Type"] = rowData[0]
		rowDataDict["Future Index Long"] = rowData[1]
		rowDataDict["Future Index Short"] = rowData[2]
		rowDataDict["Future Stock Long"] = rowData[3]
		rowDataDict["Future Stock Short"] = rowData[4]
		rowDataDict["Option Index Call Long"] = rowData[5]
		rowDataDict["Option Index Put Long"] = rowData[6]
		rowDataDict["Option Index Call Short"] = rowData[7]
		rowDataDict["Option Index Put Short"] = rowData[8]
		rowDataDict["Option Stock Call Long"] = rowData[9]
		rowDataDict["Option Stock Put Long"] = rowData[10]
		rowDataDict["Option Stock Call Short"] = rowData[11]
		rowDataDict["Option Stock Put Short"] = rowData[12]
		rowDataDict["Total Long Contracts"] = rowData[13]
		rowDataDict["Total Short Contracts"] = rowData[14]

		return rowDataDict
		 

	def __init__(self):
		global databaseFileName
		self.participantDataObject = dict()
		#print(databaseFileName)
		fileListToParse = self.filesInDir(databaseFileName)
		for x in fileListToParse:
			

			currFile = open(databaseFileName+x[1])
			dataInFile = currFile.read()

			currFile.close()

			dataInFile = dataInFile.split("\n")
			dateDataDict = dict()
			


			for line in  dataInFile:

				if("DII," in line):
					dateDataDict["DII"] = self.extractRowData(line)
				if("FII," in line):
					dateDataDict["FII"] = self.extractRowData(line)
				if("Client," in line):
					dateDataDict["Client"] = self.extractRowData(line)
				if("Pro," in line):
					dateDataDict["Pro"] = self.extractRowData(line)
			#print(dateDataDict)
			self.participantDataObject[x[0]] = dateDataDict

		finalDict = dict()

		#Now fetch Cash market reports
		f = open(cashMarketReportFile)
		cashMarketData = f.read()
		f.close()
		response = json.loads(cashMarketData)

		finalDict["CASH_MARKET"] = response
		finalDict["FUTURES_MARKET"] = self.participantDataObject

		self.participantDataObject = finalDict


	def filesInDir(self,dirName):
		#file names should be of the form mmdd
		files = os.listdir(dirName)

		#contains list of lists [date in integer form , in orignal String form]
		fileNames = []
		for x in files:
			if("participantData" in x):
				sp = x.split("_")
				fileNames.append([int(sp[1]),x])

		fileNames.sort(reverse=True)
		return fileNames

class fetchHistoricalData:

	listOfFilesToParse = []

	def __init__(self):
		global databaseFileName
		
		## first try to figure out the names of the file in the database already.
		existingFiles = self.filesInDir(databaseFileName)

		## figure out the list of files to download and their equivalent target and web links, it will also return the names of old files to delete
		newFilesToGet,toBeDeletedFiles,validFiles = self.newFileList(existingFiles)
		debug("TO BE ADDED")
		debug(newFilesToGet)
		debug("TO BE Deleted Files")
		debug(toBeDeletedFiles)

		filesDownloadedSuccesfully = self.downloadFiles(self.buildDownloadListFromToBeAdded(newFilesToGet))
		debug("FILES DOWNLOADED SUCCESSFULLY")
		debug(filesDownloadedSuccesfully)
		self.deleteOldFiles(toBeDeletedFiles)
		self.listOfFilesToParse = validFiles

	def getListOfFilesToParse(self):
		global databaseFileName
		x = random.randint(1,5)
		if(x==2):
			debug("REFETCH")

		
			## first try to figure out the names of the file in the database already.
			existingFiles = self.filesInDir(databaseFileName)

			## figure out the list of files to download and their equivalent target and web links, it will also return the names of old files to delete
			newFilesToGet,toBeDeletedFiles,validFiles = self.newFileList(existingFiles)
			debug("TO BE ADDED")
			debug(newFilesToGet)
			debug("TO BE Deleted Files")
			debug(toBeDeletedFiles)

			filesDownloadedSuccesfully = self.downloadFiles(self.buildDownloadListFromToBeAdded(newFilesToGet))
			debug("FILES DOWNLOADED SUCCESSFULLY")
			debug(filesDownloadedSuccesfully)
			self.deleteOldFiles(toBeDeletedFiles)
			self.listOfFilesToParse = validFiles
			return self.listOfFilesToParse

		return self.listOfFilesToParse

	def buildDownloadListFromToBeAdded(self,newFilesToGet):
		allUrlsList = []

		for x in newFilesToGet:
			strRepr = x[1]
			day = strRepr[4:]
			month = strRepr[2:4]
			year = strRepr[:2]
			allUrlsList.append([strRepr,day,month,year])
		debug("NEW FILES TO GET")
		debug(allUrlsList)
		return allUrlsList


	#url will look like https://www1.nseindia.com/content/historical/EQUITIES/2020/JUL/cm07JUL2020bhav.csv.zip
	#the day and month as 01, 02 ... and year "20","21"... is expected from caller
	#[fileNameToSaveAs, dd, mm , yy]
	def downloadFiles(self,allUrlsList):
		try:
			os.mkdir("temp")
		except:
			pass

		filesDownloadedSuccesfully = []

		for x in allUrlsList:
			fileName = x[0]
			dd = x[1]
			mm = int(x[2])
			debug(mm)


			monthLis = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
			origMonthNos = x[2]
			mm = monthLis[mm-1].upper()
			yy = "20"+x[3]

			url = "https://www1.nseindia.com/content/historical/EQUITIES/"+yy+"/"+mm+"/"+"cm"+dd+mm+yy+"bhav.csv.zip"
			urlForDelivs = "https://www.nseindia.com/api/reports?archives=%5B%7B%22name%22%3A%22CM%20-%20Security-wise%20Delivery%20Positions%22%2C%22type%22%3A%22archives%22%2C%22category%22%3A%22capital-market%22%2C%22section%22%3A%22equities%22%7D%5D&date="+dd+"-"+mm+"-"+yy+"&type=equities&mode=single" 
			
			#for the participantData
			urlParticipantData = "https://www1.nseindia.com/content/nsccl/fao_participant_oi_"+x[1]+x[2]+yy+".csv"


			#new url for deliv
			#https://archives.nseindia.com/archives/equities/mto/MTO_25092020.DAT
			#urlForDelivs = "https://archives.nseindia.com/archives/equities/mto/MTO_"+dd+origMonthNos+yy+".DAT"
			#urlParticipantData  = "https://www1.nseindia.com/content/nsccl/fao_participant_oi_23112021.csv"
			#TODO write implementation for backup fetch using BSE Data
			#https://www.bseindia.com/BSEDATA/gross/2020/SCBSEALL2809.zip



			curlCmdToExecute = "curl "+url+" -o file.zip -k  > /dev/null 2>&1"
			debug("EXECUTING")
			debug(curlCmdToExecute)

			try:
				output = os.system(curlCmdToExecute)
				if(output != 0 ):
					print("ERROR IN EXECUTING "+curlCmdToExecute)
					continue

				output = os.system("unzip file.zip")
				if(output != 0 ):
					print("ERROR IN EXECUTING "+"unzip file.zip > /dev/null 2>&1")
					os.exit()
					continue

				output = os.system("rm file.zip")
				if(output != 0 ):
					print("ERROR IN EXECUTING "+"rm file.zip > /dev/null 2>&1")

					continue

				output = os.system("mv "+"cm"+dd+mm+yy+"bhav.csv"+ " "+fileName+" > /dev/null 2>&1")
				if(output != 0 ):
					print("ERROR IN EXECUTING "+"mv "+"cm"+dd+mm+yy+"bhav.csv"+ " "+fileName)
					continue

				output = os.system("mv "+fileName+" "+databaseFileName+". > /dev/null 2>&1")
				if(output != 0 ):
					print("ERROR IN EXECUTING "+"mv "+fileName+" "+databaseFileName+".")
					continue

				filesDownloadedSuccesfully.append("cm"+dd+mm+yy+"bhav.csv")

			except:
				os.exit()
				debug("UNABLE TO DOWNLOAD FILE")
				debug(curlCmdToExecute)


			##now try to download the deliv data and save to appropriate dir.

			try:
				print("DOWNLOADING  >>>"+urlForDelivs)

				nse1 = Nse()

				#dataDeliv = nse1.downloadUrlNewSite_archiveSite(urlForDelivs)
				dataDeliv = nse.downloadUrlNewSite(urlForDelivs)
				
				fHandle = open(databaseFileName+fileName+"_Deliv","w")
				fHandle.write(dataDeliv)
				fHandle.close()
				time.sleep(random.randint(1,3))
			except Exception as e:
				print(e)
				debug("UNABLE TO LOAD THE DELIV FILE "+urlForDelivs)

			## now download participant data.


			curlCmdToExecute = "curl "+urlParticipantData+" -o participantData_"+yy+x[2]+dd+" -k  > /dev/null 2>&1"
			debug("EXECUTING")
			debug(curlCmdToExecute)

			try:
				print("DOWNLOADING  >>>"+urlParticipantData)

				output = os.system(curlCmdToExecute)
				if(output != 0 ):
					print("ERROR IN EXECUTING "+curlCmdToExecute)
					continue

				output = os.system("mv "+"participantData_"+yy+x[2]+dd+ " "+databaseFileName+". > /dev/null 2>&1")
				if(output != 0 ):
					print("ERROR IN EXECUTING "+"participantData_"+dd+x[2]+yy+ " "+databaseFileName)
					continue


			except Exception as e:
				print(e)
				debug("UNABLE TO LOAD THE PARTICIPANT FILE "+urlParticipantData)

		return filesDownloadedSuccesfully


	#reads the existing files in the directory
	def filesInDir(self,dirName):
		#file names should be of the form mmdd
		files = os.listdir(dirName)

		#contains list of lists [date in integer form , in orignal String form]
		fileNames = []
		for x in files:
			if("Deliv" not in x and "participantData" not in x):
				fileNames.append([int(x),x])

		fileNames.sort(reverse=True)
		return fileNames

	#this will return integerReprOfDate , stringReprOfDate
	def subtractDays(self,days_to_subtract):
		newDate  = datetime.today() - timedelta(days=days_to_subtract)

		retDay = newDate.day
		if(retDay<10):
			retDay = str("0")+str(retDay)
		else:
			retDay = str(retDay)

		retMonth = newDate.month
		if(retMonth<10):
			retMonth = str("0")+str(retMonth)
		else:
			retMonth = str(retMonth)


		retYear  = str(newDate.year)
		retYear  = retYear[2:]

		return int(retYear+retMonth+retDay),str(retYear+retMonth+retDay)


	def getFormattedStamps(self,timestamp):
		day   = timestamp.day
		month = timestamp.month
		year  = timestamp.year



		retDay = day
		if(retDay<10):
			retDay = str("0")+str(retDay)
		else:
			retDay = str(retDay)

		retMonth = month
		if(retMonth<10):
			retMonth = str("0")+str(retMonth)
		else:
			retMonth = str(retMonth)


		retYear  = str(year)
		retYear  = retYear[2:]

		return int(retYear+retMonth+retDay),str(retYear+retMonth+retDay)

	def deleteOldFiles(self,toBeDeletedFiles):
		for x in toBeDeletedFiles:
			try:
				os.system("rm ./"+databaseFileName+"/"+x[1])
			except:
				pass

	#returns true if the current date was a holiday

	def checkIfDateIsHoliday(self,dateToCheck):
		#hardcoding it for now will fetch from relevant archive in future
		#format YYYY-MM-DD
		lisOfHolidays = ["2021-11-04","2021-11-05","2021-11-19","2022-01-26"]

		dateToCheck   = str(dateToCheck).split(" ")[0]

		if(dateToCheck in lisOfHolidays):
			return True
		else:return False

	#
	def newFileList(self,existingFiles):
		global fileDaysLimit

		#first fetch current date
		year  = time.strftime("%y",localtime())
		#will be 20 , 21 and so on

		month = time.strftime("%m",localtime())
		date  = time.strftime("%d",localtime())

		#assuming the date returned will be 04 if the day is 4

		integerReprOfDate = int(year+month+date)
		stringReprOfDate  = str(year+month+date)

		debug("CURRENT DATE FETCHED and conv to int ")
		debug(integerReprOfDate)

		fileNamesToDownload = []

		#used to calculate the to be deleted files.
		lastValOfX = 1
		debug("DATE LIMIT: "+str(fileDaysLimit))
		currentDate = datetime.today()

		#this will be used to fetch the dates in subtract Days
		adder = 0
		validFiles = []

		for x in range(1,fileDaysLimit):
			#checkWeekday ? if yes move the dates one or two days back depending.

			if(currentDate.weekday()==6):

				#saturday -> friday one day back
				debug("ENCOUNTERED SUNDAY")
				currentDate = currentDate - timedelta(days=2)
				adder += 2
				integerReprOfDate,stringReprOfDate = self.getFormattedStamps(currentDate)
			else:
				if(currentDate.weekday()==5):
					debug("ENCOUNTERED SATURDAY")
					currentDate = currentDate - timedelta(days=1)
					adder += 0
					integerReprOfDate,stringReprOfDate = self.getFormattedStamps(currentDate)


			if(self.checkIfDateIsHoliday(currentDate)):
				debug(str(currentDate)+" WAS A HOLIDAY")
				currentDate = currentDate - timedelta(days=1)
				adder += 0
				integerReprOfDate,stringReprOfDate = self.getFormattedStamps(currentDate)
				if(currentDate.weekday()==6):

					#saturday -> friday one day back
					debug("ENCOUNTERED SUNDAY")
					currentDate = currentDate - timedelta(days=2)
					adder += 2
					integerReprOfDate,stringReprOfDate = self.getFormattedStamps(currentDate)
				else:
					if(currentDate.weekday()==5):
						debug("ENCOUNTERED SATURDAY")
						currentDate = currentDate - timedelta(days=1)
						adder += 0
						integerReprOfDate,stringReprOfDate = self.getFormattedStamps(currentDate)

			
			debug("Adder ")
			debug(adder)
			debug(x)
			
			debug(currentDate)
			debug("READY TO ADD")
			debug(integerReprOfDate)
			debug(stringReprOfDate)
			
			lastValOfX = x+adder
			if(len(existingFiles)>(x-1)):
				
				if(existingFiles[x-1][1] ==  stringReprOfDate):
					debug("The last file already is downloaded")

					#all the files to be downloaded are added to the list

			#this file has to be downloaded generate the fileName
			toAdd = True

			for y in existingFiles:
				if(y[1]==stringReprOfDate):
					#validFiles.append([integerReprOfDate,stringReprOfDate])
					toAdd = False


			if(toAdd):
				
				fileNamesToDownload.append([integerReprOfDate,stringReprOfDate])

			validFiles.append([integerReprOfDate,stringReprOfDate])

			#generate the next fileName
			debug("CURRENT DATE")
			debug(currentDate)
			currentDate = currentDate - timedelta(days=1)
			integerReprOfDate,stringReprOfDate = self.getFormattedStamps(currentDate)


		#All the files to download have been calculated at this point
		#Now calculate the file names to delete


		debug("VALID FILES")
		debug(validFiles)
 
		filesToDelete =[]

		for x in existingFiles:
			if(x not in validFiles):
				filesToDelete.append(x)


		if(len(fileNamesToDownload)>=1):
			valid = self.isLastDateValid(fileNamesToDownload[0][1])
			debug("IS VALID")
			debug(valid)
			if(valid == False):
				fileNamesToDownload = fileNamesToDownload[1:]
				validFiles = validFiles[1:]

		return fileNamesToDownload,filesToDelete,validFiles

	#check if the current bhav data file is available or not ?
	def isLastDateValid(self,value):
		global nse
		year = "20"+value[:2]
		month = value[2:4]
		day = value[4:]
		debug("URL FOR VALIDATION")
		date = day+"-"+month+"-"+year
		debug(date)
		url = "https://www1.nseindia.com/ArchieveSearch?h_filetype=eqbhav&date="+date+"&section=EQ"
		debug(url)
		content = nse.downloadUrl(url)
		if("Try another date" in content):
			return False
		return True


#this builds the basic datastructure for the past x days of data
class pastDataStructure:

	collectedData = dict()

	"""
	STRUCTURE 

	collectedData{
		SYMBOLNAME1{
			TIMESTAMP1{
				Open
				close
				high
				totalTrades
				...
			}
			TIMESTAMP2{
				...
			}
		}
		SYMBOLNAME2{
			...
		}
	}

	"""

	def __init__(self,listOfFilesToParse):
		for x in listOfFilesToParse:
			fileHandle = open(databaseFileName+x[1])
			content    = fileHandle.read().split("\n")[1:]
			fileHandle.close()

			fileHandle = open(databaseFileName+x[1]+"_Deliv")
			contentDeliv = fileHandle.read().split("\n")[3:]
			fileHandle.close()

			#loadthe content of deliv to a dict so it can be used by the code below

			delivForThisDate = dict()

			for row in contentDeliv:
				allConRow = row.split(",")
				if(len(allConRow)>=7):
					#if("ZEEL" in allConRow[2]):print(">>>>>>>>>>",row)
					if("EQ" in allConRow[3]):delivForThisDate[allConRow[2]]=allConRow[6]

			rowNames = ["SYMBOL","SERIES","OPEN","HIGH","LOW","CLOSE","LAST","PREVCLOSE","TOTTRDQTY","TOTTRDVAL","TIMESTAMP","TOTALTRADES","ISIN"]


			for rows in content:
				allCols = rows.split(",")

				symbName = allCols[0]



				if(symbName==None or len(symbName)<1):
					continue

				symbData = dict()

				for i in range (1,len(rowNames)-1):

					try:
						symbData[rowNames[i]] = allCols[i]
					except:
						print(">>",allCols,rowNames,i)
						os.exit()

				if(symbData["SERIES"] != "EQ"):
					continue

				try:
					symbData["pDeliv"] = delivForThisDate[symbName]
				except:
					debug("NO DELIV INFO FOUND FOR STOCK "+symbName+" FOR DATE "+x[1])
					symbData["pDeliv"] = 40

				#print(symbName,symbData)
				self.addToGlobalStructure(symbName,x[1],symbData)

	def addToGlobalStructure(self,symbolName,timestamp,dataToAdd):

		timestampStructure = dict()

		if(symbolName in blacklist):
			return

		if(self.collectedData.get(symbolName,None)==None):
			self.collectedData[symbolName] = dict()

		self.collectedData[symbolName][timestamp] = dataToAdd

	def writeCollectedDataToJson(self,filename):

		with open(filename, 'w') as f:
			json.dump(self.collectedData, f)


class findPatternsFromCollectedData:

	symbol = None
	currPrice = None
	deliv4  = None
	deliv10 = None
	deliv3 = None
	deliv15 = None
	avv4 = None
	avv3 = None
	avv10 = None
	avv15 = None
	avgT4 = None
	avgT10 = None
	deliv50_b = None
	sqeeze_b = None
	volSpr1_b = None
	volSpr2_b = None
	volSpr10_b = None
	volSpr4_b = None
	deliv25_b = None
	avgT20_b = None

#candle stick patterns 

	dogi_b = None
	bullEng_b = None
	bearEng_b = None
	hammer_sh_b = None
	hammer_han_b = None
	morningStarDoji_b = None
	dragonflyDoji_b = None
	gravestoneDoji_b = None
	bullish_harami = None
	bullish_hanging_man = None
	hanging_man = None
	bearish_harami = None
	gravestone_doji = None
	dark_cloud_cover = None
	doji_star = None
	dragonfly_doji = None
	bearish_engulfing = None
	bullish_engulfing = None
	hammer = None
	inverted_hammer = None
	morning_star = None
	morning_star_doji = None
	piercing_pattern = None
	rain_drop = None
	rain_drop_doji = None
	star = None
	shooting_star = None


#candlestick 3 days pattern (if the same pattern is present in last 3 days) still TODO.

	dogi_b3 = None
	bullEng_b3 = None
	bearEng_b3 = None
	hammer_sh_b3 = None
	hammer_han_b3 = None

	symbolInfo = None
	timestamps = None


	def __init__(self,symbol,globalStructure):
		self.symbolInfo = globalStructure[symbol]
		self.symbol     = symbol
		

		self.currPrice  
		self.timestamps = []

		#build list of timestamps/keys so it can be sorted in ascending or descending order
		
		#print("CALLED INIT FOR ",self.symbol)
		#print(self.timestamps)

		for x in self.symbolInfo:
			self.timestamps.append(x)
		self.timestamps.sort(reverse=True)
		self.currPrice = float(self.symbolInfo[self.timestamps[0]]["CLOSE"])
		self.initiate()

	#precalculate all the values
	def initiate(self):
		self.calc_avv_vals()
		self.calc_avgT_vals()
		self.calc_avgDeliv_val()
		self.calc_candle_patterns()

	def OLHC_extract(self,timestamps):
		O = self.symbolInfo[timestamps]["OPEN"]
		H = self.symbolInfo[timestamps]["HIGH"]
		L = self.symbolInfo[timestamps]["LOW"]
		C = self.symbolInfo[timestamps]["CLOSE"]

		OLHC  = dict()
		OLHC["OPEN"] = float(O)
		OLHC["HIGH"] = float(H)
		OLHC["LOW"] =float(L)
		OLHC["CLOSE"] = float(C)

		return OLHC

	def form_candlestick_pattern(self,present,past,fpast):

		candlestickPatt = dict()
		candlestickPatt["present"] = present
		candlestickPatt["past"]    = past
		candlestickPatt["fpast"]   = fpast

		return candlestickPatt

	def calc_candle_patterns(self):


		try:
			present = self.OLHC_extract(self.timestamps[0])
			past    = self.OLHC_extract(self.timestamps[1])
			fpast   = self.OLHC_extract(self.timestamps[2])

			candlestickPatt = self.form_candlestick_pattern(present,past,fpast)

			
			try:
				self.dogi_b = candlestick.doji(candlestickPatt)
			except:
				self.dogi_b = False

			try:
				self.bullish_harami = candlestick.bullish_harami(candlestickPatt)
			except:
				self.bullish_harami = False

			try:
				self.bullish_hanging_man = candlestick.bullish_hanging_man(candlestickPatt)
			except:
				self.bullish_hanging_man = False

			try:
				self.hanging_man = candlestick.hanging_man(candlestickPatt)
			except:
				self.hanging_man = False

			try:
				self.bearish_harami = candlestick.bearish_harami(candlestickPatt)
			except:
				self.bearish_harami = False

			try:
				self.gravestone_doji = candlestick.gravestone_doji(candlestickPatt)
			except:
				self.gravestone_doji = False

			try:
				self.dark_cloud_cover = candlestick.dark_cloud_cover(candlestickPatt)
			except:
				self.dark_cloud_cover = False

			try:
				self.doji_star = candlestick.doji_star(candlestickPatt)
			except:
				self.doji_star = False

			try:
				self.dragonfly_doji = candlestick.dragonfly_doji(candlestickPatt)
			except:
				self.dragonfly_doji = False

			try:
				self.bearish_engulfing = candlestick.bearish_engulfing(candlestickPatt)
			except:
				self.bearish_engulfing = False

			try:
				self.bullish_engulfing = candlestick.bullish_engulfing(candlestickPatt)
			except:
				self.bullish_engulfing = False

			try:
				self.hammer = candlestick.hammer(candlestickPatt)
			except:
				self.hammer = False

			try:
				self.inverted_hammer = candlestick.inverted_hammer(candlestickPatt)
			except:
				self.inverted_hammer = False

			try:
				self.morning_star = candlestick.morning_star(candlestickPatt)
			except:
				self.morning_star = False

			try:
				self.morning_star_doji = candlestick.morning_star_doji(candlestickPatt)
			except:
				self.morning_star_doji = False

			try:
				self.piercing_pattern = candlestick.piercing_pattern(candlestickPatt)
			except:
				self.piercing_pattern = False

			try:
				self.rain_drop = candlestick.rain_drop(candlestickPatt)
			except:
				self.rain_drop = False

			try:
				self.rain_drop_doji = candlestick.rain_drop_doji(candlestickPatt)
			except:
				self.rain_drop_doji = False

			try:
				self.star = candlestick.star(candlestickPatt)
			except:
				self.star = False

			try:
				self.shooting_star = candlestick.shooting_star(candlestickPatt)
			except:
				self.shooting_star = False

		#print("DDEBUG Calculated Candlesticks")
		except:
			print("OLHC EXTRACTION FAILED")




		#SHOOTING STAR





	#startD is the first day from the end to start counting
	#endD is the last day from the end to stop counting at
	def addValForDays(self,key,startD,endD):

		summation = 0

		for s in range(startD,endD):
			try:
				summation += int(self.symbolInfo[self.timestamps[s]][key])
			except Exception as E:
				#print(E," ",self.symbol)
				return 0


		return summation

	def addValForDays_pDeliv(self,key,startD,endD):

		summation = 0
		totTradesInRange = 0
		totDelivInRange  = 0

		#print("START ",startD," END ",endD)
		#print("TIMESTAMP LIST ",self.timestamps)
		for s in range(startD,endD):

			try:

				per = float(self.symbolInfo[self.timestamps[s]][key])
				totDelivInRange   += int(self.symbolInfo[self.timestamps[s]]["TOTTRDQTY"])*per/100.0
				totTradesInRange  += int(self.symbolInfo[self.timestamps[s]]["TOTTRDQTY"])
				#print("==========================================")
				#print("SYMB ",self.symbol)
				#print("value == ",self.symbolInfo[self.timestamps[s]])
				#print("key == ",self.timestamps[s])
				#print("s === ",s)
				#print(s,"  ",per)
				#print("DELIV ",totDelivInRange)
				#print("TOT TRADES ",totTradesInRange)
				#print("==========================================")


			except Exception as E:
				#print(E," ",self.symbol)
				break
		try:
			return (totDelivInRange/totTradesInRange)*100
		except:
			return 0

	def calc_avv_vals(self):
		self.avv3 = self.addValForDays("TOTTRDQTY",0,3)/3.0
		self.avv4 = self.addValForDays("TOTTRDQTY",0,4)/4.0
		self.avv10 = self.addValForDays("TOTTRDQTY",0,10)/10.0
		self.avv15 = self.addValForDays("TOTTRDQTY",0,15)/15.0

	def calc_avgT_vals(self):
		self.avgT3 = self.addValForDays("TOTALTRADES",0,3)/3.0
		self.avgT4 = self.addValForDays("TOTALTRADES",0,4)/4.0
		self.avgT10 = self.addValForDays("TOTALTRADES",0,10)/10.0
		self.avgT15 = self.addValForDays("TOTALTRADES",0,15)/15.0

	def calc_avgDeliv_val(self):
		self.deliv4 = self.addValForDays_pDeliv("pDeliv",0,4)
		self.deliv10 = self.addValForDays_pDeliv("pDeliv",0,10)
		self.deliv3 = self.addValForDays_pDeliv("pDeliv",0,3)
		self.deliv15 = self.addValForDays_pDeliv("pDeliv",0,15)


	def printAll(self):
		print("symbol  ",self.symbol)
		print("CurrPrice ",self.currPrice)
		print("deliv4  ",self.deliv4)
		print("deliv10  ",self.deliv10)
		print("deliv15  ",self.deliv15)
		print("deliv3  ",self.deliv3)
		print("avv4  ",self.avv4)
		print("avv3  ",self.avv3)
		print("avv10  ",self.avv10)
		print("avv15  ",self.avv15)
		print("avgT3  ",self.avgT3)
		print("avgT4  ",self.avgT4)
		print("avgT10  ",self.avgT10)
		print("avgT15  ",self.avgT15)
		print("deliv50_b  ",self.deliv50_b)
		print("dogi_b  ",self.dogi_b)
		print("sqeeze_b  ",self.sqeeze_b)
		print("bullEng_b  ",self.bullEng_b)
		print("bearEng_b  ",self.bearEng_b)
		print("volSpr1_b  ",self.volSpr1_b)
		print("volSpr2_b  ",self.volSpr2_b)
		print("volSpr10_b  ",self.volSpr10_b)
		print("volSpr4_b  ",self.volSpr4_b)
		print("deliv25_b  ",self.deliv25_b)
		print("avgT20_b  ",self.avgT20_b)
		print()

	def result(self):
		resultArray = dict()
		resultArray["symbol"]  = self.symbol
		resultArray["CurrPrice"]  = self.currPrice
		resultArray["deliv4"]  = self.deliv4
		resultArray["deliv10"]  = self.deliv10
		resultArray["deliv15"]  = self.deliv15
		resultArray["deliv3"]  = self.deliv3
		resultArray["avv4"]  = self.avv4
		resultArray["avv3"]  = self.avv3
		resultArray["avv10"]  = self.avv10
		resultArray["avv15"]  = self.avv15
		resultArray["avgT3"]  = self.avgT3
		resultArray["avgT4"]  = self.avgT4
		resultArray["avgT10"]  = self.avgT10
		resultArray["avgT15"]  = self.avgT15
		resultArray["deliv50_b"]  = self.deliv50_b
		resultArray["dogi_b"]  = self.dogi_b
		resultArray["bullish_harami"] = self.bullish_harami
		resultArray["sqeeze_b"]  = self.sqeeze_b
		resultArray["bullEng_b"]  = self.bullEng_b
		resultArray["bearEng_b"]  = self.bearEng_b
		resultArray["volSpr1_b"]  = self.volSpr1_b
		resultArray["volSpr2_b"]  = self.volSpr2_b
		resultArray["volSpr10_b"]  = self.volSpr10_b
		resultArray["volSpr4_b"]  = self.volSpr4_b
		resultArray["deliv25_b"]  = self.deliv25_b
		resultArray["avgT20_b"]  = self.avgT20_b
		resultArray["hammer_sh_b"] = self.hammer_sh_b
		resultArray["hammer_han_b"] = self.hammer_han_b
		resultArray["bullish_hanging_man"] = self.bullish_hanging_man
		resultArray["hanging_man"] = self.hanging_man
		resultArray["bearish_harami"] = self.bearish_harami
		resultArray["gravestone_doji"] = self.gravestone_doji
		resultArray["dark_cloud_cover"] = self.dark_cloud_cover
		resultArray["doji_star"] = self.doji_star
		resultArray["dragonfly_doji"] = self.dragonfly_doji
		resultArray["bearish_engulfing"] = self.bearish_engulfing
		resultArray["bullish_engulfing"] = self.bullish_engulfing
		resultArray["hammer"] = self.hammer
		resultArray["inverted_hammer"] = self.inverted_hammer
		resultArray["morning_star"] = self.morning_star
		resultArray["morning_star_doji"] = self.morning_star_doji
		resultArray["piercing_pattern"] = self.piercing_pattern
		resultArray["rain_drop"] = self.rain_drop
		resultArray["rain_drop_doji"] = self.rain_drop_doji
		resultArray["star"] = self.star
		resultArray["shooting_star"] = self.shooting_star

		return resultArray

	"""

	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	CUSTOM DERIVED DATA POINTS
	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	deliv3	    Past 3 days Deliverable percentage average 
	deliv4	    past 4 days delivery percentage average
	deliv10	    past 10 days delivery percentage average
	deliv15	    past 15 days delivery percentage average
	avv4	    Average Vol Past 4 days
	avv3		Average vol Past 3 days
	avv10	    Average vol past 10 days
	avv15	    Average vol past 15 days
	avgT3		avergae number of individual trades past 10 days
	avgT4	    average number of individual trades past 4 days
	avgT10	    avergae number of individual trades past 10 days
	avgT15 		avergae number of individual trades past 10 days

	deliv50_b	delivery percentage >50 and increasing for 5 days                              T/F
	volSpr1_b	moderate volume spurt (vol of the day > 20% of the avg vol for past 10 days)   T/F
	volSpr2_b	huge volume spurt  (vol of day >35% of avg  vol past 10  days)                 T/F
	volSpr10_b  volume 1d >= average 10d with low price movement ~1percent on either side      T/F
	volSpr4_b	volume 1d >= average 4d with low price movement ~1percent on either side       T/F
	deliv25_b	delivery percentage >25% of the last 10 days average                           T/F
	avgT20_b	number of individual trades for the day > 20% of 4 days or 10 days average     T/F
	
	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	CANDLESTICK PATTERNS
	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	dogi_b 	    dogi pattern formation in last 3 days 										   T/F
	sqeeze_b	price sqeeze (L and H values for OLHC continously decreasing for last 3 days)  T/F
	bullEng_b	bullish engulfing                                                              T/F
	bearEng_b	bearish engulfing															   T/F
	hammer_sh_b   shootng star or inverted hammer											   T/F
	gravestoneDoji_b 																		   T/F
	hammer_han_b  hanging man or hammer pattern												   T/F

	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	CUSTOM INDICATORS
	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	momI	momentum indicator (oscilator between 0-1 calculated based on a custom formula)
				vol3  = 3 day vol avg
				vol15 = 15 day vol average
				noTrades3  = 3 day number of trades average
				noTrades15 = 15 day trades average
				HL3 = average of 3 days high and low average
				HL10 = average of 10 days high and low average

				volStrength = (vol3/vol15)*((noTrades3+100)/(noTrades15+100))
				priceMovement = abs((HL3-HL10)/HL10)

				momentum = volStrength*priceMovement

	buildUp  build up indicator to notice the high Delivery percentage in last 3 days average as compated to 15 days average



	"""







def customScan():
	his = fetchHistoricalData()
	print(his.getListOfFilesToParse())
	s = pastDataStructure(his.getListOfFilesToParse())
	print(s.collectedData["ZEEL"])

	symbolLis = []
	for x in s.collectedData:
		symbolLis.append(x)

	computedPatterns = dict()

	for x in symbolLis:
		#if(x == "VSTIND" or x=="INFY"):
		if(True):
			
			computedPatterns[x] = findPatternsFromCollectedData(x,s.collectedData)

	for x in symbolLis:
		patt = computedPatterns[x]

		if(patt.deliv15==0):
			continue
		if(patt.deliv3/patt.deliv15>1.90 and patt.currPrice>50 and patt.avgT3>500 and float(patt.symbolInfo[patt.timestamps[0]]["pDeliv"]) > 50):
			patt.printAll()

	print("=============")

	for x in symbolLis:
		continue
		patt = computedPatterns[x]

		if(patt.avgT15==0):
			continue
		if(patt.avgT3/patt.avgT15>1.89  and patt.currPrice>50 and patt.avgT3>500):
			patt.printAll()

	print("=============")

	for x in symbolLis:
		continue
		patt = computedPatterns[x]
	 
		if(patt.avgT15==0 or patt.deliv15==0 ):
			continue

		if(patt.avgT3/patt.avgT15>1.20  and patt.currPrice>50 and patt.deliv3/patt.deliv15>1.20 and patt.avgT3>500):
			patt.printAll()


#customScan()
#print(computedPatterns["VSTIND"].printAll())
#s.writeCollectedDataToJson("output.json")


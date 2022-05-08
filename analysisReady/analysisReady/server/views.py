from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import pastAnalysis
import html
import json
import time
import os
from nsetools import Nse
import requests


pastAnalysisObj = None
structure = None
computedPatterns = None
dateMap = None
pastParticipantData = None


#const files

varMargins = None
symbolNameDict = None
priceBand = None
nifty50Script = None
niftyBankScript = None
nifty100Script = None

#scripts traded in F&O 
FOScripts = None

#script part of analysisReadyServer DeleveriesAPI

lastUpdatedTimeStamp = None

nse = Nse()


"""
STRUCTURE OF computed DATE MAP

sample structure

DATE{
    SYMBOLNAME{
      "SERIES":"EQ",
      "OPEN":"934.9",
      "HIGH":"954.15",
      "LOW":"931",
      "CLOSE":"945.7",
      "LAST":"944.5",
      "PREVCLOSE":"940.05",
      "TOTTRDQTY":"6672082",
      "TOTTRDVAL":"6307865395.75",
      "TIMESTAMP":"11-SEP-2020",
      "TOTALTRADES":"124065",
      "pDeliv":"38.78"
    }
}

"""

debug = True

def debug(msg):
    global debug

    #if(debug):print(msg)

#this file is a part of analysisReadyServer.

def refreshData():
    global pastAnalysisObj
    global pastParticipantData
    global structure
    global computedPatterns
    global dateMap
    global varMargins

    global nifty50Script
    global niftyBankScript
    global nifty100Script
    global FOScripts

    global lastUpdatedTimeStamp
    dateMap = None

    varMargins = None

    if(varMargins == None):loadVarFile()

    

    if(symbolNameDict==None):readSymbolNameDict()
    if(priceBand==None):readSymbolPriceBand()
    if(nifty50Script==None):
        nifty50Script = loadScriptFiles("/home/pi/Feynman-Server/staticContentHelper/MW-NIFTY-50-13-Sep-2020.csv")
    if(niftyBankScript==None):
        niftyBankScript =loadScriptFiles("/home/pi/Feynman-Server/staticContentHelper/MW-NIFTY-BANK-13-Sep-2020.csv")
    if(nifty100Script==None):
        nifty100Script =loadScriptFiles("/home/pi/Feynman-Server/staticContentHelper/MW-NIFTY-100-13-Sep-2020.csv")
    if(FOScripts==None):
        FOScripts =     loadScriptFiles("/home/pi/Feynman-Server/staticContentHelper/MW-SECURITIES-IN-F&O-13-Sep-2020.csv")

    debug("nifty50Script")
    debug(nifty50Script)
    debug("niftyBankScript")
    debug(niftyBankScript)
    debug("nifty100Script")
    debug(nifty100Script)
    debug("FOScripts")
    debug(FOScripts)

    print("CREATING THE STRUCT AGAIN ")
    pastAnalysisObj = pastAnalysis.fetchHistoricalData()
    structure = pastAnalysis.pastDataStructure(pastAnalysisObj.getListOfFilesToParse())
    lastUpdatedTimeStamp = time.time()
    symbolLis = []

    #print("DEBUG >>>",structure.collectedData["ZEEL"])

    for x in structure.collectedData:
        symbolLis.append(x)

    computedPatterns = dict()

    for x in symbolLis:
        computedPatterns[x] = pastAnalysis.findPatternsFromCollectedData(x,structure.collectedData)

    #calculate date specific map to be used for deliverable patterns
    for symb in structure.collectedData:
        for key in structure.collectedData[symb]:
            TIMESTAMP = structure.collectedData[symb][key]["TIMESTAMP"]
            if(dateMap==None):
                dateMap = dict()

            symbMapForDate = dateMap.get(TIMESTAMP,dict())
            symbMapForDate[symb] = structure.collectedData[symb][key]
            dateMap[TIMESTAMP] = symbMapForDate


    #parse participant data
    participantData = pastAnalysis.fetchParticipantData()
    print(participantData)
    pastParticipantData = participantData.participantDataObject
    print(">>>",pastParticipantData)




def requiresAnUpdate():

    global lastUpdatedTimeStamp
    oldDay = 0 
    try:
        oldDay = int(lastUpdatedTimeStamp)
    except:
        oldDay = 0

    currTimestamp = int(time.time())

    difference = currTimestamp - oldDay

    if(difference>36000):
        lastUpdatedTimeStamp = time.time()
        return True
    return False    

# Create your views here.
def index(request):
    global pastAnalysisObj
    global structure
    global computedPatterns

    if(pastAnalysisObj == None or requiresAnUpdate()):
    	refreshData()

    SYMBOL_NAME = None

    try:
        SYMBOL_NAME = html.unescape(request.GET["SYMBOL"])
    except:
        print("NO SYMBOLO NAME PROVIDED")

    print("SYMBOL  ",SYMBOL_NAME)

    
    if(SYMBOL_NAME != None):
        print("JSON RESPONSE :",computedPatterns[SYMBOL_NAME].result())
        resp = computedPatterns[SYMBOL_NAME].result()
        return JsonResponse(resp)

    new = dict()
    return JsonResponse(new)


def getBarometerData(request):

    global pastAnalysisObj
    global structure
    global computedPatterns

    if(pastAnalysisObj == None or requiresAnUpdate()):
        refreshData()

    SYMBOL_NAME = None

    try:
        SYMBOL_NAME = html.unescape(request.GET["SYMBOL"])
    except:
        print("NO SYMBOLO NAME PROVIDED")

    print("SYMBOL  ",SYMBOL_NAME)

    
    if(SYMBOL_NAME != None):
        print("JSON RESPONSE :",computedPatterns[SYMBOL_NAME].result())
        resp = computedPatterns[SYMBOL_NAME].result()
        return JsonResponse(resp)

    new = dict()

    #get adv decline data.
    nseData = nse.downloadUrlNewSite("https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100")

    nseData = json.loads(nseData)

    finalDict = dict()

    finalDict["ADV/DEC"] = nseData["advance"]


    #now get the list of symbols with highest deliv
    datesAvailabe = []
    for x in dateMap:
        datesAvailabe.append(x)

    print(datesAvailabe)



    maxData = requests.get("http://localhost:8081/analysisReady/DeleveriesAPI",params={"MODE":"MAX","CONTEXT":"NIFTY100","DATE":datesAvailabe[0],"MAXELEMS":"10000"})
    maxData = json.loads(maxData.text)

    finalDict["HIGH DELIVERY"] = maxData

    #stocks near 52W high
    high52W = dict()

    #near 52W high.
    for y in nseData["data"]:
        t = dict()
        t = y
        try:
            t["PASTPATTERN"] = computedPatterns[y["symbol"]].result()
        except:
            pass



        high52W[y["symbol"]] = t

    finalDict["COMPLETE_DETAIL"] = high52W




    return JsonResponse(finalDict)





def loadVarFile():
    global varMargins
    #print("<><><><<><><><>")

    file = open("/home/pi/Feynman-Server/staticContentHelper/varMArgins.csv")
    data = file.read().split("\n")
    data = data[1:]
    #print("VAR MARGIN ",data[3])


    varMargins = dict()

    for x in data:
        allD = x.split(",")
        try:
            varMargins[allD[1]] = float(allD[7])
        except:
            try:
                varMargins[allD[1]] = 1
            except:
                pass
   # print(varMargins)

def readSymbolNameDict():
    global symbolNameDict

    symbolNameDict = dict()

    file = open("/home/pi/Feynman-Server/staticContentHelper/EQUITY_L.csv")
    data = file.read().split("\n")
    data = data[1:]
    for x in data:
        d = x.split(",")
        try:
            symbolNameDict[d[0]]=d[1]
        except:
            pass

#try to only keep shares which have a possibility to move >10 percent in a day
def readSymbolPriceBand():
    global priceBand 

    priceBand = dict()
    fl = open("/home/pi/Feynman-Server/staticContentHelper/priceBand.csv")

    #print("PRICE  BAND UPDATED")
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

        if("No Band" in allRows[3]):
            band = 20

        if("EQ" in allRows[1]):
            priceBand[allRows[0]] = band


    #print(">>>>>>>>>>>>>>>      ",priceBand["TANLA"])
    #print(">>>>>>>>>>>>>>> ",priceBand["WELSPUNIND"])


def loadScriptFiles(scriptFileName):

    symbs = dict()

    handle = open(scriptFileName)
    data   = handle.read().split("\n")
    handle.close()

    for x in data:
        row = x.split(",")
        if(len(row)>10):
            symbolName = row[0].replace("\"","")
            symbs[symbolName] = 1

    return symbs

def computeResponseDeleveries(mode,context,date,VARCutOffMin,VARCutOffMax,minPrice,maxPrice,minTurnOver,minTraded,priceBandCutoff,elements):
    finalList = []
    global dateMap
    global priceBand
    global varMargins


    #print(dateMap)

    array = []
    addedSymbs = 0
    rejectedSymbs = 0

    for symbols in dateMap[date]:

        allSymbInfo = dateMap[date][symbols]

        volatility = 1
        try:
            volatility = varMargins[symbols]
        except:
            print("VOLATILITY NOT FOUND ",symbols)

        #print(volatility)
        volatilityCheck = volatility>=VARCutOffMin and volatility <=VARCutOffMax

        priceBandCheck = True
        band = 10

        try:
            band = priceBand[symbols]
        except:
            print("BAND info not found for "+symbols)

        #only include stocks which can move more than 5 percent in a day
        if(band >= priceBandCutoff):
            priceBandCheck = True
            debug("PRICE BAND CHECK SET TO TRUE for "+symbols)
        else:
            debug("PRICE BAND CHECK SET TO FALSE for "+symbols)
            priceBandCheck = False

        if(volatilityCheck==False):
            debug("VOLATILITY CHECK SET TO FALSE FOR "+symbols)

        noOfTradesCheck = float(allSymbInfo["TOTTRDQTY"])>=minTraded

        if(noOfTradesCheck==False):
            debug("NO OF TRADES CHECK SET TO FALSE FOR "+symbols)

        turnOverMedian = 60000000
        #TODO MEDIAN IMPLEMENTATION 

        turnOverMedian = minTurnOver

        debug("TURNOVER CUTOFF "+str(turnOverMedian))

        

        turnoverCheck = float(allSymbInfo["TOTTRDVAL"])>int(turnOverMedian)

        if(turnoverCheck==False):
            debug("Turnover CHECK SET TO FALSE FOR "+symbols)

        deleverableCheck = True

        #if there are more than 95 percent develeries share is mos likely an ETF.
        try:
            if(float(allSymbInfo["pDeliv"])>=95):
                deleverableCheck = False
        except:
            pass
        

        #figure out the context
        if("FULL" in context):

            if("-" not in allSymbInfo["pDeliv"] and float(allSymbInfo["LAST"].strip())>30 and deleverableCheck and turnoverCheck and noOfTradesCheck and "EQ" in allSymbInfo["SERIES"] and volatilityCheck and priceBandCheck):
                array.append([float(allSymbInfo["pDeliv"].strip()),symbols,allSymbInfo["CLOSE"]])
                #print("ADDING "+symbols)
                addedSymbs += 1
            else:
                #print("REJECTED : SYMBOL "+symbols,"   ", deleverableCheck , turnoverCheck , noOfTradesCheck , allSymbInfo["SERIES"] , volatilityCheck , priceBandCheck)
                rejectedSymbs += 1
        else:
            deleverableCheck    = True
            turnoverCheck   = True
            noOfTradesCheck = True
            volatilityCheck = True
            priceBandCheck  = True


        if("NIFTY50" in context):
            if(nifty50Script.get(symbols,None)!=None):
                if("-" not in allSymbInfo["pDeliv"] and "EQ" in allSymbInfo["SERIES"]):
                    array.append([float(allSymbInfo["pDeliv"].strip()),symbols,allSymbInfo["CLOSE"]])
                    #debug("ADDING "+symbols)
                    addedSymbs += 1
                else:
                    #debug("REJECTED : SYMBOL "+symbols)
                    rejectedSymbs += 1

        if("BANKNIFTY" in context):
            if(niftyBankScript.get(symbols,None)!=None):
                if("-" not in allSymbInfo["pDeliv"] and "EQ" in allSymbInfo["SERIES"]):
                    array.append([float(allSymbInfo["pDeliv"].strip()),symbols,allSymbInfo["CLOSE"]])
                    #debug("ADDING "+symbols)
                    addedSymbs += 1
                else:
                    #debug("REJECTED : SYMBOL "+symbols)
                    rejectedSymbs += 1

        if("NIFTY100" in context):
            if(nifty100Script.get(symbols,None)!=None):
                if("-" not in allSymbInfo["pDeliv"] and "EQ" in allSymbInfo["SERIES"]):
                    array.append([float(allSymbInfo["pDeliv"].strip()),symbols,allSymbInfo["CLOSE"]])
                    #debug("ADDING "+symbols)
                    addedSymbs += 1
                else:
                    #debug("REJECTED : SYMBOL "+symbols)
                    rejectedSymbs += 1

        if("F&O" in context):
            if(FOScripts.get(symbols,None)!=None):
                if("-" not in allSymbInfo["pDeliv"] and "EQ" in allSymbInfo["SERIES"]):
                    array.append([float(allSymbInfo["pDeliv"].strip()),symbols,allSymbInfo["CLOSE"]])
                    #debug("ADDING "+symbols)
                    addedSymbs += 1
                else:
                    #debug("REJECTED : SYMBOL "+symbols)
                    rejectedSymbs += 1

    debug("ADDED "+str(addedSymbs))
    debug("REJECTED "+str(rejectedSymbs))

    if("MAX" in mode):
        array.sort(reverse=True)
    else:
        array.sort()

    response = dict()

    response["response"] = array[:elements]

    return response

def getMedianTradedAndTurnoverVal(date):

    global dateMap

    allTradedQuantity = []

    for symbols in dateMap[date]:
        allSymbInfo = dateMap[date][symbols]

        curr_trdVal  =0
        curr_trdQuan =0

        try:
            curr_trdVal = float(allSymbInfo["TOTTRDVAL"])
        except:
            pass

        try:
            curr_trdQuan = float(allSymbInfo["TOTTRDQTY"])
        except:
            pass
        
        if(curr_trdVal>5000000 and curr_trdQuan > 500):
            allTradedQuantity.append([curr_trdVal,curr_trdQuan])


    
    allTradedQuantity.sort(key = lambda x: x[0])

    median_trdVal = allTradedQuantity[int(len(allTradedQuantity)/2)][0]

    allTradedQuantity.sort(key = lambda x: x[1])

    median_trdQuan = allTradedQuantity[int(len(allTradedQuantity)/2)-35][1]



    #print(allTradedQuantity)

    return median_trdVal,median_trdQuan






#this defines the analysis ready server Deleverires API
#returns the list of stocks with a particular parameters assiciated with Delivery percentage.
#accepts REQUIRED params

#   MODE    = MAX/MIN
#   CONTEXT = FULL/NIFTY50/BANKNIFTY/NIFTY100/FO
#   DATE    = DATE OF WHICH THE DATA IS REQ FOR
#   ======  Non mandatory parameters/filters  =======
#
#
#   VARCutOffMin = min var acceptable
#   VARCutOffMax = max var acceptable
#   minPrice     = min price of stock
#   maxPrice     = max price of stock
#   minTurnOver  = min turover
#   minTraded    = min traded val
#   priceBandCutoff    = min price band

def DeleveriesAPI(request):
    global pastAnalysisObj
    global structure
    global computedPatterns

    if(pastAnalysisObj == None or requiresAnUpdate()):
        refreshData()


    elements = 15

    mode    = request.GET["MODE"]
    context = html.unescape(request.GET["CONTEXT"])
    date    = request.GET["DATE"]
    try:
        elements = int(request.GET["MAXELEMS"])
    except:
        elements = 15

    #default values
    VARCutOffMin    = 0.6
    VARCutOffMax    = 1.2
    minPrice    = 30
    maxPrice    = 10000

    if(debug and False):
        with open('data.json', 'w') as f:
            json.dump(dateMap, f)

    #currently 600 lacks it has to be extended to median value of the turnover later on for that day
    minTurnOver = 80000000
    minTraded   = 7000

    median_trdVal,median_trdQuan = getMedianTradedAndTurnoverVal(date)

    minTurnOver = median_trdVal
    minTraded   = median_trdQuan

    print("min Trades ",minTraded)
    print("min Turnover",minTurnOver)


    priceBandCutoff = 10

    debug(mode+" "+str(context)+" "+str(date)+" "+str(VARCutOffMax)+" "+str(VARCutOffMin)+" "+str(minPrice)+" "+str(maxPrice)+" "+str(minTurnOver)+" "+str(minTraded)+" "+str(priceBandCutoff))

    resp = computeResponseDeleveries(mode,context,date,VARCutOffMin,VARCutOffMax,minPrice,maxPrice,minTurnOver,minTraded,priceBandCutoff,elements)
    print(resp)

    return JsonResponse(resp)


#convert a input of type 12-SEP-2020 to timestamp >>  20200912  
def  dateToStamp(currDate):
    elements = currDate.split("-")
    day = str(elements[0])
    month = str(elements[1])
    year  = str(elements[2])
    monthLis = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    counter = 1
    for x in monthLis:
        if(month.lower()==x.lower()):
            if(counter<10):
                month = "0"+str(counter)
            else:
                month = str(counter)
        counter += 1

    return int(year+month+day)

def availDates(request):
    global pastAnalysisObj
    global structure
    global computedPatterns
    global dateMap

    if(pastAnalysisObj == None or requiresAnUpdate()):
        refreshData()

    resp = dict()

    datesAvailabe  = []

    #adding a inherent sorter.

    for x in dateMap:
        datesAvailabe.append([x,dateToStamp(x)])

    datesAvailabe.sort(reverse=True,key = lambda x: x[1])

    retDatesAvailable = []

    for x in datesAvailabe:
        retDatesAvailable.append(x[0])

    resp["AvailableDates"] = retDatesAvailable

    return JsonResponse(resp)


def refreshConstantFiles(request):
    #refresh constant dependency like var margins.
    token = None

    try:
        token = request.GET["TOKEN"]
    except:
        token = ""

    if(token != "refr123"):
        return HttpResponse("Invalid TOKEN Provided")



    datesAvailabe  = []

    #adding a inherent sorter.

    for x in dateMap:
        datesAvailabe.append([x,dateToStamp(x)])

    datesAvailabe.sort(reverse=True,key = lambda x: x[1])

    retDatesAvailable = []

    for x in datesAvailabe:
        retDatesAvailable.append(x[0])


    #currently replacing following files.

    #1 var margin file  "/home/pi/Feynman-Server/staticContentHelper/varMArgins.csv"
    #2 price band updated Info

    #extract the date. 

    monthLis = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    dates    = retDatesAvailable[2].split("-")

    count = 1

    mon = ""

    for x in monthLis:


        if(dates[1].lower()==x.lower()):
            if(count<10):
                mon = "0"+str(count)
            else:
                mon = str(count)

        count += 1

    fullStamp = str(dates[0]+mon+dates[2])
    #print(fullStamp)

    try:
        os.system("curl -o /tmp/output.varmargin https://archives.nseindia.com/archives/nsccl/volt/CMVOLT_"+fullStamp+".CSV")
        os.system("mv /tmp/output.varmargin /home/pi/Feynman-Server/staticContentHelper/varMArgins.csv")
        os.system("rm /tmp/output.varmargin")
        loadVarFile()


        os.system("curl -o /tmp/output.bandInfo https://archives.nseindia.com/content/equities/sec_list_"+fullStamp+".csv")
        os.system("mv /tmp/output.bandInfo /home/pi/Feynman-Server/staticContentHelper/priceBand.csv")
        os.system("rm /tmp/output.bandInfo")
        readSymbolPriceBand()

    except Exception as e:
        print("EXCEPTION AT 523")
        print(e)
        return HttpResponse("Unable To Update"+str(e))

    return HttpResponse("Files Successfully Updated")


def participantDataAPI(request):
    global pastParticipantData
    global pastAnalysisObj

    if(pastAnalysisObj == None or requiresAnUpdate() or pastAnalysisObj == None):
        refreshData()

    resp = dict()

    resp = pastParticipantData
    print(resp)

    return JsonResponse(resp)
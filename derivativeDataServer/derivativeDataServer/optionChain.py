
import html
import json
import time
import os.path
from nsetools import Nse
from time import localtime, strftime 
from datetime import datetime, timedelta
import pprint
from dateutil.tz import *


#default symbol option chain location.

optionChainDBLocation = "/home/pi/Feynman-Server/DATA/"
nse = Nse()

#for the global raw data 
daysToKeepGlobalDataFor = 2

#for the analysed data
timstampToKeepAnalyzedDataFor = 250

debug = False

######################################
"""
/home/optionChainDatabase/<symbol name 1>, <symbol name 2>

json object that has the same structure to that of CompleteOptionChainStructure

"""
######################################

#Option Chain Structure
#This is valid only for a single symbol.

#### structure looks like ####

"""
SYMBOL
    - underlyingValue
    - strikePricesList
    - expiryList
    - symbolName
    - timestamp

    <NOTE ITS not nesessary that all the expiry dates in Futures data will match the above option chain futures list for expiry>

    <Futures Extracted Data>
    - marketLot
    - marketWidePositionLimits
    - dailyvolatility
    - futureData
        - expiry 1
            - lastPrice
            - pChange
            - totalTurnover
            - totalBuyQuantity
            - totalSellQuantity
            - openInterest
            - pchangeinOpenInterest
            - highPrice
            - lowPrice
            - traded

        - expiry 2
            - ...
    
    <Options Related Data>
    - strikes
        - <strike price 1>
        - <strike price 2>
                -expiry1
                    - PE
                            - strikeprice 
                            - expiry
                            - symbol
                            - OI
                            - COI
                            - pCOI
                            - totalTradedVolume
                            - impliedVolatility
                            - lastPrice
                            - change
                            - pChange
                            - totalBuyQuantity
                            - totalSellQuantity
                            - underlyingValue
                            - touched (If the value in this is default or fetched) default value "False"
                    - CE
                - expiry2 ...

This is a per symbol structure only.

This will become a part of the complete chain detail

capability include 

- readFromNSE
    > Read the option chain details from NSE website structure for a comaplete instance result.
- readFromFile
    > Read from the orignal structure it is saved in the file.
- fetchDict
    > get the python dict object for this structure

"""

class symbolOptionStructure:

    symbolStructure = None

    def getDefaultDataInOptionTypes(self):

        optType = dict()
        optType["strikeprice"]    = "0.0"
        optType["expiry"]   = "0.0"
        optType["symbol"]   = "0.0"
        optType["OI"]   = "0.0"
        optType["COI"]   = "0.0"
        optType["pCOI"]   = "0.0"
        optType["totalTradedVolume"]   = "0.0"
        optType["impliedVolatility"]   = "0.0"
        optType["lastPrice"]   = "0.0"
        optType["change"]   = "0.0"
        optType["pChange"]   = "0.0"
        optType["totalBuyQuantity"]   = "0.0"
        optType["totalSellQuantity"]   = "0.0"
        optType["underlyingValue"]   = "0.0"
        optType["touched"]   = "False"
        return optType


    def readFromNSE(self,data,origfuturesData,symbol):
        global debug

        nseStructure = json.loads(data)
        origfuturesData  = json.loads(origfuturesData)

        if(self.symbolStructure == None):
            self.symbolStructure = dict()

        symbData = dict()
        #print(data)

        symbData["underlyingValue"] = nseStructure["records"]["underlyingValue"]
        symbData["strikePricesList"] = nseStructure["records"]["strikePrices"]
        symbData["expiryList"] = nseStructure["records"]["expiryDates"]
        symbData["symbolName"] = symbol
        stamp = datetime.today()
        symbData["timestamp"] = nseStructure["records"]["timestamp"]

        #now load the CE and PE details.

        
        detailsPE = []
        strikePrices = dict()

        for strike in symbData["strikePricesList"]:
            
            expiry = dict()

            for expiryDate in symbData["expiryList"]:

                optTypes = dict()
                optTypes["CE"] = self.getDefaultDataInOptionTypes()
                optTypes["PE"] = self.getDefaultDataInOptionTypes()
                expiry[expiryDate]  = optTypes

            strikePrices[strike] = expiry

        for allData in nseStructure["records"]["data"]:

            currStrikePrice = allData["strikePrice"]
            #currStrikePrice  = str(currStrikePrice)

            currExpiry = allData["expiryDate"]
            lis = ["PE","CE"]

            for currOptType in lis:
                try:
                    currOptData = allData[currOptType]

                    strikePrices[currStrikePrice][currExpiry][currOptType]["strikeprice"]    = currOptData["strikePrice"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["expiry"]   = currOptData["expiryDate"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["symbol"]   = symbol
                    strikePrices[currStrikePrice][currExpiry][currOptType]["OI"]   = currOptData["openInterest"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["COI"]   = currOptData["changeinOpenInterest"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["pCOI"]   = currOptData["pchangeinOpenInterest"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["totalTradedVolume"]   = currOptData["totalTradedVolume"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["impliedVolatility"]   = currOptData["impliedVolatility"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["lastPrice"]   = currOptData["lastPrice"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["change"]   = currOptData["change"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["pChange"]   = currOptData["pChange"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["totalBuyQuantity"]   = currOptData["totalBuyQuantity"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["totalSellQuantity"]   = currOptData["totalSellQuantity"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["underlyingValue"]   = currOptData["underlyingValue"]
                    strikePrices[currStrikePrice][currExpiry][currOptType]["touched"]   = "True"
                except Exception as e :
                    if(debug):print("NOT FOUND ",e," ",currStrikePrice,"   ",currExpiry,"  SYMBOL = ",symbol)

        #clear up the empty values, ie the strike  prices which dont have anything in CE or PE should be cleared.

        for currStrikePrice in strikePrices:

            #currStrikePrice  = str(currStrikePrice)

            for currExp in strikePrices[currStrikePrice]:

                currExpiry = allData["expiryDate"]
                lis = ["PE","CE"]

                for currOptType in lis:

                    try:
                        if("True" not in strikePrices[currStrikePrice][currExp][currOptType]["touched"]):
                            #print("DELETING")
                            #print(strikePrices[currStrikePrice][currExpiry])
                            strikePrices[currStrikePrice][currExp][currOptType] = dict()
                            #print(strikePrices[currStrikePrice][currExpiry])

                    except:
                        #strikePrices[currStrikePrice][currExp][currOptType] = dict()
                        print("Unable to delete ",currOptType,currStrikePrice,currExpiry)


        symbData["strikes"] = strikePrices
        #print(">>>",symbData["strikes"][4600])

        


        #now read the futures data and put it to same Datastructure.
        #print(self.symbolStructure)

        #this contanins the full futures data iw under the ...["futures"] tag.
        futuresExpiryData = dict()

        allDataPoints = origfuturesData["stocks"]

        #data point extracts the part of stocks-> "metadata",underlyingValue,marketDepthorder,tradeInfo in the actual nse data.

        globalDataLoaded = False

        totalOverallContracts = 0

        for dataPoint in allDataPoints:

            totalOverallContracts += int(dataPoint["marketDeptOrderBook"]["tradeInfo"]["openInterest"])

            #continue only for futures data.
            if("Futures" not in dataPoint["metadata"]["instrumentType"]):
                continue

            futuresData = dict()

            #load global data
            if(not globalDataLoaded):
                globalDataLoaded = True
                futuresExpiryData["marketLot"]               = dataPoint["marketDeptOrderBook"]["tradeInfo"]["marketLot"]
                futuresExpiryData["marketWidePositionLimits"]= dataPoint["marketDeptOrderBook"]["otherInfo"]["marketWidePositionLimits"]
                futuresExpiryData["dailyvolatility"]         = dataPoint["marketDeptOrderBook"]["otherInfo"]["dailyvolatility"]

            #now find out the expiry date.
            expiryDate = dataPoint["metadata"]["expiryDate"]

            futuresData["lastPrice"] = dataPoint["metadata"]["lastPrice"]
            futuresData["openPrice"] = dataPoint["metadata"]["openPrice"]
            futuresData["highPrice"] = dataPoint["metadata"]["highPrice"]
            futuresData["lowPrice"] = dataPoint["metadata"]["lowPrice"]
            futuresData["pChange"] = dataPoint["metadata"]["pChange"]
            futuresData["totalTurnover"] = dataPoint["metadata"]["totalTurnover"]
            futuresData["traded"] = dataPoint["metadata"]["numberOfContractsTraded"]

            futuresData["openInterest"] = dataPoint["marketDeptOrderBook"]["tradeInfo"]["openInterest"]
            futuresData["pchangeinOpenInterest"] = dataPoint["marketDeptOrderBook"]["tradeInfo"]["pchangeinOpenInterest"]
            futuresData["changeinOpenInterest"] = dataPoint["marketDeptOrderBook"]["tradeInfo"]["changeinOpenInterest"]



            futuresExpiryData[expiryDate] = futuresData

        futuresExpiryData["totalOverallContracts"] = totalOverallContracts

        symbData["futuresData"] = futuresExpiryData

        #print(symbData)

        #finally add everything to the relevant DataStructure.
        self.symbolStructure[symbol] = symbData


"""
CompleteOptionChainStructure

<Date : YYYYMMDD>
    - timestamp1
        - symbolOptionStructure
    - timestamp2
        - symbolOptionStructure

"""

class completeOptionChainStructure:

    completeStructure = None
    timestampStructure = None
    symbolName = None

    global nse
    global optionChainDBLocation


    def __init__(self,symbol):
        self.symbolName = symbol

    def saveToFile(self):

        global daysToKeepGlobalDataFor

        fileName = optionChainDBLocation+"/"+self.symbolName
        filePresent = os.path.isfile(fileName)
        if(filePresent == False):
            file = open(fileName,"w")
            file.write("{}")
            file.close()

        file = open(fileName)
        dataInFile = file.read()
        file.close()

        fileJSONStructure = json.loads(dataInFile)

        timestamp = self.timestampStructure[self.symbolName]["timestamp"]

        #print(timestamp)
        
        date = timestamp.split(" ")[0]

        timestampStr = dict()
        try:
            timestampStr = fileJSONStructure[date]
        except:
            pass


        timestampStr[timestamp] = self.timestampStructure[self.symbolName]

        fileJSONStructure[date] = timestampStr


        #try to limit the global timestamp count to x days.

        allStampList = []

        for x in fileJSONStructure:
            allStampList.append([optionChainAnalysis.generateabsoluteTimestamp(None,x),x])

        #print(allStampList)

        if(len(allStampList)>daysToKeepGlobalDataFor):
            #only delete if the size is greater than the limit.

            allStampList.sort(reverse=True)

            allStampList = allStampList[daysToKeepGlobalDataFor:]

            #print(allStampList)

            for x in allStampList:
                #print("DELETING ")
                del(fileJSONStructure[x[1]])

        with open(fileName, 'w') as f:
            json.dump(fileJSONStructure, f)

    def downloadNewSource(self):
        url = ""

        futuresDataUrl  =  ""

        if("NIFTY" in self.symbolName):
            url = "https://www.nseindia.com/api/option-chain-indices?symbol="+self.symbolName
        else:
            url = "https://www.nseindia.com/api/option-chain-equities?symbol="+self.symbolName

        futuresDataUrl = "https://www.nseindia.com/api/quote-derivative?symbol="+self.symbolName

        print(url)

        data = nse.downloadUrlNewSite(url)
        #print(futuresDataUrl)
        futuresData = nse.downloadUrlNewSite(futuresDataUrl)

        #print(futuresData)

        symbStr = symbolOptionStructure()
        symbStr.readFromNSE(data,futuresData,self.symbolName)
        self.timestampStructure = symbStr.symbolStructure
        
        #debug
        #for x in self.timestampStructure:
        #   print("dfvdvd === ",x)

        self.saveToFile()

    def loadFromFileAndGetDict(self):
        fileName = optionChainDBLocation+"/"+self.symbolName
        filePresent = os.path.isfile(fileName)
        if(filePresent == False):
            file = open(fileName,"w")
            file.write("{}")
            file.close()
            self.downloadNewSource()

        file = open(fileName)
        dataInFile = file.read()
        file.close()

        fileJSONStructure = json.loads(dataInFile)

        return fileJSONStructure

"""
This will generate a time slices structure of the following.

each element of the list contains the following

timestamp
    - PCR-OI
    - PCR-VO
    - PCR-COI
    - MAX-PAIN      (for all expiry combined)
    - MAX-PAIN-CURR (for current series)
    - MAX-PAIN2         (for all expiry combined)
    - MAX-PAIN-CURR2 (for current series)
    - MAX-PAIN COI (For all series)
    - IV change (for +/- 5 strikes)
        - strike 1
        - strike 2
        - ...
    - S1,S2,S3
    - R1,R2,R3
    - strength value for S1,S2,S3,R1,R2,R3 calculated by total OI value of all these values if S1 has highest OI then strength becomes 3 and so on.
    - maxTradedStrike  (calculated by maximum traded volume in all the strike values)
    - 
"""

class analysisPatterns:
    symbolName = None
    date  = None

    PCR_OI   = None
    PCR_VO   = None
    PCR_COI   = None
    ITM_PCR_COI = None
    MAX_PAIN   = None
    MAX_PAIN_CURR    = None
    MAX_PAIN2      = None   
    MAX_PAIN_CURR2    = None
    MAX_PAIN_COI   = None

    IV = dict()

    supports = dict()
    supports["S1"] = None
    supports["S2"] = None
    supports["S3"] = None

    resistance = dict()
    resistance["R1"] = None
    resistance["R2"] = None
    resistance["R3"] = None

    strengthValues = dict()
    strengthValues["S1"] = None
    strengthValues["S2"] = None
    strengthValues["S3"] = None
    strengthValues["R1"] = None
    strengthValues["R2"] = None
    strengthValues["R3"] = None

    maxTradedStrike_CALL  = None
    maxTradedStrike_PUT   = None

    newlyAddedCOISupport = None
    newlyAddedCOIResistance= None

    #below only gets reported for current series and next 3 series for Nifty and Bank Nifty.

    pChangeInOI = None
    OLHC        = dict()
    
    OLHC["OPEN"] = None
    OLHC["HIGH"] = None
    OLHC["LOW"]  = None

    lotSize         = None

    #this is to keep a record of how much percent of OI limit has been reached of total market wide limit.

    totalMarketWideOIPercent = None
    pChange = None
    traded  = None


    def getAnalysisDict(self):

        completeAnalysis = dict()
        completeAnalysis["symbolName"] = self.symbolName
        completeAnalysis["date"] = self.date

        completeAnalysis["PCR_OI"]   = self.PCR_OI
        completeAnalysis["PCR_VO"]   = self.PCR_VO
        completeAnalysis["PCR_COI"]   = self.PCR_COI
        completeAnalysis["ITM_PCR_COI"]  = self.ITM_PCR_COI
        completeAnalysis["MAX_PAIN"]   = self.MAX_PAIN
        completeAnalysis["MAX_PAIN_CURR"]    = self.MAX_PAIN_CURR
        completeAnalysis["MAX_PAIN2"]      = self.MAX_PAIN2 
        completeAnalysis["MAX_PAIN_CURR2"]    = self.MAX_PAIN_CURR2
        completeAnalysis["MAX_PAIN_COI"]   = self.MAX_PAIN_COI

        completeAnalysis["IV"] = self.IV

        completeAnalysis["supports"] = self.supports
        completeAnalysis["resistance"] = self.resistance
        completeAnalysis["strengthValues"] = self.strengthValues
        completeAnalysis["maxTradedStrike_CALL"] = self.maxTradedStrike_CALL
        completeAnalysis["maxTradedStrike_PUT"] = self.maxTradedStrike_PUT

        completeAnalysis["newlyAddedCOISupport"] = self.newlyAddedCOISupport
        completeAnalysis["newlyAddedCOIResistance"] = self.newlyAddedCOIResistance

        #futures Data
        completeAnalysis["pChangeInOI"] = self.pChangeInOI
        completeAnalysis["OLHC"] = self.OLHC
        completeAnalysis["lotSize"] = self.lotSize
        completeAnalysis["totalMarketWideOIPercent"] = self.totalMarketWideOIPercent
        completeAnalysis["pChange"] = self.pChange
        completeAnalysis["traded"] = self.traded

        return completeAnalysis



class optionChainAnalysis:

    symbolName = None
    entireStructure = None

    analysis = None
    timestamps = None
    #timestamps looks like [<timestamp with time>,<unix stamp>,<timestamp without time>]


    def __init__(self,symbol):
        self.symbolName = symbol

    def generateabsoluteTimestamp(self,stamp):
        #print(stamp)
        st = stamp.split(" ")
        date = st[0]
        time = "00:00:00"
        

        try:
            time = st[1].split(":")
        except:
            time = time.split(":")

        

        date = date.split("-")
        monthLis = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

        mm = date[1]
        for x in range(0,12):
            if(mm in monthLis[x]):
                mm = x+1
                break

        mm = int(mm)
        dd = int(date[0])
        yyyy = int(date[2])

        mi = int(time[1])
        ho = int(time[0])
        ss = int(time[2])

        #print(mm,dd,yyyy,"   ",ho,mi,ss)

        stamp = datetime(yyyy,mm,dd, ho, mi, ss,tzinfo=tzlocal())

        unixStamp = stamp.timestamp()
        return unixStamp


    #get the list of timestamps and prepare the default analysis structure for that
    def extractPointers(self):

        timestamps = []

        for x in self.entireStructure:

            
            for y in self.entireStructure[x]:
                unixStamp = self.generateabsoluteTimestamp(y)
                timestamps.append([y,unixStamp,x])

        timestamps.sort(key=lambda x:x[1],reverse=True)
        self.timestamps = timestamps

        #limit the list from here.

        self.analysis = dict()

        for x in timestamps:
            patterns = analysisPatterns()
            patterns.symbolName = self.symbolName
            patterns.date = x[0]

            self.analysis[x[1]]= patterns.getAnalysisDict()


            ###### REMOVE THIS WHEN INCLUDING MULTIPLE TIMELINE SUPPORT 
            break

    def findClosestStrike(self,currSymbolData):

        val = float(currSymbolData["underlyingValue"])

        closestStrike = 0
        difference = 999999

        for x in currSymbolData["strikes"]:
            if(abs(val-float(x))<difference):
                difference = abs(val-float(x))
                closestStrike = x

        return closestStrike

    def saveAnalysis(self):

        #create a analysis file in the optionDB analysis folder.
        global optionChainDBLocation

        analysisFilePath = optionChainDBLocation+"/Analysis/"+self.symbolName

        #first attempt to read the orignal/previous analysis file
        exists = os.path.isfile(analysisFilePath)

        content = "{}"


        if(not exists):
            #file does not exists

            #check if the folder exists or not
            if not os.path.exists(os.path.dirname(analysisFilePath)):
                try:
                    os.makedirs(os.path.dirname(analysisFilePath))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

        else:
            file = open(analysisFilePath)
            content = file.read()
            file.close()


        analysisContent = json.loads(content)
        
        #add new content
        for x in self.analysis:
            analysisContent[x] = self.analysis[x]


        #write analysis file

        with open(analysisFilePath, 'w') as f:
            json.dump(analysisContent, f)


        #TODO write first to a temp file then do cp to avoid race conditions. 
        #also we have to limit the count of datapoints as per the 
        # timstampToKeepAnalyzedDataFor




    def generateAnalysis(self):
        self.extractPointers()

        global debug

        #calculate PCR_OI,   PCR_VOL,   PCR_COI

        #print(">>>",self.timestamps)
        currSymbolData = self.entireStructure[self.timestamps[0][2]][self.timestamps[0][0]]

        currentPrice = float(currSymbolData["underlyingValue"])
        self.analysis[self.timestamps[0][1]]["currentPrice"]= currentPrice

        closestStrike = float(self.findClosestStrike(currSymbolData))


        PutOIs = dict()
        CallOIs = dict()

        PutCOIs = dict()
        CallCOIs = dict()

        PutVOs = dict()
        CallVOs = dict()

        PutOIs_Current  = dict()
        CallOIs_Current = dict()

        for x in currSymbolData["strikePricesList"]:
            PutOIs[str(x)] = 0
            CallOIs[str(x)] = 0
            PutCOIs[str(x)] = 0
            CallCOIs[str(x)] = 0
            PutVOs[str(x)] = 0
            CallVOs[str(x)] = 0

            PutOIs_Current[str(x)] = 0
            CallOIs_Current[str(x)] = 0

        currValueSet_put  = False
        currValueSet_call = False


        #global loop try to finish everything here itself
        for strike in currSymbolData["strikes"]:
            for expiry in currSymbolData["expiryList"]:

                types = ["CE","PE"]

                for typ in types:

                    data = currSymbolData["strikes"][strike][expiry][typ]

                    if(typ == "PE"):

                        try:
                            PutOIs[strike] =PutOIs[strike] +  float(data["OI"])
                            PutCOIs[strike] =PutCOIs[strike] +  float(data["COI"])
                            PutVOs[strike] =PutVOs[strike] + float(data["totalTradedVolume"])
                        except:
                            #must have encountered a null/None value
                            PutOIs[strike]  += 0
                            PutCOIs[strike] += 0
                            PutVOs[strike]  += 0


                    if(typ == "CE"):
                        try:
                            CallOIs[strike] =CallOIs[strike] +  float(data["OI"])
                            CallCOIs[strike] =CallCOIs[strike] +  float(data["COI"])
                            CallVOs[strike] =CallVOs[strike] +  float(data["totalTradedVolume"])
                        except:
                            #must have encountered a null/None value
                            PutOIs[strike] += 0
                            PutCOIs[strike] += 0
                            PutVOs[strike] += 0

        latest_expiry = None

        for x in currSymbolData["expiryList"]:
            latest_expiry = x
            break

        for strike in currSymbolData["strikes"]:
            #print(strike)
            #print(latest_expiry)

            

            types = ["CE","PE"]
            for typ in types:
                data = currSymbolData["strikes"][strike][latest_expiry][typ]
                if(typ == "PE"):
                    try:
                        PutOIs_Current[strike] = float(data["OI"])
                    except:
                        #print("FAILED")
                        pass
                if(typ == "CE"):
                    try:
                        CallOIs_Current[strike] = float(data["OI"])
                    except:
                        pass

        #print(CallOIs_Current)
        #print(PutOIs_Current)

        #calculate MAX pain
        strikePrices = []

        for strikes in currSymbolData["strikes"]:
            strikePrices.append([strikes,float(strikes)])




        callOptionsOIAdder = [0]
        putOptionOIAdder   = [0]

        putOptionOIAdder_Current = [0]
        callOptionsOIAdder_Current = [0]


        strikePrices.sort(key=lambda x:x[1],reverse=True)
        #print(PutOIs)

        totalPutCOI  = 0
        totalCallCOI = 0

        totalCallVol = 0
        totalPutVol  = 0

        callOI_list = []
        putOI_list  = []
        callCOI_list= []
        putCOI_list = []
        callVolList = []
        putVolList  = []

        #these are summation of in the money calls and puts they are more risky to write.
        ITM_callCOI_tot= 0
        ITM_putCOI_tot = 0



        for x in strikePrices:
            callOptionsOIAdder.append(CallOIs[x[0]] +callOptionsOIAdder[len(callOptionsOIAdder)-1])
            putOptionOIAdder.append(PutOIs[x[0]] +putOptionOIAdder[len(putOptionOIAdder)-1])

            callOptionsOIAdder_Current.append(CallOIs_Current[x[0]] +callOptionsOIAdder_Current[len(callOptionsOIAdder_Current)-1])
            #print(x,"       ",CallOIs_Current[x[0]])
            putOptionOIAdder_Current.append(PutOIs_Current[x[0]] +putOptionOIAdder_Current[len(putOptionOIAdder_Current)-1])

            totalPutCOI  += PutCOIs[x[0]]
            totalCallCOI += CallCOIs[x[0]]

            totalCallVol += CallVOs[x[0]]
            totalPutVol  += PutVOs[x[0]]
            
            callOI_list.append([float(x[0]),float(CallOIs[x[0]])-float(PutOIs[x[0]])])
            putOI_list.append([float(x[0]),float(PutOIs[x[0]])-float(CallOIs[x[0]])])
            callCOI_list.append([float(x[0]),CallCOIs[x[0]]])
            putCOI_list.append([float(x[0]),PutCOIs[x[0]]])
            callVolList.append([float(x[0]),CallVOs[x[0]]])
            putVolList.append([float(x[0]),PutVOs[x[0]]])

            if(float(x[0])<closestStrike):
                ITM_callCOI_tot += float(CallCOIs[x[0]])
            if(float(x[0])>closestStrike):
                ITM_putCOI_tot += float(PutCOIs[x[0]])


        #calculate Resistance.

        callOI_list.sort(key=lambda x:x[1],reverse=True)

        self.analysis[self.timestamps[0][1]]["resistance"]["R1"] = callOI_list[0][0]
        self.analysis[self.timestamps[0][1]]["resistance"]["R2"] = callOI_list[1][0]
        self.analysis[self.timestamps[0][1]]["resistance"]["R3"] = callOI_list[2][0]
        

        #calculate Support.
        putOI_list.sort(key=lambda x:x[1],reverse=True)

        self.analysis[self.timestamps[0][1]]["supports"]["S1"] = putOI_list[0][0]
        self.analysis[self.timestamps[0][1]]["supports"]["S2"] = putOI_list[1][0]
        self.analysis[self.timestamps[0][1]]["supports"]["S3"] = putOI_list[2][0]




        putVolList.sort(key=lambda x:x[1],reverse=True)
        callVolList.sort(key=lambda x:x[1],reverse=True)

        maxTradedStrike_CALL = dict()
        maxTradedStrike_CALL[1]=callVolList[0][0]
        maxTradedStrike_CALL[2]=callVolList[1][0]
        maxTradedStrike_CALL[3]=callVolList[2][0]

        self.analysis[self.timestamps[0][1]]["maxTradedStrike_CALL"] = maxTradedStrike_CALL

        maxTradedStrike_PUT = dict()
        maxTradedStrike_PUT[1] = putVolList[0][0]
        maxTradedStrike_PUT[2] = putVolList[1][0]
        maxTradedStrike_PUT[3] = putVolList[2][0]

        self.analysis[self.timestamps[0][1]]["maxTradedStrike_PUT"] = maxTradedStrike_PUT


        #calculate newlyAddedCOIResistance and newlyAddedCOISupport

        #remove all OI's which are negative or zero

        #print("PUTS COI",putCOI_list)
        #print("CALL COI",callCOI_list)


        callCOI_list = list(filter(lambda a:float(a[1])>0,callCOI_list))
        putCOI_list  = list(filter(lambda a:float(a[1])>0,putCOI_list))

        callCOI_list.sort(key=lambda x:x[1],reverse=True)
        putCOI_list.sort(key=lambda x:x[1],reverse=True)
        #print(putCOI_list)
        #print("PUTS COI",putCOI_list)
        #print("CALL COI",callCOI_list)


        callCOIList = dict()
        putCOIList  = dict()

        try:
            for x in range(0,3):
                callCOIList[x+1]= callCOI_list[x][0]
        except:
            pass

        try:
            for x in range(0,3):
                putCOIList[x+1] = putCOI_list[x][0]
        except:
            pass


        self.analysis[self.timestamps[0][1]]["newlyAddedCOIResistance"] = callCOIList
        self.analysis[self.timestamps[0][1]]["newlyAddedCOISupport"] = putCOIList




        callOISummation = 0
        putOISummation = 0

        callCOISummation = 0
        putCOISummation = 0

        worthlessOI = dict()
        validOI     = dict()

        worthlessCOI = dict()
        validCOI     = dict()

        totalOIs = callOptionsOIAdder[len(callOptionsOIAdder)-1] + putOptionOIAdder[len(putOptionOIAdder)-1]

        totalOIs_Current = callOptionsOIAdder_Current[len(callOptionsOIAdder_Current)-1] + putOptionOIAdder_Current[len(putOptionOIAdder_Current)-1]

        totalcallOI = callOptionsOIAdder[len(callOptionsOIAdder)-1]
        totalputOI  = putOptionOIAdder[len(putOptionOIAdder)-1]


        if(debug):print("CALL OI : ",totalcallOI,"  PUT OI :",totalputOI)
        if(debug):print("CALL COI : ",totalCallCOI,"  PUT COI :",totalPutCOI)
        if(debug):print("CALL VOL : ",totalCallVol,"  PUT VOL :",totalPutVol)

        PCR_OI = str(float(float(totalputOI)/float(totalcallOI)))+"    "
        self.analysis[self.timestamps[0][1]]["PCR_OI"] = float(PCR_OI[:4])

        PCR_COI = dict()
        PCR_COI["PUT COI"] = totalPutCOI
        PCR_COI["CALL COI"] = totalCallCOI
        self.analysis[self.timestamps[0][1]]["PCR_COI"] = PCR_COI

        ITM_PCR_COI = dict() 
        ITM_PCR_COI["ITM CALL COI"] = ITM_callCOI_tot
        ITM_PCR_COI["ITM PUT COI"] = ITM_putCOI_tot

        self.analysis[self.timestamps[0][1]]["ITM_PCR_COI"] =  ITM_PCR_COI

        PCR_VO =  str(float(float(totalPutVol)/float(totalCallVol)))+"    "
        self.analysis[self.timestamps[0][1]]["PCR_VO"] = float(PCR_VO[:4])


        self.analysis[self.timestamps[0][1]]["totalOI"] = totalOIs


        i  = len(putOptionOIAdder)-1

        #print("putADDER  ", putOptionOIAdder)
        #print("callADDER  ",callOptionsOIAdder)
        #print("totalOI ",totalOIs)

        ##print(""""strike=",x,"  ",totalOIs,"   ",callOptionsOIAdder[i],"  ",putOISummation,"   ",validOIs""")

        for x in callOptionsOIAdder_Current:
            #print(">> ",x)
            pass

        strikePrices.sort(key=lambda x:x[1])

        for x in strikePrices:

            #here we can use 2 CallOIs or CallOIs_Current(for current series)
            

            #pcallOI = CallOIs[x[0]]
            pcallOI = CallOIs_Current[x[0]]
            pcallCOI = CallCOIs[x[0]]

            #pputOI = PutOIs[x[0]]
            pputOI = PutOIs_Current[x[0]]
            pputCOI = PutCOIs[x[0]]
            putOISummation  += pputOI

            validOIs = totalOIs_Current - callOptionsOIAdder_Current[i-1]  - putOISummation
            #print(totalOIs_Current,"          ",callOptionsOIAdder_Current[i-1],"           ",putOISummation)
            callOISummation   += pcallOI
            
            callCOISummation  += pcallCOI
            putCOISummation  += pputCOI

            worthlessOIs = totalOIs  

            #print("strike=",x,"  ",totalOIs,"   ",callOptionsOIAdder[i],"  ",putOISummation,"   ",validOIs)

            worthlessOI[x[0]] = worthlessOIs

            #print(CallOIs_Current[x[0]],"           ",x,"           ",PutOIs_Current[x[0]],"             ValidOis = ",validOIs, "       put summ= ",putOISummation,"   call summ= ",callOISummation) 


            validOI[x[0]]     = validOIs
            i = i-1

        lis = []
        for x in validOI:
            lis.append([validOI[x],float(x)])

        lis.sort()
        if(debug):print(lis)

        #print(">>>",lis)
        #print(self.timestamps[0])
        self.analysis[self.timestamps[0][1]]["MAX_PAIN"] = lis[0][1]
        self.analysis[self.timestamps[0][1]]["MAX_PAIN2"] = lis[1][1]

        ########################################################################
        #########                                                      #########
        #########                    FUTURES DATA                      #########
        #########                                                      #########
        ########################################################################

        #Now prepare the futures analysis values

        #now for next 3 we need to gather data across multiple series.

        totalOI = 0
        totalCOI = 0
        totalTraded = 0

        strikePriceListFut = []

        currentSeriespCOI = 0
        currentSeriesCOI  = 0 
        currentSeriespCOI_Changed = False



        for allSeries in currSymbolData["futuresData"]:
            if("-" in allSeries):
                #means we are at a key which specifies the timestamp or expiry date.
                totalOI += int(currSymbolData["futuresData"][allSeries]["openInterest"])
                totalCOI += int(currSymbolData["futuresData"][allSeries]["changeinOpenInterest"])
                #//
                totalTraded += int(currSymbolData["futuresData"][allSeries]["traded"])

                strikePriceListFut.append([self.generateabsoluteTimestamp(allSeries),allSeries])

                if(currentSeriespCOI_Changed == False):
                    currentSeriespCOI = str(round(float(currSymbolData["futuresData"][allSeries]["pchangeinOpenInterest"]),2))
                    currentSeriesCOI = str(round(float(currSymbolData["futuresData"][allSeries]["changeinOpenInterest"]),2))
                    currentSeriespCOI_Changed = True

        strikePriceListFut.sort(key=lambda x:x[0],reverse=False)


        #totalMarketWideOIPercent = round(float(int(currSymbolData["futuresData"]["totalOverallContracts"])/int(currSymbolData["futuresData"]["marketWidePositionLimits"])),2)
        pChangeInOI = round(float(totalCOI/totalOI)*100,2)

        #self.analysis[self.timestamps[0][1]]["totalMarketWideOIPercent"] = str(totalMarketWideOIPercent)
        self.analysis[self.timestamps[0][1]]["pChangeInOI"] = str(pChangeInOI)
        self.analysis[self.timestamps[0][1]]["traded"] = str(totalTraded)
        self.analysis[self.timestamps[0][1]]["pChaneInOI_CURR_SERIES"] = str(currentSeriespCOI)
        self.analysis[self.timestamps[0][1]]["ChaneInOI_CURR_SERIES"] = str(currentSeriesCOI)
        #print(currSymbolData["futuresData"])
        self.analysis[self.timestamps[0][1]]["OLHC"]["OPEN"] = currSymbolData["futuresData"][strikePriceListFut[0][1]]["openPrice"]
        self.analysis[self.timestamps[0][1]]["OLHC"]["HIGH"] = currSymbolData["futuresData"][strikePriceListFut[0][1]]["highPrice"]
        self.analysis[self.timestamps[0][1]]["OLHC"]["LOW"]  = currSymbolData["futuresData"][strikePriceListFut[0][1]]["lowPrice"]
        self.analysis[self.timestamps[0][1]]["pChange"]      = str(round(float(currSymbolData["futuresData"][strikePriceListFut[0][1]]["pChange"]),2))


        self.analysis[self.timestamps[0][1]]["lotSize"]  = currSymbolData["futuresData"]["marketLot"]

        self.saveAnalysis()



    def analyzeOptionChain(self,refresh=False):
        entireOptionChainStructureObject = completeOptionChainStructure(self.symbolName)
        if(refresh):entireOptionChainStructureObject.downloadNewSource()
        self.entireStructure = entireOptionChainStructureObject.loadFromFileAndGetDict()
        self.generateAnalysis()

        #pprint.pprint(self.analysis)
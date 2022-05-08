from urllib.parse import urlencode, quote_plus
from urllib import   request
import urllib.request

import time
import six
import re
import json
import random 
import pprint
import os.path
from os import path
import sys
from datetime import datetime

currentOptionDetailsFile = "/home/pi/Feynman-Server/DATA/currentOptionDataDetails.db"



class optionBlock:
        Type            = ""#Call/Put
        StrikePrice     = 0
        OI              = 0
        COI             = 0
        volume          = 0
        LTP             = 0 
        netChange       = 0

def printOptionDetail(option):
        print(option.Type)
        print("Strike Price =",option.StrikePrice)
        print("OI           =",option.OI)
        print("COI          =",option.COI)
        print("volume       =",option.volume)
        print("LTP          =",option.LTP)
        print("Net Change   =",option.netChange)


class executeAndFetchAllData:

        def byte_adaptor(fbuffer):

                if six.PY3:
                        strings = fbuffer.decode('latin-1')
                        fbuffer = six.StringIO(strings)
                        return fbuffer
                else:
                        return fbuffer

        def nse_headers():
                return {'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Host': 'www1.nseindia.com',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
                        'X-Requested-With': 'XMLHttpRequest'
                        }

        def printOptionDetail(self,option):
                print(option.Type)
                print("Strike Price =",option.StrikePrice)
                print("OI           =",option.OI)
                print("COI          =",option.COI)
                print("volume       =",option.volume)
                print("LTP          =",option.LTP)
                print("Net Change   =",option.netChange)

        def parseOptionData(self,currStrikePriceData):
                #print(currStrikePriceData)
                callOpt = optionBlock()
                putOpt  = optionBlock()

                relevantData = ""
                #print(currStrikePriceData+"\n\n\n########")
                #currStrikePriceData = currStrikePriceData.split("\n")

                lis = []
                #print(currStrikePriceData)
                

                while(True):
                        #print(currStrikePriceData,currStrikePriceData.find("<td class="),currStrikePriceData.find("</td>"))
                        if(currStrikePriceData.find("<td class=")==-1):
                                break
                        first = currStrikePriceData[currStrikePriceData.find("<td class="):]
                        currStrikePriceData = first
                        currStrikePriceData = currStrikePriceData[first.find("</td>")+5:]
                        strs = first[:first.find("</td>")]
                        strs = strs.replace("\n","")
                        strs = strs.replace(" ","")
                        strs = strs.replace("\t","")
                        strs = strs.replace("\b","")
                        strs = strs.replace("\r","")
                        lis.append(strs)

                for x in currStrikePriceData:
                        if("a href=\"javascript:chartPopup" in x and len(relevantData)>1):
                                relevantData = relevantData[0:len(relevantData)-1]
                        if("a href=\"javascript:chartPopup" in x or "td class=" in x or "live_market/dynaContent/live_watch" in x):
                                if(len(x)>5):
                                        strs = x.strip()
                                        relevantData +=  strs+ "\n"
                #relevantData = relevantData.replace("\t","")
                #relevantData = relevantData[0:len(relevantData)-1]
                #print(relevantData)
                relevantData = lis
                
                #print("###",len(relevantData))
                #print(relevantData,len(relevantData))

                #return 1,2
                callOpt.Type = "Call"

                strs = relevantData[0]
                strs = strs[strs.find("<tdclass=\"nobg\">")+16:]
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace(",","")
                strs = strs.replace(">","")
                strs = strs.replace("\"","")
                if(strs.find("-")>=0):
                        strs = 0
                callOpt.OI   = strs


                strs = relevantData[10]
                strs = strs[strs.find("\"><b>")+5:strs.find("</b></a>")]
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace(">","")
                strs = strs.replace("\"","")
                if(strs.find("-")>=0):
                        strs = 0
                callOpt.StrikePrice   = strs

                strs = relevantData[1]
                #print(strs)
                strs = strs[strs.find("nobg\">")+6:]
                strs = strs.replace("</td>","")
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace(">","")
                strs = strs.replace("ass=\"ylwbg\"","")
                strs = strs.replace("\"","")
                digit = any(char.isdigit() for char in strs)
                if(strs.find("-")>=0 and not digit):
                        strs = 0
                callOpt.COI   = strs

                strs = relevantData[2]
                strs = strs[strs.find("nobg\">")+6:]
                strs = strs.replace("</td>","")
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace(">","")
                strs = strs.replace("ass=\"ylwbg\"","")
                if(strs.find("-")>=0):
                        strs = 0
                callOpt.volume   = strs

                strs = relevantData[4]
                strs = strs.replace("\n","")
                strs = strs.replace(" ","")

                start = strs.find("target=")+16
                end   = strs.find("</a>")
                #print(start,end)
                strs = strs[strs.find("target=")+16:]
                strs = strs[:strs.find("</a>")]
                #print(strs)
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace("\"","")
                strs = strs.replace(">","")
                if(strs.find("-")>=0):
                        strs = 0
                
                if(start>15):
                        callOpt.LTP   = strs
                else:
                        callOpt.LTP   = "0"
                

                strs = relevantData[5]
                
                strs = strs[strs.find(";\">")+3:]
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace("\"","")
                strs = strs.replace(">","")
                if(strs.find("-")>=0 and strs.find(".")<0):
                        strs = 0
                
                callOpt.netChange   = strs

                putOpt.Type = "Put"
                strs = relevantData[10]
                strs = strs[strs.find("\"><b>")+5:strs.find("</b></a>")]
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace(">","")
                strs = strs.replace("\"","")
                if(strs.find("-")>=0):
                        strs = 0
                putOpt.StrikePrice   = strs

                strs = relevantData[19]
                
                strs = strs[strs.find("nobg\">")+6:]
                strs = strs.replace(" ","")
                strs = strs.replace("</td>","")

                strs = strs.replace(",","")
                strs = strs.replace(">","")
                strs = strs.replace("ass=\"ylwbg\"","")

                digit = any(char.isdigit() for char in strs)
                if(strs.find("-")>=0 and not digit):
                        strs = 0
                
                putOpt.COI   = strs

                strs = relevantData[18]
                
                strs = strs[strs.find("nobg\">")+6:]
                strs = strs.replace("</td>","")
                strs = strs.replace("ass=\"ylwbg\"","")
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace(">","")
                if(strs.find("-")>=0):
                        strs = 0
                putOpt.volume   = strs

                strs = relevantData[16]
                #print(">>> ",repr(strs),len(strs))
                strs = strs.replace("\n","")
                strs = strs.replace(" ","")
                start = strs.find("target=")+16
                end   = strs.find("</a>")
                #print(start,end)
                strs = strs[strs.find("target=")+16:]
                strs = strs[:strs.find("</a>")]
                #print(strs)
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace(">","")
                if(strs.find("-")>=0):
                        strs = 0
                
                if(start>15):
                        putOpt.LTP   = strs
                else:
                        putOpt.LTP   = "0"
                #print(">>>",putOpt.LTP)

                strs = relevantData[15]
                strs = strs[strs.find(";\">")+3:]
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace(">","")
                strs = strs.replace("\"","")
                if(strs.find("-")>=0 and strs.find(".")<0):
                        strs = 0
                putOpt.netChange   = strs

                strs = relevantData[20]
                strs = strs[strs.find("<tdclass=\"ylwbg\">11,000")+17:]
                strs = strs.replace(" ","")
                strs = strs.replace(",","")
                strs = strs.replace(">","")
                strs = strs.replace("\"","")
                if(strs.find("-")>=0):
                        strs = 0
                putOpt.OI = strs

                #self.printOptionDetail(callOpt)
                #self.printOptionDetail(putOpt)
                
                return callOpt,putOpt

        def extractPriceAndTimeStamp(self,webData):
                webData = webData.split("\n")
                timestamp = ""
                currPrice = ""

                #print(webData)
                for x in webData:
                        if("Underlying Stock:" in x and "span" in x):
                                strs = x 
                                currPrice = strs[strs.find("em;\">")+5:strs.find("</b>&")].split()[1]
                        if("Underlying Index:" in x and "span" in x):
                                strs = x 
                                currPrice = strs[strs.find("em;\">")+5:strs.find("</b>&")].split()[1]
                        if("As on " in x):
                                strs = x
                                timestamp = strs[strs.find("As on ")+6:strs.find("IST")]

                #print(timestamp,currPrice)
                return timestamp,currPrice



        def fetchDataForStock(self,symbol):
                url = self.urlBuilder(symbol)
                #print(url)
                request = urllib.request.Request(url,None,executeAndFetchAllData.nse_headers())

                response = None
                while(True):
                    try:
                        response = urllib.request.urlopen(request,timeout=10)
                        break
                    except:
                        print("Request Timed Out : Trying Again")
                dataArray = executeAndFetchAllData.byte_adaptor(response.read())
                
                currStrikePrice = ""
                completeData = ""
                currStrikePriceData = ""


                startReading = False
                callOptList = []
                putOptList  = []


                for line in dataArray.read().split('\n'):
                        #print(line)
                        completeData += line+"\n"

                        if("a href=\"javascript:chartPopup" in line and startReading==False):
                                startReading = True
                                #print("set to  True")
                        elif("a href=\"javascript:chartPopup" in line and startReading==True):
                                startReading = False
                                #print("set to  False")
                                callOpt,putOpt = self.parseOptionData(currStrikePriceData)
                                callOptList.append(callOpt)
                                putOptList.append(putOpt)

                                
                                currStrikePriceData = ""

                        if(startReading):
                                #print(line)
                                currStrikePriceData += line+"\n"

                timestamp,currPrice =  self.extractPriceAndTimeStamp(completeData)
                data = dict()
                data["Current price"] = currPrice
                data["Puts"]          = putOptList
                data["Calls"]         = callOptList

                optionData = dict()

                optionData[timestamp] = data
                return optionData


        def urlBuilder(self,symbol):
                if("BANKNIFTY" in symbol):
                    return "https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=-9999&symbol=BANKNIFTY&symbol=BANKNIFTY&instrument=OPTIDX&date=-&segmentLink=17&segmentLink=17"
                if("NIFTY" in symbol):
                    url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=-10003&symbol=NIFTY&symbol=NIFTY&instrument=OPTIDX&date=-&segmentLink=17&segmentLink=17"
                else:
                    url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=1606&symbol="+symbol+"&symbol="+symbol+"&instrument=-&date=-&segmentLink=17&symbolCount=2&segmentLink=17"
                return url


#returns IO for Calls, OI for Puts
def getTotalOIForAStrikePrice(data,strikeP):
    OICalls = 1
    OIPuts = 1

    #print(strikeP)

    #add code here to get list of strike prices and get the closest value for the strikeP
    allStrikePrices = []
    calls = data["Calls"]

    for x in calls:
        allStrikePrices.append(float(x.StrikePrice))

    allStrikePrices.sort()

    #print(allStrikePrices)

    for x in range(0,len(allStrikePrices)):
        if(float(allStrikePrices[x])>=float(strikeP)):
            mins = allStrikePrices[x] - float(strikeP)
            maxs = float(strikeP) - allStrikePrices[x-1]
            if(mins>maxs):
                strikeP = allStrikePrices[x-1]
            else:
                strikeP = allStrikePrices[x]
            break

    #print("Selected Strike Price ",strikeP)

    calls = data["Calls"]
    for x in calls:
        #crazy workaroudn  for comaring the float values 
        if(abs(float(x.StrikePrice)-strikeP)<0.5):
            OICalls = x.OI
            break

    puts = data["Puts"]
    for x in puts:
        if(abs(float(x.StrikePrice)-strikeP)<0.5):
            OIPuts = x.OI
            break

    #print(OICalls,OIPuts,strikeP)
    if(OICalls==0):OICalls=1
    if(OIPuts==0):OIPuts=1
    return OICalls,OIPuts

def processCandP(callTot,putTot):
    message = ""
    rat = float(float(putTot)/float(callTot))

    if(rat>1.3):
        message = "Bulls More Powerful at this level P/C: "+str(rat)
    elif(rat<0.7):
        message = "Bears More Powerful at this level P/C: "+str(rat)
    else:
        message = "Bull/Bear Neutral at this level P/C: "+str(rat)

    return message

def saveCurrentInfoToFile(symbol,top3CALLSOI,top3PUTOI,top3CALLSCOI,top3PUTCOI,currPrice):
    global currentOptionDetailsFile
    data = "{}"
    try:
        file = open(currentOptionDetailsFile,"r")
        data=file.read()
        if(len(data)==0):
            data = "{}"
        file.close()
    except:
        pass

    #print(data)

    jsonData = json.loads(data)

    symbolData = dict()

    R1 = float(top3CALLSOI[0][3])
    R2 = float(top3CALLSOI[1][3])

    S1 = float(top3PUTOI[0][3])
    S2 = float(top3PUTOI[1][3])

    curr = float(currPrice)

    R1_p = round(float(((R1-curr)/curr)*100),1)
    R2_p = round(float(((R2-curr)/curr)*100),1)
    S1_p = round(float(((S1-curr)/curr)*100),1)
    S2_p = round(float(((S2-curr)/curr)*100),1)

    A_put = float(top3PUTCOI[0][3])
    A_call= float(top3CALLSCOI[0][3])

    symbolData["R1"]  = R1
    symbolData["R2"] = R2
    symbolData["S1"] = S1
    symbolData["S2"] = S2
    symbolData["R1_p"] =   R1_p
    symbolData["R2_p"] =   R2_p
    symbolData["S1_p"] =   S1_p
    symbolData["S2_p"]  =  S2_p
    symbolData["ActivePut"]  = A_put
    symbolData["ActiveCall"]  = A_call
    symbolData["TIMESTAMP"] = str(datetime.today().strftime('%Y-%m-%d %H-%M'))
    symbolData["CurrentPrice"] = str(curr)

    jsonData[symbol] = symbolData

    file     = open(currentOptionDetailsFile,'w')
    json.dump(jsonData,file)
    file.close()


def analyzeChainData(chainData,symbolCode):
    timeStamp = None
    for x in chainData:
        timeStamp = x
    #print(chainData)
    try:
        currPrice = float(chainData[timeStamp]["Current price"])
    except:
        print("UNABLE TO FETCH CURRENT PRICE")

    upperPrice = currPrice*1.30
    lowerPrice = currPrice*0.70


    print("Symbol : ",symbolCode)
    print("Current Price: ",currPrice)

    chainData = chainData[timeStamp]

    calls = []
    puts  = []

    currPriceCALLOI = 0
    currPricePUTOI  = 0
    diff = 99999

    allPutsWithinRange = 0
    allCallsWithinRange = 0 
    allPutsChangeWithinRange = 5000000
    allCallsChangeWithinRange = 5000000

    for x in chainData["Puts"]:
        OI = float(x.OI)
        COI = float(x.COI)

        if(float(x.StrikePrice)>=lowerPrice and float(x.StrikePrice)<=upperPrice):
            allPutsWithinRange += OI
            allPutsChangeWithinRange += COI

        COIAction = "Added"

        strikePrice = x.StrikePrice
        if(COI<0):
            COIAction = "Removed"
            COI = COI*-1

        if(abs(float(strikePrice)-currPrice)<diff):
            diff = abs(float(strikePrice)-currPrice)
            currPricePUTOI = OI
            if(currPricePUTOI==0):currPricePUTOI=1

        puts.append([OI,COI,COIAction,strikePrice])

    diff = 99999

    for x in chainData["Calls"]:
        OI = float(x.OI)
        COI = float(x.COI)
        COIAction = "Added"

        if(float(x.StrikePrice)>=lowerPrice and float(x.StrikePrice)<=upperPrice):
            allCallsWithinRange += OI
            allCallsChangeWithinRange += COI

        strikePrice = x.StrikePrice
        if(COI<0):
            COIAction = "Removed"
            COI = COI*-1

        if(abs(float(strikePrice)-currPrice)<diff):
            diff = abs(float(strikePrice)-currPrice)
            currPriceCALLOI = OI
            if(currPriceCALLOI==0):currPriceCALLOI=1

        calls.append([OI,COI,COIAction,strikePrice])

    #sort Based on CALL OI
    calls.sort(reverse=True,key = lambda x: x[0])

    top3CALLSOI = []

    for x in range(0,3):
        Call_OI,Put_OI = getTotalOIForAStrikePrice(chainData,calls[x][3])
        bullBear = processCandP(Call_OI,Put_OI)
        #print(calls[x][3]," ",Call_OI,"   ",Put_OI)
        OI = calls[x][0]
        COI = calls[x][1]
        COIAction = calls[x][2]
        strikePrice = float(calls[x][3])
        callInferredType = "Resistance"
        if(strikePrice<currPrice):
            callInferredType = "In The Money Resistance"

        top3CALLSOI.append([OI,COI,COIAction,strikePrice,callInferredType,bullBear])


    #sort Based on CALL COI
    calls.sort(reverse=True,key = lambda x: x[1])

    top3CALLSCOI = []

    for x in range(0,3):
        Call_OI,Put_OI = getTotalOIForAStrikePrice(chainData,calls[x][3])
        bullBear = processCandP(Call_OI,Put_OI)
        #print(calls[x][3]," ",Call_OI,"   ",Put_OI)
        OI = calls[x][0]
        COI = calls[x][1]
        COIAction = calls[x][2]
        strikePrice = float(calls[x][3])
        callInferredType = "Resistance"
        if(strikePrice<currPrice):
            callInferredType = "In The Money Resistance"

        top3CALLSCOI.append([OI,COI,COIAction,strikePrice,callInferredType,bullBear])

    #sort Based on PUT OI
    puts.sort(reverse=True,key = lambda x: x[0])

    top3PUTOI = []

    for x in range(0,3):
        Call_OI,Put_OI = getTotalOIForAStrikePrice(chainData,puts[x][3])
        bullBear = processCandP(Call_OI,Put_OI)
        
        OI = puts[x][0]
        COI = puts[x][1]
        COIAction = puts[x][2]
        strikePrice = float(puts[x][3])
        putInferredType = "Support"
        if(strikePrice>currPrice):
            putInferredType = "In The Money Support"

        #print(strikePrice,"  ",puts[x][3]," ",Call_OI,"   ",Put_OI)

        top3PUTOI.append([OI,COI,COIAction,strikePrice,putInferredType,bullBear])


    #sort Based on CALL COI
    puts.sort(reverse=True,key = lambda x: x[1])

    top3PUTCOI = []

    for x in range(0,3):
        Call_OI,Put_OI = getTotalOIForAStrikePrice(chainData,puts[x][3])
        bullBear = processCandP(Call_OI,Put_OI)
        #print(puts[x][3]," ",Call_OI,"   ",Put_OI)
        OI = puts[x][0]
        COI = puts[x][1]
        COIAction = puts[x][2]
        strikePrice = float(puts[x][3])
        callInferredType = "Support"
        if(strikePrice>currPrice):
            callInferredType = "In The Money Support"

        top3PUTCOI.append([OI,COI,COIAction,strikePrice,callInferredType,bullBear])


    

    print("\nHighest OI in Calls")
    for x in top3CALLSOI:

        print("")
        print(x[4]," At ",x[3]," :: ",x[5])
        print("    OI     :",x[0])
        print("    COI    :",x[1],"  ",x[2])
        print("    P From Current Price OI :",(float(x[0])/float(currPricePUTOI+currPriceCALLOI))*100," %")
        print("    P Away From Current Price :",((float(x[3])-currPrice)/currPrice)*100," %")
    
    print("\nHighest OI in Puts")
    for x in top3PUTOI:
        print("")
        print(x[4]," At ",x[3]," :: ",x[5])
        print("    OI     :",x[0])
        print("    COI    :",x[1],"  ",x[2])
        print("    P From Current Price OI :",(float(x[0])/float(currPricePUTOI+currPriceCALLOI))*100," %")
        print("    P Away From Current Price :",((float(x[3])-currPrice)/currPrice)*100," %")


    print("\nHighest COI in Calls")
    for x in top3CALLSCOI:
        print("")
        print(x[4]," At ",x[3]," :: ",x[5])
        print("    OI     :",x[0])
        print("    COI    :",x[1],"  ",x[2])
        print("    P From Current Price OI :",(float(x[0])/float(currPricePUTOI+currPriceCALLOI))*100," %")
        print("    P Away From Current Price :",((float(x[3])-currPrice)/currPrice)*100," %")
    
    print("\nHighest COI in Puts")
    for x in top3PUTCOI:
        print("")
        print(x[4]," At ",x[3]," :: ",x[5])
        print("    OI     :",x[0])
        print("    COI    :",x[1],"  ",x[2])
        print("    P From Current Price OI :",(float(x[0])/float(currPricePUTOI+currPriceCALLOI))*100," %")
        print("    P Away From Current Price :",((float(x[3])-currPrice)/currPrice)*100," %")

    isRealSupportDifferentThanAbove = False
    isRealResistanceDifferentThanAbove = False
    realSupportPrice = 99999
    realResistancePrice = 99999

    if(float(top3PUTOI[0][3])>currPrice):
        isRealSupportDifferentThanAbove = True
    if(float(top3CALLSOI[0][3])<currPrice):
        isRealResistanceDifferentThanAbove = True

    if(isRealSupportDifferentThanAbove):
        for x in top3PUTOI:
            if(float(x[3])<currPrice):
                print("\nOrignal Current Support At ",x[3]," ",x[5])
                realSupportPrice = float(x[3])
                break

    if(isRealResistanceDifferentThanAbove):
        for x in top3CALLSOI:
            if(float(x[3])>currPrice):
                print("\nOrignal Current Resistance At ",x[3]," ",x[5])
                realResistancePrice = float(x[3])
                break


    print("\n\n")
    print("P/C ratio Within Range        : ",float(allPutsWithinRange/allCallsWithinRange))
    print("P/C change ratio Within Range : ",float(allPutsChangeWithinRange/allCallsChangeWithinRange))

    pcRatio = float(allPutsWithinRange/allCallsWithinRange)
    pcChangeRatio = float(allPutsChangeWithinRange/allCallsChangeWithinRange)
    if(pcChangeRatio<2):
        print("\nShort Term Bearish")
    if(pcRatio<0.5):
        print("\nLong Term Bearish")
    if(pcRatio>1.2):
        print("\nLong Term Bullish")

    if(pcChangeRatio>8):
        print("\nShort Term Bullish")


    resistance = top3CALLSOI[0][3]
    support = top3PUTOI[0][3]

    if(realResistancePrice!=99999):
        resistance = realResistancePrice

    if(realSupportPrice != 99999):
        support = realSupportPrice

    print(support,currPrice,resistance)

    upside = resistance-currPrice
    downside = currPrice - support

    upsideP = float(float(upside/currPrice)*100)
    downsideP = float(float(downside/currPrice)*100)

    Pdiff = upsideP - downsideP

    upsideP = float("{:.2f}".format(upsideP))
    downsideP = float("{:.2f}".format(downsideP))

    #saveCurrentInfoToFile(symbolCode,top3CALLSOI,top3PUTOI,top3CALLSCOI,top3PUTCOI,currPrice)

    print("\n")
    if(Pdiff>8):
        print("Favourable Risk Reward (Upside/Downside) : ",upsideP," / ",downsideP, " %")
    elif(Pdiff>5):
        print("Moderate Risk Reward (Upside/Downside) : ",upsideP," / ",downsideP, " %")
    else:
        print("UnFavourable Risk Reward (Upside/Downside) : ",upsideP," / ",downsideP, " %")



optionData = executeAndFetchAllData()

symbolList = ["BANKNIFTY","NIFTY","ACC","ADANIENT","ADANIPORTS","ADANIPOWER","AMARAJABAT","AMBUJACEM","APOLLOHOSP","APOLLOTYRE","ASHOKLEY","ASIANPAINT","AUROPHARMA","AXISBANK","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BALKRISIND","BANDHANBNK","BANKBARODA","BATAINDIA","BEL","BERGEPAINT","BHARATFORG","BHARTIARTL","BHEL","BIOCON","BOSCHLTD","BPCL","BRITANNIA","CADILAHC","CANBK","CENTURYTEX","CHOLAFIN","CIPLA","COALINDIA","COLPAL","CONCOR","CUMMINSIND","DABUR","DIVISLAB","DLF","DRREDDY","EICHERMOT","EQUITAS","ESCORTS","EXIDEIND","FEDERALBNK","GAIL","GLENMARK","GMRINFRA","GODREJCP","GODREJPROP","GRASIM","HAVELLS","HCLTECH","HDFC","HDFCBANK","HDFCLIFE","HEROMOTOCO","HINDALCO","HINDPETRO","HINDUNILVR","IBULHSGFIN","ICICIBANK","ICICIPRULI","IDEA","IDFCFIRSTB","IGL","INDIGO","INDUSINDBK","INFRATEL","INFY","IOC","ITC","JINDALSTEL","JSWSTEEL","JUBLFOOD","JUSTDIAL","KOTAKBANK","L&amp;TFH","LICHSGFIN","LT","LUPIN","M&amp;M","M&amp;MFIN","MANAPPURAM","MARICO","MARUTI","MCDOWELL-N","MFSL","MGL","MINDTREE","MOTHERSUMI","MRF","MUTHOOTFIN","NATIONALUM","NAUKRI","NCC","NESTLEIND","NIITTECH","NMDC","NTPC","ONGC","PAGEIND","PEL","PETRONET","PFC","PIDILITIND","PNB","POWERGRID","PVR","RAMCOCEM","RBLBANK","RECLTD","RELIANCE","SAIL","SBILIFE","SBIN","SHREECEM","SIEMENS","SRF","SRTRANSFIN","SUNPHARMA","SUNTV","TATACHEM","TATACONSUM","TATAMOTORS","TATAPOWER","TATASTEEL","TCS","TECHM","TITAN","TORNTPHARM","TORNTPOWER","TVSMOTOR","UBL","UJJIVAN","ULTRACEMCO","UPL","VEDL","VOLTAS","WIPRO","ZEEL"]
inputSymbol = sys.argv[1]

symbol = None

for x in symbolList:
    if(inputSymbol == x):
        print("Interpreting ",inputSymbol," as ",x)
        symbol = x
        break

if(symbol == None):
    for x in symbolList:
        if(inputSymbol in x):
            print("Interpreting ",inputSymbol," as ",x)
            symbol = x
            break

if(symbol==None):
    print("Cannot Find the Symbol In Database")
    exit()

chainData = optionData.fetchDataForStock(symbol)

analyzeChainData(chainData,symbol)
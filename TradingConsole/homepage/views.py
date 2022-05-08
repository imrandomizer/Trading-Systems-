from django.shortcuts import render
from django.http import HttpResponse
from nsetools import Nse
from django.http import JsonResponse 
import html
import json
import sys
import requests
import os
from  nsetools import Nse
import time
from time import localtime, strftime 
from datetime import datetime, timedelta
import pprint
from dateutil.tz import *



#this caters to the requests from the http://192.168.0.7:8000/table_deliverable_low_high?DATE=14-SEP-2020&CONTEXT=NIFTY100
#also core delivery tamplate via DeliveryPatterns


#constants 

#maximum number of elements passed
maxelems = 30
numberOfPastDaysToDisplay = 7


from time import localtime, strftime
from .models import sidebar
sys.path.append("/home/pi/Feynman-Server/TradingConsole/Deleveries/")
import entirePriceMovementDataDaily

debug = False


advdecMap = dict()


def debug(msg):

    global debug
    if(debug == True):
        print(msg)

sidebars_Elems = sidebar()
symbolNameDict = None


def readSymbolNameDict():
    global symbolNameDict
    symbolNameDict = dict()
    file = open("/home/pi/DjangoServer/staticContentHelper/EQUITY_L.csv")
    data = file.read().split("\n")
    data = data[1:]
    for x in data:
        d = x.split(",")
        try:
            symbolNameDict[d[0]]=d[1]
        except:
            pass
    #print("SYMBOL NAME DICT",symbolNameDict)


def index(request):

    return render(request, 'index.html', {'sidebars_Elems': sidebars_Elems.data,'PageName':'Home'})

def table_deliverable_low_high(request):
    global symbolNameDict
    global maxelems

    #DEFAULT
    colNames = ["Symbol","Name","Percent Deliverable","Current Price","P Change","Day Vol/min ","3 days vol/min"]

    if(symbolNameDict == None):
        readSymbolNameDict()
        #print(symbolNameDict)

    date = None
    context = "ALL"

    try:
        context = request.GET["CONTEXT"]
    except:
        pass

    date = request.GET["DATE"]

    maxData = requests.get("http://localhost:8081/analysisReady/DeleveriesAPI",params={"MODE":"MAX","CONTEXT":context,"DATE":date,"MAXELEMS":maxelems})

    maxData = maxData.text
    maxData = json.loads(maxData)
    #print(">>>",maxData)
    rows    = maxData["response"]

    #currently adding  past price  data to all the results.
    isFetchingPastDateData = True

    #logic to figure out if we are fetching data for current date or a past date.

    tm = strftime("%D", localtime()).split(":")

    currDate  = int(tm[0].split("/")[1])
    providedDate = int(date.split("-")[0])

    print(">>>>>",currDate,providedDate)

    if(currDate > providedDate):
        isFetchingPastDateData = True


    if(isFetchingPastDateData):
        colNames = ["Symbol","Name","Percent Deliverable","Current Price","P Change","Day Vol/min ","3 days vol/min","Past Price","Patterns"]


    listOfElements = []

    allSymbolData_highest = [[]]
    allSymbolData_lowest  = [[]]

    for x in  rows:
        print(x)
        delivPer = x[0]
        symbol   = x[1]
        name     = x[1]
        try:
            name     = symbolNameDict[x[1]]
        except:
            print("UNABE TO FIND",x[1])

        if(isFetchingPastDateData):
            allSymbolData_highest.append([symbol,name,delivPer,0,0,0,0,x[2]," "])
        else:
            allSymbolData_highest.append([symbol,name,delivPer,0,0,0,0])

    maxData = requests.get("http://localhost:8081/analysisReady/DeleveriesAPI",params={"MODE":"MIN","CONTEXT":context,"DATE":date,"MAXELEMS":maxelems})

    maxData = maxData.text

    maxData = json.loads(maxData)

    

    rows    = maxData["response"]

    print(">>>",rows)
    for x in  rows:

        delivPer = x[0]
        symbol   = x[1]
        name     = x[1]
        try:
            name     = symbolNameDict[x[1]]
        except:
            pass

        if(isFetchingPastDateData):
            allSymbolData_lowest.append([symbol,name,delivPer,0,0,0,0,x[2]," "])
        else:
            allSymbolData_lowest.append([symbol,name,delivPer,0,0,0,0])

    if("BANKNIFTY" in context):
        allSymbolData_lowest  = [[]]

    return render(request, 'table_deliverable_low_high.html',{'sidebars_Elems': sidebars_Elems.data,'PageName':'Delivery Patterns','colNames': colNames, 'colContent': allSymbolData_highest,'colContent_lowest':allSymbolData_lowest})

def DeliveryPatterns(request):
    global numberOfPastDaysToDisplay
    
    
    #print(colNames)
    #fetch cuurent time if its a premarket timing return the relevant file.
    tm = strftime("%H:%M:%w", localtime()).split(":")
    #print(tm)
    hr = int(tm[0])
    mm = int(tm[1])
    day = int(tm[2])

    preopenOverride = False
    
    #get Availabe dates for the webpage
    x = requests.get("http://localhost:8081/analysisReady/Dates",params={})
    response = json.loads(x.text)
    availDates = response["AvailableDates"]

    dateArray = []

    for x in  availDates:
        dateArray.append(x)

    dateArray = dateArray[:numberOfPastDaysToDisplay]

    try:
        preopenOverride = request.GET["PREOPEN"]
        preopenOverride = True
    except:
        pass


    return render(request, 'DeliveryPatterns.html',{'sidebars_Elems': sidebars_Elems.data,'PageName':'Delivery Patterns','date':dateArray[0],'dateArray':dateArray})

def DerivativeDataAnalysis(request):
    x = requests.get("http://localhost:8082/derivativeDataAnalysis/getSymbolList")

    x = json.loads(x.text)

    symbolList = dict()
    symbolList["EQUITY"] = []
    symbolList["INDEX"]  = []

    for symbolName in x["SYMBOLS"]:
        if("NIFTY" not in symbolName):
            symbolList["EQUITY"].append(symbolName)

    symbolList["INDEX"].append("NIFTY")
    symbolList["INDEX"].append("BANKNIFTY")
    print(symbolList)
    return render(request,'DerivativeDataAnalysis.html',{'sidebars_Elems': sidebars_Elems.data,'symbolList':symbolList})
    

def fetchSymbolDerivativeData(request):

    symbolName = request.GET["SYMBOL"]
    x = requests.get("http://localhost:8082/derivativeDataAnalysis/getSymbolDerivativeData",params={"SYMBOL":symbolName})
    response = json.loads(x.text)
    return  JsonResponse(response)


def MarketActivity(request):

    x = requests.get("http://192.168.0.107:8081/analysisReady/participantDataAPI",params={})

    response = json.loads(x.text)
    #print(response)

    return render(request, 'marketActivityReport.html', {'sidebars_Elems': sidebars_Elems.data,'PageName':'Market Actity Report',"ParticipantData":response})


def barometer(request):

    
    #print(response)

    return render(request, 'barometer.html', {'sidebars_Elems': sidebars_Elems.data,'PageName':'Barometer'})


def getNewBarometerData(request):

    #build all the blocks. 
    #block 1

    #get NIFTY.
    execCurl  = os.system("""curl 'https://in.investing.com/portfolio/?portfolioID=ZWFkNzNjNGlhNWBuZTFjZQ%3D%3D'   -H 'authority: in.investing.com'   -H 'cache-control: max-age=0'   -H 'sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"'   -H 'sec-ch-ua-mobile: ?0'   -H 'sec-ch-ua-platform: "Windows"'   -H 'dnt: 1'   -H 'upgrade-insecure-requests: 1'   -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'   -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'   -H 'sec-fetch-site: same-origin'   -H 'sec-fetch-mode: navigate'   -H 'sec-fetch-user: ?1'   -H 'sec-fetch-dest: document'   -H 'referer: https://in.investing.com/equities/hathway-cable---datacom'   -H 'accept-language: en-GB,en-US;q=0.9,en;q=0.8'   -H 'cookie: logglytrackingsession=f8ec0b6d-5c85-49a9-b054-03f9399c7909; G_AUTHUSER_H=0; portfolioState91dea96e61eced28d426049eb95a1c66=10612274:open; adBlockerNewUserDomains=1622972952; udid=63f4e4f381a21f89729a17271670fa7c; _ga=GA1.2.1551697408.1622972953; welcomePopup=1; G_ENABLED_IDPS=google; _tz_id=777c40cdd0af43fda26690611e2103ea; StickySession=id.83908539191.690.in.investing.com; PHPSESSID=9fj86ijfabjnuv6b9uevvt2ijv; billboardCounter_56=1; SideBlockUser=a%3A2%3A%7Bs%3A10%3A%22stack_size%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Bi%3A8%3B%7Ds%3A6%3A%22stacks%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Ba%3A1%3A%7Bi%3A0%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A5%3A%2224014%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A37%3A%22%2Frates-bonds%2Findia-10-year-bond-yield%22%3B%7D%7D%7D%7D; r_p_s_n=1; geoC=IN; smd=63f4e4f381a21f89729a17271670fa7c-1643211524; __cflb=0H28uv9TXEXY1dxGsSwM21AWkmXN8C3K4g7Wcxpus2j; comment_notification_202981552=1; Adsfree_conversion_score=2; adsFreeSalePopUp91dea96e61eced28d426049eb95a1c66=1; gtmFired=OK; nyxDorf=ZWQ3bWYuYT8wZm9kZitkZDFgMG9heDIxNzFjaQ%3D%3D; ses_id=NngyczU6Y2sydj07YTBmZDdkPmxmaTQ3MTVuaDYzNSM5LTU7NGM0cmFubyFhYmR4ZWIxOTY2YWZgNTc9N2E3MDYzMmg1MWM4Mjc9N2ExZmU3YT4wZmg0ZDE4bm42ODU%2FOTw1ZTQzNDNhNm9gYTxkbGV3MS02cmFwYDI3Zzd2N3A2OTJzNWVjPjIyPTBhNGY2N2Y%2BN2ZhNDMxZm5rNjQ1LTly'  -o outps""")
    data = open("outps")
    data = data.read()
    data = data.split("\n")

    allData = dict()

    lines = len(data)
    for x in range(0,lines-30):
        
        if('<span class="aqPopupWrapper js-hover-me-wrapper">' in  data[x]):
            
            y = data[x][data[x].find("title=\"")+7:]
            name = y[:y.find("\"")]

            dataElem = dict()

            for z in range(x,x+20):
                s = data[z]
                if('data-column-name="last"' in s):
                    dataElem["PRICE"] = s[s.find(">")+1:s.find("</")]
                if('data-column-name="high"' in s):
                    dataElem["HIGH"] = s[s.find(">")+1:s.find("</")]

                if('data-column-name="low"' in s):
                    dataElem["LOW"] = s[s.find(">")+1:s.find("</")]

                if('data-column-name="chgpercent"' in s):
                    dataElem["CHANGE"] = s[s.find(">")+1:s.find("</")]

            allData[name] = dataElem


    



    execCurl  = os.system("""curl 'https://in.investing.com/portfolio/?portfolioID=NDA1ZmUzYTVkMmtvZDU1Mw%3D%3D'   -H 'authority: in.investing.com'   -H 'cache-control: max-age=0'   -H 'sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"'   -H 'sec-ch-ua-mobile: ?0'   -H 'sec-ch-ua-platform: "Windows"'   -H 'dnt: 1'   -H 'upgrade-insecure-requests: 1'   -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'   -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'   -H 'sec-fetch-site: same-origin'   -H 'sec-fetch-mode: navigate'   -H 'sec-fetch-user: ?1'   -H 'sec-fetch-dest: document'   -H 'referer: https://in.investing.com/equities/hathway-cable---datacom'   -H 'accept-language: en-GB,en-US;q=0.9,en;q=0.8'   -H 'cookie: logglytrackingsession=f8ec0b6d-5c85-49a9-b054-03f9399c7909; G_AUTHUSER_H=0; portfolioState91dea96e61eced28d426049eb95a1c66=10612274:open; adBlockerNewUserDomains=1622972952; udid=63f4e4f381a21f89729a17271670fa7c; _ga=GA1.2.1551697408.1622972953; welcomePopup=1; G_ENABLED_IDPS=google; _tz_id=777c40cdd0af43fda26690611e2103ea; StickySession=id.83908539191.690.in.investing.com; PHPSESSID=9fj86ijfabjnuv6b9uevvt2ijv; billboardCounter_56=1; SideBlockUser=a%3A2%3A%7Bs%3A10%3A%22stack_size%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Bi%3A8%3B%7Ds%3A6%3A%22stacks%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Ba%3A1%3A%7Bi%3A0%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A5%3A%2224014%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A37%3A%22%2Frates-bonds%2Findia-10-year-bond-yield%22%3B%7D%7D%7D%7D; r_p_s_n=1; geoC=IN; smd=63f4e4f381a21f89729a17271670fa7c-1643211524; __cflb=0H28uv9TXEXY1dxGsSwM21AWkmXN8C3K4g7Wcxpus2j; comment_notification_202981552=1; Adsfree_conversion_score=2; adsFreeSalePopUp91dea96e61eced28d426049eb95a1c66=1; gtmFired=OK; nyxDorf=ZWQ3bWYuYT8wZm9kZitkZDFgMG9heDIxNzFjaQ%3D%3D; ses_id=NngyczU6Y2sydj07YTBmZDdkPmxmaTQ3MTVuaDYzNSM5LTU7NGM0cmFubyFhYmR4ZWIxOTY2YWZgNTc9N2E3MDYzMmg1MWM4Mjc9N2ExZmU3YT4wZmg0ZDE4bm42ODU%2FOTw1ZTQzNDNhNm9gYTxkbGV3MS02cmFwYDI3Zzd2N3A2OTJzNWVjPjIyPTBhNGY2N2Y%2BN2ZhNDMxZm5rNjQ1LTly'  -o outps""")
    data = open("outps")
    data = data.read()
    data = data.split("\n")

    lines = len(data)
    for x in range(0,lines-30):
        
        if('<span class="aqPopupWrapper js-hover-me-wrapper">' in  data[x]):
            
            y = data[x][data[x].find("title=\"")+7:]
            name = y[:y.find("\"")]

            dataElem = dict()

            for z in range(x,x+20):
                s = data[z]
                if('data-column-name="last"' in s):
                    dataElem["PRICE"] = s[s.find(">")+1:s.find("</")]
                if('data-column-name="high"' in s):
                    dataElem["HIGH"] = s[s.find(">")+1:s.find("</")]

                if('data-column-name="low"' in s):
                    dataElem["LOW"] = s[s.find(">")+1:s.find("</")]

                if('data-column-name="chgpercent"' in s):
                    dataElem["CHANGE"] = s[s.find(">")+1:s.find("</")]

            allData[name] = dataElem


    nameDict = dict()
    nameDict["CBOE VIX"] = "CBOE Volatility Index (CFD)"
    nameDict["NIFTY 50"] = "Nifty 50"
    nameDict["Nasdaq 100"] = "Nasdaq 100"
    nameDict["India VIX"] = "India VIX"
    nameDict["SGX NIFTY"] = "Nifty 50 Futures (Singapore)"
    nameDict["Dow Jones"] = "Dow Jones Futures"
    nameDict["Nifty Bank"] = "Nifty Bank"
    nameDict["Gold"] = "Gold Futures (CFD)"
    nameDict["ICICI Bank"] = "ICICI Bank Ltd"
    nameDict["Infosys"] = "Infosys Ltd"
    nameDict["Reliance"] = "Reliance Industries Ltd"
    nameDict["HDFC Bank"] = "HDFC Bank Ltd"



    #fetch OI data from analysis API.
    x = requests.get("http://localhost:8082/derivativeDataAnalysis/getSymbolDerivativeData?SYMBOL=NIFTY",params={})

    response = json.loads(x.text)

    derivativeData = None

    timestamp = 0.0
    for x in response:
        if(float(x)>timestamp):
            derivativeData = response[x]
            timestamp = float(x)


    #fetch participant data. 
    x = requests.get("http://localhost:8081/analysisReady/participantDataAPI",params={})

    response = json.loads(x.text)

    participantData_Cash = None

    
    for x in response["CASH_MARKET"]:
        participantData_Cash = response["CASH_MARKET"][x]
        participantData_Cash["DATE"] = x
    


    participantData_Fut = dict()

    i = 0
    ars = []
    for x in response["FUTURES_MARKET"]:
        participantData_Fut[x] = response["FUTURES_MARKET"][x]
        ars.append(int(x))
        if(i==1):
            break
        i += 1

    ars.sort()
    newArr = []
    for z in  ars:
        newArr.append(str(z))

    ars = newArr

    longFutFIInew = int(response["FUTURES_MARKET"][ars[0]]["FII"]["Future Index Long"])-int(response["FUTURES_MARKET"][ars[0]]["FII"]["Future Index Short"])
    longFutFIIold = int(response["FUTURES_MARKET"][ars[1]]["FII"]["Future Index Long"])-int(response["FUTURES_MARKET"][ars[1]]["FII"]["Future Index Short"])

    FIIlongChange = ((longFutFIInew-longFutFIIold)/longFutFIIold)*100

    longFutDIInew = int(response["FUTURES_MARKET"][ars[0]]["DII"]["Future Index Long"])-int(response["FUTURES_MARKET"][ars[0]]["DII"]["Future Index Short"])
    longFutDIIold = int(response["FUTURES_MARKET"][ars[1]]["DII"]["Future Index Long"])-int(response["FUTURES_MARKET"][ars[1]]["DII"]["Future Index Short"])

    DIIlongChange = ((longFutDIInew-longFutDIIold)/longFutDIIold)*100


    NetLongNew = 0
    NetShortNew = 0
    NetLongOld = 0
    NetShortOld = 0

    
    NetLongNew += int(response["FUTURES_MARKET"][ars[0]]["Client"]["Future Index Long"])
    NetShortNew += int(response["FUTURES_MARKET"][ars[0]]["Client"]["Future Index Short"])

    
    NetLongOld += int(response["FUTURES_MARKET"][ars[1]]["Client"]["Future Index Long"])
    NetShortOld += int(response["FUTURES_MARKET"][ars[1]]["Client"]["Future Index Short"])

    print(">>",NetLongOld," ",NetShortOld,NetLongNew,NetShortNew)
    NetLongChange = (((NetLongNew-NetShortNew)-(NetLongOld-NetShortOld))/(NetLongOld-NetShortOld))*100





    """
    THIS  WILL BE MOVED TO analysis ready.


        #now fetch the nifty ADV decline data.
        nse = Nse()
        nseData = nse.downloadUrlNewSite("https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100")
        nseLive = json.loads(nseData)

        avdDecline = nseLive["advance"]
        
        looks like 

        "advance":{
    "declines":"31",
    "advances":"69",
    "unchanged":"0},"""

    block1 = dict()
    block1["allData"] = allData
    block1["nameDict"] = nameDict 
    block1["derivativeData"] = derivativeData 
    block1["participantData_Cash"] = participantData_Cash 
    block1["participantData_Fut"]  = participantData_Fut 
    block1["DIIlongChange"] = str("{:.2f}".format(DIIlongChange))+"%"
    block1["FIIlongChange"] = str("{:.2f}".format(FIIlongChange))+"%"
    block1["ClientLongChange"] = str("{:.2f}".format(NetLongChange))+"%"
    block1["FUT LONG FII"] = str(longFutFIInew)
    block1["FUT LONG DII"] = str(longFutDIInew)
    block1["ClientLong"] = str(NetLongNew-NetShortNew)



    x = requests.get("http://localhost:8081/analysisReady/getBarometerData",params={})

    res = json.loads(x.text)

    #from here we compute 4 different blocks
    #1. Adv Decline
    #2. Highest Delivery
    #3. close to 52 W high.
    #4. volume burst.
    hh = datetime.now().hour
    if(hh>=16):
        hh = 15
    if(hh<8):
        hh = 9

    advdecMap[hh] = res["ADV/DEC"]

    block1["ADV/DEC"] = advdecMap


    advDecLast5 = dict()
    key = hh

    for o in range(6,0,-1):
        print(o)
        print(key)
        if(key<9):
            key = 15
        print(key)

        try:
            print(advdecMap)
            print(advDecLast5)
            advDecLast5[o] = advdecMap[key]
            key = key - 1
        except:
            advDecLast5[o] = advdecMap[hh]
            pass

    block1["ADV/DEC LATEST"] = advDecLast5



    deliv = dict()

    for x in res["HIGH DELIVERY"]["response"]:
        if(int(x[0])>65):
            deliv[x[1]] = x[0]

    block1["HIGH DELIVERY"] = deliv


    high  = dict()
    volBurst10 = dict()
    volBurst15 = dict()

    #now calculate 52 High and vol burst.

    for x in res["COMPLETE_DETAIL"]:
        isNearHigh = float(res["COMPLETE_DETAIL"][x]["nearWKH"])
        if(isNearHigh<5):
            #this needs to be added.
            high[x] = str("{:.2f}".format(isNearHigh))

        try:
            if(int(res["COMPLETE_DETAIL"][x]["totalTradedVolume"]) > int(res["COMPLETE_DETAIL"][x]["PASTPATTERN"]["avv10"])*1.5):
                volBurst10[x] = "10 D Vol Burst"
            if(int(res["COMPLETE_DETAIL"][x]["totalTradedVolume"]) > int(res["COMPLETE_DETAIL"][x]["PASTPATTERN"]["avv15"])*1.5):
                volBurst15[x] = "15 D Vol Burst"

        except:
            pass

    block1["52WHigh"] = high 
    block1["VOLUME BURST 10D"] = volBurst10
    block1["VOLUME BURST 15D"] = volBurst15



    #fetch latest news links. 

    urlForNews = "https://newsapi.org/v2/top-headlines/?country=in&apiKey=165bd184f8fc450cba30ccac8597842a&category=business&pageSize=100"
    x = requests.get(urlForNews,params={})

    res = json.loads(x.text)

    block1["NEWS"] = res


    return JsonResponse(block1)
    """

    the sample looks like 
        {
        "allData": {
            "CBOE Volatility Index (CFD)": {
                "PRICE": "29.73",
                "HIGH": "32.31",
                "LOW": "28.44",
                "CHANGE": "-6.98%"
            },
            "Nifty Bank": {
                "PRICE": "37,982.10",
                "HIGH": "38,147.65",
                "LOW": "37,012.25",
                "CHANGE": "+0.73%"
            },
            "Nifty 50 Futures (Singapore)": {
                "PRICE": "17,108.50",
                "HIGH": "17,295.00",
                "LOW": "16,741.50",
                "CHANGE": "-0.65%"
            },
            "Dow Jones Futures": {
                "PRICE": "34,545.00",
                "HIGH": "34,658.00",
                "LOW": "33,532.00",
                "CHANGE": "+1.44%"
            },
            "Dow Jones Composite": {
                "PRICE": "11,587.2",
                "HIGH": "11,640.2",
                "LOW": "11,477.1",
                "CHANGE": "+1.31%"
            },
            "NASDAQ Composite": {
                "PRICE": "13,663.1",
                "HIGH": "13,765.9",
                "LOW": "13,558.2",
                "CHANGE": "+0.89%"
            },
            "S&P 500 (CFD)": {
                "PRICE": "4,401.13",
                "HIGH": "4,429.39",
                "LOW": "4,373.79",
                "CHANGE": "+1.18%"
            },
            "Nasdaq 100 Futures": {
                "PRICE": "14,297.75",
                "HIGH": "14,409.25",
                "LOW": "13,844.50",
                "CHANGE": "+0.98%"
            },
            "Gold Futures (CFD)": {
                "PRICE": "1,796.50",
                "HIGH": "1,821.45",
                "LOW": "1,794.65",
                "CHANGE": "-1.81%"
            },
            "Nifty 50 Futures (CFD)": {
                "PRICE": "17,203.75",
                "HIGH": "17,227.75",
                "LOW": "16,861.20",
                "CHANGE": "-0.34%"
            },
            "India VIX": {
                "PRICE": "21.0650",
                "HIGH": "23.8675",
                "LOW": "20.4425",
                "CHANGE": "-1.37%"
            },
            "FTSE 350 Software & Computer Services": {
                "PRICE": "1,911.64",
                "HIGH": "1,923.14",
                "LOW": "1,889.98",
                "CHANGE": "-0.60%"
            },
            "FTSE 350 Financial Services": {
                "PRICE": "11,618.73",
                "HIGH": "11,708.14",
                "LOW": "11,498.46",
                "CHANGE": "-0.30%"
            },
            "Nifty Next 50": {
                "PRICE": "40,299.30",
                "HIGH": "40,671.75",
                "LOW": "39,909.45",
                "CHANGE": "-1.71%"
            },
            "Nasdaq 100": {
                "PRICE": "14,312.28",
                "HIGH": "14,419.45",
                "LOW": "14,202.21",
                "CHANGE": "+0.98%"
            },
            "Nifty Auto": {
                "PRICE": "11,561.60",
                "HIGH": "11,654.30",
                "LOW": "11,296.90",
                "CHANGE": "+0.34%"
            },
            "BSE Sensex 30": {
                "PRICE": "57,276.94",
                "HIGH": "57,508.61",
                "LOW": "56,439.36",
                "CHANGE": "-1.00%"
            },
            "Nifty 50": {
                "PRICE": "17,110.15",
                "HIGH": "17,182.50",
                "LOW": "16,866.75",
                "CHANGE": "-0.97%"
            },
            "Nifty Pharma": {
                "PRICE": "12,847.90",
                "HIGH": "12,981.00",
                "LOW": "12,767.40",
                "CHANGE": "-1.87%"
            },
            "Nifty IT": {
                "PRICE": "33,475.05",
                "HIGH": "34,362.85",
                "LOW": "33,251.70",
                "CHANGE": "-3.55%"
            },
            "NYSE Technology": {
                "PRICE": "3,672.60",
                "HIGH": "3,819.59",
                "LOW": "3,629.01",
                "CHANGE": "-0.40%"
            },
            "FTSE 100 (CFD)": {
                "PRICE": "7,564.85",
                "HIGH": "7,596.41",
                "LOW": "7,380.60",
                "CHANGE": "+1.27%"
            },
            "Nifty PSU Bank": {
                "PRICE": "2,907.30",
                "HIGH": "2,914.85",
                "LOW": "2,717.65",
                "CHANGE": "+5.07%"
            },
            "NYSE Financials": {
                "PRICE": "9,939.6",
                "HIGH": "10,131.7",
                "LOW": "9,852.0",
                "CHANGE": "+0.04%"
            },
            "NYSE Healthcare": {
                "PRICE": "22,264.8",
                "HIGH": "22,594.4",
                "LOW": "22,095.9",
                "CHANGE": "-0.46%"
            },
            "FTSE 350 Household Goods": {
                "PRICE": "14,602.61",
                "HIGH": "14,721.53",
                "LOW": "14,442.23",
                "CHANGE": "-0.81%"
            },
            "Dow Jones Consumer Finance": {
                "PRICE": "475.56",
                "HIGH": "477.47",
                "LOW": "468.90",
                "CHANGE": "+0.94%"
            },
            "NYSE Energy": {
                "PRICE": "10,564.5",
                "HIGH": "10,767.4",
                "LOW": "10,474.2",
                "CHANGE": "+0.23%"
            },
            "FTSE 350 Construction & Building Materials": {
                "PRICE": "7,902.40",
                "HIGH": "7,948.92",
                "LOW": "7,717.34",
                "CHANGE": "+0.33%"
            },
            "ICICI Bank Ltd": {
                "PRICE": "794.65",
                "HIGH": "801.50",
                "LOW": "781.05",
                "CHANGE": "-0.87%"
            },
            "Infosys Ltd": {
                "PRICE": "1,678.60",
                "HIGH": "1,709.70",
                "LOW": "1,665.00",
                "CHANGE": "-2.53%"
            },
            "Quess Corp Ltd": {
                "PRICE": "725.00",
                "HIGH": "740.00",
                "LOW": "719.50",
                "CHANGE": "-2.02%"
            },
            "Zee Entertainment Enterprises Ltd.": {
                "PRICE": "283.20",
                "HIGH": "286.55",
                "LOW": "278.55",
                "CHANGE": "-1.94%"
            },
            "Bank of Baroda Ltd": {
                "PRICE": "103.50",
                "HIGH": "104.00",
                "LOW": "96.10",
                "CHANGE": "+5.08%"
            },
            "UltraTech Cement Ltd": {
                "PRICE": "7,109.95",
                "HIGH": "7,150.30",
                "LOW": "6,950.00",
                "CHANGE": "+0.16%"
            },
            "Rashtriya Chemicals and Fertilizers Ltd": {
                "PRICE": "78.20",
                "HIGH": "79.00",
                "LOW": "76.70",
                "CHANGE": "-0.32%"
            },
            "United Breweries Ltd. (BSE)": {
                "PRICE": "1,515.00",
                "HIGH": "1,556.00",
                "LOW": "1,494.20",
                "CHANGE": "-2.76%"
            },
            "Interglobe Aviation Ltd": {
                "PRICE": "1,862.60",
                "HIGH": "1,935.00",
                "LOW": "1,838.00",
                "CHANGE": "-5.29%"
            },
            "Aditya Birla Fashion and Retail Ltd": {
                "PRICE": "284.30",
                "HIGH": "294.50",
                "LOW": "279.60",
                "CHANGE": "-1.78%"
            },
            "Parag Milk Foods Ltd": {
                "PRICE": "113.15",
                "HIGH": "115.50",
                "LOW": "112.00",
                "CHANGE": "-1.22%"
            },
            "Sonata Software Ltd": {
                "PRICE": "803.95",
                "HIGH": "818.30",
                "LOW": "793.50",
                "CHANGE": "-1.55%"
            },
            "Westlife Development Ltd-BO": {
                "PRICE": "487.95",
                "HIGH": "506.40",
                "LOW": "483.30",
                "CHANGE": "-2.96%"
            },
            "Lincoln Pharmaceuticals Ltd": {
                "PRICE": "352.70",
                "HIGH": "353.75",
                "LOW": "347.00",
                "CHANGE": "+0.67%"
            },
            "IndusInd Bank Ltd.": {
                "PRICE": "888.10",
                "HIGH": "893.60",
                "LOW": "861.10",
                "CHANGE": "+0.44%"
            },
            "Reliance Industries Ltd": {
                "PRICE": "2,338.10",
                "HIGH": "2,356.10",
                "LOW": "2,311.05",
                "CHANGE": "-1.48%"
            },
            "ITC Ltd": {
                "PRICE": "214.60",
                "HIGH": "215.50",
                "LOW": "211.10",
                "CHANGE": "+0.14%"
            },
            "Unitech Ltd.": {
                "PRICE": "3.200",
                "HIGH": "3.200",
                "LOW": "3.100",
                "CHANGE": "-1.54%"
            },
            "SBI Cards and Payment Services Ltd": {
                "PRICE": "842.10",
                "HIGH": "850.20",
                "LOW": "826.55",
                "CHANGE": "-0.93%"
            },
            "Larsen & Toubro Ltd": {
                "PRICE": "1,910.85",
                "HIGH": "1,922.00",
                "LOW": "1,867.00",
                "CHANGE": "-0.75%"
            },
            "NBCC India Ltd (BSE)": {
                "PRICE": "45.75",
                "HIGH": "46.55",
                "LOW": "45.10",
                "CHANGE": "-0.97%"
            },
            "HDFC Bank Ltd": {
                "PRICE": "1,474.95",
                "HIGH": "1,485.00",
                "LOW": "1,435.00",
                "CHANGE": "-0.88%"
            },
            "Persistent Systems Ltd": {
                "PRICE": "4,066.80",
                "HIGH": "4,160.05",
                "LOW": "3,993.60",
                "CHANGE": "-1.86%"
            },
            "NCC Ltd": {
                "PRICE": "71.20",
                "HIGH": "72.50",
                "LOW": "68.55",
                "CHANGE": "+2.67%"
            },
            "Indus Towers Ltd (BSE)": {
                "PRICE": "250.00",
                "HIGH": "255.00",
                "LOW": "245.00",
                "CHANGE": "-1.40%"
            },
            "NMDC Ltd": {
                "PRICE": "134.85",
                "HIGH": "136.55",
                "LOW": "132.80",
                "CHANGE": "-0.59%"
            },
            "Future Retail Ltd": {
                "PRICE": "48.20",
                "HIGH": "49.45",
                "LOW": "47.00",
                "CHANGE": "-1.33%"
            }
        },
        "nameDict": {
            "CBOE VIX": "CBOE Volatility Index (CFD)",
            "NIFTY 50": "Nifty 50",
            "Nasdaq 100": "Nasdaq 100",
            "India VIX": "India VIX",
            "SGX NIFTY": "Nifty 50 Futures (Singapore)",
            "Dow Jones": "Dow Jones Futures",
            "Nifty Bank": "Nifty Bank",
            "Gold": "Gold Futures (CFD)",
            "ICICI Bank": "ICICI Bank Ltd",
            "Infosys": "Infosys Ltd",
            "Reliance": "Reliance Industries Ltd",
            "HDFC Bank": "HDFC Bank Ltd"
        },
        "derivativeData": {
            "symbolName": "NIFTY",
            "date": "27-Jan-2022 15:30:00",
            "PCR_OI": 0.89,
            "PCR_VO": 0.84,
            "PCR_COI": {
                "PUT COI": 325937.0,
                "CALL COI": 257327.0
            },
            "ITM_PCR_COI": {
                "ITM CALL COI": 144450.0,
                "ITM PUT COI": -100923.0
            },
            "MAX_PAIN": 17100.0,
            "MAX_PAIN_CURR": null,
            "MAX_PAIN2": 17050.0,
            "MAX_PAIN_CURR2": null,
            "MAX_PAIN_COI": null,
            "IV": {},
            "supports": {
                "S1": 16500.0,
                "S2": 16000.0,
                "S3": 16800.0
            },
            "resistance": {
                "R1": 19000.0,
                "R2": 17400.0,
                "R3": 18000.0
            },
            "strengthValues": {
                "S1": null,
                "S2": null,
                "S3": null,
                "R1": null,
                "R2": null,
                "R3": null
            },
            "maxTradedStrike_CALL": {
                "1": 17100.0,
                "2": 17000.0,
                "3": 17200.0
            },
            "maxTradedStrike_PUT": {
                "1": 17000.0,
                "2": 16900.0,
                "3": 17100.0
            },
            "newlyAddedCOISupport": {
                "1": 17100.0,
                "2": 16600.0,
                "3": 15100.0
            },
            "newlyAddedCOIResistance": {
                "1": 17400.0,
                "2": 17100.0,
                "3": 17150.0
            },
            "pChangeInOI": "13.9",
            "OLHC": {
                "OPEN": 16995,
                "HIGH": 17174,
                "LOW": 16862
            },
            "lotSize": 50,
            "totalMarketWideOIPercent": null,
            "pChange": "-1.0",
            "traded": "532738",
            "currentPrice": 17110.15,
            "totalOI": 4956252.5,
            "pChaneInOI_CURR_SERIES": "48.57",
            "ChaneInOI_CURR_SERIES": "67140.0"
        },
        "participantData_Cash": {
            "DII **": {
                "category": "DII **",
                "date": "27-Jan-2022",
                "buyValue": "10727.48",
                "sellValue": "7846.16",
                "netValue": "2881.32"
            },
            "FII/FPI *": {
                "category": "FII/FPI *",
                "date": "27-Jan-2022",
                "buyValue": "11417.36",
                "sellValue": "17684.11",
                "netValue": "-6266.75"
            },
            "DATE": "27-Jan-2022"
        },
        "participantData_Fut": {
            "Client": {
                "Client Type": "Client",
                "Future Index Long": "199156",
                "Future Index Short": "130564",
                "Future Stock Long": "1574513",
                "Future Stock Short": "152114",
                "Option Index Call Long": "882008",
                "Option Index Put Long": "730331",
                "Option Index Call Short": "868853",
                "Option Index Put Short": "1020737",
                "Option Stock Call Long": "512154",
                "Option Stock Put Long": "174037",
                "Option Stock Call Short": "331344",
                "Option Stock Put Short": "279342",
                "Total Long Contracts": "4072199",
                "Total Short Contracts": "2782954"
            },
            "DII": {
                "Client Type": "DII",
                "Future Index Long": "17362",
                "Future Index Short": "61433",
                "Future Stock Long": "31217",
                "Future Stock Short": "1661459",
                "Option Index Call Long": "819",
                "Option Index Put Long": "29299",
                "Option Index Call Short": "0",
                "Option Index Put Short": "0",
                "Option Stock Call Long": "266",
                "Option Stock Put Long": "0",
                "Option Stock Call Short": "18827",
                "Option Stock Put Short": "0",
                "Total Long Contracts": "78963",
                "Total Short Contracts": "1741719"
            },
            "FII": {
                "Client Type": "FII",
                "Future Index Long": "42913",
                "Future Index Short": "86419",
                "Future Stock Long": "914167",
                "Future Stock Short": "903984",
                "Option Index Call Long": "239128",
                "Option Index Put Long": "359235",
                "Option Index Call Short": "179011",
                "Option Index Put Short": "121986",
                "Option Stock Call Long": "29690",
                "Option Stock Put Long": "28773",
                "Option Stock Call Short": "44186",
                "Option Stock Put Short": "27655",
                "Total Long Contracts": "1613905",
                "Total Short Contracts": "1363241"
            },
            "Pro": {
                "Client Type": "Pro",
                "Future Index Long": "38892",
                "Future Index Short": "19907",
                "Future Stock Long": "271263",
                "Future Stock Short": "73603",
                "Option Index Call Long": "307943",
                "Option Index Put Long": "335087",
                "Option Index Call Short": "382033",
                "Option Index Put Short": "311228",
                "Option Stock Call Long": "74244",
                "Option Stock Put Long": "164879",
                "Option Stock Call Short": "221997",
                "Option Stock Put Short": "60692",
                "Total Long Contracts": "1192307",
                "Total Short Contracts": "1069460"
            },
            "DATE": "20220127"
        }
    }"""

from django.shortcuts import render
from django.http import JsonResponse
import requests 
import json
import os

#This file is a part of fetchAnalysis app of Deleveries Server for Trading Console

derivativeData = dict()
listOfFuturesSymbol = None
optionChainDBLocation = "/home/pi/Feynman-Server/DATA/"

FOsymbolFiles = "/home/pi/Feynman-Server/DATA/Analysis/"
optionChainSymbols = None

def getList(dict): 
    lis = [] 
    for key in dict.keys(): 
        lis.append(key) 
          
    return lis

def preloadReqData():
	global listOfFuturesSymbol
	if(listOfFuturesSymbol == None):
		listOfFuturesSymbol = getList(loadScriptFiles("/home/pi/Feynman-Server/staticContentHelper/MW-SECURITIES-IN-F&O-13-Sep-2020.csv"))


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

def updateData(request):
	preloadReqData()
	return JsonResponse(dict())


def optionChain(request):

	symbol = "None"

	response = dict()
	if(listOfFuturesSymbol == None):
		preloadReqData()
		
	for x in listOfFuturesSymbol:
		response[x] = 1

	return JsonResponse(response)

def getSymbolDerivativeData(request):

    symbolName = request.GET["SYMBOL"]
    analysisFileName = optionChainDBLocation+"/Analysis/"+symbolName
    analysisFileName = open(analysisFileName)
    data = analysisFileName.read()
    analysisFileName.close()

    data = json.loads(data)

    #TODO add one more attribute to get how many data points.
    #defaults to all.


    return JsonResponse(data)

def getSymbolList(request):
    global FOsymbolFiles
    global optionChainSymbols

    #to get this list we will read the content of the file optionChainDBLocation+"/Analysis/
    #and fetch the file names.

    #this data will not change much at all so set it as global param and if its not null  no need to reparse.
    if(optionChainSymbols==None):
        optionChainSymbols =  os.listdir(FOsymbolFiles)

    symbols = dict()
    symbols["SYMBOLS"] = optionChainSymbols
    
    return JsonResponse(symbols)



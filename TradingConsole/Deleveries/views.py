from django.shortcuts import render
from django.http import HttpResponse
import sys
from time import localtime, strftime

sys.path.append("/home/pi/DjangoServer/TradingConsole/Deleveries/")
#import entirePriceMovementDataDaily

#this is the views for the Deleveries App of Trading console
#main app responsible for generating the root(For now) HTML file

def index(request):
	colNames = ["Symbol","Name","Percent Deliverable","Current Price","P Change","Day Vol/min ","3 days vol/min"]

	
	#allSymbolData_highest,allSymbolData_lowest,date = entirePriceMovementDataDaily.deliverablePattern(None)

	#print(allSymbolData_highest)
	
	#print(colNames)
	#fetch cuurent time if its a premarket timing return the relevant file.
	tm = strftime("%H:%M:%w", localtime()).split(":")
	#print(tm)
	hr = int(tm[0])
	mm = int(tm[1])
	day = int(tm[2])

	preopenOverride = False

	try:
		preopenOverride = request.GET["PREOPEN"]
		preopenOverride = True
	except:
		pass

	print(">>>>",hr,mm,day)

	if((hr==9 and mm>00 and mm<15 and day>=1 and day<=5) or preopenOverride):
		colNames = ["Symbol","Name","Percent Deliverable","Current Price","P Change","totalTradedVolume","Buy/Sell","Vol Past 3 days/min"]
		return render(request, 'PreMarket.html', {'colNames': colNames, 'colContent': allSymbolData_highest,'colContent_lowest':allSymbolData_lowest,'date':date})
	else:
		return render(request, 'Deliveries.html', {'colNames': colNames, 'colContent': allSymbolData_highest,'colContent_lowest':allSymbolData_lowest,'date':date})

def fetchPriceInfo(request):
	return "NULL"
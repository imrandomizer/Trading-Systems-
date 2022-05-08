from nsetools import Nse
nse = Nse()

data = nse.downloadUrlNewSite("https://www.nseindia.com/api/master-quote").split(",")

symbolFileName = "/home/pi/DjangoServer/staticContentHelper/FOSYMBOLS"


lisOfSymbol = ["NIFTY","BANKNIFTY"]

lisOfSymbolToIgnore = ["NIFTYIT"]

switch =False

for x in data:
	symbol = x
	symbol = symbol.replace("\"","")
	symbol = symbol.replace("[","")
	symbol = symbol.replace("]","")

	lisOfSymbol.append(symbol)


file = open(symbolFileName,"w")

for x in lisOfSymbol:
	file.write(x+"\n")

file.close()

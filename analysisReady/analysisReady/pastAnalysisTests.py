import pastAnalysis

pastAnalysisObj = pastAnalysis.fetchHistoricalData()
s = pastAnalysis.pastDataStructure(pastAnalysisObj.getListOfFilesToParse())

#print(structure.collectedData)

symbolLis = []

for x in s.collectedData:
	symbolLis.append(x)

computedPatterns = dict()

for x in symbolLis:
	#if(x == "VSTIND" or x=="INFY"):
	if(True):
		
		computedPatterns[x] = pastAnalysis.findPatternsFromCollectedData(x,s.collectedData)

symbolLis = ["INFY","ZEEL","TRENT","TATAMOTORS","SBICARD","MINDTREE","HEXAWARE","CENTURYPLY","BATAINDIA","ADANIPORTS","ASIANPAINT","BAJAJFINSV","BAJFINANCE","BPCL","CIPLA","DRREDDY","GRASIM","HCLTECH","INDUSINDBK","INFRATEL","IOC","SBIN","SHREECEM","TATAMOTORS","TATASTEEL","TITAN","ULTRACEMCO"]

for x in symbolLis:
	patt = computedPatterns[x]
	strs = ""
	if(patt.dogi_b == True):strs += "\tDOJI PATTERN \n"
	if(patt.bullish_harami == True):strs += "\tBULLISH HARAMI PATTERN \n"
	if(patt.bullish_hanging_man == True): strs += "\tbullish_hanging_man pattern \n"
	if(patt.hanging_man == True): strs += "\thanging_man pattern \n"
	if(patt.bearish_harami == True): strs += "\tbearish_harami pattern \n"
	if(patt.gravestone_doji == True): strs += "\tgravestone_doji pattern \n"
	if(patt.dark_cloud_cover == True): strs += "\tdark_cloud_cover pattern \n"
	if(patt.doji_star == True): strs += "\tdoji_star pattern \n"
	if(patt.dragonfly_doji == True): strs += "\tdragonfly_doji pattern \n"
	if(patt.bearish_engulfing == True): strs += "\tbearish_engulfing pattern \n"
	if(patt.bullish_engulfing == True): strs += "\tbullish_engulfing pattern \n"
	if(patt.hammer == True): strs += "\thammer pattern \n"
	if(patt.inverted_hammer == True): strs += "\tinverted_hammer pattern \n"
	if(patt.morning_star == True): strs += "\tmorning_star pattern \n"
	if(patt.morning_star_doji == True): strs += "\tmorning_star_doji pattern \n"
	if(patt.piercing_pattern == True): strs += "\tpiercing_pattern pattern \n"
	if(patt.rain_drop == True): strs += "\train_drop pattern \n"
	if(patt.rain_drop_doji == True): strs += "\train_drop_doji pattern \n"
	if(patt.star == True): strs += "\tstar pattern \n"
	if(patt.shooting_star == True): strs += "\tshooting_star pattern \n"

	if(len(strs)>1):
		print("SYMBOL "+x)
		print(strs)


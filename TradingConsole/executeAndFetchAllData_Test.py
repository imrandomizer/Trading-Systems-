import sys

sys.path.append("/home/pi/DjangoServer/TradingConsole/Deleveries/")

import entirePriceMovementDataDaily

allSymbolData_highest,allSymbolData_lowest,date = entirePriceMovementDataDaily.deliverablePattern(None)

print(allSymbolData_highest)

print(allSymbolData_lowest)
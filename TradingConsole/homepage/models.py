from django.db import models

# Create your models here.

#object to handle the existing apps and other obj's in sidebar
class sidebar:
    containers = []
    #first one is for a home page icon
    data = dict()
    #data["Dashboard"] = []
    
    apps = dict()
    apps["Deliveries"] = ["DeliveryPatterns"]
    apps["Stock Analysis"] = ["StockAnalysis"]
    apps["SAST"] = ["SAST"]
    apps["Derivative Data"] = ["DerivativeDataAnalysis"]
    apps["Market Activity"] = ["MarketActivity"]
    apps["Barometer"] = ["Barometer"]
    
        
    data["Apps"] = apps
    
    monitors = dict()
    monitors["Interesting Stocks"] = ["InterestingStocks"]
    monitors["Marked"] = ["Marked"]
    monitors["Triggers"] = ["Triggers"]
    
    
    data["Monitors"] = monitors 
    
    
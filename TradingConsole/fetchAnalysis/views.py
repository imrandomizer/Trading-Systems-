from django.shortcuts import render
from django.http import JsonResponse
import requests 
import json

#This file is a part of fetchAnalysis app of Deleveries Server for Trading Console


def index(request):
	symbol = "None"

	try:
		symbol = request.GET["SYMBOL"]
	except:
		print("NO SYMBOL PROVIDED")
		empty = dict()
		return empty
	
	response = None
	x = requests.get("http://localhost:5000/analysisReady",params={"SYMBOL":symbol})
	response = json.loads(x.text)
	print(response)

	return JsonResponse(response)
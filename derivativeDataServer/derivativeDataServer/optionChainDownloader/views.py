from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

import html
import json
import time
import os
from nsetools import Nse
from time import localtime, strftime 
from datetime import datetime, timedelta


# Create your views here.
def generateOptionChainData
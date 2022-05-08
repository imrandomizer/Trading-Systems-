from urllib.parse import urlencode, quote_plus
from urllib import   request
import urllib.request

from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.parse import urlencode
from http.cookiejar import CookieJar



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

        def printOptionDetail(option):
                print(option.Type)
                print("Strike Price =",option.StrikePrice)
                print("OI           =",option.OI)
                print("COI          =",option.COI)
                print("volume       =",option.volume)
                print("LTP          =",option.LTP)
                print("Net Change   =",option.netChange)

        def fetchDataForStock(symbol):
                #url = "https://www.nseindia.com/api/quote-equity?symbol="+symbol
                url = "http://www.google.com"
                print(url)
                cj = CookieJar()
                opener = build_opener(HTTPCookieProcessor(cj))
                req = urllib.request.urlopen(url,None,executeAndFetchAllData.nse_headers())
                #res = opener.open(req)
                res = byte_adaptor(res).read()
                print(res)
                return res

executeAndFetchAllData.fetchDataForStock("THOMASCOOK")
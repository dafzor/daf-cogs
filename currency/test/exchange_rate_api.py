#!/usr/bin/python3


# needed to fetch current currency exchange
from urllib import request
from urllib.error import HTTPError
from re import search
#import xml.etree.ElementTree as ET

# european bank api returning xml with how much 1€ is in each currency, including dkk
# further documentation in: http://www.ecb.int/stats/exchange/eurofxref/html/index.en.html#dev
api_url = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

# sets a default exchange rate in case we cant get current one 
dkk_exchange = 7.45

# retrive the xml file with current exchange rate content
try:
   response = request.urlopen(api_url)
   
   # good reply, parse
   xml = response.read().decode('utf-8')
   print(xml)
   result = search(r"\s<Cube currency=\'DKK\' rate=\'([0-9]*\.[0-9]*)\'/>", xml)
   dkk_exchange = result.group(1)
   print(result.group(1))

#    xml = ET.fromstring(response.read())
#    print(xml.findall(u'./gesmes:Envelope/Cube/Cube//Cube[@currency="DKK"]', namespaces=xml.nsmap))
   
except HTTPError as e:
  print("Error getting current currency. using fixed one")
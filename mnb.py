import xmltodict
from zeep import Client

client = Client('http://www.mnb.hu/arfolyamok.asmx?wsdl')
# client = Client('http://www.mnb.hu/arfolyamok.asmx?singleWsdl')
result = client.service.GetExchangeRates("2022-11-01","2022-11-12","EUR")

# print(result)
print(xmltodict.parse(result))

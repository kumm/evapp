function test_() {
  const rows = mnb_rates("2022-09-01","2023-01-01", "EUR,USD")
  Logger.log(rows)
}

/**
 * Show MNB exchange rates table.
 * One row per day, one column per currency.
 *
 * @param fromDate from date string in 'YYYY-MM-DD' format
 * @param toDate to date string in 'YYYY-MM-DD' format
 * @param currencies comma separated currencies as string
 *
 * @return Table of mnb exchange rates.
 *        One row per day, one column per currency.
 * @customfunction
 */
function mnb_rates(fromDate, toDate, currencies) {

  const querySoap = function() {
    const soapQuery = `
        <soap12:Envelope
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xmlns:xsd="http://www.w3.org/2001/XMLSchema"
              xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <GetExchangeRates xmlns="http://www.mnb.hu/webservices/">
                <startDate>${fromDate}</startDate>
                <endDate>${toDate}</endDate>
                <currencyNames>${currencies}</currencyNames>
            </GetExchangeRates>
          </soap12:Body>
        </soap12:Envelope>`;
      const url = 'http://www.mnb.hu/arfolyamok.asmx';
      const options = {
        'method' : 'post',
        'contentType': 'application/soap+xml',
        'payload' : soapQuery
      };

      const response = UrlFetchApp.fetch(url, options);
      const soapRespDoc = XmlService.parse(response);
      const result = soapRespDoc.getRootElement().getChildren()[0].getChildren()[0].getChildren()[0].getContent(0)
      const doc = XmlService.parse(result);
      return doc.getRootElement().getChildren()
  }

  const parseResultDoc = function(days) {
    const dayMap = {}
    for (dayNdx in days) {
      const day = days[dayNdx]
      const date = day.getAttribute("date").getValue()
      const rates = day.getChildren()
      const rateMap = {}
      for (rateNdx in rates) {
        const rate = rates[rateNdx]
        const curr = rate.getAttribute('curr').getValue()
        const rateVal = 1.0 * rate.getContent(0).getValue().replace(',', '.')
        rateMap[curr] = rateVal
      }
      dayMap[date] = rateMap
    }
    return dayMap
  }

  const mapToRows = function(dayMap) {
    const currList = currencies.split(',')
    const rows = [['', ...currList]]
    var date = new Date(Date.parse(fromDate))
    var last = {}
    const endDate = Date.parse(toDate)
    while(date<endDate) {
      const dateStr = date.toISOString().split('T')[0]
      const rates = dayMap[dateStr] || last
      row = [dateStr]
      for(c in currList) {
        row.push(rates[currList[c]])
      }
      rows.push(row)
      date.setDate(date.getDate() + 1)
      last = rates
    }
    return rows
  }

  const resultDoc = querySoap()
  const result = parseResultDoc(resultDoc)
  return mapToRows(result)
}


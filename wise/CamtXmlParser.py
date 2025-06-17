import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import dateutil.parser as dateparser

ns = {'ns': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.10'}

class CamtXmlParser:

    def __init__(self, xml_data, tz):
        self.root = ET.fromstring(xml_data)
        self.tz = tz

    def parse_transactions(self):
        transactions = []
        for tx in self.root.findall('.//ns:Ntry', namespaces=ns):
            amt, ccy = self.__parse_amt(tx)
            transaction = {
                'id': tx.findtext('ns:BkTxCd/ns:Prtry/ns:Cd', namespaces=ns),
                'ts': dateparser.isoparse(tx.findtext('ns:BookgDt/ns:DtTm', namespaces=ns)).astimezone(self.tz),
                'amt': amt,
                'ccy': ccy,
                'ref': tx.findtext('ns:NtryRef', '', namespaces=ns),
                'pty': tx.findtext('ns:NtryDtls/ns:TxDtls/ns:RltdPties/ns:Cdtr/ns:Pty/ns:Nm', None, namespaces=ns),
                'inf': tx.findtext('ns:AddtlNtryInf', namespaces=ns),
                # 'xml': ET.tostring(tx, encoding='unicode')
            }
            transactions.append(transaction)

        return transactions

    def parse_balance(self):
        bal_elem = self.root.find(".//ns:Bal/ns:Tp/ns:CdOrPrtry/ns:Cd[.='CLBD']../../..", namespaces=ns)
        return self.__parse_amt(bal_elem)


    @staticmethod
    def __parse_amt(parent_elem: Element):
        amt_elem = parent_elem.find("ns:Amt", namespaces=ns)
        amt = amt_elem.text
        ccy = amt_elem.get('Ccy')
        sgn = '-' if parent_elem.findtext('ns:CdtDbtInd', namespaces=ns) == "DBIT" else ''
        return sgn + amt, ccy

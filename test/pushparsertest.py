from unittest import TestCase

from lxml.etree import tostring
from meresco.xml.pushparser import PushParser


class PushParserTest(TestCase):
    def testFeed(self):
        records = []
        def handleRecord(record):
            records.append(record)

        parser = PushParser(elementPath=["XML", "records", "record"], onResultDo=handleRecord)

        parser.feed("<XML><records><record>")
        parser.feed("aap</record>")

        self.assertEquals(1, len(records))
        self.assertEquals('<record>aap</record>', tostring(records[0]))

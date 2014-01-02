## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2013 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Meresco-Xml"
#
# "Meresco-Xml" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco-Xml" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco-Xml"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

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
        self.assertEquals(b'<record>aap</record>', tostring(records[0]))

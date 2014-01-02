## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2012-2014 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012-2013 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
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

from seecr.test import SeecrTestCase

from meresco.xml import namespaces, xpathFirst, xpath
from lxml.etree import XML, _Element


class NamespacesTest(SeecrTestCase):
    def testCopyUpdate(self):
        ns1 = namespaces
        self.assertEquals('http://www.loc.gov/zing/srw/', ns1['srw'])
        ns2 = ns1.copyUpdate({'srw':'SRW', 'newPrefix':'URI'})
        self.assertEquals('http://www.loc.gov/zing/srw/', ns1['srw'])
        self.assertEquals('SRW', ns2['srw'])
        self.assertEquals('URI', ns2['newPrefix'])
        self.assertFalse('newPrefix' in ns1)
        self.assertTrue(hasattr(ns2, 'xpath'))

    def testSelect(self):
        ns1 = namespaces
        self.assertEquals('http://www.loc.gov/zing/srw/', ns1['srw'])
        self.assertEquals('http://purl.org/dc/elements/1.1/', ns1['dc'])
        ns2 = ns1.select('dc', 'oai')
        self.assertEquals('http://www.loc.gov/zing/srw/', ns1['srw'])
        self.assertEquals('http://purl.org/dc/elements/1.1/', ns2['dc'])
        self.assertEquals('http://www.openarchives.org/OAI/2.0/', ns2['oai'])
        self.assertFalse('srw' in ns2)
        self.assertTrue(hasattr(ns2, 'xpath'))

    def testCurieToTag(self):
        self.assertEquals('{http://www.loc.gov/zing/srw/}record', namespaces.expandNsTag('srw:record'))
        self.assertEquals('{http://purl.org/dc/elements/1.1/}title', namespaces.curieToTag('dc:title'))

    def testExpandNs_backwardsCompatible(self):
        self.assertEquals('{http://purl.org/dc/elements/1.1/}title', namespaces.expandNs('dc:title'))

    def testExpandNsTag_backwardsCompatible(self):
        self.assertEquals('{http://purl.org/dc/elements/1.1/}title', namespaces.expandNsTag('dc:title'))

    def testCurieToUri(self):
        self.assertEquals('http://www.loc.gov/zing/srw/record', namespaces.curieToUri('srw:record'))
        self.assertEquals('http://purl.org/dc/elements/1.1/title', namespaces.curieToUri('dc:title'))
        self.assertEquals('http://www.w3.org/1999/02/22-rdf-syntax-ns#type', namespaces.curieToUri('rdf:type'))

    def testExpandNsUri_backwardsCompatible(self):
        self.assertEquals('http://purl.org/dc/elements/1.1/title', namespaces.expandNsUri('dc:title'))

    def testTagToCurie(self):
        self.assertEquals('dc:title', namespaces.tagToCurie('{http://purl.org/dc/elements/1.1/}title'))
        self.assertRaises(KeyError, namespaces.tagToCurie, '{unknown}tag')
        self.assertRaises(ValueError, namespaces.tagToCurie, 'no-uri-in-tag')
        self.assertEquals('srw:records', namespaces.tagToCurie(namespaces.expandNsTag('srw:records')))
        ns2 = namespaces.copyUpdate({'new':'uri:new'})
        self.assertEquals('new:tag', ns2.tagToCurie('{uri:new}tag'))

    def testPrefixedTag_backwardsCompatible(self):
        self.assertEquals('dc:title', namespaces.prefixedTag('{http://purl.org/dc/elements/1.1/}title'))

    def testNotAllDictMethodsSupported(self):
        def deleteNsItem():
            del namespaces['dc']
        self.assertRaises(TypeError, deleteNsItem)
        def setNsItem():
            namespaces['new'] = 'uri'
        self.assertRaises(TypeError, setNsItem)
        self.assertRaises(TypeError, lambda: namespaces.update({'new':'uri'}))
        self.assertRaises(TypeError, lambda: namespaces.setdefault('key', 'value'))

    def testFormatting(self):
        self.assertEquals('Uri=http://purl.org/dc/elements/1.1/', 'Uri=%(dc)s' % namespaces)

    def testXmlns(self):
        self.assertEquals('xmlns:dc="http://purl.org/dc/elements/1.1/"', namespaces['xmlns_dc'])
        self.assertEquals('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">', '<rdf:RDF %(xmlns_rdf)s>' % namespaces)
        self.assertFalse('xmlns_rdf' in list(namespaces.keys()))

    def testNsToPrefix(self):
        self.assertEqual('dc', namespaces.nsToPrefix(namespaces.dc))
        self.assertEqual(None, namespaces.nsToPrefix('asdfasdf'))

    def testUriToCurie(self):
        self.assertEqual('dcterms:fluffy', namespaces.uriToCurie(uri='http://purl.org/dc/terms/fluffy'))

    def testXpath(self):
        self.assertEqual(_Element, type(xpath(ANY_XML, "/root/sub")[0]))
        self.assertEqual(str, type(xpath(ANY_XML, "/root/sub1/text()")[0]))
        self.assertEqual(["text"], xpath(ANY_XML, "/root/sub1/text()"))

    def testXpathFirst(self):
        self.assertEqual(None, xpathFirst(ANY_XML, "/root/not_found"))
        self.assertEqual(_Element, type(xpathFirst(ANY_XML, "/root/sub")))
        self.assertEqual(str, type(xpathFirst(ANY_XML, "/root/sub1/text()")))
        self.assertEqual("text", xpathFirst(ANY_XML, "/root/sub1/text()"))

    def testCurieToTagSpeed(self):
        from time import time
        t = 0
        for i in xrange(20000):
            t0 = time()
            namespaces.curieToTag('dc:%s' % (i / 200))
            t += (time() - t0)
        self.assertTiming(0.025, t, 0.035)

ANY_XML = XML('''\
<root>
  <sub>
    <stuff/>
  </sub>
  <sub1>text</sub1>
</root>''')

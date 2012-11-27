## begin license ##
# 
# "Meresco-Xml" is a set of components and tools for handling xml data objects. 
# 
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
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

from meresco.xml import namespaces

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

    def testExpandNs(self):
        self.assertEquals('{http://www.loc.gov/zing/srw/}record', namespaces.expandNs('srw:record'))
        self.assertEquals('{http://purl.org/dc/elements/1.1/}title', namespaces.expandNs('dc:title'))

    def testExpandNsUri(self):
        self.assertEquals('http://www.loc.gov/zing/srw/record', namespaces.expandNsUri('srw:record'))
        self.assertEquals('http://purl.org/dc/elements/1.1/title', namespaces.expandNsUri('dc:title'))
        self.assertEquals('http://www.w3.org/1999/02/22-rdf-syntax-ns#type', namespaces.expandNsUri('rdf:type'))



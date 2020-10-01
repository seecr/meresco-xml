## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2011, 2017, 2020 Seecr (Seek You Too B.V.) http://seecr.nl
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

from meresco.xml.utils import sortRootTagAttrib, createElement, createSubElement
from meresco.xml import namespaces

class UtilsTest(SeecrTestCase):
    def testSortRootTagAttrib(self):
        input = """<a:root xmlns:b="namespace B" xmlns:a="namespace A">
    <b:sub>tag</b:sub>
</a:root>"""
        self.assertEqual("""<a:root xmlns:a="namespace A" xmlns:b="namespace B">
    <b:sub>tag</b:sub>
</a:root>""", sortRootTagAttrib(input))

    def testCreateElement(self):
        dc = createElement('oai_dc:dc', nsmap=namespaces.select('oai_dc', 'dc'))
        createSubElement(dc, 'dc:title', text='<title>')
        self.assertXmlEquals('<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>&lt;title&gt;</dc:title></oai_dc:dc>', dc)

        self.assertXmlEquals('<dc:iets xmlns:dc="http://purl.org/dc/elements/1.1/" key="&lt;&quot;value&quot;>">te"xt</dc:iets>', createElement('dc:iets', attrib={'key':'<"value">'}, text='te"xt', nsmap=namespaces.select('dc')))

    def testFixUnwantedChars(self):
        dc = createElement('dc:title', nsmap=namespaces.select('dc'), text='\x0b\x1e\x1f\x01Text')
        self.assertXmlEquals('<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Text</dc:title>', dc)
        dc = createElement('dc:title', nsmap=namespaces.select('dc'), attrib={'key':'\x0b\x1e\x1f\x01Text'})
        self.assertXmlEquals('<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/" key="Text"/>', dc)

        

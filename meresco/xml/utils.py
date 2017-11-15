## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2011, 2014, 2017 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
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

from lxml.etree import Element
from meresco.xml.namespaces import namespaces as _namespaces

def sortRootTagAttrib(xmlString):
    root, remainder = xmlString.split(">", 1)
    rootAttribs = root[root.find(' '):].strip()

    def nextAtrrib(text):
        pos = 0
        while True:
            newPos = text.find('"', pos)
            if newPos == -1:
                return
            newPos = text.find('"', newPos+1)
            if newPos == -1:
                return
            yield text[pos:newPos + 1]
            pos = newPos + 2

    newXmlString = root[:root.find(' ') + 1]
    newXmlString += ' '.join(sorted(list(nextAtrrib(rootAttribs))))
    newXmlString += '>'
    newXmlString += remainder
    return newXmlString

def createSubElement(parent, name, **kwargs):
    element = createElement(name, **kwargs)
    parent.append(element)
    return element

def createElement(name, text=None, attrib=None, nsmap=None, namespaces=_namespaces):
    element = Element(namespaces.curieToTag(name), nsmap=nsmap)
    if text is not None:
        element.text = removeControlCharacters(text)
    if attrib:
        for k,v in attrib.items():
            attr = namespaces.curieToTag(k) if ':' in k else k
            element.attrib[attr] = removeControlCharacters(v)
    return element

_controlchars_replacement = {i:None for i in range(ord(' ')) if i not in [ord('\r'), ord('\t'), ord('\n')]}
def removeControlCharacters(aString):
    return unicode(aString).translate(_controlchars_replacement)


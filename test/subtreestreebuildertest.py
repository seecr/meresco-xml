## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2013, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
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
from meresco.xml.subtreestreebuilder import SubTreesTreeBuilder, SimpleSaxFileParser

from lxml.etree import parse, XMLParser, tostring

from math import ceil
from io import StringIO


namespaces = namespaces.copyUpdate({
    'def_': 'u:ri/default#',
    'newdef_': 'u:ri/newdefault#',
    'other_': 'u:ri/other#',
    'pre_': 'u:ri/prefixed#',
})
xpath = namespaces.xpath
xpathFirst = namespaces.xpathFirst


# lxml / LibXML implementation detail; data feed()'ed can be buffered or otherwise unprocessed, until close() is called on the feedparsing interface.
# This will result in 0...n (start|comment|data|pi|end)-calls and
# then a close-call on the TreeBuilder-interface.
#
# Therefor, getSubtrees() *must* be called after a close() on the XMLParser.

class SubTreesTreeBuilderTest(SeecrTestCase):
    def testParseAndProcessSimpleFile(self):
        builder = SubTreesTreeBuilder(elementPath=['records', 'record'])
        result, loops = parseIncrementallyBy20(builder=builder, inputXml=XML)

        self.assertEqual(ceil(len(XML) / 20.0), loops)
        self.assertEqual(3, len(result))
        self.assertEqual(['record']*3, [r[0] for r in result])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML), '/records/record[1]'),
            result[0][1])
        self.assertEqualsLxml(xpathFirst(parseString(XML), '/records/record[2]'), result[1][1])
        self.assertEqualsLxml(xpathFirst(parseString(XML), '/records/record[3]'), result[2][1])

    def testParseDifferentStructure(self):
        builder = SubTreesTreeBuilder(buildFor={
            'sub': lambda stack: [d['tag'] for d in stack] == ['root', 'sub']
        })
        result, loops = parseIncrementallyBy20(builder=builder, inputXml=XML2)

        self.assertEqual(2, len(result))
        self.assertEqual(['sub']*2, [r[0] for r in result])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML2), '/root/sub[1]'),
            result[0][1])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML2), '/root/sub[2]'),
            result[1][1])

    def testMultipleBuildForFunctionsWithNS(self):
        builder = SubTreesTreeBuilder(buildFor={
            'records': lambda stack: [d['tag'] for d in stack] == ['records'],
            'record': lambda stack: [d['tag'] for d in stack] == ['records', 'record'],
            'default-ns': lambda stack: [d['tag'] for d in stack] == ['records', 'record', '{u:ri/default#}subtag.NS'],
            'prefixed': lambda stack: [d['tag'] for d in stack] == ['records', 'record', '{u:ri/prefixed#}fixed'],
        })
        result, loops = parseIncrementallyBy20(builder=builder, inputXml=XML)

        self.assertEqual(['record', 'record', 'default-ns', 'prefixed', 'record', 'records'], [r[0] for r in result])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML), '/records/record[1]'),
            result[0][1])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML), '/records/record[2]'),
            result[1][1])
        self.assertEqualsLxml(
                xpathFirst(parseString(XML), '/records/record[3]/def_:subtag.NS'),
            result[2][1])
        self.assertEqualsLxml(
                xpathFirst(parseString(XML), '/records/record[3]/pre_:fixed'),
            result[3][1])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML), '/records/record[3]'),
            result[4][1])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML), '/records'),
            result[5][1])

    def testIdentityTransformWithNS(self):
        builder = SubTreesTreeBuilder(buildFor={
            'one': lambda stack: [d['tag'] for d in stack] == ['{u:ri/default#}root'],
        })
        parser = XMLParser(target=builder)
        parser.feed(XML_NS)
        parser.close()

        subtrees = [t for t in builder.getSubtrees()]
        self.assertEqual(1, len(subtrees))

        id, lxml = subtrees[0]
        self.assertEqual('one', id)
        self.assertEqualsLxml(parseString(XML_NS), lxml)

    def testNamespacePrefixesAndDefaultsPreserved(self):
        builder = SubTreesTreeBuilder(buildFor={
            'sub_def': lambda stack: [d['tag'] for d in stack] == ['{u:ri/default#}root', '{u:ri/default#}subInDefaultNS'],
            'prefixed': lambda stack: [d['tag'] for d in stack] == ['{u:ri/default#}root', '{u:ri/default#}subInDefaultNS', '{u:ri/prefixed#}fixed'],
            'preother': lambda stack: [d['tag'] for d in stack] == ['{u:ri/default#}root', '{u:ri/default#}subInDefaultNS', '{u:ri/other#}other'],
            'preinside': lambda stack: [d['tag'] for d in stack] == ['{u:ri/default#}root', '{u:ri/default#}subInDefaultNS', '{u:ri/other#}other', '{u:ri/other#}inside'],
            'newdefault': lambda stack: [d['tag'] for d in stack] == ['{u:ri/default#}root', '{u:ri/default#}subInDefaultNS', '{u:ri/other#}other', '{u:ri/newdefault#}newdefault'],
            'node': lambda stack: [d['tag'] for d in stack] == ['{u:ri/default#}root', '{u:ri/default#}subInDefaultNS', '{u:ri/other#}other', '{u:ri/newdefault#}newdefault', '{u:ri/newdefault#}node'],
        })
        result, loops = parseIncrementallyBy20(builder=builder, inputXml=XML_NS)

        self.assertEqual(6, len(result))
        self.assertEqual(['prefixed', 'preinside', 'node', 'newdefault', 'preother', 'sub_def'], [r[0] for r in result])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML_NS), '/def_:root/def_:subInDefaultNS/pre_:fixed'),
            result[0][1])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML_NS), '/def_:root/def_:subInDefaultNS/other_:other/other_:inside'),
            result[1][1])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML_NS), '/def_:root/def_:subInDefaultNS/other_:other/newdef_:newdefault/newdef_:node'),
            result[2][1])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML_NS), '/def_:root/def_:subInDefaultNS/other_:other/newdef_:newdefault'),
            result[3][1])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML_NS), '/def_:root/def_:subInDefaultNS/other_:other'),
            result[4][1])
        self.assertEqualsLxml(
            xpathFirst(parseString(XML_NS), '/def_:root/def_:subInDefaultNS'),
            result[5][1])

    def testSimpleSaxFileParser(self):
        xml = StringIO("""<a><b/><b/><c/><b/></a>""")
        result = []
        saxfp = SimpleSaxFileParser(stream=xml, path=['a', 'b'], callback=result.append)
        saxfp.start()

        self.assertEqual(3, len(result))
        self.assertEqual('b', result[0].tag)

    def testOnResult(self):
        trees = []
        def onResult(tree):
            trees.append(tree)
        xml = """<a><b>Dit is een tag in een tag</b></a>"""
        builder = SubTreesTreeBuilder(elementPath=['r', 'a', 'b'], onResult=onResult)
        parser = XMLParser(target=builder)
        parser.feed("<r>")
        parser.feed(xml)
        parser.feed(xml)
        self.assertEqual(2, len(trees))
        self.assertEqual(b'<b>Dit is een tag in een tag</b>', tostring(trees[0]))



def parseIncrementallyBy20(builder, inputXml):
    parser = XMLParser(target=builder)
    xmlStream = StringIO(inputXml)
    result = []
    data = xmlStream.read(20)
    loops = 0
    while data:
        loops += 1
        parser.feed(data)
        for id, subtree in builder.getSubtrees():
            result.append((id, subtree))
        data = xmlStream.read(20)
    retval = parser.close()
    for id, subtree in builder.getSubtrees():
        result.append((id, subtree))
    assert retval is None, 'Errr?'
    assert ceil(len(inputXml) / 20.0) == loops, 'Errr?'
    return result, loops


def parseString(s):
    return parse(StringIO(s))

XML = '''\
<records>
  <record attr="value">
    <!-- comment -->
    <?pi data?>
    <subtag attr="value" xml:lang="en">subtext</subtag>
    text
  </record>
  <record>text</record>
  <record>
    <subtag.NS xmlns='u:ri/default#' />
    <pre:fixed xmlns:pre="u:ri/prefixed#" />
  </record>
</records>'''

XML2 = '''\
<root>
  <sub>
    <stuff/>
  </sub>
  <sub>
    <other/>
  </sub>
</root>'''

XML_NS = '''\
<root xmlns="u:ri/default#" xmlns:pre="u:ri/prefixed#">
  <subInDefaultNS>
    <pre:fixed />
    <pre:other xmlns:pre="u:ri/other#">
        <pre:inside />
        <newdefault xmlns="u:ri/newdefault#">
            <node />
        </newdefault>
    </pre:other>
  </subInDefaultNS>
</root>'''


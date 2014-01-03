## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2005-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2012-2013 Seecr (Seek You Too B.V.) http://seecr.nl
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
from lxml.etree import parse, XMLParser
from meresco.xml.xmlrewrite import XMLRewrite, lxmltostring
from seecr.test import SeecrTestCase
from io import BytesIO
from difflib import unified_diff
from os.path import dirname, abspath

class XMLRewriteTest(SeecrTestCase):

    def assertRewrite(self, rules, newRootTagName, soll, src, defaultNamespace=None, newNsMap={}, schemaLocation={}, sourceNsMap={}):
        rewrite = XMLRewrite(parse(BytesIO(src)), rootTagName=newRootTagName, defaultNameSpace=defaultNamespace,
                newNsMap=newNsMap, schemaLocation=schemaLocation, rules=rules, sourceNsMap=sourceNsMap)
        rewrite.applyRules()
        istText = rewrite.toString()
        s = parse(BytesIO(soll), XMLParser(remove_blank_text=True))
        sollText = lxmltostring(s, pretty_print=True).decode('UTF-8')
        diffs = list(unified_diff(sollText.split('\n'), istText.split('\n'), fromfile='soll', tofile='ist', lineterm=''))
        self.assertFalse(diffs, '\n' + '\n'.join(diffs))

    def testOneValue(self):
        # newTag, oldTag, valuesWithInOldTag, template
        rules = [('.', 'b', ('.',), '<y>%s</y>')]
        src = b'<a><b>aap</b></a>'
        dst = b'<z><y>aap</y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testOneValueWithNamespace(self):
        # newTag, oldTag, valuesWithInOldTag, template
        rules = [('.', 'b', ('.',), '<y>%s</y>')]
        src = b'<a><b>aap</b></a>'
        dst = b'<a:z xmlns:a="nsA"><y>aap</y></a:z>'
        self.assertRewrite(rules, 'a:z', dst, src, newNsMap={'a':'nsA'})

    def testEscaping(self):
        # newTag, oldTag, valuesWithInOldTag, template
        rules = [('y', 'b', ('c',), '<x>%s</x>')]
        src = b'<a><b><c>a&amp;b</c></b></a>'
        dst = b'<z><y><x>a&amp;b</x></y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testWithTwoValues(self):
        rules = [('.', '.', ('b', 'c'), '<ownTag attr="%s">%s</ownTag>')]
        src = b'<a><b>aap</b><c>noot</c></a>'
        dst = b'<z><ownTag attr="aap">noot</ownTag></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testSubPaths(self):
        rules = [('y', '.', ('b',), '<w>%s</w>')]
        src = b'<a><b>aap</b></a>'
        dst = b'<z><y><w>aap</w></y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testSubPathsInSource(self):
        rules = [('y/x', 'b/c/d', ('e',), '<w>%s</w>')]
        src = b'<a><b><c><d><e>aap</e></d></c></b></a>'
        dst = b'<z><y><x><w>aap</w></x></y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testTwoRules(self):
        rules = [   ('y', 'b', ('.',), '<w>%s</w>'),
                        ('x', 'c', ('.',), '<v>%s</v>')]
        src = b'<a><b>aap</b><c>noot</c></a>'
        dst = b'<z><y><w>aap</w></y><x><v>noot</v></x></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testMultipleSourceTagsEndUpInSameAmountOfDstTags(self):
        # for each tag 'b' an tag /z/y is generated
        rules = [   ('y', 'b', ('.',), '<w>%s</w>'),
                        ('x', 'c', ('.',), '<v>%s</v>')]
        src = b'<a><b>aap</b><b>mies</b><c>noot</c></a>'
        dst = b'<z><y><w>aap</w></y><y><w>mies</w></y><x><v>noot</v></x></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testIterationOverSubtags(self):
        # for each tag 'b' an tag /z/y is generated
        rules = [   ('y', 'b/c', ('d',), '%s'),
                ]
        src = b'<a><b><c><d>aap</d></c><c><d>mies</d></c></b></a>'
        dst = b'<z><y>aap</y><y>mies</y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testPandQareInSameContext(self):
        rules = [   ('y/p', 'b', ('.',), '%s'),
                    ('y/q', 'c', ('.',), '%s')]
        src = b'<a><b>aap</b><b>mies</b><c>noot</c></a>'
        dst = b'<z><y><p>aap</p><p>mies</p><q>noot</q></y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testNewContentExistsOfTwoXmlNodes(self):
        rules = [ ('y/r', 'b/c', ('.',), '<s>source</s><p>%s</p>'),
                  ('y/t', 'b/d', ('.',), '%s')]
        src = b'<a><b><c>aap</c><d>noot</d></b><b><c>mies</c><d>vuur</d></b></a>'
        dst = b'<z><y><r><s>source</s><p>aap</p></r><t>noot</t></y><y><r><s>source</s><p>mies</p></r><t>vuur</t></y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testPandQareInSameContextNowWithNamespace(self):
        rules = [   ('dst:y/dst:p', 'src:b', ('.',), '%s'),
                    ('dst:y/dst:q', 'src:c', ('.',), '%s')]
        src = b'<a xmlns:src="src"><src:b>aap</src:b><src:b>mies</src:b><src:c>noot</src:c></a>'
        dst = b'<z xmlns:dst="dst"><dst:y><dst:p>aap</dst:p><dst:p>mies</dst:p><dst:q>noot</dst:q></dst:y></z>'
        self.assertRewrite(rules, 'z', dst, src, sourceNsMap={'src':'src'}, newNsMap={'dst':'dst'})

    def testNotAllElementsAreEqual(self):
        rules = [   ('y/p', 'b/c', ('.',), '%s'),
                        ('y/q', 'b/d', ('.',), '%s')]
        src = b'<a><b><c>aap</c></b><b><c>mies</c><d>noot</d></b></a>'
        dst = b'<z><y><p>aap</p></y><y><p>mies</p><q>noot</q></y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testNestedAndRepeatedElementsForPathDir(self):
        rules = [   ('path', 'path', ('source',), '<src>%s</src>'),
                        ('path', 'path', ('dir',), '<directory>%s</directory>')]
        src = b'<a><path><source>A</source><dir>B</dir><dir>C</dir></path>'  \
              b'<path><source>D</source><dir>E</dir><dir>F</dir></path></a>'
        soll = b'<x><path><src>A</src><directory>B</directory><directory>C</directory></path>' \
                        b'<path><src>D</src><directory>E</directory><directory>F</directory></path></x>'
        self.assertRewrite(rules, 'x', soll, src)

    def testNamespaceAndSchema(self):
        #rules = []
        #defaultNamespace = "http://ape"
        #newNsMap = {'xsi': "http://www.w3.org/2001/XMLSchema-instance"}
        #schemaLocation = {"http://ape": "http://ape.xsd"}
        #self.assertRewrite(rules, 'x', '<x xmlns="http://ape" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ape http://ape.xsd"/>', '<a/>', defaultNamespace=defaultNamespace, newNsMap=newNsMap, schemaLocation=schemaLocation)

        #==
        srcNode = parse(BytesIO(b'<a/>'))
        rewrite = XMLRewrite(srcNode, 'x', 'http://ape', rules=[], sourceNsMap={}, schemaLocation={"http://ape": "http://ape.xsd"}, newNsMap={'xsi': "http://www.w3.org/2001/XMLSchema-instance"})
        rewrite.applyRules()
        result = rewrite.toString()
        self.assertTrue('xmlns="http://ape"' in result, result)
        self.assertTrue('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' in result, result)
        self.assertTrue('xsi:schemaLocation="http://ape http://ape.xsd"' in result, result)

    def testXPathNameSpaces(self):
        src = b'<x:a xmlns:x="http://x"><x:b>aap</x:b></x:a>'
        srcNode = parse(BytesIO(src))
        rules = [('p', 'Q:b', ('.',), '%s')]
        rewrite = XMLRewrite(srcNode, 'A', 'http://y', rules=rules, sourceNsMap = {'Q': 'http://x'})
        rewrite.applyRules()
        self.assertEqualsWS('<A xmlns="http://y">\n  <p>aap</p>\n</A>', rewrite.toString())

    def testNamespaceInTagVersusXPath(self):
        src = b'<a><b><c>ape</c></b></a>'
        dst = b'<p xmlns="http://p"><q><r>ape</r></q></p>'
        rules = [('q/r', 'b/c', ('.',), '%s')]
        rewrite = XMLRewrite(parse(BytesIO(src)), 'p', 'http://p', rules=rules)
        rewrite.applyRules()
        self.assertEqualsWS(dst.decode('UTF-8'), rewrite.toString())

    def testProveBugNamespaceProblemInGeneratedTree(self):
        from lxml.etree import Element, SubElement
        root = Element('root', nsmap={None: 'default_namespace'})
        SubElement(root, 'sub1')
        xPathResult = root.xpath('sub1')
        self.assertEqual(1, len(xPathResult))
        xPathResult = root.xpath('Y:sub1', namespaces={'Y': 'default_namespace'})
        self.assertEqual(0, len(xPathResult)) #and that's exactly what the bug is...

    def testXPathWithSlashes(self):
        src = b'<a><b>B1<c><d>aap</d></c></b><b>B2<c><d>noot</d></c></b></a>'
        rules = [('p', 'b[c/d="aap"]', ('.',), '%s')]
        rewrite = XMLRewrite(parse(BytesIO(src)), 'A', rules=rules)
        rewrite.applyRules()
        self.assertEqualsWS('<A>\n  <p>B1</p>\n</A>', rewrite.toString())

    def testDefaultNamespacesInTemplates(self):
        src = b"<a><b>ape</b></a>"
        rules = [('q', 'b', ('.',), '<r>%s</r>')]
        rewrite = XMLRewrite(parse(BytesIO(src)), 'p', 'ns_Y', rules=rules)
        rewrite.applyRules()
        self.assertEqualsWS('<p xmlns="ns_Y"><q><r>ape</r></q></p>', rewrite.toString())

    def testNamespacesInTemplates(self):
        src = b"<a><b>ape</b></a>"
        rules = [('q', 'b', ('.',), '<X:r>%s</X:r>')]
        rewrite = XMLRewrite(parse(BytesIO(src)), 'p', 'ns_Y', rules=rules, newNsMap = {'X': 'ns_X'})
        rewrite.applyRules()
        self.assertTrue('xmlns:X="ns_X"' in rewrite.toString())
        self.assertTrue('xmlns="ns_Y"' in rewrite.toString())
        self.assertTrue('<q><X:r>ape</X:r></q></p>', rewrite.toString())

    def testCompleteRecord(self):
        with open(abspath(dirname(__file__))+'/data/triple-lrecord.xml') as f:
            data = f.read()
        rules = [
#contextPath, oldElementPath, valuePaths, template
('general/title', 'general/title/langstring', ('language', 'value'), '<string language="%s">%s</string>'),
('general', 'general/catalogentry', ('catalog', 'entry/langstring/value'), '<identifier><catalog>%s</catalog><entry>%s</entry></identifier>'),
('general', 'general/grouplanguage', ('.',), '<language>%s</language>'),
('general/description', 'general/description/langstring', ('language', 'value'), '<string language="%s">%s</string>\n'),
('lifeCycle/contribute', 'lifecycle/contribute/role', ('source/langstring/value', 'value/langstring/value'), '<role><source>%s</source><value>%s</value></role>'),
('lifeCycle/contribute', 'lifecycle/contribute/centity', ('vcard',), '<entity>%s</entity>'),
('lifeCycle/contribute/date', 'lifecycle/contribute/date', ('datetime',), '<dateTime>%s</dateTime>',
     [[('(\d{2,4}-\d{2}-\d{2}) (\d{2}:\d{2})', '%sT%s',),]]),
('metaMetadata', 'metametadata/metadatascheme', ('.',), '<metadataSchema>%s</metadataSchema>'),
('technical/format', 'technical/format', ('.',), '%s'),
('technical/location', 'technical/location', ('value',), '%s'),
('educational', 'educational/learningresourcetype', ('source/langstring/value', 'value/langstring/value'), '<learningResourceType><source>%s</source><value>%s</value></learningResourceType>'),
('educational', 'educational/context', ('source/langstring/value', 'value/langstring/value'), '<context><source>%s</source><value>%s</value></context>'),
('rights', 'rights/cost', ('source/langstring/value', 'value/langstring/value'), '<cost><source>%s</source><value>%s</value></cost>'),
('rights', 'rights/copyrightandotherrestrictions', ('source/langstring/value', 'value/langstring/value'), '<copyrightAndOtherRestrictions><source>%s</source><value>%s</value></copyrightAndOtherRestrictions>'),
('classification', 'classification/purpose', ('source/langstring/value', 'value/langstring/value'), '<purpose><source>%s</source><value>%s</value></purpose>'),
('classification/taxonPath/source', 'classification/taxonpath/source/langstring', ('language', 'value'), '<string language="%s">%s</string>'),
('classification/taxonPath', 'classification/taxonpath', ('taxon/id',), '<taxon><id>%s</id></taxon>'),
('classification/taxonPath/taxon/entry', 'classification/taxonpath/taxon/entry', ('langstring/language', 'langstring/value'), '<string language="%s">%s</string>\n'),

]
        """
"""

        should = b"""<lom>
<general>
<title>
<string language="nl">Religie Nu (12) Kan theater zonder religie?</string>
</title>
<identifier>
<catalog>nl.uva.uba.triple-l</catalog>
<entry>217134</entry>
</identifier>
<language>nl</language>
<description>
<string language="nl">Kunst zonder God is een verarming.

Religie - een wijder begrip schenkt kleur en diepgang aan het leven in de kunst. In dramatisch opzicht geven goden de mogelijkheid aan de toneelschrijver de geest van de mens te projecteren. Grote schrijvers hebben ver voor het Christendom zijn intrede deed de mens in de kosmos geplaatst, van waaruit allerlei krachten hem bedreigen of te hulp schieten of hem uitdagen. Van Aischylos tot Sartre, van Shakespeare tot Beckett hebben goden het leven van dramatische figuren benvloed. En zo zal het blijven. Het wachten is op Godot.</string>
</description>
</general>
<lifeCycle>
<contribute>
<role>
<source>LOMv1.0</source>
<value>Speaker</value></role>
<entity>
BEGIN:VCARD
VERSION:2.1
N:Vos;E.
FN:E. Vos
END:VCARD
				</entity>
<date>
<dateTime>2006-11-28T19:00</dateTime></date>
</contribute>
</lifeCycle>
<metaMetadata>
<metadataSchema>LORENET</metadataSchema>
</metaMetadata>
<technical>
<format>text/html</format>
<location>http://www.iis-communities.nl/access/content/group/Religie/MAP%201/College%2012%20-%20Erik%20Vos%20-%2028-11-06</location></technical>
<educational>
<learningResourceType>
<source>TPPOVOv1.0</source>
<value>informatiebron</value>
</learningResourceType>
<context>
<source>TPPOVOv1.0</source>
<value>WO</value>
</context>
</educational>
<rights>
<cost>
<source>LOMv1.0</source>
<value>nee</value>
</cost>
<copyrightAndOtherRestrictions>
<source>CCv2.5</source>
<value>http://creativecommons.org/licenses/by-nc-sa/2.5/nl/</value>
</copyrightAndOtherRestrictions>
</rights>
<classification>
<purpose>
<source></source>
<value></value>
</purpose>
<taxonPath>
<source>
<string language="x-none">NBC</string></source>
<taxon>
<id>24</id>
<entry>
<string language="nl">Theaterwetenschap, muziekwetenschap</string>
<string language="en">Dramaturgy, musicology</string>
</entry>
</taxon>
</taxonPath>
</classification>
</lom>
"""
        self.assertRewrite(rules, 'lom', should, data.encode('utf-8'))

    def testTaxonPath(self):
        src = b"""<root>
            <classification>
                <taxonpath>
                    <taxon>
                        <id>2</id>
                        <entry>
                            <langstring><value>aap</value></langstring>
                            <langstring><value>noot</value></langstring>
                        </entry>
                    </taxon>
                </taxonpath>
                <taxonpath>
                    <taxon>
                        <id>1</id>
                        <entry>
                            <langstring><value>boom</value></langstring>
                            <langstring><value>vuur</value></langstring>
                        </entry>
                    </taxon>
                </taxonpath>
            </classification>
            </root>"""
        dst = b"""<lom>
  <classification>
    <taxonPath>
      <taxon>
        <entry>
          <ja>aap</ja>
          <ja>noot</ja>
        </entry>
      </taxon>
    </taxonPath>
    <taxonPath>
      <taxon>
        <entry>
          <ja>boom</ja>
          <ja>vuur</ja>
        </entry>
      </taxon>
    </taxonPath>
  </classification>
</lom>"""
        rules = [
                    #('classification', 'classification', ('taxonPath/taxon/id',), '<taxonPath><taxon><id>%s</id></taxon></taxonPath>'),
                    ('classification/taxonPath/taxon/entry', 'classification/taxonpath/taxon/entry', ('langstring/value',), '<ja>%s</ja>') ]
        self.assertRewrite(rules, 'lom', dst, src)

    def testNamespaceInNewTag(self):
        rules = [('a:p', 'b:q', ('.',), '%s')]
        src = b'<y><c:q xmlns:c="http://b">aap</c:q></y>'
        dst = b'<z xmlns:a="http://a"><a:p>aap</a:p></z>'
        self.assertRewrite(rules, 'z', dst, src, sourceNsMap={'b': 'http://b'}, newNsMap={'a': 'http://a'})

    def testNormalizeDiffersForEachMatch(self):
        rules = [('a', 'b', ('c', 'd'), '<result c="%s">%s</result>', [[('(.*)', 'CCC %s CCC', (str,))],[('(.*)', 'DDD %s DDD', (str,))]])]
        src = b'<outerTag><b><c>ccc</c><d>ddd</d></b></outerTag>'
        dst = b'<rootTag><a><result c="CCC ccc CCC">DDD ddd DDD</result></a></rootTag>'
        self.assertRewrite(rules, 'rootTag', dst, src)

    def testXPathAfterCrosswalkTest(self):
        """after building a complete new lxmltree, xpaths dont' work.
        This is probably a bug in the lxml parser. This test will
        test our workaround"""
        rules = [('mods:originInfo', 'b', ('c',), '<mods:dateIssued>%s</mods:dateIssued>')]
        src = b"<a><b><c>2008-08-01</c></b></a>"
        rewrite = XMLRewrite(
            parse(BytesIO(src)),
            rootTagName='mods',
            defaultNameSpace = "http://www.loc.gov/mods/v3",
            newNsMap = {'mods': 'http://www.loc.gov/mods/v3'},
            schemaLocation={},
            rules=rules,
            sourceNsMap={})
        rewrite.applyRules()

        theNewTree = rewrite._newTree # hack to get the original lxml node.
        lxmlResult = theNewTree.xpath('/mods:mods/mods:originInfo/mods:dateIssued/text()', namespaces={'mods': 'http://www.loc.gov/mods/v3'})
        self.assertEqual([], lxmlResult, """If this test fails, lxml has finally resolved a bug.""")

        newNode = rewrite.asLxml()
        result = newNode.xpath('/mods:mods/mods:originInfo/mods:dateIssued/text()', namespaces={'mods': 'http://www.loc.gov/mods/v3'})

        self.assertEqual(['2008-08-01'], result)

    def testWithDestinationLengthLongerThanSource(self):
        rules = [(   'dst:one/dst:two/dst:three',
            'src:one/src:two',
            ('.',), '%s'
            )]
        src = b'<src><one xmlns="source"><two>data</two></one></src>'
        dst = b'<rootTag xmlns:dst="destination"><dst:one><dst:two><dst:three>data</dst:three></dst:two></dst:one></rootTag>'
        self.assertRewrite(rules, 'rootTag', dst, src, sourceNsMap={'src': 'source'}, newNsMap={'dst': 'destination'})


    def testNormalizeWithFunction(self):
        def myNormalization(c,d):
            return c.lower(), d.lower()
        rules = [('y', 'b', ('c','d'), '%s %s', myNormalization)]
        src = b'<a><b><c>CCC</c><d>DDD</d></b></a>'
        dst = b'<z><y>ccc ddd</y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testNormalizeWithFunctionReturningOneElement(self):
        def myNormalization(c,d):
            return '%s %s' % (c.lower(), d.lower()),
        rules = [('y', 'b', ('c','d'), '%s', myNormalization)]
        src = b'<a><b><c>CCC</c><d>DDD</d></b></a>'
        dst = b'<z><y>ccc ddd</y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testUseNoneValueFromNormalizationAsFilter(self):
        def filterIgnored(value):
            if 'ignored' in value:
                return (None,)
            return (value,)
        rules = [('y', 'b', ('.',), '%s', filterIgnored)]
        src = b'<a><b>ignoredvalue</b><b>value</b></a>'
        # in this case an empty tag will be created.
        # this is an already existing "feature"
        dst = b'<z><y/><y>value</y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testNormalizationRulesWithFunction(self):
        rules = [('y', 'b',
            ('c','d'),
            '%s %s',
            (
                [('(.*)', '%s', (str.lower,))],
                str.lower
            ))]
        src = b'<a><b><c>CCC</c><d>DDD</d></b></a>'
        dst = b'<z><y>ccc ddd</y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testUseNoneValueFromNormalizationRuleAsFilter(self):
        def filterIgnored(value):
            return None if 'ignored' in value else value
        rules = [('y', 'b', ('.',), '%s', [filterIgnored])]
        src = b'<a><b>ignoredvalue</b><b>value</b></a>'
        # in this case an empty tag will be created.
        # this is an already existing "feature"
        dst = b'<z><y/><y>value</y></z>'
        self.assertRewrite(rules, 'z', dst, src)

    def testWithLomRecord(self):
        lomNamespace = 'http://ltsc.ieee.org/xsd/LOM'
        rules = [(
            'lom:general/lom:identifier/lom:catalog',
            'imsmd:general/imsmd:catalogentry/imsmd:catalog',
            ('.',),
            '%s'
        )]
        src = b"""<lom:lom xmlns:lom="http://www.imsglobal.org/xsd/imsmd_v1p2">
    <lom:general><lom:catalogentry><lom:catalog>ISBN</lom:catalog></lom:catalogentry></lom:general>
</lom:lom>"""
        dst = b"""<lom xmlns="http://ltsc.ieee.org/xsd/LOM">
    <general>
        <identifier>
            <catalog>ISBN</catalog>
        </identifier>
    </general>
</lom>"""
        self.assertRewrite(rules, 'lom', dst, src, newNsMap={'lom':lomNamespace}, sourceNsMap={'imsmd':'http://www.imsglobal.org/xsd/imsmd_v1p2'}, defaultNamespace=lomNamespace)

    def testWithLomRecordNamespaceSortingInRootElement(self):
        lomNamespace = 'http://ltsc.ieee.org/xsd/LOM'
        rules = [(
            'lom:general/lom:identifier/lom:catalog',
            'imsmd:general/imsmd:catalogentry/imsmd:catalog',
            ('.',),
            '%s'
        )]
        src = b"""<lom:lom xmlns:lom="http://www.imsglobal.org/xsd/imsmd_v1p2">
</lom:lom>"""
        dst = """<lom xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="%s"  xsi:schemaLocation="%s http://example.org/xsd"/>""" % (lomNamespace, lomNamespace)
        dst = dst.encode('UTF-8')
        self.assertRewrite(rules, 'lom', dst, src,
                newNsMap={'lom':lomNamespace, 'xsi':'http://www.w3.org/2001/XMLSchema-instance'},
                sourceNsMap={'imsmd':'http://www.imsglobal.org/xsd/imsmd_v1p2'},
                defaultNamespace=lomNamespace,
                schemaLocation={lomNamespace:'http://example.org/xsd'})


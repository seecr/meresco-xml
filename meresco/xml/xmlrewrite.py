## begin license ##
# 
# "Meresco-Xml" is a set of components and tools for handling xml data objects. 
# 
# Copyright (C) 2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
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

from StringIO import StringIO
from itertools import groupby
from normalize import Normalize
from lxml.etree import Element, ElementTree, SubElement, parse, XMLSyntaxError, XPathSyntaxError, _Element, XMLParser
from lxml.objectify import ObjectifiedElement
from xml.sax.saxutils import escape as _xmlEscape, unescape as xmlUnescape
from re import compile
try:
    from meresco.components import lxmltostring
except ImportError:
    # backwards compatible
    from lxml.etree import tostring
    def lxmltostring(lxmlNode, **kwargs):
        return tostring(lxmlNode, encoding="UTF-8", **kwargs)


unzip = lambda listOfTuples: zip(*listOfTuples)
xPathSplitter = compile('[^/]*\[[^\]]*\]|[^/]+')

def xmlEscape(value):
    return _xmlEscape(value) if value != None else value

def xpath(node, path, nsmap):
    try:
        return node.xpath(path, namespaces=nsmap)
    except XPathSyntaxError, e:
        raise XPathSyntaxError, '"%s" defined prefixes: %s' % (path, nsmap)

class XMLRewrite:
    """
    XMLRewrite processes rules that create a new XML record out of an existing one.
    The new record is written from scratch.  The rules are tuples in the following format:
    (newPath, oldPath, (valuePath,...), template, *normalizationRules)

    newPath:    The names of the elements to create under the root tag e.g. 'lifecycle/contribute'.
        The multiplicity of these elements will correspond to the oldPath so the tree described by
        newPath will be exactly the same as the one described by oldPath, except for the
        tag names.  If newPath is longer than oldPath, the system descents into newPath --
        meanwhile creating elements when needed -- until the remainder is as long as oldPath.
        The it starts creating elements from there.

    oldPath:        The names of the elements in the source that are to be taken as source, e.g.
        'lifeCycle/contribute'.  For each elements found in this path a corresponding element in newPath
        is created.  The subtree identified by oldPath is mirrored in newPath.  If oldPath is longer
        than newPath, the systems descents into oldPath until the remainder is as long as newPath.
        It then starts mirroring the tree from there.

    (valuePath,...):        For each leaf element found in oldPath a tuple of values is collected by
        evaluating the valuePaths relative to the leaf element.  E.g. to collect 'language' and 'value'
        from a 'langstring' element within the leaf element, use: ('langstring/language', langstring/value').
        The system will create a series of value tuples when the valuePaths have multiple   matches, e.g.
        when multiple 'langstring's are present.

    template:   Each tuple with values from valuePath is applied to a template string using the modulo
        operator.  The template must be a Python formatting string with as many slots as valuePaths. For
        example '<string language="%s">%s</language>'. When valuePaths result in multiple matches,
        the template is applied once for each tuple in the series.  The template can contain either valid
        XML or plain text.  Valid XML is parsed and added to the leaf element. Plain text is inserted into
        the leaf element directly.

    normalizationRules:  This is an optional list of rules which will be used to normalize the values
        returned by the valuePath.
        Default use:
            Each list of rules are executed using the Normalize class for each value yielded by
            valuePaths, before it is fed to the template.
            See the documentation of Normalize for more information.
            E.g. for two valuePaths the normalizationRules might look like:
            [
                [('.*', '%s', (lambda x: x.lower(),)],
                [('.*', 'text %s text')]
            ]
        Alternative use of rules:
            Instead of using a list of rules you can use a function to normalize the corresponding 
            valuePath.
            E.g. the previous example can also be written as:
            [
                lambda x: x.lower(),
                [('.*', 'text %s text')]
            ]
        Alternative use of normalizationRules:
            the normalizationRules can also be a function which will take the values from valuePath as
            input.  E.g. a method like def myMethod(arg0, arg1): ... can be used when there are 2 
            valuePaths specified.



    """

    def __init__(self, orgElementTree, rootTagName=None, defaultNameSpace=None, schemaLocation=None,
                 rules=None, vocabDict=None, newNsMap=None, sourceNsMap=None):
        assert isinstance(rootTagName, basestring), type(rootTagName)

        schemaLocation = schemaLocation or {}
        vocabDict = vocabDict or {}
        newNsMap = newNsMap or {}
        sourceNsMap = sourceNsMap or {}
       
        self.sourceNsMap = sourceNsMap
        self.orgTree = orgElementTree
        if type(orgElementTree) == ObjectifiedElement:
            self.orgTree = ElementTree(orgElementTree)

        self.newNsMap = newNsMap

        self.defaultNameSpace = defaultNameSpace
        if defaultNameSpace:
            newNsMap = dict((k,v) for k,v in newNsMap.items() if v != defaultNameSpace)
            newNsMap[None] = defaultNameSpace
        
        rootTag = rootTagName.split(":")
        if len(rootTag) > 1:
            rootTagName = "{%s}%s" % (newNsMap[rootTag[0]], rootTag[1])
        self._newTree = ElementTree(Element(rootTagName, nsmap=newNsMap))
        if schemaLocation:
            xsiSchemaLocation = ' '.join('%s %s' % (ns, xsd) for ns, xsd in schemaLocation.items())
            self._newTree.getroot().set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', xsiSchemaLocation)

        self.rules = rules
        self.globalVocabRewrite = vocabDict
        self.globalVocabRewrite[None] = ''

    def toString(self):
        return lxmltostring(self._newTree, pretty_print=True)

    def asLxml(self):
        return parse(StringIO(lxmltostring(self._newTree)))

    def descent(self, (orgContext, orgPath), (newContext, newPath), *args):
        if len(orgPath) > len(newPath):
            for orgContext in xpath(orgContext, orgPath[0], self.sourceNsMap):
                self.descent((orgContext, orgPath[1:]), (newContext, newPath), *args)
        elif len(newPath) > len(orgPath):
            newContexts = xpath(newContext, newPath[0], self.newNsMap)
            if not newContexts:
                self._createSubElement(newContext, newPath[0])
            for newContext in xpath(newContext, newPath[0], self.newNsMap):
                self.descent((orgContext, orgPath), (newContext, newPath[1:]), *args)
        else:
            if orgPath:
                orgSubContexts = xpath(orgContext, orgPath[0], self.sourceNsMap)
                newSubContexts = xpath(newContext, newPath[0], self.newNsMap)
                for n in range(len(newSubContexts), len(orgSubContexts)):
                    self._createSubElement(newContext, newPath[0])
                newSubContexts = xpath(newContext, newPath[0], self.newNsMap)
                for orgSubContext, newSubContext in zip(orgSubContexts, newSubContexts):
                    self.descent((orgSubContext, orgPath[1:]), (newSubContext, newPath[1:]), *args)
            else:
                self.createSubElements(orgContext, newContext, *args)

    def _createSubElement(self, newContext, tagName):
        if ':' in tagName:
            prefix, tagName = tagName.split(':', 1)
            tagName = '{%s}%s' % (self.newNsMap[prefix], tagName)
        SubElement(newContext, tagName)

    def createSubElements(self, orgContext, newContext, valuePaths, template, normalizationRules=None):
        valueElements = tuple(xpath(orgContext, path, self.sourceNsMap) for path in valuePaths)
        values = tuple(self.mapValues(values, normalizationRules) for values in unzip(valueElements))
        for arguments in values:
            if None in arguments:
                continue
            try:
                data = template % arguments
            except TypeError, e:
                raise TypeError('%s: %s: %s %% %s' % (e, context, template, arguments))
            if data and data.startswith('<'):
                try:
                    nsString = ' '.join('xmlns:%s="%s"' % (prefix,namespace)
                        for prefix, namespace in self.newNsMap.items())
                    wrapperTag = '<root ' + nsString +">" + data + "</root>"
                    newElements = parse(StringIO(wrapperTag), XMLParser(remove_blank_text=True)).getroot().getchildren()
                except XMLSyntaxError, e:
                    raise XMLSyntaxError('%s: %s' % (str(e), (template, arguments, data)))
                for newElement in newElements:
                    newContext.append(newElement)
            elif data:
                newContext.text = unicode(xmlUnescape(data))

    def mapValues(self, values, normalizationRulesListOrFunction):
        newValues = (self.globalVocabRewrite.get(getattr(value,'text', value), getattr(value,'text', value)) for value in values)
        if normalizationRulesListOrFunction:
            if callable(normalizationRulesListOrFunction):
                newValues = normalizationRulesListOrFunction(*newValues)
                assert isinstance(newValues, tuple), '%s should return a tuple.' % normalizationRulesListOrFunction
            else:
                normalizedValues = []
                for newValue, normalizationRulesOrFunction in zip(newValues, normalizationRulesListOrFunction):
                    if callable(normalizationRulesOrFunction):
                        newNormalizedValue = normalizationRulesOrFunction(newValue)
                    else:
                        newNormalizedValue = Normalize(normalizationRulesOrFunction).process(newValue)
                    normalizedValues.append(newNormalizedValue)
                newValues = normalizedValues
        return tuple(xmlEscape(value) for value in newValues)

    def rewrite2(self, dstEltPath, srcEltPath, *args):
        self.descent((self.orgTree.getroot(), xPathSplitter.findall(srcEltPath)), (self._newTree.getroot(), xPathSplitter.findall(dstEltPath)), *args)

    def applyRules(self):
        for rule in self.rules:
            self.rewrite2(*rule)

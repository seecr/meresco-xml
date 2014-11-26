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
from lxml.etree import _ElementStringResult


class _namespaces(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._reverse = dict((v,k) for k,v in self.items())
        self._curieToTag = {}
        self._curieToUri = {}
        self._tagToCurie = {}
        self._uriToCurie = {}

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __getitem__(self, key):
        _, xmlns, key = key.rpartition('xmlns_')
        result = dict.__getitem__(self, key)
        if xmlns == 'xmlns_':
            return 'xmlns:%s="%s"' % (key, result)
        return result

    def xpath(self, node, path):
        return [
            str(n) if type(n) is _ElementStringResult else n
            for n in node.xpath(path, namespaces=self)
        ]

    def xpathFirst(self, node, path):
        nodes = self.xpath(node, path)
        return nodes[0] if nodes else None

    def copyUpdate(self, d):
        return self.__class__(dict(self, **d))

    def select(self, *prefixes):
        return self.__class__((k, self[k]) for k in prefixes)

    def curieToTag(self, name):
        try:
            return self._curieToTag[name]
        except KeyError:
            pass
        ns, value = name.split(':', 1)
        value = self._curieToTag[name] = '{%s}%s' % (self[ns], value)
        return value

    expandNsTag = curieToTag  # deprecated
    expandNs = curieToTag  # deprecated

    def curieToUri(self, name):
        try:
            return self._curieToUri[name]
        except KeyError:
            pass
        ns, value = name.split(':', 1)
        value = self._curieToUri[name] = '%s%s' % (self[ns], value)
        return value

    expandNsUri = curieToUri  # deprecated

    def tagToCurie(self, tag):
        try:
            return self._tagToCurie[tag]
        except KeyError:
            pass
        if not (tag.startswith('{') and '}' in tag):
            raise ValueError("Expected '{some:uri}tagname', but got '%s'" % tag)
        uri, _, localtag = tag[1:].partition('}')
        prefix = self._reverse[uri]
        value = self._tagToCurie[tag] = '%s:%s' % (prefix, localtag)
        return value

    prefixedTag = tagToCurie  # deprecated, kept for backwards compatibility

    def uriToCurie(self, uri):
        try:
            return self._uriToCurie[uri]
        except KeyError:
            pass
        lhs, divider, localPart = uri.rpartition('#')
        if not divider:
            lhs, divider, localPart = uri.rpartition('/')
        if not divider:
            raise ValueError('Uri <%s> does not have a hash or slash, cannot guess namespace from this Uri.' % uri)
        prefix = self.nsToPrefix(lhs + divider)
        value = self._uriToCurie[uri] = None if prefix is None else prefix + ':' + localPart
        return value

    def nsToPrefix(self, namespace):
        return self._reverse.get(namespace)

    def _notsupported(self, *args, **kwargs):
        raise TypeError('The namespaces object is readonly. Use select(..) or copyUpdate(..) to create a new namespaces object.')

    __delitem__ = _notsupported
    __setitem__ = _notsupported
    clear = _notsupported
    setdefault = _notsupported
    update = _notsupported


namespaces = _namespaces(
    dc="http://purl.org/dc/elements/1.1/",
    dcterms="http://purl.org/dc/terms/",
    diag='http://www.loc.gov/zing/srw/diagnostic/',
    document="http://meresco.org/namespace/harvester/document",
    drilldown="http://meresco.org/namespace/drilldown",
    edm="http://www.europeana.eu/schemas/edm/",
    foaf="http://xmlns.com/foaf/0.1/",
    html="http://www.w3.org/1999/xhtml",
    meresco_ext="http://meresco.org/namespace/xslt/extensions",
    meresco_srw="http://meresco.org/namespace/srw#",
    meta="http://meresco.org/namespace/harvester/meta",
    oai="http://www.openarchives.org/OAI/2.0/",
    oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/",
    oaiprov="http://www.openarchives.org/OAI/2.0/provenance",
    owl="http://www.w3.org/2002/07/owl#",
    prov="http://www.w3.org/ns/prov#",
    rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    rdfs="http://www.w3.org/2000/01/rdf-schema#",
    sfr="http://docs.oasis-open.org/ns/search-ws/facetedResults",
    skos="http://www.w3.org/2004/02/skos/core#",
    soapenv="http://schemas.xmlsoap.org/soap/envelope/",
    srw='http://www.loc.gov/zing/srw/',
    srw_dc='info:srw/schema/1/dc-v1.1',
    sug='http://meresco.org/namespace/suggestions',
    ti='http://meresco.org/namespace/timing',
    ucp='info:lc/xmlns/update-v1',
    wsdl='http://schemas.xmlsoap.org/wsdl/',
    xcql='http://www.loc.gov/zing/cql/xcql/',
    xml='http://www.w3.org/XML/1998/namespace',
    xsd='http://www.w3.org/2001/XMLSchema',
    xsi='http://www.w3.org/2001/XMLSchema-instance',
    xsl='http://www.w3.org/1999/XSL/Transform',
    zr='http://explain.z3950.org/dtd/2.0/',
)

xpath = namespaces.xpath
xpathFirst = namespaces.xpathFirst

curieToTag = namespaces.curieToTag
curieToUri = namespaces.curieToUri
tagToCurie = namespaces.tagToCurie
uriToCurie = namespaces.uriToCurie

expandNs = namespaces.curieToTag  # deprecated
expandNsUri = namespaces.curieToUri  # deprecated

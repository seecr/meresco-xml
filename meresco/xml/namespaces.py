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

class _namespaces(dict):
    def __getattr__(self, key):
        try: 
            return self[key]
        except KeyError, e:
            raise AttributeError(key)

    def xpath(self, node, path):
        return node.xpath(path, namespaces=self)

    def xpathFirst(self, node, path):
        nodes = self.xpath(node, path)
        return nodes[0] if nodes else None

    def copyUpdate(self, d):
        newNamespaces = self.__class__(self)
        newNamespaces.update(d)
        return newNamespaces

    def select(self, *prefixes):
        return self.__class__((k, self[k]) for k in prefixes)

    def expandNs(self, name):
        ns, value = name.split(':', 1)
        return '{%s}%s' % (self[ns], value)


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
    srw='http://www.loc.gov/zing/srw/',
    srw_dc='info:srw/schema/1/dc-v1.1',
    sug='http://meresco.org/namespace/suggestions',
    ti='http://meresco.org/namespace/timing',
    ucp='info:lc/xmlns/update-v1',
    wsdl='http://schemas.xmlsoap.org/wsdl/',
    xsd='http://www.w3.org/2001/XMLSchema',
    xsi='http://www.w3.org/2001/XMLSchema-instance',
    xsl='http://www.w3.org/1999/XSL/Transform',
    zr='http://explain.z3950.org/dtd/2.0/',
)

xpath = namespaces.xpath
xpathFirst = namespaces.xpathFirst
expandNs = namespaces.expandNs
